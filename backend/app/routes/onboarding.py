"""
Onboarding routes — Tenant provisioning, business setup, channel auto-setup, progress tracking.
"""

import uuid
import re
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import structlog

from pydantic import BaseModel
import httpx
from bs4 import BeautifulSoup
from app.schemas import ScrapeUrlRequest, ScrapeUrlResponse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import get_settings
from app.auth import require_superadmin, get_current_user, check_tenant_access
from app.models import (
    Tenant, User, TenantMembership, Business,
    OnboardingProgress, KBDocument,
)
from app.schemas import (
    ProvisionTenantRequest, ProvisionTenantResponse,
    OnboardingProgressResponse, InviteUserRequest,
)

logger = structlog.get_logger()
router = APIRouter()


def _slugify(name: str) -> str:
    """Convert a name to a URL-safe slug."""
    slug = re.sub(r"[^\w\s-]", "", name.lower())
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug.strip("-")[:255]


def _compute_score(progress: OnboardingProgress) -> tuple[int, str | None]:
    """
    Compute the gamified onboarding completion score (0-100) and next milestone.
    """
    milestones = [
        ("account_created", True, 10),  # Always true once provisioned
        ("channels_connected", _channels_connected(progress), 20),
        ("kb_populated", progress.kb_populated, 20),
        ("first_inquiry", progress.first_inquiry_received, 15),
        ("first_morning_report", progress.first_morning_report_sent, 15),
        ("first_lead", progress.first_lead_captured, 10),
        ("owner_first_login", progress.owner_first_login, 10),
    ]

    score = 0
    next_milestone = None
    for name, completed, points in milestones:
        if completed:
            score += points
        elif next_milestone is None:
            next_milestone = name

    return score, next_milestone


def _channels_connected(progress: OnboardingProgress) -> bool:
    """Check if all non-skipped channels are active."""
    for status in [progress.whatsapp_status, progress.email_status, progress.website_status]:
        if status not in ("active", "skipped"):
            return False
    return True


# ─────────────────────────────────────────────────────────────
# Tenant Provisioning (SuperAdmin)
# ─────────────────────────────────────────────────────────────

@router.post("/onboarding/provision-tenant", response_model=ProvisionTenantResponse)
async def provision_tenant(
    body: ProvisionTenantRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """
    One-click tenant provisioning.
    Creates Tenant + Business + User + TenantMembership + OnboardingProgress.
    Sends magic link to owner. Triggers async channel setup.
    """
    settings = get_settings()

    # 1. Create Tenant
    tenant_slug = _slugify(body.tenant_name)

    # Ensure slug uniqueness
    existing = await db.execute(select(Tenant).where(Tenant.slug == tenant_slug))
    if existing.scalar_one_or_none():
        tenant_slug = f"{tenant_slug}-{uuid.uuid4().hex[:6]}"

    pilot_start = datetime.now(timezone.utc) if body.subscription_tier == "pilot" else None
    pilot_end = pilot_start + timedelta(days=body.pilot_duration_days) if pilot_start else None

    tenant = Tenant(
        name=body.tenant_name,
        slug=tenant_slug,
        subscription_tier=body.subscription_tier,
        subscription_status="trialing" if body.subscription_tier == "pilot" else "active",
        pilot_start_date=pilot_start,
        pilot_end_date=pilot_end,
        assigned_account_manager=body.assigned_account_manager,
    )
    db.add(tenant)
    await db.flush()  # Get tenant.id

    # 2. Create Business
    business_slug = _slugify(body.business_name)
    existing_prop = await db.execute(select(Business).where(Business.slug == business_slug))
    if existing_prop.scalar_one_or_none():
        business_slug = f"{business_slug}-{uuid.uuid4().hex[:6]}"

    prop = Business(
        tenant_id=tenant.id,
        name=body.business_name,
        slug=business_slug,
        timezone=body.timezone,
        plan_tier=body.subscription_tier,
        whatsapp_number=body.whatsapp_number,
        whatsapp_provider=body.whatsapp_provider,
        twilio_phone_number=body.twilio_phone_number,
        notification_email=body.reservation_email,
        website_url=body.website_url,
    )
    db.add(prop)
    await db.flush()

    # 3. Create User via Supabase Auth Admin API (sends magic link)
    magic_link_sent = False
    user_id = uuid.uuid4()

    if settings.supabase_url and settings.supabase_service_role_key:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.supabase_url}/auth/v1/admin/users",
                    headers={
                        "apikey": settings.supabase_service_role_key,
                        "Authorization": f"Bearer {settings.supabase_service_role_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "email": body.owner_email,
                        "email_confirm": True,
                        "user_metadata": {
                            "full_name": body.owner_name,
                            "tenant_id": str(tenant.id),
                        },
                    },
                    timeout=10.0,
                )
                if response.status_code < 300:
                    supabase_user = response.json()
                    user_id = uuid.UUID(supabase_user["id"])
                    logger.info("Supabase user created", user_id=str(user_id), email=body.owner_email)

                    # Send magic link
                    ml_resp = await client.post(
                        f"{settings.supabase_url}/auth/v1/magiclink",
                        headers={
                            "apikey": settings.supabase_anon_key,
                            "Content-Type": "application/json",
                        },
                        json={
                            "email": body.owner_email,
                            "options": {
                                "emailRedirectTo": settings.allowed_origins.split(",")[0]
                            }
                        },
                        timeout=10.0,
                    )
                    magic_link_sent = ml_resp.status_code < 300
                else:
                    logger.warning("Supabase user creation failed", status=response.status_code, body=response.text)
        except Exception as e:
            logger.error("Supabase API error during provisioning", error=str(e))
    else:
        logger.info("Supabase not configured — creating local user only", email=body.owner_email)

    # Create local User record
    user = User(
        id=user_id,
        email=body.owner_email,
        full_name=body.owner_name,
        phone=body.owner_phone,
    )
    db.add(user)
    await db.flush()

    # 4. Create TenantMembership
    membership = TenantMembership(
        user_id=user.id,
        tenant_id=tenant.id,
        role="owner",
    )
    db.add(membership)

    # 5. Create OnboardingProgress
    progress = OnboardingProgress(
        tenant_id=tenant.id,
        business_id=prop.id,
        whatsapp_status="pending" if "whatsapp" in body.preferred_channels else "skipped",
        email_status="pending" if "email" in body.preferred_channels else "skipped",
        website_status="pending" if "website" in body.preferred_channels else "skipped",
    )
    db.add(progress)

    # 6. Seed "Getting Started" KB documents
    getting_started_docs = [
        KBDocument(
            business_id=prop.id,
            doc_type="faqs",
            title="Welcome to Nocturn AI",
            content=(
                "Welcome to Nocturn AI! This is your AI-powered hotel concierge. "
                "I can help answer guest inquiries about your business 24/7, including room rates, "
                "facilities, directions, and booking inquiries. "
                "Your knowledge base will be customized with your specific business information."
            ),
        ),
    ]
    for doc in getting_started_docs:
        db.add(doc)

    await db.commit()

    # 7. Trigger async channel setup
    background_tasks.add_task(
        _setup_channels_async,
        tenant_id=str(tenant.id),
        business_id=str(prop.id),
        channels=body.preferred_channels,
        whatsapp_provider=body.whatsapp_provider,
    )

    logger.info(
        "Tenant provisioned",
        tenant_id=str(tenant.id),
        business_id=str(prop.id),
        user_id=str(user.id),
        tier=body.subscription_tier,
    )

    return ProvisionTenantResponse(
        tenant_id=tenant.id,
        business_id=prop.id,
        user_id=user.id,
        magic_link_sent=magic_link_sent,
        channels_setup_initiated=True,
        message=f"Tenant '{body.tenant_name}' provisioned successfully. "
                f"{'Magic link sent to ' + body.owner_email if magic_link_sent else 'Supabase not configured — manual login setup required.'}"
    )


async def _setup_channels_async(
    tenant_id: str,
    business_id: str,
    channels: list[str],
    whatsapp_provider: str = "meta",
):
    """
    Background task: Attempt to auto-configure each selected channel.
    Updates OnboardingProgress with status per channel.
    """
    from app.database import async_session_factory
    from app.services.channel_setup import setup_channels

    try:
        async with async_session_factory() as db:
            await setup_channels(
                db=db,
                tenant_id=tenant_id,
                business_id=business_id,
                channels=channels,
                whatsapp_provider=whatsapp_provider,
            )
    except Exception as e:
        logger.error("Channel setup background task failed", error=str(e), tenant_id=tenant_id)


# ─────────────────────────────────────────────────────────────
# Self-Service Provisioning (First-time magic link users)
# ─────────────────────────────────────────────────────────────

@router.post("/onboarding/self-provision")
async def self_provision(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Self-service tenant provisioning for new users arriving via magic link.
    Idempotent — returns existing tenant/business if already provisioned.
    Creates: Tenant + Business + TenantMembership + OnboardingProgress.
    """
    # Check if user already has a membership
    stmt = select(TenantMembership).where(TenantMembership.user_id == user.id)
    result = await db.execute(stmt)
    existing_membership = result.scalar_one_or_none()

    if existing_membership:
        # Return existing setup
        prop_stmt = (
            select(Business)
            .where(Business.tenant_id == existing_membership.tenant_id)
            .order_by(Business.created_at)
        )
        prop_result = await db.execute(prop_stmt)
        prop = prop_result.scalar_one_or_none()
        return {
            "tenant_id": str(existing_membership.tenant_id),
            "business_id": str(prop.id) if prop else None,
            "business_name": prop.name if prop else None,
            "is_new": False,
        }

    hotel_name = (body.get("hotel_name") or "My Hotel").strip() or "My Hotel"

    # Create Tenant
    tenant_slug = _slugify(hotel_name)
    slug_check = await db.execute(select(Tenant).where(Tenant.slug == tenant_slug))
    if slug_check.scalar_one_or_none():
        tenant_slug = f"{tenant_slug}-{uuid.uuid4().hex[:6]}"

    tenant = Tenant(
        name=hotel_name,
        slug=tenant_slug,
        subscription_tier="pilot",
        subscription_status="trialing",
    )
    db.add(tenant)
    await db.flush()

    # Create Business
    business_slug = _slugify(hotel_name)
    prop_slug_check = await db.execute(select(Business).where(Business.slug == business_slug))
    if prop_slug_check.scalar_one_or_none():
        business_slug = f"{business_slug}-{uuid.uuid4().hex[:6]}"

    prop = Business(
        tenant_id=tenant.id,
        name=hotel_name,
        slug=business_slug,
        timezone="Asia/Kuala_Lumpur",
        plan_tier="pilot",
        notification_email=user.email,
    )
    db.add(prop)
    await db.flush()

    # Create TenantMembership
    membership = TenantMembership(
        user_id=user.id,
        tenant_id=tenant.id,
        role="owner",
    )
    db.add(membership)

    # Create OnboardingProgress (all channels skipped — set up by account manager later)
    progress = OnboardingProgress(
        tenant_id=tenant.id,
        business_id=prop.id,
        whatsapp_status="skipped",
        email_status="skipped",
        website_status="skipped",
    )
    db.add(progress)

    # Seed a starter KB document
    starter_doc = KBDocument(
        business_id=prop.id,
        doc_type="faqs",
        title="Welcome to Nocturn AI",
        content=(
            f"Welcome to {hotel_name}! This business is powered by Nocturn AI. "
            "Our AI concierge is available 24/7 to assist guests with room inquiries, "
            "rates, facilities, and booking information."
        ),
    )
    db.add(starter_doc)

    await db.commit()

    logger.info(
        "Self-provisioned tenant",
        tenant_id=str(tenant.id),
        business_id=str(prop.id),
        user_id=str(user.id),
        hotel_name=hotel_name,
    )

    return {
        "tenant_id": str(tenant.id),
        "business_id": str(prop.id),
        "business_name": hotel_name,
        "is_new": True,
    }


# ─────────────────────────────────────────────────────────────
# Business Management
# ─────────────────────────────────────────────────────────────

@router.post("/onboarding/add-business/{tenant_id}")
async def add_property(
    tenant_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Add a new business under an existing tenant."""
    # Verify access
    await check_tenant_access(tenant_id, user)

    name = body.get("business_name", "New Business")
    slug = _slugify(name)
    existing = await db.execute(select(Business).where(Business.slug == slug))
    if existing.scalar_one_or_none():
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    prop = Business(
        tenant_id=uuid.UUID(tenant_id),
        name=name,
        slug=slug,
        timezone=body.get("timezone", "Asia/Kuala_Lumpur"),
        plan_tier=body.get("plan_tier", "pilot"),
    )
    db.add(prop)
    await db.flush()

    # Create onboarding progress
    progress = OnboardingProgress(
        tenant_id=uuid.UUID(tenant_id),
        business_id=prop.id,
    )
    db.add(progress)
    await db.commit()

    return {"business_id": str(prop.id), "slug": slug, "message": f"Business '{name}' created."}


# ─────────────────────────────────────────────────────────────
# User Invitation
# ─────────────────────────────────────────────────────────────

@router.post("/onboarding/invite-user/{tenant_id}")
async def invite_user(
    tenant_id: str,
    body: InviteUserRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Invite a new user to an existing tenant and send them a magic link."""
    await check_tenant_access(tenant_id, user)
    settings = get_settings()

    # Check if user already exists
    existing = await db.execute(select(User).where(User.email == body.email))
    existing_user = existing.scalar_one_or_none()

    if existing_user:
        # Check if already a member of this tenant
        existing_membership = await db.execute(
            select(TenantMembership).where(
                TenantMembership.user_id == existing_user.id,
                TenantMembership.tenant_id == uuid.UUID(tenant_id),
            )
        )
        if existing_membership.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="User is already a member of this tenant.")

        # Add membership for existing user
        membership = TenantMembership(
            user_id=existing_user.id,
            tenant_id=uuid.UUID(tenant_id),
            role=body.role,
            accessible_property_ids=[str(pid) for pid in body.accessible_property_ids] if body.accessible_property_ids else None,
        )
        db.add(membership)
        await db.commit()
        return {"user_id": str(existing_user.id), "message": f"Existing user {body.email} added to tenant."}

    # Create new user via Supabase (if configured)
    new_user_id = uuid.uuid4()
    magic_link_sent = False

    if settings.supabase_url and settings.supabase_service_role_key:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.supabase_url}/auth/v1/admin/users",
                    headers={
                        "apikey": settings.supabase_service_role_key,
                        "Authorization": f"Bearer {settings.supabase_service_role_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "email": body.email,
                        "email_confirm": True,
                        "user_metadata": {"full_name": body.full_name},
                    },
                    timeout=10.0,
                )
                if response.status_code < 300:
                    new_user_id = uuid.UUID(response.json()["id"])

                    # Send magic link
                    ml_resp = await client.post(
                        f"{settings.supabase_url}/auth/v1/magiclink",
                        headers={
                            "apikey": settings.supabase_anon_key,
                            "Content-Type": "application/json",
                        },
                        json={
                            "email": body.email,
                            "options": {
                                "emailRedirectTo": settings.allowed_origins.split(",")[0]
                            }
                        },
                        timeout=10.0,
                    )
                    magic_link_sent = ml_resp.status_code < 300
        except Exception as e:
            logger.error("Supabase user creation failed", error=str(e))

    new_user = User(
        id=new_user_id,
        email=body.email,
        full_name=body.full_name,
    )
    db.add(new_user)
    await db.flush()

    membership = TenantMembership(
        user_id=new_user.id,
        tenant_id=uuid.UUID(tenant_id),
        role=body.role,
        accessible_property_ids=[str(pid) for pid in body.accessible_property_ids] if body.accessible_property_ids else None,
    )
    db.add(membership)
    await db.commit()

    return {
        "user_id": str(new_user.id),
        "magic_link_sent": magic_link_sent,
        "message": f"User {body.email} invited as {body.role}.",
    }


# ─────────────────────────────────────────────────────────────
# Onboarding Progress (Gamified)
# ─────────────────────────────────────────────────────────────

@router.get("/onboarding/progress/{tenant_id}", response_model=OnboardingProgressResponse)
async def get_onboarding_progress(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get the gamified onboarding progress for a tenant's primary business."""
    await check_tenant_access(tenant_id, user)

    stmt = select(OnboardingProgress).where(
        OnboardingProgress.tenant_id == uuid.UUID(tenant_id)
    ).order_by(OnboardingProgress.created_at)
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    if not progress:
        raise HTTPException(status_code=404, detail="Onboarding progress not found.")

    score, next_milestone = _compute_score(progress)

    return OnboardingProgressResponse(
        tenant_id=progress.tenant_id,
        business_id=progress.business_id,
        whatsapp_status=progress.whatsapp_status,
        email_status=progress.email_status,
        website_status=progress.website_status,
        kb_populated=progress.kb_populated,
        first_inquiry_received=progress.first_inquiry_received,
        first_lead_captured=progress.first_lead_captured,
        first_morning_report_sent=progress.first_morning_report_sent,
        owner_first_login=progress.owner_first_login,
        completion_score=score,
        next_milestone=next_milestone,
    )


@router.get("/onboarding/checklist/{tenant_id}")
async def get_onboarding_checklist(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Get the full onboarding checklist with detailed milestone descriptions
    for the gamified getting-started UI.
    """
    await check_tenant_access(tenant_id, user)

    stmt = select(OnboardingProgress).where(
        OnboardingProgress.tenant_id == uuid.UUID(tenant_id)
    ).order_by(OnboardingProgress.created_at)
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    if not progress:
        raise HTTPException(status_code=404, detail="Onboarding progress not found.")

    score, next_milestone = _compute_score(progress)
    channels_ok = _channels_connected(progress)

    milestones = [
        {
            "id": "account_created",
            "title": "Account Created",
            "description": "Your Nocturn AI account is set up and ready.",
            "icon": "🏁",
            "points": 10,
            "completed": True,
            "status": "complete",
        },
        {
            "id": "channels_connected",
            "title": "Channels Connected",
            "description": "WhatsApp, Email, and Website channels are live.",
            "icon": "📱",
            "points": 20,
            "completed": channels_ok,
            "status": "complete" if channels_ok else "in_progress",
            "details": {
                "whatsapp": progress.whatsapp_status,
                "email": progress.email_status,
                "website": progress.website_status,
            },
        },
        {
            "id": "kb_populated",
            "title": "Knowledge Base Ready",
            "description": "Your business info (rates, rooms, FAQs) is loaded into the AI.",
            "icon": "📚",
            "points": 20,
            "completed": progress.kb_populated,
            "status": "complete" if progress.kb_populated else ("locked" if not channels_ok else "pending"),
            "cta": "Upload your business info" if not progress.kb_populated else None,
        },
        {
            "id": "first_inquiry",
            "title": "First AI Response",
            "description": "Nocturn AI has handled its first real guest inquiry.",
            "icon": "🤖",
            "points": 15,
            "completed": progress.first_inquiry_received,
            "status": "complete" if progress.first_inquiry_received else "pending",
        },
        {
            "id": "first_morning_report",
            "title": "First Morning Report",
            "description": "Your GM received the first daily email summary.",
            "icon": "📊",
            "points": 15,
            "completed": progress.first_morning_report_sent,
            "status": "complete" if progress.first_morning_report_sent else "pending",
        },
        {
            "id": "first_lead",
            "title": "First Lead Captured",
            "description": "The AI captured its first qualified guest lead.",
            "icon": "🎯",
            "points": 10,
            "completed": progress.first_lead_captured,
            "status": "complete" if progress.first_lead_captured else "pending",
        },
        {
            "id": "owner_first_login",
            "title": "Dashboard Explored",
            "description": "You've logged into the dashboard for the first time.",
            "icon": "🏆",
            "points": 10,
            "completed": progress.owner_first_login,
            "status": "complete" if progress.owner_first_login else "pending",
        },
    ]

    return {
        "completion_score": score,
        "next_milestone": next_milestone,
        "milestones": milestones,
        "channel_errors": progress.channel_errors,
    }


# ─────────────────────────────────────────────────────────────
# Solopreneur "Paste URL" Flow
# ─────────────────────────────────────────────────────────────

@router.post("/onboarding/scrape-url", response_model=ScrapeUrlResponse)
async def scrape_url_flow(
    body: ScrapeUrlRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Frictionless onboarding. Takes a URL, scrapes it using Jina Reader, 
    and instantly provisions a trial Business and KB document.
    """
    url = body.url
    if not url.startswith("http"):
        url = "https://" + url

    # 1. Scrape using Jina Reader (free public API for clean markdown)
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(f"https://r.jina.ai/{url}")
            if resp.status_code >= 400:
                raise HTTPException(status_code=400, detail="Failed to scrape URL.")
            markdown_content = resp.text
    except Exception as e:
        logger.error("Scraping failed", error=str(e))
        raise HTTPException(status_code=400, detail="Failed to read website content.")

    # 2. Extract Business Name from title or URL
    # We could use an LLM here, but for MVP we parse the URL or first Header
    business_name = "My Business"
    first_line = markdown_content.split("\n")[0] if markdown_content else ""
    if first_line.startswith("#"):
        business_name = first_line.replace("#", "").strip()
    else:
        # Fallback to domain name
        domain = url.split("//")[-1].split("/")[0]
        business_name = domain.replace("www.", "").split(".")[0].title()

    if len(business_name) < 2:
        business_name = "My Business"

    # 3. Create Tenant
    tenant_slug = _slugify(business_name)
    slug_check = await db.execute(select(Tenant).where(Tenant.slug == tenant_slug))
    if slug_check.scalar_one_or_none():
        tenant_slug = f"{tenant_slug}-{uuid.uuid4().hex[:6]}"

    tenant = Tenant(
        name=business_name,
        slug=tenant_slug,
        subscription_tier="trial",
        subscription_status="trialing",
    )
    db.add(tenant)
    await db.flush()

    # 4. Create Business
    business_slug = _slugify(business_name)
    prop_slug_check = await db.execute(select(Business).where(Business.slug == business_slug))
    if prop_slug_check.scalar_one_or_none():
        business_slug = f"{business_slug}-{uuid.uuid4().hex[:6]}"

    prop = Business(
        tenant_id=tenant.id,
        name=business_name,
        slug=business_slug,
        timezone="Asia/Kuala_Lumpur",
        plan_tier="trial",
        website_url=url,
    )
    db.add(prop)
    await db.flush()

    # 5. Save Knowledge Base Document
    doc = KBDocument(
        business_id=prop.id,
        doc_type="faqs",
        title="Website Content",
        content=markdown_content[:30000], # Cap size
    )
    db.add(doc)
    await db.commit()

    logger.info("URL Scraped and Business Provisioned", url=url, business_id=str(prop.id))

    return ScrapeUrlResponse(
        tenant_id=tenant.id,
        business_id=prop.id,
        business_name=business_name,
        message="Website ingested successfully. AI is ready to test."
    )

