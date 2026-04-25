"""
Shadow Pilot Message Processor
Receives events from the Baileys bridge and updates ShadowPilotConversation records.
"""
import hashlib
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.models import ShadowPilotConversation, Property
from app.services.pii_encryption import get_pii_service
from app.services.shadow_pilot_classifier import classify_intent

logger = structlog.get_logger()


def hash_phone(phone_jid: str) -> str:
    return hashlib.sha256(phone_jid.encode()).hexdigest()


def phone_from_jid(jid: str) -> str:
    return "+" + jid.split("@")[0]


def _is_after_hours(prop: Property, message_time: datetime) -> bool:
    """Check if message_time is outside the property's operating hours."""
    schedule = prop.operating_hours or {}
    tz_name = prop.timezone or "Asia/Kuala_Lumpur"
    try:
        from zoneinfo import ZoneInfo
        local_time = message_time.astimezone(ZoneInfo(tz_name))
    except Exception:
        local_time = message_time

    weekday = local_time.strftime('%A').lower()
    day_sched = schedule.get(weekday, schedule.get('default', {}))
    open_str = str(day_sched.get('open', '09:00'))
    close_str = str(day_sched.get('close', '18:00'))
    open_h, open_m = int(open_str.split(':')[0]), int(open_str.split(':')[1])
    close_h, close_m = int(close_str.split(':')[0]), int(close_str.split(':')[1])
    local_minutes = local_time.hour * 60 + local_time.minute
    open_minutes = open_h * 60 + open_m
    close_minutes = close_h * 60 + close_m
    return local_minutes < open_minutes or local_minutes >= close_minutes


async def handle_message_received(
    db: AsyncSession,
    property_slug: str,
    sender_jid: str,
    message_id: str,
    content_preview: Optional[str],
    timestamp_ms: int,
    has_media: bool,
) -> None:
    """
    Process an incoming guest message during shadow pilot.
    Creates or updates a ShadowPilotConversation. NEVER sends any reply.
    """
    prop = await db.scalar(select(Property).where(Property.slug == property_slug))
    if not prop or not prop.shadow_pilot_mode:
        return

    message_time = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    phone_hash = hash_phone(sender_jid)

    existing = await db.scalar(
        select(ShadowPilotConversation)
        .where(
            ShadowPilotConversation.property_id == prop.id,
            ShadowPilotConversation.guest_phone_hash == phone_hash,
            ShadowPilotConversation.status == "open",
        )
        .order_by(ShadowPilotConversation.first_guest_message_at.desc())
    )

    after_hours = _is_after_hours(prop, message_time)

    if existing:
        existing.last_guest_message_at = message_time
        existing.message_count_guest += 1
        existing.updated_at = datetime.utcnow()
    else:
        prior = await db.scalar(
            select(ShadowPilotConversation)
            .where(
                ShadowPilotConversation.property_id == prop.id,
                ShadowPilotConversation.guest_phone_hash == phone_hash,
            )
        )
        is_repeat = prior is not None
        intent, confidence, topic, language = await classify_intent(content_preview or "")

        pii = get_pii_service()
        conv = ShadowPilotConversation(
            property_id=prop.id,
            guest_phone_encrypted=pii.encrypt(sender_jid),
            guest_phone_hash=phone_hash,
            first_guest_message_at=message_time,
            last_guest_message_at=message_time,
            is_after_hours=after_hours,
            is_booking_intent=intent in ("room_booking", "rate_query", "availability_check"),
            is_group_booking=intent == "group_booking",
            is_repeat_guest=is_repeat,
            intent=intent,
            intent_confidence=confidence,
            top_topic=topic,
            language_detected=language,
            message_count_guest=1,
            first_guest_message_preview=content_preview[:200] if content_preview else None,
            status="open",
        )
        db.add(conv)

    await db.commit()
    logger.info("shadow_message_received", property=property_slug, after_hours=after_hours)


async def handle_message_sent(
    db: AsyncSession,
    property_slug: str,
    recipient_jid: str,
    message_id: str,
    timestamp_ms: int,
) -> None:
    """
    Process a staff outgoing reply. Updates response_time_minutes.
    Staff message CONTENT is never captured — timestamp only.
    """
    prop = await db.scalar(select(Property).where(Property.slug == property_slug))
    if not prop or not prop.shadow_pilot_mode:
        return

    reply_time = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    phone_hash = hash_phone(recipient_jid)

    conv = await db.scalar(
        select(ShadowPilotConversation)
        .where(
            ShadowPilotConversation.property_id == prop.id,
            ShadowPilotConversation.guest_phone_hash == phone_hash,
            ShadowPilotConversation.status == "open",
        )
        .order_by(ShadowPilotConversation.first_guest_message_at.desc())
    )
    if not conv:
        return

    if conv.first_staff_reply_at is None:
        conv.first_staff_reply_at = reply_time
        conv.response_time_minutes = float(
            (reply_time - conv.first_guest_message_at).total_seconds() / 60
        )

    conv.last_staff_reply_at = reply_time
    conv.message_count_staff += 1
    conv.status = "staff_replied"
    conv.updated_at = datetime.utcnow()

    if conv.is_booking_intent and conv.estimated_value_rm is None:
        prop_adr = float(prop.adr or 230.0)
        prop_nights = float(prop.avg_stay_nights or 1.0)
        conv.estimated_value_rm = prop_adr * prop_nights * 0.20

    await db.commit()
