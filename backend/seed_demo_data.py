import asyncio
import uuid
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import random

from sqlalchemy import delete, select
from app.database import async_session, engine
from app.models import Base, Property, KBDocument, Conversation, Message, Lead, AnalyticsDaily
from app.services import ingest_document

# Demo Config — mirrors the Vivatel KL pilot profile
DEMO_PROPERTY_NAME = "Vivatel Kuala Lumpur"
DEMO_META_PHONE = "+60312345678"
DEMO_WEBSITE = "https://vivatelhotels.com"
DEMO_ADR = Decimal("230.00")
DEMO_HOURLY_RATE = Decimal("25.00")

async def seed_demo_data():
    async with async_session() as db:
        print("🌱 Seeding Demo Data (Vivatel KL profile)...")

        # 1. Cleanup Existing Demo Data — DELETE existing Vivatel KL data
        print("   Cleaning up old data...")
        # Find existing demo property by name first
        existing_prop = await db.execute(
            select(Property).where(Property.name == DEMO_PROPERTY_NAME)
        )
        existing_props = existing_prop.scalars().all()
        for ep in existing_props:
            await db.execute(delete(AnalyticsDaily).where(AnalyticsDaily.property_id == ep.id))
            await db.execute(delete(Lead).where(Lead.property_id == ep.id))
            existing_convs = await db.execute(
                select(Conversation).where(Conversation.property_id == ep.id)
            )
            for ec in existing_convs.scalars().all():
                await db.execute(delete(Message).where(Message.conversation_id == ec.id))
            await db.execute(delete(Conversation).where(Conversation.property_id == ep.id))
            await db.execute(delete(KBDocument).where(KBDocument.property_id == ep.id))
            await db.execute(delete(Property).where(Property.id == ep.id))
        await db.flush()

        # 2. Create Property
        prop_id = uuid.uuid4()

        from app.config import get_settings
        settings = get_settings()

        twilio_number = settings.twilio_phone_number
        provider = "twilio" if twilio_number else "meta"
        meta_phone = twilio_number if provider == "twilio" else DEMO_META_PHONE

        prop = Property(
            id=prop_id,
            name=DEMO_PROPERTY_NAME,
            whatsapp_number=meta_phone,
            whatsapp_provider=provider,
            twilio_phone_number=twilio_number,
            website_url=DEMO_WEBSITE,
            notification_email="reservations@vivatel.com.my",
            operating_hours={"start": "09:00", "end": "22:00", "timezone": "Asia/Kuala_Lumpur"},
            adr=DEMO_ADR,
            hourly_rate=DEMO_HOURLY_RATE,
            ota_commission_pct=Decimal("18.00"),
        )
        db.add(prop)
        print(f"   Created Property: {DEMO_PROPERTY_NAME}")

        # 3. Knowledge Base — rich content with embeddings for RAG retrieval
        await db.flush()  # flush property so FK is available for ingest_document
        print("   Generating KB embeddings (calling Gemini API)...")
        kb_specs = [
            ("rooms", "Room Types and Rates",
             "Vivatel KL offers the following room types:\n"
             "- Superior Room: RM 230/night, inclusive of breakfast for 2. "
             "23 sqm, king or twin bed, city view. Max 2 adults + 1 child.\n"
             "- Deluxe Room: RM 280/night, inclusive of breakfast for 2. "
             "28 sqm, king bed, higher floor with KL skyline view.\n"
             "- Deluxe Suite: RM 350/night, inclusive of breakfast for 2. "
             "40 sqm, separate living area, panoramic city view.\n"
             "- Family Room: RM 320/night, inclusive of breakfast for 4. "
             "35 sqm, 2 queen beds. Max 4 adults.\n"
             "All rates subject to 10% service charge and 8% government tax.\n"
             "Harga bilik Superior RM 230/malam, Deluxe RM 280/malam, Suite RM 350/malam. "
             "Semua harga termasuk sarapan pagi untuk 2 orang."),
            ("facilities", "Hotel Facilities",
             "Vivatel KL facilities:\n"
             "- Swimming Pool: Rooftop infinity pool, open 7am-10pm daily\n"
             "  (Kolam renang rooftop buka 7 pagi hingga 10 malam)\n"
             "- Gym / Fitness Centre: 24-hour access for all guests\n"
             "  (Pusat kecergasan 24 jam untuk semua tetamu)\n"
             "- Restaurant: 'Viv Café' — halal-certified, breakfast 6:30am-10:30am\n"
             "- Meeting Rooms: 3 rooms, capacity 10-50 pax. From RM 500 half-day, RM 800 full-day.\n"
             "- Parking: Basement at RM 10/day for hotel guests\n"
             "- Laundry: Same-day laundry and dry cleaning available"),
            ("faqs", "Check-in, Check-out and Frequently Asked Questions",
             "Check-in: 3:00 PM (Masa daftar masuk: pukul 3 petang)\n"
             "Check-out: 12:00 PM (Masa daftar keluar: pukul 12 tengah hari)\n"
             "Early check-in: available from 12pm at RM 50 surcharge (subject to availability)\n"
             "Late check-out: until 3pm at 50% room rate; until 6pm at full room rate\n\n"
             "Q: Is breakfast included? / Sarapan termasuk ke?\n"
             "A: Yes, breakfast included in all room rates. Served at Viv Café 6:30am-10:30am.\n\n"
             "Q: Extra bed? / Boleh tambah katil?\n"
             "A: Extra bed RM 80/night, subject to availability.\n\n"
             "Q: Is the hotel halal? / Hotel ni halal ke?\n"
             "A: Yes, Viv Café is JAKIM halal-certified.\n\n"
             "Q: Pets? / Boleh bawa kucing?\n"
             "A: Pets are not allowed. Haiwan peliharaan tidak dibenarkan.\n\n"
             "Q: Airport transfer?\n"
             "A: KLIA to hotel RM 120/car. Book 24 hours in advance.\n\n"
             "Q: Smoking?\n"
             "A: Smoking prohibited in all rooms. Designated smoking area on Level 3."),
            ("directions", "Location and Directions",
             "Vivatel KL is at Jalan Sultan Ismail, Kuala Lumpur.\n"
             "From KLIA: KLIA Ekspres to KL Sentral (28 min), then Grab ~RM 15 (10 min).\n"
             "From KL Sentral: Grab 10 min (~RM 10-15) or Monorail 2 stops to Bukit Bintang.\n"
             "Nearby: Pavilion KL (5-min walk), KLCC (10-min drive), Bukit Bintang (3-min walk), "
             "Jalan Alor food street (7-min walk).\n"
             "Complimentary shuttle to Pavilion and KLCC runs hourly 9am-9pm."),
            ("policies", "Hotel Policies",
             "- Minimum check-in age: 18 years with valid ID\n"
             "- Children under 12 stay free in existing bedding\n"
             "- Pets are not allowed\n"
             "- Smoking prohibited in all rooms. Designated area: Level 3\n"
             "- Damage deposit: RM 200 at check-in\n"
             "- 24-hour cancellation policy. Late cancellations charged 1 night."),
            ("rates", "Group and Corporate Rates",
             "Group bookings (10+ rooms):\n"
             "- 10-19 rooms: 10% off published rates\n"
             "- 20-49 rooms: 15% off published rates\n"
             "- 50+ rooms: Contact sales for custom pricing\n\n"
             "Corporate rates (minimum 10 room nights/month):\n"
             "- Superior: RM 190/night (nett)\n"
             "- Deluxe: RM 230/night (nett)\n"
             "- Deluxe Suite: RM 300/night (nett)\n\n"
             "For weddings, events, and conferences: our Grand Ballroom fits up to 300 pax. "
             "Contact our events team for packages."),
        ]
        for doc_type, title, content in kb_specs:
            await ingest_document(db, prop_id, doc_type, title, content)
            print(f"     ✓ {title}")
        print("   Added Knowledge Base (6 docs with embeddings — RAG ready)")

        # 4. Demo Conversations (3 scenarios matching the sales demo script)

        # Scenario A: High-Value Lead — Wedding inquiry (after hours)
        # This is "ACT 3" of the demo — shows high-value flag, lead capture
        conv1_id = uuid.uuid4()
        conv1 = Conversation(
            id=conv1_id, property_id=prop_id,
            guest_identifier="60123456789", channel="whatsapp",
            guest_name="Sarah Lee", status="active", ai_mode="lead_capture",
            message_count=4, is_after_hours=True,
            last_message_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )
        msgs1 = [
            Message(conversation_id=conv1_id, role="guest",
                    content="Hi, I'm looking to book a wedding venue for Dec 2026. We need about 20 rooms for 3 nights.",
                    sent_at=datetime.now(timezone.utc) - timedelta(hours=2, minutes=5)),
            Message(conversation_id=conv1_id, role="ai",
                    content="Congratulations on your upcoming wedding! 🎊 We'd love to host your special day at Vivatel KL. For 20 rooms over 3 nights, you'd be looking at our group rate — 15% off published rates. May I ask what dates you have in mind, and roughly how many guests for the event itself?",
                    sent_at=datetime.now(timezone.utc) - timedelta(hours=2, minutes=4),
                    metadata_={"response_time_ms": 3200, "mode": "lead_capture", "model": "gemini-2.5-flash"}),
            Message(conversation_id=conv1_id, role="guest",
                    content="December 20-22, 2026. Around 150 pax for the reception. Do you have a ballroom?",
                    sent_at=datetime.now(timezone.utc) - timedelta(hours=2, minutes=2)),
            Message(conversation_id=conv1_id, role="ai",
                    content="Yes! Our Grand Ballroom seats up to 300 guests comfortably. For 20 rooms (Dec 20-22) + the ballroom, I'm flagging this as a priority enquiry for our Events Manager. Could I get your name and email so they can send you a full package proposal first thing tomorrow morning?",
                    sent_at=datetime.now(timezone.utc) - timedelta(hours=2, minutes=1),
                    metadata_={"response_time_ms": 4100, "mode": "lead_capture", "model": "gemini-2.5-flash"}),
        ]
        lead1 = Lead(
            conversation_id=conv1_id, property_id=prop_id,
            guest_name="Sarah Lee", guest_phone="60123456789",
            intent="event",  # matches extract schema: room_booking|event|fb_inquiry|general
            source_channel="whatsapp",
            is_after_hours=True,
            priority="high_value",
            flag_reason="Keyword match (Event/Group)",
            estimated_value=Decimal("13800.00"),  # 20 rooms × 3 nights × RM 230 ADR
            status="new",
        )
        db.add(conv1)
        db.add_all(msgs1)
        db.add(lead1)

        # Scenario B: BM inquiry (pool question) — shows bilingual response
        conv2_id = uuid.uuid4()
        conv2 = Conversation(
            id=conv2_id, property_id=prop_id,
            guest_identifier="60198765432", channel="whatsapp",
            guest_name="Ahmad", status="active", ai_mode="concierge",
            message_count=2, is_after_hours=False,
            last_message_at=datetime.now(timezone.utc) - timedelta(minutes=45),
        )
        msgs2 = [
            Message(conversation_id=conv2_id, role="guest",
                    content="Pool buka sampai pukul berapa? Ada gym tak?",
                    sent_at=datetime.now(timezone.utc) - timedelta(minutes=46)),
            Message(conversation_id=conv2_id, role="ai",
                    content="Kolam renang rooftop kami dibuka dari pukul 7 pagi hingga 10 malam setiap hari. Untuk pusat kecergasan (gym), ia tersedia 24 jam untuk semua tetamu — boleh pergi pada bila-bila masa! 💪\n\nAdakah anda ingin tahu tentang kemudahan lain atau ingin membuat tempahan?",
                    sent_at=datetime.now(timezone.utc) - timedelta(minutes=45),
                    metadata_={"response_time_ms": 2800, "mode": "concierge", "model": "gemini-2.5-flash"}),
        ]
        db.add(conv2)
        db.add_all(msgs2)

        # Scenario C: Complaint handoff — "ACT 4" of the demo
        conv3_id = uuid.uuid4()
        conv3 = Conversation(
            id=conv3_id, property_id=prop_id,
            guest_identifier="60101112222", channel="whatsapp",
            guest_name="Karen Tan", status="handed_off", ai_mode="handoff",
            message_count=3, is_after_hours=False,
            last_message_at=datetime.now(timezone.utc) - timedelta(minutes=20),
        )
        msgs3 = [
            Message(conversation_id=conv3_id, role="guest",
                    content="My aircond is not working and the room is boiling. This is unacceptable!",
                    sent_at=datetime.now(timezone.utc) - timedelta(minutes=22)),
            Message(conversation_id=conv3_id, role="ai",
                    content="I completely understand, and I'm sorry for this — a non-functioning aircond is genuinely uncomfortable. I'm flagging this conversation for our Duty Manager right now, along with all the details. They will reach out to you within the next 15 minutes. Is there anything else I can note down for them?",
                    sent_at=datetime.now(timezone.utc) - timedelta(minutes=21),
                    metadata_={"response_time_ms": 3500, "mode": "handoff", "model": "gemini-2.5-flash"}),
            Message(conversation_id=conv3_id, role="guest",
                    content="Please hurry, I have an early morning flight.",
                    sent_at=datetime.now(timezone.utc) - timedelta(minutes=20)),
        ]
        db.add(conv3)
        db.add_all(msgs3)

        print("   Added Conversations (3 demo scenarios)")

        # 5. Historical Analytics — 30 Days with all required fields
        print("   Generating 30-day analytics history...")
        start_date = datetime.now(timezone.utc).date() - timedelta(days=30)
        for i in range(30):
            day = start_date + timedelta(days=i)
            # Realistic daily volume: 20-35 base + weekend boost
            inquiries = random.randint(20, 35)
            if day.weekday() >= 5:
                inquiries += random.randint(10, 20)

            # After-hours: ~40% of total inquiries
            after_hours = int(inquiries * random.uniform(0.35, 0.50))
            # 100% of after-hours responded (AI is always on)
            after_hours_responded = after_hours

            # Lead capture: 30-45% of all inquiries
            leads = int(inquiries * random.uniform(0.30, 0.45))

            # Handoffs: 1-4 per day
            handoffs = random.randint(1, 4)

            # AI handled = total - handoffs
            ai_handled = inquiries - handoffs
            manually_handled = handoffs

            # Revenue: after-hours leads × ADR × 20% conversion
            after_hours_leads = int(after_hours * random.uniform(0.30, 0.45))
            estimated_revenue = Decimal(str(after_hours_leads)) * DEMO_ADR * Decimal("0.20")

            # Cost savings: AI handled × 0.25 hrs × hourly rate
            cost_savings = Decimal(str(ai_handled)) * Decimal("0.25") * DEMO_HOURLY_RATE

            # Avg response time: 2.5–8 seconds
            avg_rt = Decimal(str(round(random.uniform(2.5, 8.0), 1)))

            # Channel breakdown: mostly WhatsApp for a Malaysian hotel
            whatsapp_count = int(inquiries * random.uniform(0.70, 0.85))
            web_count = int(inquiries * random.uniform(0.10, 0.20))
            email_count = inquiries - whatsapp_count - web_count

            stat = AnalyticsDaily(
                property_id=prop_id,
                report_date=day,
                total_inquiries=inquiries,
                after_hours_inquiries=after_hours,
                after_hours_responded=after_hours_responded,
                leads_captured=leads,
                handoffs=handoffs,
                inquiries_handled_by_ai=ai_handled,
                inquiries_handled_manually=manually_handled,
                estimated_revenue_recovered=estimated_revenue,
                actual_revenue_recovered=Decimal("0"),
                cost_savings=cost_savings,
                avg_response_time_sec=avg_rt,
                channel_breakdown={
                    "whatsapp": whatsapp_count,
                    "web": web_count,
                    "email": email_count,
                    "facebook": 0,
                    "instagram": 0,
                    "tiktok": 0,
                },
            )
            db.add(stat)

        await db.commit()
        print("✅ Demo Data Seeded Successfully!")
        print(f"   Property ID: {prop_id}")
        print(f"   Property: {DEMO_PROPERTY_NAME}")
        print(f"   KB: 6 documents (rates, facilities, FAQs, directions, policies, group rates)")
        print(f"   Conversations: 3 (wedding lead, BM inquiry, complaint handoff)")
        print(f"   Analytics: 30 days of realistic data")

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
