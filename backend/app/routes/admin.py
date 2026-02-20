"""
Admin routes — Property CRUD, knowledge base, onboarding, settings.
"""

import uuid
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Property
from app.schemas import (
    PropertyResponse,
    PropertyCreateRequest,
    KBIngestRequest,
    KBIngestResponse,
)
from app.services import ingest_knowledge_base
from app.auth import verify_jwt, check_property_access

logger = structlog.get_logger()
router = APIRouter()


@router.get("/properties", response_model=List[PropertyResponse])
async def list_properties(
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """List all properties (for dashboard selection)."""
    result = await db.execute(select(Property))
    return result.scalars().all()


@router.post("/properties", response_model=PropertyResponse, status_code=201)
async def create_property(
    body: PropertyCreateRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Create a new property (tenant)."""
    prop = Property(
        name=body.name,
        whatsapp_number=body.whatsapp_number,
        website_url=body.website_url,
        operating_hours=body.operating_hours,
        adr=Decimal(str(body.adr)),
        ota_commission_pct=Decimal(str(body.ota_commission_pct)),
    )
    db.add(prop)
    await db.flush()

    return PropertyResponse(
        id=str(prop.id),
        name=prop.name,
        whatsapp_number=prop.whatsapp_number,
        website_url=prop.website_url,
        adr=float(prop.adr),
        ota_commission_pct=float(prop.ota_commission_pct),
        created_at=prop.created_at,
    )


@router.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Get property details."""
    result = await db.execute(
        select(Property).where(Property.id == uuid.UUID(property_id))
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    return PropertyResponse(
        id=str(prop.id),
        name=prop.name,
        whatsapp_number=prop.whatsapp_number,
        website_url=prop.website_url,
        adr=float(prop.adr),
        ota_commission_pct=float(prop.ota_commission_pct),
        created_at=prop.created_at,
    )


@router.get("/properties/{property_id}/settings")
async def get_property_settings(
    property_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """Get property configuration."""
    result = await db.execute(
        select(Property).where(Property.id == uuid.UUID(property_id))
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    return {
        "id": str(prop.id),
        "name": prop.name,
        "operating_hours": prop.operating_hours,
        "knowledge_base_config": prop.knowledge_base_config,
        "timezone": prop.timezone,
        "plan_tier": prop.plan_tier,
        "is_active": prop.is_active,
    }


@router.put("/properties/{property_id}/knowledge-base", response_model=KBIngestResponse)
async def upload_knowledge_base(
    property_id: str,
    body: KBIngestRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """Upload or replace a property's knowledge base."""
    pid = uuid.UUID(property_id)

    result = await db.execute(select(Property).where(Property.id == pid))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Property not found")

    count = await ingest_knowledge_base(
        db=db,
        property_id=pid,
        documents=[doc.model_dump() for doc in body.documents],
    )

    return KBIngestResponse(documents_ingested=count, property_id=property_id)


@router.post("/properties/{property_id}/onboard")
async def onboard_property(
    property_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """Trigger onboarding."""
    return {"status": "onboarded", "property_id": property_id}


@router.get("/system/integrations")
async def get_integrations(
    token: dict = Depends(verify_jwt),
):
    """Get status of all external integrations (for Settings page)."""
    from app.services.integration_registry import get_integration_status
    return get_integration_status()


@router.get("/system/info")
async def get_system_info(
    token: dict = Depends(verify_jwt),
):
    """Get system environment info."""
    from app.config import get_settings
    s = get_settings()
    return {
        "environment": s.environment,
        "is_demo": s.is_demo,
        "is_production": s.is_production,
        "channels_are_live": s.channels_are_live,
    }


@router.delete("/gdpr/delete-guest/{property_id}/{guest_identifier}")
async def delete_guest_data(
    property_id: str,
    guest_identifier: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """
    PDPA Right-to-Delete (PDPA 2010, Section 7(2)).

    Anonymizes all guest data for a given identifier within a property:
    - Conversations: guest_name, guest_identifier replaced
    - Messages: content redacted
    - Leads: PII fields cleared
    """
    from sqlalchemy import update, delete
    from app.models import Conversation, Message, Lead

    pid = uuid.UUID(property_id)

    # 1. Find all conversations for this guest
    result = await db.execute(
        select(Conversation.id).where(
            Conversation.property_id == pid,
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
        property_id=property_id,
        guest_identifier=guest_identifier,
        conversations_affected=len(conv_ids),
    )

    return {
        "status": "deleted",
        "conversations_affected": len(conv_ids),
        "message": "Guest data has been anonymized per PDPA 2010.",
    }


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
