"""
Admin routes — Business CRUD, knowledge base, onboarding, settings.
"""

import uuid
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Business, Announcement, TenantMembership
from app.schemas import (
    BusinessResponse,
    BusinessCreateRequest,
    KBIngestRequest,
    KBIngestResponse,
)
from app.services import ingest_knowledge_base
from app.auth import verify_jwt, check_property_access

logger = structlog.get_logger()
router = APIRouter()


@router.get("/businesses", response_model=List[BusinessResponse])
async def list_properties(
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """List all businesses (for dashboard selection)."""
    result = await db.execute(select(Business))
    return result.scalars().all()


@router.post("/businesses", response_model=BusinessResponse, status_code=201)
async def create_property(
    body: BusinessCreateRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Create a new business (tenant)."""
    prop = Business(
        name=body.name,
        whatsapp_number=body.whatsapp_number,
        website_url=body.website_url,
        operating_hours=body.operating_hours,
        brand_vocabulary=body.brand_vocabulary,
        required_questions=body.required_questions,
    )
    db.add(prop)
    await db.flush()

    return BusinessResponse(
        id=str(prop.id),
        name=prop.name,
        whatsapp_number=prop.whatsapp_number,
        website_url=prop.website_url,
        brand_vocabulary=prop.brand_vocabulary,
        required_questions=prop.required_questions,
        created_at=prop.created_at,
    )


@router.get("/businesses/{business_id}", response_model=BusinessResponse)
async def get_property(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Get business details."""
    result = await db.execute(
        select(Business).where(Business.id == uuid.UUID(business_id))
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Business not found")

    return BusinessResponse(
        id=str(prop.id),
        name=prop.name,
        whatsapp_number=prop.whatsapp_number,
        website_url=prop.website_url,
        hourly_rate=float(prop.hourly_rate) if prop.hourly_rate else 25.0,
        brand_vocabulary=prop.brand_vocabulary,
        required_questions=prop.required_questions,
        created_at=prop.created_at,
    )


@router.get("/businesses/{business_id}/settings")
async def get_property_settings(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """Get business configuration."""
    result = await db.execute(
        select(Business).where(Business.id == uuid.UUID(business_id))
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Business not found")

    return {
        "id": str(prop.id),
        "name": prop.name,
        "notification_email": prop.notification_email,
        "operating_hours": prop.operating_hours,
        "timezone": prop.timezone,
        "plan_tier": prop.plan_tier,
        "is_active": prop.is_active,
        "hourly_rate": float(prop.hourly_rate) if prop.hourly_rate else 25.00,
        "brand_vocabulary": prop.brand_vocabulary,
        "required_questions": prop.required_questions,
        "whatsapp_number": prop.whatsapp_number,
        "website_url": prop.website_url,
    }

from app.schemas import BusinessSettingsUpdateRequest

@router.put("/businesses/{business_id}/settings")
async def update_property_settings(
    business_id: str,
    body: BusinessSettingsUpdateRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """Update business configuration via the Settings page."""
    result = await db.execute(
        select(Business).where(Business.id == uuid.UUID(business_id))
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Business not found")

    if body.notification_email is not None:
        prop.notification_email = body.notification_email
    if body.operating_hours is not None:
        prop.operating_hours = body.operating_hours
    if body.timezone is not None:
        prop.timezone = body.timezone
    if body.brand_vocabulary is not None:
        prop.brand_vocabulary = body.brand_vocabulary
    if body.required_questions is not None:
        prop.required_questions = body.required_questions

    await db.flush()
    return {"status": "success"}


@router.put("/businesses/{business_id}/knowledge-base", response_model=KBIngestResponse)
async def upload_knowledge_base(
    business_id: str,
    body: KBIngestRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """Upload or replace a business's knowledge base."""
    pid = uuid.UUID(business_id)

    result = await db.execute(select(Business).where(Business.id == pid))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Business not found")

    count = await ingest_knowledge_base(
        db=db,
        business_id=pid,
        documents=[doc.model_dump() for doc in body.documents],
    )

    return KBIngestResponse(documents_ingested=count, business_id=business_id)


@router.post("/businesses/{business_id}/onboard")
async def onboard_property(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """Trigger onboarding."""
    return {"status": "onboarded", "business_id": business_id}


@router.get("/system/integrations")
async def get_integrations(
    token: dict = Depends(verify_jwt),
):
    """Get status of all external integrations (for Settings page)."""
    from app.services.integration_registry import get_integration_status
    return get_integration_status()


@router.get("/system/info")
async def get_system_info(
    db: AsyncSession = Depends(get_db),
):
    """Get system environment info. No auth required — used by frontend layout for maintenance polling."""
    from app.config import get_settings
    from app.services.system_config import get_maintenance_config
    s = get_settings()
    maintenance = await get_maintenance_config(db)
    return {
        "environment": s.environment,
        "is_demo": s.is_demo,
        "is_production": s.is_production,
        "channels_are_live": s.channels_are_live,
        "maintenance": maintenance,
    }


@router.delete("/gdpr/delete-guest/{business_id}/{guest_identifier}")
async def delete_guest_data(
    business_id: str,
    guest_identifier: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """
    PDPA Right-to-Delete (PDPA 2010, Section 7(2)).

    Anonymizes all guest data for a given identifier within a business:
    - Conversations: guest_name, guest_identifier replaced
    - Messages: content redacted
    - Leads: PII fields cleared
    """
    from sqlalchemy import update, delete
    from app.models import Conversation, Message, Lead

    pid = uuid.UUID(business_id)

    # 1. Find all conversations for this guest
    result = await db.execute(
        select(Conversation.id).where(
            Conversation.business_id == pid,
            Conversation.guest_identifier == guest_identifier,
        )
    )
    conv_ids = [row[0] for row in result.fetchall()]

    if not conv_ids:
        raise HTTPException(status_code=404, detail="No data found for this guest.")

    # 2. Anonymize messages
    await db.execute(
        update(Message)
        .where(Message.conversation_id.in_(conv_ids))
        .values(content="[REDACTED — PDPA Delete Request]")
    )

    # 3. Anonymize leads
    await db.execute(
        update(Lead)
        .where(Lead.conversation_id.in_(conv_ids))
        .values(
            guest_name="[DELETED]",
            guest_phone=None,
            guest_email=None,
            flag_reason=None,
        )
    )

    # 4. Anonymize conversations
    await db.execute(
        update(Conversation)
        .where(Conversation.id.in_(conv_ids))
        .values(
            guest_name="[DELETED]",
            guest_identifier=f"deleted_{uuid.uuid4().hex[:8]}",
        )
    )

    await db.commit()

    logger.info(
        "PDPA_DELETE",
        business_id=business_id,
        guest_identifier=guest_identifier,
        conversations_affected=len(conv_ids),
    )

    return {
        "status": "deleted",
        "conversations_affected": len(conv_ids),
        "message": "Guest data has been anonymized per PDPA 2010.",
    }


@router.get("/announcements/active")
async def get_active_announcements(
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """
    Active announcements visible to the authenticated user's tenant.
    Scoped by: all-tenant announcements OR matching tier OR matching tenant_id.
    No superadmin required — called by /dashboard and /portal layouts.
    """
    from datetime import datetime, timezone
    from sqlalchemy import or_

    # Resolve tenant_id from the user's TenantMembership (first active membership)
    user_id = token.get("sub") or token.get("user_id")
    tenant_id = None
    tier = None

    if user_id:
        mem_result = await db.execute(
            select(TenantMembership).where(TenantMembership.user_id == uuid.UUID(str(user_id))).limit(1)
        )
        membership = mem_result.scalar_one_or_none()
        if membership:
            tenant_id = membership.tenant_id
            # fetch tier from Tenant
            from app.models import Tenant
            tenant = await db.get(Tenant, tenant_id)
            if tenant:
                tier = tenant.subscription_tier

    stmt = select(Announcement).where(
        Announcement.status == "active",
        or_(
            Announcement.target_type == "all",
            (Announcement.target_type == "tier") & (Announcement.target_tier == tier),
            (Announcement.target_type == "tenant") & (Announcement.target_tenant_id == tenant_id),
        )
    ).order_by(Announcement.created_at.desc())

    result = await db.execute(stmt)
    announcements = result.scalars().all()

    return [
        {
            "id": str(a.id),
            "type": a.type,
            "title": a.title,
            "body": a.body,
            "created_at": a.created_at.isoformat(),
        }
        for a in announcements
    ]


@router.get("/system/encryption")
async def get_encryption_status(
    token: dict = Depends(verify_jwt),
):
    """Check PII encryption service status."""
    from app.services.pii_encryption import get_pii_service
    svc = get_pii_service()
    return {
        "encryption_active": svc.is_active,
        "message": "PII fields are encrypted at rest" if svc.is_active else "Encryption disabled — set FERNET_ENCRYPTION_KEY",
    }
