"""
Seed realistic demo data for the Hotel Staff Dashboard.
Creates 60 conversations, 25 leads, and 30 days of analytics_daily
for the Grand Horizon Resort property.

Usage: docker exec -i <db_container> psql -U demo nocturn_demo < seed_dashboard_demo.sql
"""

import uuid
import random
from datetime import datetime, timedelta, timezone

PROPERTY_ID = "6ac91eab-99f5-4020-91c1-49abebd2d860"
NOW = datetime.now(timezone.utc)

# ─── Guest personas ───────────────────────────────────────────
GUESTS = [
    ("Sarah Chen", "+60123456001", "sarah.chen@gmail.com"),
    ("Michael Rodriguez", "+60123456002", "m.rodriguez@outlook.com"),
    ("Aisha binti Karim", "+60123456003", "aisha.karim@yahoo.com"),
    ("James O'Brien", "+60123456004", "james.obrien@icloud.com"),
    ("Fatimah Zahra", "+60123456005", "fatimah.z@hotmail.com"),
    ("David Kim", "+60123456006", "dkim@gmail.com"),
    ("Priya Sharma", "+60123456007", "priya.sharma@company.com"),
    ("Thomas Weber", "+60123456008", "t.weber@gmail.com"),
    ("Nur Aisyah", "+60123456009", "nuraisyah@gmail.com"),
    ("Robert Taylor", "+60123456010", "robert.t@yahoo.com"),
    ("Lena Fischer", "+60123456011", "lena.fischer@web.de"),
    ("Ahmad Faisal", "+60123456012", "ahmadfaisal@gmail.com"),
    ("Emily Watson", "+60123456013", "e.watson@outlook.com"),
    ("Hiroshi Tanaka", "+60123456014", "h.tanaka@jp.company.com"),
    ("Siti Nurhaliza", "+60123456015", "siti.n@gmail.com"),
    ("Carlos Mendez", "+60123456016", "carlos.m@gmail.com"),
    ("Rachel Green", "+60123456017", "rachel.green@gmail.com"),
    ("Omar Hassan", "+60123456018", "omar.hassan@outlook.com"),
    ("Lisa Anderson", "+60123456019", "lisa.a@company.com"),
    ("Tan Wei Ming", "+60123456020", "weiming.tan@gmail.com"),
    ("Sophie Martin", "+60123456021", "sophie.m@gmail.com"),
    ("Raj Patel", "+60123456022", "raj.patel@hotmail.com"),
    ("Anna Kowalski", "+60123456023", "anna.k@gmail.com"),
    ("Muhammad Rizki", "+60123456024", "rizki.m@yahoo.com"),
    ("Jennifer Liu", "+60123456025", "jennifer.liu@gmail.com"),
]

CHANNELS = ["whatsapp", "whatsapp", "whatsapp", "web", "web", "email"]
STATUSES = ["active", "active", "resolved", "resolved", "resolved", "handed_off"]
AI_MODES = ["concierge", "concierge", "lead_capture", "handoff"]
INTENTS = ["room_booking", "room_booking", "room_booking", "event", "fb_inquiry", "general"]
LEAD_STATUSES = ["new", "new", "contacted", "contacted", "qualified", "converted"]

GUEST_MESSAGES = [
    "Hi, do you have any suites available for tomorrow night?",
    "Hello! I'm planning a wedding reception for 200 guests. What packages do you offer?",
    "Good evening, I'd like to check availability for a family room this weekend.",
    "Do you have a conference room for a corporate event next month?",
    "What are the rates for a deluxe room for 3 nights?",
    "Hi there! I'm looking for a romantic getaway package. What do you recommend?",
    "Can I book a room with an ocean view for New Year's Eve?",
    "Hello, we need 10 rooms for a company retreat next week. Group discount?",
    "Is breakfast included with the standard room?",
    "I'd like to inquire about your spa and wellness packages.",
    "Do you allow pets in the hotel? I have a small dog.",
    "What time is check-in and check-out?",
    "Can you arrange airport pickup for us? We arrive at 3 PM.",
    "I need a room with wheelchair accessibility. What options do you have?",
    "Are there any special promotions for the lunar new year period?",
    "Can I get a late check-out on Sunday? We have an afternoon flight.",
    "What's the cancellation policy for bookings?",
    "Do you have interconnecting rooms? We're traveling with kids.",
    "Is there parking available at the hotel?",
    "I'd like to book the presidential suite for my anniversary.",
]

AI_RESPONSES = [
    "Good evening! Thank you for reaching out to Grand Horizon Resort. Yes, we do have suites available for tomorrow night. Our Executive Suite (65 sqm) is available at RM 850/night, and our Grand Suite (90 sqm) is at RM 1,200/night. Both come with complimentary breakfast, airport shuttle, and access to our infinity pool and spa.\n\nWould you like me to hold one for you? I just need your preferred room type and the number of guests.",
    "Hello! Congratulations on your upcoming wedding! 🎉 We'd love to help you plan your special day. Our Grand Ballroom can comfortably accommodate 200 guests and includes:\n\n- Custom-designed setup with floral arrangements\n- 5-course gala dinner with premium beverages\n- Complimentary bridal suite for 1 night\n- Wedding coordination team\n\nPackages start from RM 280 per person. Shall I arrange a site visit for you?",
    "Thank you for your inquiry! I'd be happy to help. For this weekend, we have several family-friendly options:\n\n🏨 Family Deluxe Room (45 sqm): RM 480/night\n🏨 Family Suite (70 sqm): RM 720/night\n\nBoth include extra beds for children, kids' welcome amenity, and access to our children's pool. Shall I check exact availability for your dates?",
    "Hello! We have excellent meeting facilities available. Our Business Center offers:\n\n📋 Boardroom (up to 20 pax): RM 1,500/day\n📋 Conference Hall (up to 100 pax): RM 4,500/day\n📋 Grand Ballroom (up to 300 pax): RM 8,000/day\n\nAll include AV equipment, WiFi, coffee breaks, and a dedicated event coordinator. What size meeting are you planning?",
    "Great question! Our rates for the Deluxe Room are:\n\n- Weekday: RM 380/night\n- Weekend: RM 450/night\n- 3-night package: RM 1,050 (save 8%!)\n\nAll rates include daily breakfast buffet, WiFi, and gym access. Would you like me to proceed with a booking?",
]

def gen_uuid():
    return str(uuid.uuid4())

def sql_ts(dt):
    return dt.strftime("'%Y-%m-%d %H:%M:%S+00'")

def sql_date(dt):
    return dt.strftime("'%Y-%m-%d'")

def sql_str(s):
    if s is None:
        return "NULL"
    return "'" + s.replace("'", "''") + "'"

lines = []
lines.append("-- ═══════════════════════════════════════════════════════")
lines.append("-- Demo Data Seed: Conversations, Messages, Leads, Analytics")
lines.append("-- Grand Horizon Resort")
lines.append("-- ═══════════════════════════════════════════════════════")
lines.append("")
lines.append("BEGIN;")
lines.append("")

conversation_ids = []
lead_conversation_ids = []

# ─── 60 Conversations + Messages ──────────────────────────────
for i in range(60):
    conv_id = gen_uuid()
    conversation_ids.append(conv_id)
    guest = GUESTS[i % len(GUESTS)]
    channel = random.choice(CHANNELS)
    status = random.choice(STATUSES)
    ai_mode = random.choice(AI_MODES)
    is_after_hours = random.random() < 0.35
    days_ago = random.randint(0, 29)
    hours_offset = random.randint(0, 23)
    started = NOW - timedelta(days=days_ago, hours=hours_offset)
    last_msg = started + timedelta(minutes=random.randint(2, 120))
    msg_count = random.randint(2, 8)

    lines.append(f"INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)")
    lines.append(f"VALUES ('{conv_id}', '{PROPERTY_ID}', {sql_str(channel)}, {sql_str(guest[1])}, {sql_str(guest[0])}, {sql_str(status)}, {str(is_after_hours).lower()}, {sql_str(ai_mode)}, {sql_ts(started)}, {sql_ts(last_msg)}, {sql_ts(last_msg)}, {msg_count});")
    lines.append("")

    # Generate messages for this conversation
    guest_msg = GUEST_MESSAGES[i % len(GUEST_MESSAGES)]
    ai_msg = AI_RESPONSES[i % len(AI_RESPONSES)]

    m1_time = started
    m1_id = gen_uuid()
    lines.append(f"INSERT INTO messages (id, conversation_id, role, content, sent_at)")
    lines.append(f"VALUES ('{m1_id}', '{conv_id}', 'guest', {sql_str(guest_msg)}, {sql_ts(m1_time)});")

    m2_time = m1_time + timedelta(seconds=random.randint(3, 15))
    m2_id = gen_uuid()
    lines.append(f"INSERT INTO messages (id, conversation_id, role, content, sent_at)")
    lines.append(f"VALUES ('{m2_id}', '{conv_id}', 'ai', {sql_str(ai_msg)}, {sql_ts(m2_time)});")

    # Add 1-3 more follow-up messages
    follow_ups = [
        ("guest", "That sounds great! Can I get more details?"),
        ("ai", "Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details."),
        ("guest", f"Sure, it's {guest[0]}, {guest[2]}"),
        ("ai", f"Wonderful! Thank you, {guest[0].split()[0]}. I've noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?"),
    ]
    t = m2_time
    for j in range(min(msg_count - 2, len(follow_ups))):
        t = t + timedelta(minutes=random.randint(1, 10))
        fid = gen_uuid()
        role, content = follow_ups[j]
        lines.append(f"INSERT INTO messages (id, conversation_id, role, content, sent_at)")
        lines.append(f"VALUES ('{fid}', '{conv_id}', {sql_str(role)}, {sql_str(content)}, {sql_ts(t)});")

    lines.append("")

# ─── 25 Leads ──────────────────────────────────────────────────
for i in range(25):
    lead_id = gen_uuid()
    conv_id = conversation_ids[i]
    guest = GUESTS[i % len(GUESTS)]
    intent = random.choice(INTENTS)
    status = random.choice(LEAD_STATUSES)
    is_after_hours = random.random() < 0.35
    channel = random.choice(CHANNELS)
    est_value = random.choice([350, 480, 720, 850, 1200, 1500, 2400, 4500, 8000, 280 * random.randint(50, 200)])
    actual_rev = round(est_value * random.uniform(0.8, 1.2), 2) if status == "converted" else None
    priority = "high_value" if est_value > 2000 else "standard"
    days_ago = random.randint(0, 29)
    captured = NOW - timedelta(days=days_ago, hours=random.randint(0, 12))
    
    flag = None
    if priority == "high_value":
        flag = random.choice(["Group booking", "Corporate event", "Wedding reception", "VIP guest", "Long-stay booking"])

    lines.append(f"INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)")
    actual_str = str(actual_rev) if actual_rev else "NULL"
    lines.append(f"VALUES ('{lead_id}', '{conv_id}', '{PROPERTY_ID}', {sql_str(guest[0])}, {sql_str(guest[1])}, {sql_str(guest[2])}, {sql_str(intent)}, {sql_str(channel)}, {str(is_after_hours).lower()}, {sql_str(status)}, {est_value}, {actual_str}, {sql_str(priority)}, {sql_str(flag)}, {sql_ts(captured)});")
    lines.append("")

# ─── 30 Days of Analytics Daily ────────────────────────────────
for day_offset in range(30):
    d = (NOW - timedelta(days=29 - day_offset)).date()
    # Weekend boost
    is_weekend = d.weekday() >= 5
    base_inquiries = random.randint(12, 35) if is_weekend else random.randint(5, 20)
    after_hours = int(base_inquiries * random.uniform(0.25, 0.5))
    after_hours_responded = int(after_hours * random.uniform(0.85, 1.0))
    leads = random.randint(1, max(2, int(base_inquiries * 0.3)))
    handoffs = random.randint(0, max(1, int(base_inquiries * 0.1)))
    ai_handled = base_inquiries - handoffs
    manual = handoffs
    avg_resp = round(random.uniform(2.5, 8.0), 2)
    # Revenue: RM 350-1200 per lead, some convert
    rev = round(leads * random.uniform(350, 800), 2)
    cost_save = round(base_inquiries * random.uniform(25, 45), 2)  # RM 25-45 saved per AI-handled
    breakdown = {
        "whatsapp": int(base_inquiries * random.uniform(0.5, 0.7)),
        "web": int(base_inquiries * random.uniform(0.15, 0.3)),
        "email": int(base_inquiries * random.uniform(0.05, 0.15)),
    }

    a_id = gen_uuid()
    import json
    lines.append(f"INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)")
    lines.append(f"VALUES ('{a_id}', '{PROPERTY_ID}', {sql_date(d)}, {base_inquiries}, {after_hours}, {after_hours_responded}, {leads}, {handoffs}, {ai_handled}, {manual}, {avg_resp}, {rev}, 0, {cost_save}, '{json.dumps(breakdown)}');")
    lines.append("")

lines.append("COMMIT;")
lines.append("")

# Write to SQL file
sql_content = "\n".join(lines)
with open("seed_dashboard_demo.sql", "w", encoding="utf-8") as f:
    f.write(sql_content)

print(f"Generated seed_dashboard_demo.sql")
print(f"  - 60 conversations with messages")
print(f"  - 25 leads")
print(f"  - 30 days of analytics_daily")
print(f"\nRun: docker exec -i mvp-research-sheerssoft-demo-db-1 psql -U demo nocturn_demo < seed_dashboard_demo.sql")
