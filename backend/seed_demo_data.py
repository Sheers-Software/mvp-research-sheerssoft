import asyncio
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import random

from sqlalchemy import delete, select
from app.database import async_session, engine
from app.models import Base, Property, KBDocument, Conversation, Message, Lead, AnalyticsDaily

# Demo Config
DEMO_PROPERTY_NAME = "Grand Horizon Resort"
DEMO_PHONE = "601112223333"
DEMO_WEBSITE = "https://grandhorizon.demo"

async def seed_demo_data():
    async with async_session() as db:
        print("🌱 Seeding Demo Data...")

        # 1. Cleanup Existing Demo Data
        print("   Cleaning up old data...")
        tables = [Lead, Message, Conversation, KBDocument, AnalyticsDaily, Property]
        # In a real heavy production setup we'd be more careful, but for local demo:
        # We'll just delete data associated with our Demo Property if it exists, 
        # but to be safe and clean for a demo, let's just wipe everything 
        # (Assuming local dev DB here as per "local system" request)
        async with engine.begin() as conn:
             await conn.run_sync(Base.metadata.drop_all)
             await conn.run_sync(Base.metadata.create_all)

        # 2. Create Property
        prop_id = uuid.uuid4()
        
        from app.config import get_settings
        settings = get_settings()
        
        # Check if Twilio is configured
        twilio_number = settings.twilio_phone_number
        provider = "twilio" if twilio_number else "meta"
        
        prop = Property(
            id=prop_id,
            name=DEMO_PROPERTY_NAME,
            whatsapp_number=DEMO_PHONE,
            whatsapp_provider=provider,
            twilio_phone_number=twilio_number,
            website_url=DEMO_WEBSITE,
            operating_hours={"start": "09:00", "end": "22:00", "timezone": "Asia/Kuala_Lumpur"},
            adr=Decimal("450.00"), # Higher ADR for luxury feel
            ota_commission_pct=Decimal("18.00"),
            conversion_rate=Decimal("0.20")
        )
        db.add(prop)
        print(f"   Created Property: {DEMO_PROPERTY_NAME}")

        # 3. Knowledge Base
        kb_docs = [
            KBDocument(property_id=prop_id, doc_type="rates", title="Room Rates", 
                       content="Deluxe Room: RM450/night. Executive Suite: RM850/night. Breakfast included."),
            KBDocument(property_id=prop_id, doc_type="facilities", title="Pool & Gym", 
                       content="Infinity pool open 7am-10pm. Gym is 24/7 for guests."),
            KBDocument(property_id=prop_id, doc_type="dining", title="Restaurants", 
                       content="Sunset Grill (Western) opens 6pm-11pm. Horizon Cafe (Local) opens 7am-10pm."),
            KBDocument(property_id=prop_id, doc_type="policies", title="Check-in/Out", 
                       content="Check-in: 3:00 PM. Check-out: 12:00 PM. Late checkout available upon request."),
        ]
        db.add_all(kb_docs)
        print("   Added Knowledge Base (4 docs)")

        # 4. Conversations & Messages
        
        # Scenario A: High Value Lead (Wedding)
        conv1_id = uuid.uuid4()
        conv1 = Conversation(
            id=conv1_id, property_id=prop_id, 
            guest_identifier="60123456789", channel="whatsapp", 
            guest_name="Sarah Lee", status="active", ai_mode="concierge",
            message_count=4, is_after_hours=True
        )
        msgs1 = [
            Message(conversation_id=conv1_id, role="user", content="Hi, I'm looking to book a wedding venue for Dec 2026."),
            Message(conversation_id=conv1_id, role="assistant", content="Congratulations Sarah! We'd love to host your special day. Approximately how many guests are you expecting?"),
            Message(conversation_id=conv1_id, role="user", content="Around 150 pax. Do you have a hall?"),
            Message(conversation_id=conv1_id, role="assistant", content="Yes, our Grand Ballroom fits 200 comfortably. I'll have our events manager contact you with packages. What's your email?"),
        ]
        lead1 = Lead(
            conversation_id=conv1_id, property_id=prop_id,
            guest_name="Sarah Lee", guest_phone="60123456789", intent="booking_inquiry",
            priority="high_value", flag_reason="Keyword match (Wedding)",
            estimated_value=Decimal("15000.00"), status="new"
        )
        db.add(conv1)
        db.add_all(msgs1)
        db.add(lead1)

        # Scenario B: Standard Inquiry (Pool)
        conv2_id = uuid.uuid4()
        conv2 = Conversation(
            id=conv2_id, property_id=prop_id, 
            guest_identifier="60198765432", channel="whatsapp", 
            guest_name="Ahmad", status="active", ai_mode="concierge",
            message_count=2, is_after_hours=False
        )
        msgs2 = [
            Message(conversation_id=conv2_id, role="user", content="Pool buka sampai pukul berapa?"),
            Message(conversation_id=conv2_id, role="assistant", content="Kolam renang infiniti kami dibuka dari jam 7 pagi hingga 10 malam setiap hari."),
        ]
        db.add(conv2)
        db.add_all(msgs2)

        # Scenario C: Pending Handoff (Complaint)
        conv3_id = uuid.uuid4()
        conv3 = Conversation(
            id=conv3_id, property_id=prop_id, 
            guest_identifier="60101112222", channel="whatsapp", 
            guest_name="Karen", status="pending_handoff", ai_mode="handoff",
            message_count=3, is_after_hours=False
        )
        msgs3 = [
            Message(conversation_id=conv3_id, role="user", content="My aircond is not working! This is unacceptable."),
            Message(conversation_id=conv3_id, role="assistant", content="I apologize for the inconvenience. I will alert the duty manager immediately to check on your room."),
        ]
        db.add(conv3)
        db.add_all(msgs3)

        print("   Added Conversations (3 scenarios)")

        # 5. Historical Analytics (Last 30 Days)
        print("   Generating Analytics History...")
        start_date = datetime.now(timezone.utc).date() - timedelta(days=30)
        for i in range(30):
            day = start_date + timedelta(days=i)
            # Randomized realistic trend
            inquiries = random.randint(15, 45)
            # Weekends higher
            if day.weekday() >= 5: 
                inquiries += 15
            
            leads = int(inquiries * 0.4)
            revenue = leads * float(prop.adr) * 0.20 # 20% conversion logic
            
            stat = AnalyticsDaily(
                property_id=prop_id,
                report_date=day,
                total_inquiries=inquiries,
                leads_captured=leads,
                handoffs=random.randint(0, 3),
                estimated_revenue_recovered=Decimal(revenue),
                avg_response_time_sec=random.uniform(2.5, 15.0)
            )
            db.add(stat)

        await db.commit()
        print("✅ Demo Data Seeded Successfully!")
        print(f"   Property ID: {prop_id}")

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
