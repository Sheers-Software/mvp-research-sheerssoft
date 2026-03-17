"""
Staff routes — Conversation management, handoff, takeover.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Conversation, Message
from app.auth import verify_jwt, check_property_access
from app.services.analytics import get_realtime_stats
from app.schemas import StaffReplyRequest

logger = structlog.get_logger()
router = APIRouter()


@router.get("/properties/{property_id}/conversations")
async def list_conversations(
    property_id: str,
    status: str = None,
    after_hours: bool = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """List conversations for a property (staff dashboard)."""
    from fastapi import Query
    query = (
        select(Conversation)
        .where(Conversation.property_id == uuid.UUID(property_id))
        .options(selectinload(Conversation.lead))
        .order_by(Conversation.started_at.desc())
        .limit(limit)
    )

    if status:
        query = query.where(Conversation.status == status)
    if after_hours is not None:
        query = query.where(Conversation.is_after_hours == after_hours)

    result = await db.execute(query)
    conversations = result.scalars().all()

    return [
        {
            "id": str(c.id),
            "channel": c.channel,
            "guest_name": c.guest_name,
            "guest_identifier": c.guest_identifier,
            "status": c.status,
            "ai_mode": c.ai_mode,
            "is_after_hours": c.is_after_hours,
            "message_count": c.message_count,
            "started_at": c.started_at.isoformat(),
            "last_message_at": c.last_message_at.isoformat() if c.last_message_at else None,
            "has_lead": c.lead is not None,
            "lead_intent": c.lead.intent if c.lead else None,
        }
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Get full conversation with all messages (for staff drill-down)."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == uuid.UUID(conversation_id))
        .options(
            selectinload(Conversation.messages),
            selectinload(Conversation.lead),
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "id": str(conv.id),
        "channel": conv.channel,
        "guest_name": conv.guest_name,
        "guest_identifier": conv.guest_identifier,
        "status": conv.status,
        "ai_mode": conv.ai_mode,
        "is_after_hours": conv.is_after_hours,
        "message_count": conv.message_count,
        "started_at": conv.started_at.isoformat(),
        "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
        "messages": sorted(
            [
                {
                    "id": str(m.id),
                    "role": m.role,
                    "content": m.content,
                    "sent_at": m.sent_at.isoformat(),
                    "metadata": m.metadata_,
                }
                for m in conv.messages
            ],
            key=lambda x: x["sent_at"],
        ),
        "lead": {
            "id": str(conv.lead.id),
            "guest_name": conv.lead.guest_name,
            "guest_phone": conv.lead.guest_phone,
            "guest_email": conv.lead.guest_email,
            "intent": conv.lead.intent,
            "status": conv.lead.status,
            "estimated_value": float(conv.lead.estimated_value) if conv.lead.estimated_value else None,
            "priority": conv.lead.priority,
            "flag_reason": conv.lead.flag_reason,
        } if conv.lead else None,
    }


@router.post("/conversations/{conversation_id}/resolve")
async def resolve_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Staff resolves/closes a conversation."""
    result = await db.execute(
        select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv.status = "resolved"
    conv.ended_at = datetime.now(timezone.utc)
    await db.flush()
    return {"status": "resolved", "conversation_id": conversation_id}


@router.post("/conversations/{conversation_id}/handoff")
async def handoff_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Explicitly trigger AI handoff."""
    result = await db.execute(
        select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv.ai_mode = "handoff"
    conv.status = "handed_off"
    await db.flush()
    return {"status": "handed_off", "conversation_id": conversation_id}


@router.post("/conversations/{conversation_id}/takeover")
async def takeover_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Staff takes over conversation (pauses AI)."""
    result = await db.execute(
        select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv.ai_mode = "staff"
    conv.status = "active"
    await db.flush()
    return {"status": "staff_takeover", "conversation_id": conversation_id}


@router.post("/conversations/{conversation_id}/reply")
async def staff_reply(
    conversation_id: str,
    body: StaffReplyRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Staff sends a reply from the dashboard — saved as role='staff' and forwarded to guest via original channel."""
    from app.models import Property

    result = await db.execute(
        select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv.status == "resolved":
        raise HTTPException(status_code=400, detail="Cannot reply to a resolved conversation")

    content = body.content.strip()

    # Persist message
    msg = Message(
        conversation_id=conv.id,
        role="staff",
        content=content,
        sent_at=datetime.now(timezone.utc),
    )
    db.add(msg)
    conv.message_count = (conv.message_count or 0) + 1
    conv.last_message_at = datetime.now(timezone.utc)
    await db.flush()

    # Forward to guest via original channel
    prop_result = await db.execute(
        select(Property).where(Property.id == conv.property_id)
    )
    prop = prop_result.scalar_one_or_none()

    if prop and conv.channel == "whatsapp":
        try:
            if getattr(prop, "whatsapp_provider", "meta") == "twilio":
                from app.services.twilio_whatsapp import send_twilio_message
                await send_twilio_message(
                    to_number=conv.guest_identifier,
                    message=content,
                    from_number=getattr(prop, "twilio_phone_number", None),
                )
            else:
                from app.services.whatsapp import send_whatsapp_message
                await send_whatsapp_message(
                    to=conv.guest_identifier,
                    message=content,
                    phone_number_id=getattr(prop, "whatsapp_phone_number_id", None),
                )
        except Exception as exc:
            # Message is already saved — log the delivery failure but don't fail the request
            logger.warning("staff_reply_delivery_failed", channel=conv.channel, error=str(exc))

    # Web/email: message is in DB; web widget polls for new messages automatically

    return {
        "id": str(msg.id),
        "role": "staff",
        "content": content,
        "sent_at": msg.sent_at.isoformat(),
        "channel": conv.channel,
    }


@router.get("/analytics/dashboard")
async def get_dashboard_stats(
    property_id: Optional[str] = Query(None, description="Property UUID. Defaults to first accessible property."),
    user: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    """
    Get real-time dashboard statistics for a specific property.
    If property_id is not provided, resolves to the first property accessible
    to the authenticated user (from their JWT property_ids claim).
    """
    from app.models import Property

    if property_id:
        result = await db.execute(
            select(Property).where(
                Property.id == uuid.UUID(property_id),
                Property.is_active == True,
            )
        )
    else:
        # Resolve from the user's JWT property list
        prop_ids = user.get("property_ids", ["*"])
        if prop_ids and prop_ids[0] != "*":
            result = await db.execute(
                select(Property).where(
                    Property.id == uuid.UUID(prop_ids[0]),
                    Property.is_active == True,
                )
            )
        else:
            # Wildcard access — pick property with most activity
            from sqlalchemy import func as sqlfunc
            result = await db.execute(
                select(Property)
                .outerjoin(Conversation, Conversation.property_id == Property.id)
                .where(Property.is_active == True)
                .group_by(Property.id)
                .order_by(sqlfunc.count(Conversation.id).desc())
                .limit(1)
            )

    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="No property found")

    stats = await get_realtime_stats(db, prop.id)
    stats["property_id"] = str(prop.id)
    stats["property_name"] = prop.name
    return stats
