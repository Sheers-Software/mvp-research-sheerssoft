"""
Onboarding routes — Tenant provisioning, property setup, channel auto-setup, progress tracking.
"""

import uuid
import re
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import structlog
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import get_settings
from app.auth import require_superadmin, get_current_user, check_tenant_access
from app.models import (
    Tenant, User, TenantMembership, Property,
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
    Creates Tenant + Property + User + TenantMembership + OnboardingProgress.
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

    # 2. Create Property
    property_slug = _slugify(body.property_name)
    existing_prop = await db.execute(select(Property).where(Property.slug == property_slug))
    if existing_prop.scalar_one_or_none():
        property_slug = f"{property_slug}-{uuid.uuid4().hex[:6]}"

    prop = Property(
        tenant_id=tenant.id,
        name=body.property_name,
        slug=property_slug,
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
        property_id=prop.id,
        whatsapp_status="pending" if "whatsapp" in body.preferred_channels else "skipped",
        email_status="pending" if "email" in body.preferred_channels else "skipped",
        website_status="pending" if "website" in body.preferred_channels else "skipped",
    )
    db.add(progress)

    # 6. Seed "Getting Started" KB documents
    getting_started_docs = [
        KBDocument(
            property_id=prop.id,
            doc_type="faqs",
            title="Welcome to Nocturn AI",
            content=(
                "Welcome to Nocturn AI! This is your AI-powered hotel concierge. "
                "I can help answer guest inquiries about your property 24/7, including room rates, "
                "facilities, directions, and booking inquiries. "
                "Your knowledge base will be customized with your specific property information."
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
        property_id=str(prop.id),
        channels=body.preferred_channels,
        whatsapp_provider=body.whatsapp_provider,
    )

    logger.info(
        "Tenant provisioned",
        tenant_id=str(tenant.id),
        property_id=str(prop.id),
        user_id=str(user.id),
        tier=body.subscription_tier,
    )

    return ProvisionTenantResponse(
        tenant_id=tenant.id,
        property_id=prop.id,
        user_id=user.id,
        magic_link_sent=magic_link_sent,
        channels_setup_initiated=True,
        message=f"Tenant '{body.tenant_name}' provisioned successfully. "
                f"{'Magic link sent to ' + body.owner_email if magic_link_sent else 'Supabase not configured — manual login setup required.'}"
    )


async def _setup_channels_async(
    tenant_id: str,
    property_id: str,
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
                property_id=property_id,
                channels=channels,
                whatsapp_provider=whatsapp_provider,
            )
    except Exception as e:
        logger.error("Channel setup background task failed", error=str(e), tenant_id=tenant_id)


# ─────────────────────────────────────────────────────────────
# Property Management
# ─────────────────────────────────────────────────────────────

@router.post("/onboarding/add-property/{tenant_id}")
async def add_property(
    tenant_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Add a new property under an existing tenant."""
    # Verify access
    await check_tenant_access(tenant_id, user)

    name = body.get("property_name", "New Property")
    slug = _slugify(name)
    existing = await db.execute(select(Property).where(Property.slug == slug))
    if existing.scalar_one_or_none():
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    prop = Property(
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
        property_id=prop.id,
    )
    db.add(progress)
    await db.commit()

    return {"property_id": str(prop.id), "slug": slug, "message": f"Property '{name}' created."}


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
    """Get the gamified onboarding progress for a tenant's primary property."""
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
        property_id=progress.property_id,
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
            "description": "Your property info (rates, rooms, FAQs) is loaded into the AI.",
            "icon": "📚",
            "points": 20,
            "completed": progress.kb_populated,
            "status": "complete" if progress.kb_populated else ("locked" if not channels_ok else "pending"),
            "cta": "Upload your property info" if not progress.kb_populated else None,
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
