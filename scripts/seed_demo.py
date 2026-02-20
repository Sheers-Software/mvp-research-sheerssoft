"""
Demo Data Seeder — Seeds the demo database with impressive, realistic hotel data.

Usage:
    python scripts/seed_demo.py

This script is idempotent — running it again resets the demo to a clean state.
It creates data for a fictional "Grand Riviera Hotel" in Kuala Lumpur.
"""

import asyncio
import uuid
import sys
import os
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal

# Add parent to path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# ─── Configuration ────────────────────────────────────────

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://demo:demo_password@localhost:5434/nocturn_demo"
)

# Fixed UUIDs for reproducibility
PROPERTY_ID = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")

# ─── Demo Data ────────────────────────────────────────────

PROPERTY = {
    "id": PROPERTY_ID,
    "name": "Grand Riviera Hotel",
    "whatsapp_number": "+60123456789",
    "notification_email": "reservations@grandriviera.demo",
    "website_url": "https://grandriviera.com",
    "operating_hours": {"start": "08:00", "end": "22:00", "timezone": "Asia/Kuala_Lumpur"},
    "adr": Decimal("320.00"),
    "ota_commission_pct": Decimal("18.00"),
    "conversion_rate": Decimal("0.25"),
    "slug": "grand-riviera",
    "timezone": "Asia/Kuala_Lumpur",
    "plan_tier": "pilot",
    "is_active": True,
}

# Knowledge Base documents
KB_DOCUMENTS = [
    {"doc_type": "rooms", "title": "Deluxe King Room", "content": "Spacious 35sqm room with king bed, city view, complimentary WiFi, rain shower, mini bar. Rate: RM280/night (direct), RM320 via OTAs. Max 2 adults + 1 child."},
    {"doc_type": "rooms", "title": "Superior Twin Room", "content": "32sqm room with two single beds, garden view, work desk, complimentary WiFi. Rate: RM240/night (direct). Ideal for business travellers."},
    {"doc_type": "rooms", "title": "Premier Suite", "content": "65sqm luxury suite with separate living area, panoramic KL skyline view, butler service, Nespresso machine, soaking tub. Rate: RM580/night (direct). Includes breakfast for 2."},
    {"doc_type": "rooms", "title": "Family Room", "content": "45sqm room with king bed + pull-out sofa, connecting rooms available. Rate: RM350/night. Includes breakfast for 2 adults + 2 children. Cribs available on request."},
    {"doc_type": "rates", "title": "Seasonal Rates 2026", "content": "Peak season (Dec-Feb, Jul-Aug): 20% surcharge. CNY special package: 3 nights at RM750 including reunion dinner. Ramadan promotion: 15% off all rooms. Long stay (7+ nights): 10% discount."},
    {"doc_type": "facilities", "title": "Hotel Facilities", "content": "Infinity pool (7am-10pm), gym (24hr), spa (10am-9pm), kids club (9am-6pm weekends), business centre, 3 meeting rooms (capacity 10-50 pax), concierge desk, airport shuttle (RM60 one-way)."},
    {"doc_type": "dining", "title": "Dining Options", "content": "Riviera Bistro (all-day dining, 6am-11pm), Skybar Lounge (5pm-midnight, dress code smart casual), Room service (24hr, 15% surcharge after 10pm). Breakfast buffet: RM55 per adult. Halal certified."},
    {"doc_type": "faqs", "title": "Common Questions", "content": "Check-in: 3pm, Check-out: 12pm. Early check-in/late check-out subject to availability (RM50 per hour). Cancellation: free up to 48hrs before. Parking: complimentary for in-house guests. Pets: not allowed."},
    {"doc_type": "directions", "title": "Location & Transport", "content": "Located at Jalan Sultan Ismail, Kuala Lumpur. 5 min walk to Bukit Bintang MRT. 45 min from KLIA (airport shuttle available). Grab recommended for city travel. Walking distance to Pavilion KL and Lot 10."},
    {"doc_type": "policies", "title": "Policies", "content": "Government tax: 10% service charge + 6% SST. Tourism tax: RM10/room/night for foreign guests. ID required at check-in. Credit card pre-authorization of RM200. No smoking in rooms (RM500 penalty)."},
]

# Demo conversations — mix of channels, statuses, and scenarios
def _t(days_ago: int, hour: int = 14, minute: int = 30) -> datetime:
    """Helper to create timestamps relative to today."""
    return datetime.now(timezone.utc).replace(hour=hour, minute=minute, second=0, microsecond=0) - timedelta(days=days_ago)

CONVERSATIONS = [
    # --- After-hours recovery success (WhatsApp) ---
    {
        "id": uuid.UUID("11111111-1111-1111-1111-111111111001"),
        "channel": "whatsapp", "guest_identifier": "+60187654321",
        "guest_name": "Ahmad Rizal", "status": "resolved",
        "ai_mode": "concierge", "is_after_hours": True,
        "started_at": _t(1, 23, 15), "message_count": 6,
        "messages": [
            {"role": "guest", "content": "Hi, I'm looking for a room for this weekend. Do you have availability?", "sent_at": _t(1, 23, 15)},
            {"role": "ai", "content": "Hi Ahmad! 😊 Great to hear from you. Yes, we have availability this weekend. Our Deluxe King Room is at RM280/night with a beautiful city view. Would you like me to check specific dates for you?", "sent_at": _t(1, 23, 15)},
            {"role": "guest", "content": "Saturday and Sunday please. 2 adults.", "sent_at": _t(1, 23, 16)},
            {"role": "ai", "content": "Perfect! I have a Deluxe King Room available for Sat-Sun (2 nights) at RM280/night — that's RM560 total. This is our best direct rate, saving you RM80 compared to Booking.com! Shall I help you reserve it? I'll just need your full name and email to hold the room.", "sent_at": _t(1, 23, 16)},
            {"role": "guest", "content": "Yes please! Ahmad Rizal, ahmad.rizal@email.com", "sent_at": _t(1, 23, 17)},
            {"role": "ai", "content": "Wonderful! I've noted your details: Ahmad Rizal, ahmad.rizal@email.com, 2 nights (Sat-Sun), Deluxe King Room at RM280/night. Our reservations team will confirm your booking first thing in the morning and send you a confirmation email. Thank you for choosing Grand Riviera Hotel! 🏨", "sent_at": _t(1, 23, 17)},
        ],
        "lead": {"guest_name": "Ahmad Rizal", "guest_phone": "+60187654321", "guest_email": "ahmad.rizal@email.com", "intent": "room_booking", "status": "converted", "estimated_value": Decimal("560.00"), "source_channel": "whatsapp", "is_after_hours": True, "priority": "high_value"},
    },
    # --- Web chat lead capture ---
    {
        "id": uuid.UUID("11111111-1111-1111-1111-111111111002"),
        "channel": "web", "guest_identifier": "web_session_abc123",
        "guest_name": "Sarah Chen", "status": "resolved",
        "ai_mode": "lead_capture", "is_after_hours": False,
        "started_at": _t(2, 10, 30), "message_count": 4,
        "messages": [
            {"role": "guest", "content": "Hi! We're planning a company annual dinner for about 40 people. Do you have event spaces?", "sent_at": _t(2, 10, 30)},
            {"role": "ai", "content": "Hello Sarah! Yes, the Grand Riviera has excellent event spaces! Our Grand Ballroom comfortably seats up to 50 guests for dinner. We offer customizable packages including AV equipment, dedicated event coordinator, and our award-winning catering. Could you share your preferred date and any specific requirements? I'd love to connect you with our events team!", "sent_at": _t(2, 10, 30)},
            {"role": "guest", "content": "We're looking at March 15th. Can I get a quote? sarah.chen@company.com", "sent_at": _t(2, 10, 32)},
            {"role": "ai", "content": "Perfect! March 15th is available. I've noted your details and our events team will prepare a customised quote and send it to sarah.chen@company.com within 24 hours. For 40 pax, our packages typically start from RM3,500. Is there anything specific you'd like included — like a projector setup or special dietary requirements?", "sent_at": _t(2, 10, 32)},
        ],
        "lead": {"guest_name": "Sarah Chen", "guest_email": "sarah.chen@company.com", "intent": "event", "status": "contacted", "estimated_value": Decimal("3500.00"), "source_channel": "web", "is_after_hours": False, "priority": "high_value"},
    },
    # --- Email inquiry (bilingual BM) ---
    {
        "id": uuid.UUID("11111111-1111-1111-1111-111111111003"),
        "channel": "email", "guest_identifier": "farah@gmail.com",
        "guest_name": "Farah Aminah", "status": "resolved",
        "ai_mode": "concierge", "is_after_hours": True,
        "started_at": _t(3, 1, 0), "message_count": 4,
        "messages": [
            {"role": "guest", "content": "Salam, saya nak tanya pasal bilik untuk family. Ada bilik yang boleh muat 2 dewasa dan 3 anak-anak?", "sent_at": _t(3, 1, 0)},
            {"role": "ai", "content": "Waalaikumsalam Farah! 😊 Terima kasih kerana menghubungi Grand Riviera Hotel. Untuk keluarga anda, saya cadangkan Family Room kami (45sqm) dengan katil king + sofa tarik keluar, dan boleh sambung dengan bilik sebelah. Harga bermula RM350/malam termasuk sarapan untuk 2 dewasa + 2 kanak-kanak. Untuk anak ketiga, kami boleh sediakan katil tambahan dengan RM80/malam. Bilakah tarikh yang anda inginkan?", "sent_at": _t(3, 1, 0)},
            {"role": "guest", "content": "Untuk cuti sekolah bulan Mac, 3 malam. Boleh dapat harga special?", "sent_at": _t(3, 8, 0)},
            {"role": "ai", "content": "Untuk 3 malam semasa cuti sekolah Mac, saya cadangkan Family Room + connecting Superior Twin. Jumlah: RM350 + RM240 = RM590/malam, x3 malam = RM1,770. Saya boleh tawarkan diskaun 10% untuk tempahan terus: RM1,593! Nak saya bantu buat tempahan? Sila berikan nama penuh dan nombor telefon anda.", "sent_at": _t(3, 8, 1)},
        ],
        "lead": {"guest_name": "Farah Aminah", "guest_email": "farah@gmail.com", "intent": "room_booking", "status": "new", "estimated_value": Decimal("1593.00"), "source_channel": "email", "is_after_hours": True, "priority": "standard"},
    },
    # --- Handoff scenario (complex request) ---
    {
        "id": uuid.UUID("11111111-1111-1111-1111-111111111004"),
        "channel": "whatsapp", "guest_identifier": "+60191234567",
        "guest_name": "David Tan", "status": "handed_off",
        "ai_mode": "handoff", "is_after_hours": False,
        "started_at": _t(0, 15, 0), "message_count": 5,
        "messages": [
            {"role": "guest", "content": "I need to arrange a honeymoon package for next month. Something really special — room decorations, spa couple treatment, romantic dinner.", "sent_at": _t(0, 15, 0)},
            {"role": "ai", "content": "Congratulations on your upcoming wedding, David! 🎉 For a truly special honeymoon, our Premier Suite (RM580/night) with panoramic KL skyline views would be perfect. I can see you're looking for a comprehensive package — decorations, spa, and dining.", "sent_at": _t(0, 15, 0)},
            {"role": "guest", "content": "Yes exactly. Also want to know about airport pickup and if you can arrange a surprise birthday cake too — it's my wife's birthday during our stay.", "sent_at": _t(0, 15, 1)},
            {"role": "ai", "content": "What a wonderful surprise! This is quite a special arrangement, and I want to make sure every detail is perfect for you. Let me connect you with our dedicated concierge team who can create a bespoke honeymoon + birthday package. They'll be able to coordinate the room decorations, couple spa, dinner reservation, airport transfer, and birthday cake all together.", "sent_at": _t(0, 15, 1)},
            {"role": "ai", "content": "🔔 I've notified our concierge team about your request. They'll reach out to you shortly on this same WhatsApp number. In the meantime, could you share your preferred dates and any dietary preferences for the dinner and cake?", "sent_at": _t(0, 15, 2)},
        ],
        "lead": {"guest_name": "David Tan", "guest_phone": "+60191234567", "intent": "room_booking", "status": "new", "estimated_value": Decimal("2500.00"), "source_channel": "whatsapp", "is_after_hours": False, "priority": "high_value", "flag_reason": "Complex honeymoon + birthday package — requires personal concierge"},
    },
    # --- Quick FAQ (no lead) ---
    {
        "id": uuid.UUID("11111111-1111-1111-1111-111111111005"),
        "channel": "web", "guest_identifier": "web_session_def456",
        "guest_name": None, "status": "resolved",
        "ai_mode": "concierge", "is_after_hours": False,
        "started_at": _t(1, 11, 0), "message_count": 2,
        "messages": [
            {"role": "guest", "content": "What time is checkout?", "sent_at": _t(1, 11, 0)},
            {"role": "ai", "content": "Check-out time at Grand Riviera Hotel is 12:00 PM (noon). If you need a late check-out, it's subject to availability at RM50 per hour. Would you like help with anything else? 😊", "sent_at": _t(1, 11, 0)},
        ],
        "lead": None,
    },
    # --- More conversations for volume ---
    {
        "id": uuid.UUID("11111111-1111-1111-1111-111111111006"),
        "channel": "whatsapp", "guest_identifier": "+60145678901",
        "guest_name": "Mei Ling", "status": "resolved",
        "ai_mode": "concierge", "is_after_hours": True,
        "started_at": _t(4, 23, 45), "message_count": 3,
        "messages": [
            {"role": "guest", "content": "Do you have parking? We're driving from Penang.", "sent_at": _t(4, 23, 45)},
            {"role": "ai", "content": "Hi Mei Ling! Yes, we offer complimentary covered parking for all in-house guests. We also have valet parking available. The hotel is easily accessible via the DUKE Highway. Safe travels from Penang! Would you like to make a reservation?", "sent_at": _t(4, 23, 45)},
            {"role": "guest", "content": "Great, thanks! Will book online.", "sent_at": _t(4, 23, 50)},
        ],
        "lead": None,
    },
    {
        "id": uuid.UUID("11111111-1111-1111-1111-111111111007"),
        "channel": "email", "guest_identifier": "james.w@business.com",
        "guest_name": "James Wong", "status": "resolved",
        "ai_mode": "lead_capture", "is_after_hours": False,
        "started_at": _t(5, 9, 0), "message_count": 4,
        "messages": [
            {"role": "guest", "content": "Hi, I need to book 5 rooms for our team visiting KL next month. Corporate rate available?", "sent_at": _t(5, 9, 0)},
            {"role": "ai", "content": "Hello James! We'd be happy to accommodate your team. For group bookings of 5+ rooms, we offer corporate rates starting from RM220/night for our Superior Twin Rooms. Could you share your company name and preferred dates? I'll have our sales team send you a formal quotation.", "sent_at": _t(5, 9, 0)},
            {"role": "guest", "content": "TechCorp Sdn Bhd. March 10-14. Need WiFi and meeting room access too.", "sent_at": _t(5, 9, 5)},
            {"role": "ai", "content": "Noted! For TechCorp, March 10-14 (4 nights x 5 rooms = 20 room nights), I can offer: Superior Twin at RM220/night, complimentary high-speed WiFi, and our 50-pax meeting room at RM500/day. Total estimate: RM5,900. Our sales team will email the detailed proposal to james.w@business.com today. Thank you for choosing Grand Riviera!", "sent_at": _t(5, 9, 5)},
        ],
        "lead": {"guest_name": "James Wong", "guest_email": "james.w@business.com", "intent": "room_booking", "status": "contacted", "estimated_value": Decimal("5900.00"), "source_channel": "email", "is_after_hours": False, "priority": "high_value", "flag_reason": "Corporate group booking — 20 room nights"},
    },
    {
        "id": uuid.UUID("11111111-1111-1111-1111-111111111008"),
        "channel": "web", "guest_identifier": "web_session_ghi789",
        "guest_name": "Priya Sharma", "status": "active",
        "ai_mode": "concierge", "is_after_hours": False,
        "started_at": _t(0, 14, 0), "message_count": 2,
        "messages": [
            {"role": "guest", "content": "Is your spa open on Sundays? What treatments do you recommend?", "sent_at": _t(0, 14, 0)},
            {"role": "ai", "content": "Hi Priya! Yes, our spa is open daily from 10am to 9pm, including Sundays. 💆‍♀️ Our most popular treatments are the Traditional Malay Massage (60min, RM180) and the Couple's Aromatherapy Package (90min, RM450 for two). Would you like me to help you book a session?", "sent_at": _t(0, 14, 0)},
        ],
        "lead": None,
    },
]

# Analytics — 7 days of growth trend (looks impressive on Money Slide)
def _gen_analytics(days: int = 7) -> list:
    """Generate 7 days of analytics showing growth."""
    records = []
    for i in range(days, 0, -1):
        day = date.today() - timedelta(days=i)
        base = 35 + (days - i) * 3  # Growing trend
        after_hours = int(base * 0.45)
        leads = int(base * 0.3)
        records.append({
            "property_id": PROPERTY_ID,
            "report_date": day,
            "total_inquiries": base,
            "after_hours_inquiries": after_hours,
            "after_hours_responded": after_hours,  # 100% response rate!
            "leads_captured": leads,
            "handoffs": max(1, int(base * 0.08)),
            "avg_response_time_sec": Decimal(str(round(12 + i * 0.5, 1))),
            "estimated_revenue_recovered": Decimal(str(round(leads * 320 * 0.25, 2))),
            "channel_breakdown": {"whatsapp": int(base * 0.55), "web": int(base * 0.30), "email": int(base * 0.15)},
        })
    return records


# ─── Seed Functions ───────────────────────────────────────

async def seed():
    """Main seed function — idempotent, clears and re-seeds."""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        # Create tables if they don't exist
        from app.models import Base
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        print("🧹 Clearing existing demo data...")
        await db.execute(text("DELETE FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE property_id = :pid)"), {"pid": str(PROPERTY_ID)})
        await db.execute(text("DELETE FROM leads WHERE property_id = :pid"), {"pid": str(PROPERTY_ID)})
        await db.execute(text("DELETE FROM conversations WHERE property_id = :pid"), {"pid": str(PROPERTY_ID)})
        await db.execute(text("DELETE FROM kb_documents WHERE property_id = :pid"), {"pid": str(PROPERTY_ID)})
        await db.execute(text("DELETE FROM analytics_daily WHERE property_id = :pid"), {"pid": str(PROPERTY_ID)})
        await db.execute(text("DELETE FROM properties WHERE id = :pid"), {"pid": str(PROPERTY_ID)})
        await db.commit()

        print("🏨 Creating Grand Riviera Hotel...")
        from app.models import Property, Conversation, Message, Lead, KBDocument, AnalyticsDaily
        prop = Property(**PROPERTY)
        db.add(prop)
        await db.flush()

        print(f"📚 Seeding {len(KB_DOCUMENTS)} knowledge base documents...")
        for doc in KB_DOCUMENTS:
            kb = KBDocument(property_id=PROPERTY_ID, **doc)
            db.add(kb)

        print(f"💬 Seeding {len(CONVERSATIONS)} conversations with messages...")
        for conv_data in CONVERSATIONS:
            messages = conv_data.pop("messages")
            lead_data = conv_data.pop("lead")

            conv = Conversation(property_id=PROPERTY_ID, **conv_data)
            db.add(conv)
            await db.flush()

            for msg in messages:
                m = Message(conversation_id=conv.id, **msg)
                db.add(m)

            if lead_data:
                lead = Lead(
                    conversation_id=conv.id,
                    property_id=PROPERTY_ID,
                    **lead_data,
                )
                db.add(lead)

        analytics = _gen_analytics(7)
        print(f"📊 Seeding {len(analytics)} days of analytics...")
        for a in analytics:
            db.add(AnalyticsDaily(**a))

        await db.commit()
        print()
        print("✅ Demo data seeded successfully!")
        print(f"   Property:      Grand Riviera Hotel ({PROPERTY_ID})")
        print(f"   KB Documents:  {len(KB_DOCUMENTS)}")
        print(f"   Conversations: {len(CONVERSATIONS)}")
        print(f"   Analytics:     {len(analytics)} days")
        print(f"   Login:         demo@nocturnai.com / demo2026")
        print()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
