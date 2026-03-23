"""
SuperAdmin routes — Internal SheersSoft dashboard API.
Tenant management, global metrics, support queue, application intake.
"""

import asyncio
import time as _time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
import structlog
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.auth import require_superadmin, get_current_user
from app.models import (
    Tenant, Property, User, TenantMembership,
    Conversation, Lead, SupportTicket, Application,
    OnboardingProgress, Announcement,
)
from app.schemas import (
    TenantResponse, TenantUpdateRequest,
    SupportTicketResponse, SupportTicketUpdateRequest,
    ApplicationResponse, ApplicationUpdateRequest,
    ApplicationCreateRequest, PlatformMetricsResponse,
)

logger = structlog.get_logger()
router = APIRouter()


# ─────────────────────────────────────────────────────────────
# Platform Metrics
# ─────────────────────────────────────────────────────────────

@router.get("/superadmin/metrics", response_model=PlatformMetricsResponse)
async def get_platform_metrics(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """Global platform metrics for the SheersSoft internal dashboard."""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_tenants = (await db.execute(select(func.count(Tenant.id)))).scalar() or 0
    active_tenants = (await db.execute(
        select(func.count(Tenant.id)).where(Tenant.is_active == True)
    )).scalar() or 0
    total_properties = (await db.execute(select(func.count(Property.id)))).scalar() or 0
    total_conversations = (await db.execute(select(func.count(Conversation.id)))).scalar() or 0
    mtd_conversations = (await db.execute(
        select(func.count(Conversation.id)).where(Conversation.started_at >= month_start)
    )).scalar() or 0
    mtd_leads = (await db.execute(
        select(func.count(Lead.id)).where(Lead.captured_at >= month_start)
    )).scalar() or 0
    open_tickets = (await db.execute(
        select(func.count(SupportTicket.id)).where(
            SupportTicket.status.in_(["open", "in_progress"])
        )
    )).scalar() or 0
    pending_apps = (await db.execute(
        select(func.count(Application.id)).where(Application.status == "new")
    )).scalar() or 0

    return PlatformMetricsResponse(
        total_tenants=total_tenants,
        active_tenants=active_tenants,
        total_properties=total_properties,
        total_conversations_alltime=total_conversations,
        total_conversations_mtd=mtd_conversations,
        total_leads_mtd=mtd_leads,
        open_support_tickets=open_tickets,
        pending_applications=pending_apps,
    )


# ─────────────────────────────────────────────────────────────
# System Configuration (Scheduler Job Controls)
# ─────────────────────────────────────────────────────────────

@router.get("/superadmin/scheduler-config")
async def get_scheduler_config(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """Return current scheduler job enabled states."""
    from app.services.system_config import get_jobs_config
    config = await get_jobs_config(db)
    return {"jobs": config}


@router.put("/superadmin/scheduler-config")
async def update_scheduler_config(
    body: dict,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """Update scheduler job enabled states. Body: {jobs: {daily_report: bool, ...}}"""
    from app.services.system_config import set_jobs_config, get_jobs_config

    jobs = body.get("jobs", {})
    # Merge with existing to allow partial updates
    current = await get_jobs_config(db)
    current.update({k: bool(v) for k, v in jobs.items()})
    await set_jobs_config(current, db)
    return {"jobs": current}


# ─────────────────────────────────────────────────────────────
# Maintenance Mode
# ─────────────────────────────────────────────────────────────

@router.get("/superadmin/maintenance")
async def get_maintenance(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """Return current maintenance mode state."""
    from app.services.system_config import get_maintenance_config
    return await get_maintenance_config(db)


@router.put("/superadmin/maintenance")
async def set_maintenance(
    body: dict,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """
    Set maintenance mode. Body: {enabled: bool, message: str, eta: str|null}
    When enabled, all non-admin channel and API requests receive a 503 with
    the maintenance message. The /admin and /api/v1/internal/* paths are exempt.
    """
    from app.services.system_config import set_maintenance_config
    config = {
        "enabled": bool(body.get("enabled", False)),
        "message": str(body.get("message", "")) or "Scheduled maintenance in progress. We'll be back shortly.",
        "eta": body.get("eta"),  # ISO8601 string or null
    }
    await set_maintenance_config(config, db)
    # Bust the in-process cache so the middleware picks up the change immediately
    from app.middleware import _maintenance_cache
    _maintenance_cache["expires_at"] = 0.0
    logger.info("Maintenance mode updated", enabled=config["enabled"], eta=config["eta"])
    return config


# ─────────────────────────────────────────────────────────────
# Service Health Dashboard
# ─────────────────────────────────────────────────────────────

# In-process cache for health results (20s TTL)
_health_cache: dict = {"value": None, "expires_at": 0.0}


async def _check_service(name: str, fn) -> dict:
    """Run a single health check coroutine, returning a result dict."""
    start = _time.monotonic()
    try:
        await asyncio.wait_for(fn(), timeout=3.0)
        latency_ms = int((_time.monotonic() - start) * 1000)
        return {"name": name, "status": "ok", "latency_ms": latency_ms}
    except asyncio.TimeoutError:
        return {"name": name, "status": "timeout", "latency_ms": 3000}
    except Exception as exc:
        latency_ms = int((_time.monotonic() - start) * 1000)
        return {"name": name, "status": "error", "latency_ms": latency_ms, "detail": str(exc)[:120]}


@router.get("/superadmin/service-health")
async def get_service_health(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """
    Parallel health check for all external services.
    Results are cached for 20 seconds. Force-refresh by appending ?refresh=1.
    """
    now = _time.monotonic()
    if _health_cache["value"] and now < _health_cache["expires_at"]:
        return _health_cache["value"]

    from app.config import get_settings
    s = get_settings()

    # ── Check functions ─────────────────────────────────────────

    async def check_postgres():
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))

    async def check_redis():
        from app.core.redis import get_redis
        r = await get_redis()
        if r.client:
            await r.client.ping()
        # In-memory fallback is expected on Cloud Run without Memorystore — report ok
        # (sessions survive per-instance; no cross-instance pub/sub)

    async def check_supabase():
        if not s.supabase_url:
            raise Exception("SUPABASE_URL not configured")
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{s.supabase_url}/auth/v1/health", timeout=3.0)
            resp.raise_for_status()

    async def check_gemini():
        if not s.gemini_api_key:
            raise Exception("GEMINI_API_KEY not configured")
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://generativelanguage.googleapis.com/v1beta/models",
                params={"key": s.gemini_api_key},
                timeout=3.0,
            )
            resp.raise_for_status()

    async def check_openai():
        if not s.openai_api_key:
            raise Exception("OPENAI_API_KEY not configured")
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {s.openai_api_key}"},
                timeout=3.0,
            )
            resp.raise_for_status()

    async def check_anthropic():
        if not s.anthropic_api_key:
            raise Exception("ANTHROPIC_API_KEY not configured")
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.anthropic.com/v1/models",
                headers={
                    "x-api-key": s.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                },
                timeout=3.0,
            )
            resp.raise_for_status()

    async def check_sendgrid():
        if not s.sendgrid_api_key:
            raise Exception("SENDGRID_API_KEY not configured")
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.sendgrid.com/v3/user/profile",
                headers={"Authorization": f"Bearer {s.sendgrid_api_key}"},
                timeout=3.0,
            )
            resp.raise_for_status()

    async def check_whatsapp():
        if not s.whatsapp_api_token:
            raise Exception("WHATSAPP_API_TOKEN not configured")
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://graph.facebook.com/v18.0/me",
                params={"access_token": s.whatsapp_api_token},
                timeout=3.0,
            )
            resp.raise_for_status()

    async def check_stripe():
        if not s.stripe_api_key:
            raise Exception("STRIPE_API_KEY not configured")
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.stripe.com/v1/balance",
                headers={"Authorization": f"Bearer {s.stripe_api_key}"},
                timeout=3.0,
            )
            resp.raise_for_status()

    # ── Run all checks in parallel ──────────────────────────────

    checks = [
        ("PostgreSQL", check_postgres),
        ("Redis", check_redis),
        ("Supabase Auth", check_supabase),
        ("Gemini", check_gemini),
        ("OpenAI", check_openai),
        ("Anthropic", check_anthropic),
        ("SendGrid", check_sendgrid),
        ("WhatsApp API", check_whatsapp),
        ("Stripe", check_stripe),
    ]

    results = await asyncio.gather(*[_check_service(name, fn) for name, fn in checks])

    overall = "ok"
    for r in results:
        if r["status"] == "error":
            overall = "degraded"
            break
        if r["status"] == "timeout":
            overall = "degraded"

    payload = {
        "overall": overall,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "services": results,
    }

    _health_cache["value"] = payload
    _health_cache["expires_at"] = now + 20.0
    return payload


# ─────────────────────────────────────────────────────────────
# Tenant Management
# ─────────────────────────────────────────────────────────────

@router.get("/superadmin/tenants")
async def list_tenants(
    status: str | None = None,
    tier: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """List all tenants with property count and stats."""
    stmt = select(Tenant).options(selectinload(Tenant.properties))

    if status:
        stmt = stmt.where(Tenant.subscription_status == status)
    if tier:
        stmt = stmt.where(Tenant.subscription_tier == tier)

    stmt = stmt.order_by(Tenant.created_at.desc())
    result = await db.execute(stmt)
    tenants = result.scalars().all()

    return [
        {
            "id": str(t.id),
            "name": t.name,
            "slug": t.slug,
            "subscription_tier": t.subscription_tier,
            "subscription_status": t.subscription_status,
            "pilot_start_date": t.pilot_start_date.isoformat() if t.pilot_start_date else None,
            "pilot_end_date": t.pilot_end_date.isoformat() if t.pilot_end_date else None,
            "assigned_account_manager": t.assigned_account_manager,
            "is_active": t.is_active,
            "property_count": len(t.properties),
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in tenants
    ]


@router.get("/superadmin/tenants/{tenant_id}")
async def get_tenant_detail(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """Detailed tenant view with properties, users, and usage stats."""
    stmt = (
        select(Tenant)
        .options(
            selectinload(Tenant.properties),
            selectinload(Tenant.memberships).selectinload(TenantMembership.user),
            selectinload(Tenant.onboarding_progress),
        )
        .where(Tenant.id == uuid.UUID(tenant_id))
    )
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Get conversation stats for this tenant's properties
    property_ids = [p.id for p in tenant.properties]
    total_convos = 0
    total_leads = 0
    if property_ids:
        convos_result = await db.execute(
            select(func.count(Conversation.id)).where(
                Conversation.property_id.in_(property_ids)
            )
        )
        total_convos = convos_result.scalar() or 0

        leads_result = await db.execute(
            select(func.count(Lead.id)).where(
                Lead.property_id.in_(property_ids)
            )
        )
        total_leads = leads_result.scalar() or 0

    return {
        "id": str(tenant.id),
        "name": tenant.name,
        "slug": tenant.slug,
        "subscription_tier": tenant.subscription_tier,
        "subscription_status": tenant.subscription_status,
        "pilot_start_date": tenant.pilot_start_date.isoformat() if tenant.pilot_start_date else None,
        "pilot_end_date": tenant.pilot_end_date.isoformat() if tenant.pilot_end_date else None,
        "assigned_account_manager": tenant.assigned_account_manager,
        "is_active": tenant.is_active,
        "created_at": tenant.created_at.isoformat() if tenant.created_at else None,
        "properties": [
            {
                "id": str(p.id),
                "name": p.name,
                "slug": p.slug,
                "is_active": p.is_active,
            }
            for p in tenant.properties
        ],
        "users": [
            {
                "id": str(m.user.id),
                "email": m.user.email,
                "full_name": m.user.full_name,
                "role": m.role,
            }
            for m in tenant.memberships
        ],
        "onboarding": [
            {
                "property_id": str(op.property_id),
                "whatsapp_status": op.whatsapp_status,
                "email_status": op.email_status,
                "website_status": op.website_status,
                "kb_populated": op.kb_populated,
                "first_inquiry_received": op.first_inquiry_received,
                "channel_errors": op.channel_errors,
            }
            for op in tenant.onboarding_progress
        ],
        "stats": {
            "total_conversations": total_convos,
            "total_leads": total_leads,
            "property_count": len(tenant.properties),
            "user_count": len(tenant.memberships),
        },
    }


@router.patch("/superadmin/tenants/{tenant_id}")
async def update_tenant(
    tenant_id: str,
    body: TenantUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """Update tenant tier, status, or account manager."""
    stmt = select(Tenant).where(Tenant.id == uuid.UUID(tenant_id))
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if body.subscription_tier is not None:
        tenant.subscription_tier = body.subscription_tier
    if body.subscription_status is not None:
        tenant.subscription_status = body.subscription_status
    if body.is_active is not None:
        tenant.is_active = body.is_active
    if body.assigned_account_manager is not None:
        tenant.assigned_account_manager = body.assigned_account_manager

    await db.commit()

    return {"message": f"Tenant '{tenant.name}' updated.", "tenant_id": tenant_id}


@router.post("/superadmin/tenants/{tenant_id}/retry-channel/{channel}")
async def retry_channel_setup(
    tenant_id: str,
    channel: str,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """Retry a failed channel setup for a tenant's primary property."""
    from app.services.channel_setup import setup_channels

    # Get the primary property
    stmt = select(OnboardingProgress).where(
        OnboardingProgress.tenant_id == uuid.UUID(tenant_id)
    )
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    if not progress:
        raise HTTPException(status_code=404, detail="Onboarding progress not found")

    # Get property's whatsapp provider
    prop_stmt = select(Property).where(Property.id == progress.property_id)
    prop_result = await db.execute(prop_stmt)
    prop = prop_result.scalar_one_or_none()

    errors = await setup_channels(
        db=db,
        tenant_id=tenant_id,
        property_id=str(progress.property_id),
        channels=[channel],
        whatsapp_provider=prop.whatsapp_provider if prop else "meta",
    )

    if errors:
        return {"status": "failed", "errors": errors}
    return {"status": "success", "message": f"Channel '{channel}' setup retried successfully."}


# ─────────────────────────────────────────────────────────────
# Onboarding Pipeline
# ─────────────────────────────────────────────────────────────

@router.get("/superadmin/pipeline")
async def get_onboarding_pipeline(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """
    Kanban-style onboarding pipeline:
    Provisioned → Channels Setup → Live → First Week Review
    """
    stmt = (
        select(OnboardingProgress)
        .options(selectinload(OnboardingProgress.tenant))
    )
    result = await db.execute(stmt)
    progress_list = result.scalars().all()

    pipeline = {
        "provisioned": [],
        "channels_setup": [],
        "live": [],
        "first_week_review": [],
        "fully_onboarded": [],
    }

    for p in progress_list:
        channels_done = all(
            s in ("active", "skipped")
            for s in [p.whatsapp_status, p.email_status, p.website_status]
        )
        has_inquiry = p.first_inquiry_received
        has_report = p.first_morning_report_sent

        item = {
            "tenant_id": str(p.tenant_id),
            "tenant_name": p.tenant.name if p.tenant else "Unknown",
            "property_id": str(p.property_id),
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }

        if has_report and has_inquiry:
            pipeline["fully_onboarded"].append(item)
        elif has_inquiry:
            pipeline["first_week_review"].append(item)
        elif channels_done:
            pipeline["live"].append(item)
        elif any(s == "configuring" for s in [p.whatsapp_status, p.email_status, p.website_status]):
            pipeline["channels_setup"].append(item)
        else:
            pipeline["provisioned"].append(item)

    return pipeline


# ─────────────────────────────────────────────────────────────
# Support Tickets (Admin View)
# ─────────────────────────────────────────────────────────────

@router.get("/superadmin/tickets")
async def list_all_tickets(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """List all support tickets across all tenants."""
    stmt = (
        select(SupportTicket)
        .options(
            selectinload(SupportTicket.tenant),
            selectinload(SupportTicket.created_by),
        )
    )
    if status:
        stmt = stmt.where(SupportTicket.status == status)
    else:
        stmt = stmt.where(SupportTicket.status.in_(["open", "in_progress"]))

    stmt = stmt.order_by(SupportTicket.created_at.desc()).limit(100)
    result = await db.execute(stmt)
    tickets = result.scalars().all()

    return [
        {
            "id": str(t.id),
            "tenant_id": str(t.tenant_id),
            "tenant_name": t.tenant.name if t.tenant else None,
            "subject": t.subject,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "created_by_name": t.created_by.full_name if t.created_by else None,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in tickets
    ]


@router.patch("/superadmin/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: str,
    body: SupportTicketUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """Assign, update status, or change priority on a support ticket."""
    stmt = select(SupportTicket).where(SupportTicket.id == uuid.UUID(ticket_id))
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if body.status is not None:
        ticket.status = body.status
    if body.priority is not None:
        ticket.priority = body.priority
    if body.assigned_to_user_id is not None:
        ticket.assigned_to_user_id = body.assigned_to_user_id

    await db.commit()

    return {"message": "Ticket updated.", "ticket_id": ticket_id}


# ─────────────────────────────────────────────────────────────
# Support Chat Queue (Handed-off conversations)
# ─────────────────────────────────────────────────────────────

@router.get("/superadmin/support-chats")
async def list_support_chats(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """List all handed-off support conversations awaiting human response."""
    from app.models import Conversation, Property

    stmt = (
        select(Conversation)
        .join(Property, Conversation.property_id == Property.id)
        .where(
            Property.slug == "nocturn-ai-support",
            Conversation.status == "handed_off",
        )
        .order_by(Conversation.last_message_at.desc())
        .limit(50)
    )
    result = await db.execute(stmt)
    conversations = result.scalars().all()

    return [
        {
            "conversation_id": str(c.id),
            "guest_name": c.guest_name,
            "guest_identifier": c.guest_identifier,
            "message_count": c.message_count,
            "last_message_at": c.last_message_at.isoformat() if c.last_message_at else None,
            "started_at": c.started_at.isoformat() if c.started_at else None,
        }
        for c in conversations
    ]


# ─────────────────────────────────────────────────────────────
# Application Intake (from ai.sheerssoft.com/apply)
# ─────────────────────────────────────────────────────────────

@router.post("/applications", response_model=ApplicationResponse)
async def submit_application(
    body: ApplicationCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Public endpoint: Receive applications from the website.
    No authentication required.
    """
    application = Application(
        hotel_name=body.hotel_name,
        contact_name=body.contact_name,
        email=body.email,
        phone=body.phone,
        property_name=body.property_name,
        room_count=body.room_count,
        current_channels=body.current_channels,
        message=body.message,
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)

    # Notify SheersSoft team
    try:
        from app.services.email import send_email
        from app.config import get_settings
        settings = get_settings()

        await send_email(
            to_email=settings.staff_notification_email,
            subject=f"🏨 New Application: {body.hotel_name}",
            content=(
                f"<p><strong>New Founding Cohort Application</strong></p>"
                f"<p>Hotel: {body.hotel_name}<br>"
                f"Contact: {body.contact_name}<br>"
                f"Email: {body.email}<br>"
                f"Phone: {body.phone or 'N/A'}<br>"
                f"Rooms: {body.room_count or 'N/A'}<br>"
                f"Channels: {', '.join(body.current_channels) if body.current_channels else 'N/A'}</p>"
                f"<p>Message: {body.message or 'None'}</p>"
            ),
            is_html=True,
            hotel_name="Nocturn AI",
        )
    except Exception as e:
        logger.error("Failed to send application notification", error=str(e))

    logger.info("New application received", hotel=body.hotel_name, email=body.email)

    return ApplicationResponse(
        id=application.id,
        hotel_name=application.hotel_name,
        contact_name=application.contact_name,
        email=application.email,
        phone=application.phone,
        room_count=application.room_count,
        status=application.status,
        notes=None,
        converted_to_tenant_id=None,
        created_at=application.created_at,
    )


@router.get("/superadmin/applications")
async def list_applications(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """List all applications from the website."""
    stmt = select(Application)
    if status:
        stmt = stmt.where(Application.status == status)
    stmt = stmt.order_by(Application.created_at.desc()).limit(100)

    result = await db.execute(stmt)
    apps = result.scalars().all()

    return [
        ApplicationResponse(
            id=a.id,
            hotel_name=a.hotel_name,
            contact_name=a.contact_name,
            email=a.email,
            phone=a.phone,
            room_count=a.room_count,
            status=a.status,
            notes=a.notes,
            converted_to_tenant_id=a.converted_to_tenant_id,
            created_at=a.created_at,
        )
        for a in apps
    ]


@router.patch("/superadmin/applications/{app_id}")
async def update_application(
    app_id: str,
    body: ApplicationUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """Update application status or add internal notes."""
    stmt = select(Application).where(Application.id == uuid.UUID(app_id))
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if body.status is not None:
        app.status = body.status
    if body.notes is not None:
        app.notes = body.notes

    await db.commit()

    return {"message": "Application updated.", "app_id": app_id}


# ─────────────────────────────────────────────────────────────
# Announcements
# ─────────────────────────────────────────────────────────────

_VALID_TYPES = {"maintenance", "incident", "feature", "billing"}
_VALID_STATUSES = {"draft", "scheduled", "active", "resolved", "archived"}
_VALID_TARGET_TYPES = {"all", "tier", "tenant"}


@router.post("/superadmin/announcements", status_code=201)
async def create_announcement(
    body: dict,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """Create a new announcement. Set status='active' to make it immediately visible to tenants."""
    ann_type = body.get("type", "")
    if ann_type not in _VALID_TYPES:
        raise HTTPException(400, f"type must be one of {sorted(_VALID_TYPES)}")

    target_type = body.get("target_type", "all")
    if target_type not in _VALID_TARGET_TYPES:
        raise HTTPException(400, f"target_type must be one of {sorted(_VALID_TARGET_TYPES)}")

    ann = Announcement(
        type=ann_type,
        status=body.get("status", "draft"),
        title=str(body.get("title", "")).strip(),
        body=str(body.get("body", "")).strip(),
        target_type=target_type,
        target_tier=body.get("target_tier"),
        target_tenant_id=uuid.UUID(body["target_tenant_id"]) if body.get("target_tenant_id") else None,
        scheduled_at=body.get("scheduled_at"),
        send_email=bool(body.get("send_email", False)),
        created_by=admin.id,
    )
    db.add(ann)
    await db.commit()
    await db.refresh(ann)
    logger.info("Announcement created", id=str(ann.id), type=ann.type, status=ann.status)
    return _ann_dict(ann)


@router.get("/superadmin/announcements")
async def list_announcements(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """List all announcements (admin view, all statuses by default)."""
    stmt = select(Announcement).order_by(Announcement.created_at.desc())
    if status:
        stmt = stmt.where(Announcement.status == status)
    result = await db.execute(stmt)
    return [_ann_dict(a) for a in result.scalars().all()]


@router.patch("/superadmin/announcements/{ann_id}")
async def update_announcement(
    ann_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_superadmin),
):
    """Update an announcement. Pass status='active'|'resolved'|'archived' to change lifecycle."""
    ann = await db.get(Announcement, uuid.UUID(ann_id))
    if not ann:
        raise HTTPException(404, "Announcement not found")

    for field in ("title", "body", "type", "target_type", "target_tier", "scheduled_at", "send_email"):
        if field in body:
            setattr(ann, field, body[field])

    if "status" in body:
        new_status = body["status"]
        if new_status not in _VALID_STATUSES:
            raise HTTPException(400, f"status must be one of {sorted(_VALID_STATUSES)}")
        ann.status = new_status
        if new_status == "resolved" and not ann.resolved_at:
            ann.resolved_at = datetime.now(timezone.utc)

    ann.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(ann)
    return _ann_dict(ann)


def _ann_dict(ann: Announcement) -> dict:
    return {
        "id": str(ann.id),
        "type": ann.type,
        "status": ann.status,
        "title": ann.title,
        "body": ann.body,
        "target_type": ann.target_type,
        "target_tier": ann.target_tier,
        "target_tenant_id": str(ann.target_tenant_id) if ann.target_tenant_id else None,
        "scheduled_at": ann.scheduled_at.isoformat() if ann.scheduled_at else None,
        "resolved_at": ann.resolved_at.isoformat() if ann.resolved_at else None,
        "send_email": ann.send_email,
        "created_at": ann.created_at.isoformat(),
        "updated_at": ann.updated_at.isoformat(),
    }


# ─────────────────────────────────────────────────────────────
# Active Announcements (Tenant-facing)
# ─────────────────────────────────────────────────────────────

@router.get("/announcements/active")
async def get_active_announcements(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Return active announcements scoped to the current user's tenant/tier.
    Accessible by any authenticated user — not superadmin-only.
    Superadmins (no TenantMembership) receive all active announcements.
    """
    # Determine the user's tenant_id and subscription_tier
    tenant_id: uuid.UUID | None = None
    tenant_tier: str | None = None

    # Legacy dict user (no memberships)
    if isinstance(user, dict):
        pass
    elif user.memberships:
        sorted_memberships = sorted(user.memberships, key=lambda m: m.created_at)
        primary = sorted_memberships[0]
        tenant_id = primary.tenant_id

        # Load tenant tier
        tenant_result = await db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = tenant_result.scalar_one_or_none()
        if tenant:
            tenant_tier = tenant.subscription_tier

    # Load all active announcements
    stmt = select(Announcement).where(Announcement.status == "active")
    result = await db.execute(stmt)
    all_active = result.scalars().all()

    # Scope by target_type
    visible = []
    for ann in all_active:
        if tenant_id is None:
            # Superadmin / no membership: see all
            visible.append(ann)
        elif ann.target_type == "all":
            visible.append(ann)
        elif ann.target_type == "tier" and ann.target_tier == tenant_tier:
            visible.append(ann)
        elif ann.target_type == "tenant" and ann.target_tenant_id == tenant_id:
            visible.append(ann)

    return [
        {
            "id": str(a.id),
            "type": a.type,
            "title": a.title,
            "body": a.body,
            "created_at": a.created_at.isoformat(),
        }
        for a in visible
    ]
