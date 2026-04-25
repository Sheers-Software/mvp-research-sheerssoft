#!/usr/bin/env python3
"""
Shadow Pilot Demo Data Seeder.

Creates 7 days of synthetic WhatsApp observation data for the Vivatel KL property.
Allows the token-gated GM dashboard to render with realistic numbers without
needing a live Baileys bridge session.

Requires seed_demo_data.py to have been run first.

Usage:
    python backend/seed_shadow_pilot_demo.py
"""
import asyncio
import hashlib
import os
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete, select

from app.database import async_session
from app.models import Property, ShadowPilotAnalyticsDaily, ShadowPilotConversation
from app.services.pii_encryption import get_pii_service

# ─── Intent / preview pool ────────────────────────────────────────────────────

# (intent, topic, is_booking_intent)
INTENTS = [
    ("room_booking",       "room booking",        True),
    ("room_booking",       "room booking",        True),
    ("rate_query",         "rate enquiry",        True),
    ("rate_query",         "rate enquiry",        True),
    ("availability_check", "availability check",  True),
    ("group_booking",      "group booking",       False),
    ("facilities_inquiry", "pool and gym",        False),
    ("facilities_inquiry", "breakfast inquiry",   False),
    ("general",            "general enquiry",     False),
]

EN_PREVIEWS = [
    "Hi, I would like to book a room for 2 nights this weekend. Do you have availability?",
    "What is the price for a deluxe room? Is breakfast included?",
    "Are there any rooms available from 3rd to 5th May?",
    "Can you check if you have rooms available on the 15th for 3 people?",
    "What is your rate for a standard room on weekdays?",
    "I want to make a reservation for our company trip, around 10 people.",
    "Do you have a swimming pool? What are the operating hours?",
    "Is breakfast included in the room rate or charged separately?",
    "Can I get a late check-out? I need until 2pm.",
    "What is the parking fee per night for guests?",
    "Hi I want to book your Superior room for 15 May. How much?",
    "Do you have a halal dining option in the hotel?",
    "Is there a gym? What are the gym hours?",
    "Looking for a honeymoon package, do you have any?",
]

BM_PREVIEWS = [
    "Saya nak tempah bilik untuk 2 malam hujung minggu ni, ada tak?",
    "Berapa harga bilik standard untuk malam Sabtu?",
    "Ada bilik kosong pada 10 hingga 12 Mei tak?",
    "Bilik suite harganya berapa? Sarapan sekali tak?",
    "Boleh check availability untuk tarikh 20 Mei untuk 2 orang?",
    "Ada kolam renang tak? Pukul berapa buka?",
    "Sarapan pagi disediakan ke dengan harga bilik?",
    "Boleh check-out lambat tak sampai pukul 2 tengah hari?",
    "Parking percuma ke kenakan bayaran?",
    "Saya nak tanya pasal kadar bilik untuk group 8 orang.",
    "Bilik ada aircond tak? Berapa watt?",
    "Ada pakej bulan madu tak?",
]

# Pool of phone JIDs to simulate distinct guests
PHONE_JIDS = [f"601{str(i).zfill(8)}@s.whatsapp.net" for i in range(10010000, 10010050)]


def _is_after_hours_local(dt: datetime) -> bool:
    """Determine after-hours using 09:00–22:00 Asia/Kuala_Lumpur window."""
    try:
        from zoneinfo import ZoneInfo
        local = dt.astimezone(ZoneInfo("Asia/Kuala_Lumpur"))
    except Exception:
        local = dt
    return local.hour < 9 or local.hour >= 22


def _make_msg_time(day_offset: int, is_ah: bool) -> datetime:
    """Return a UTC timestamp for day_offset days ago, in the appropriate time band."""
    now_utc = datetime.now(timezone.utc)
    base = (now_utc - timedelta(days=day_offset)).replace(
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
        microsecond=0,
    )
    # KL is UTC+8
    if is_ah:
        kl_hour = random.choice([22, 23, 0, 1, 2, 5, 6, 7, 8])
    else:
        kl_hour = random.randint(9, 21)
    utc_hour = (kl_hour - 8) % 24
    return base.replace(hour=utc_hour)


def _make_conversation(prop: Property, day_offset: int) -> ShadowPilotConversation:
    pii = get_pii_service()
    jid = random.choice(PHONE_JIDS)

    is_ah = random.random() < 0.45          # 45% of messages are after-hours
    intent, topic, is_booking = random.choice(INTENTS)
    lang = random.choice(["en", "en", "bm"])  # ~66% English, 33% BM

    msg_time = _make_msg_time(day_offset, is_ah)

    # Unanswered probability:
    #  - after-hours + booking intent  → 65% unanswered (the leakage case)
    #  - after-hours only              → 35% unanswered
    #  - business hours                → 5% unanswered
    rand = random.random()
    if is_ah and is_booking:
        is_unanswered = rand < 0.65
    elif is_ah:
        is_unanswered = rand < 0.35
    else:
        is_unanswered = rand < 0.05

    first_staff_reply_at = None
    response_time_minutes = None

    if not is_unanswered:
        delay = random.randint(360, 900) if is_ah else random.randint(2, 25)
        first_staff_reply_at = msg_time + timedelta(minutes=delay)
        response_time_minutes = float(delay)

    previews = BM_PREVIEWS if lang == "bm" else EN_PREVIEWS
    preview = random.choice(previews)

    prop_adr = float(prop.adr or 230)
    prop_nights = float(prop.avg_stay_nights or 1.0)

    return ShadowPilotConversation(
        property_id=prop.id,
        guest_phone_encrypted=pii.encrypt(jid),
        guest_phone_hash=hashlib.sha256(jid.encode()).hexdigest(),
        first_guest_message_at=msg_time,
        last_guest_message_at=msg_time,
        first_staff_reply_at=first_staff_reply_at,
        last_staff_reply_at=first_staff_reply_at,
        response_time_minutes=response_time_minutes,
        is_after_hours=_is_after_hours_local(msg_time),
        is_unanswered=is_unanswered,
        is_booking_intent=is_booking,
        is_group_booking=(intent == "group_booking"),
        is_repeat_guest=False,
        intent=intent,
        intent_confidence=round(random.uniform(0.6, 0.95), 2),
        top_topic=topic,
        language_detected=lang,
        message_count_guest=random.randint(1, 3),
        message_count_staff=0 if is_unanswered else random.randint(1, 2),
        first_guest_message_preview=preview[:200],
        status="abandoned" if is_unanswered else "staff_replied",
        estimated_value_rm=round(prop_adr * prop_nights * 0.20, 2) if is_booking else None,
    )


async def seed_shadow_pilot_demo() -> None:
    async with async_session() as db:
        # ── Find Vivatel KL ──────────────────────────────────────────────────
        prop = await db.scalar(
            select(Property).where(Property.name == "Vivatel Kuala Lumpur")
        )
        if not prop:
            print("ERROR: Vivatel KL property not found. Run seed_demo_data.py first.")
            sys.exit(1)

        print(f"Property: {prop.name}  (slug={prop.slug or 'vivatel-kl'})")

        # ── Clear stale shadow pilot data ────────────────────────────────────
        await db.execute(
            delete(ShadowPilotAnalyticsDaily).where(
                ShadowPilotAnalyticsDaily.property_id == prop.id
            )
        )
        await db.execute(
            delete(ShadowPilotConversation).where(
                ShadowPilotConversation.property_id == prop.id
            )
        )
        await db.flush()

        # ── Enable shadow pilot mode on the property ─────────────────────────
        prop.shadow_pilot_mode = True
        prop.shadow_pilot_session_active = True
        if not prop.shadow_pilot_start_date:
            prop.shadow_pilot_start_date = datetime.now(timezone.utc) - timedelta(days=7)
        await db.commit()

        # ── Seed 7 days of conversations ─────────────────────────────────────
        total_convs = 0
        for day_offset in range(1, 8):
            count = random.randint(9, 14)
            for _ in range(count):
                conv = _make_conversation(prop, day_offset)
                db.add(conv)
                total_convs += 1
        await db.commit()
        print(f"Seeded {total_convs} conversations across 7 days.")

        # ── Run daily aggregation for each past day ───────────────────────────
        from app.services.shadow_pilot_aggregator import _aggregate_property

        now_utc = datetime.now(timezone.utc)
        for day_offset in range(1, 8):
            target = (now_utc - timedelta(days=day_offset)).date()
            count = await _aggregate_property(db, prop, target)
            print(f"  Day -{day_offset} ({target}): {count} conversations → analytics row created.")

        # ── Generate 30-day JWT dashboard token ───────────────────────────────
        try:
            import jwt as pyjwt
        except ImportError:
            import PyJWT as pyjwt  # fallback

        from app.config import get_settings
        settings = get_settings()

        exp = datetime.now(timezone.utc) + timedelta(days=30)
        token = pyjwt.encode(
            {
                "property_id": str(prop.id),
                "type": "shadow_dashboard",
                "exp": exp,
            },
            settings.jwt_secret,
            algorithm="HS256",
        )
        prop.shadow_pilot_dashboard_token = token
        prop.shadow_pilot_dashboard_token_expires = exp
        await db.commit()

        slug = prop.slug or "vivatel-kl"
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3001")
        dashboard_url = f"{frontend_url}/shadow/{slug}?token={token}"

        print(f"\n✅ Shadow Pilot Demo Data Ready!")
        print(f"   Total conversations : {total_convs}")
        print(f"   Dashboard token     : valid for 30 days")
        print(f"\n   GM Dashboard URL:")
        print(f"   {dashboard_url}")
        print(f"\n   Open in browser to verify the revenue report renders.")


if __name__ == "__main__":
    asyncio.run(seed_shadow_pilot_demo())
