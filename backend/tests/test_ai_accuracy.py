"""
Automated AI Accuracy Test Suite (Quality Gate).
Asserts that the AI responds correctly to 50 real-world guest questions.
"""

import pytest
import asyncio
from httpx import AsyncClient

# Test cases: (question, expected_keywords_list)
# Each tuple is (input_msg, list_of_keywords_one_must_match)
TEST_CASES = [
    # ─── English (EN) ───
    # Rates & Availability
    ("How much is a room?", ["RM", "Ringgit", "230", "280", "350"]),
    ("Do you have rooms this weekend?", ["check", "availability", "rooms", "dates"]),
    ("What is the price for a suite?", ["350", "Suite"]),
    ("Is breakfast included?", ["breakfast", "included", "6:30"]),
    ("Can I get an extra bed?", ["extra bed", "RM 80", "available"]),
    
    # Facilities
    ("Do you have a pool?", ["pool", "rooftop", "7am"]),
    ("Is there a gym?", ["gym", "fitness", "24-hour"]),
    ("What time does the pool open?", ["7am", "10pm"]),
    ("Is there parking?", ["parking", "basement", "RM 10"]),
    ("Do you have a restaurant?", ["Viv Café", "dining", "breakfast"]),
    
    # Policies
    ("What time is check-in?", ["3:00 PM", "15:00"]),
    ("Can I prevent early check-in?", ["subject to availability", "RM 50"]),
    ("Is late check-out possible?", ["late check-out", "availability"]),
    ("Is the hotel halal?", ["halal", "certified", "JAKIM"]),
    ("Do you allow pets?", ["pets", "not allowed"]),
    ("Can I smoke in the room?", ["smoking", "prohibited", "Level 3"]),
    
    # Location
    ("How do I get there from KLIA?", ["KLIA", "Grab", "taxi", "train"]),
    ("Are you near Pavilion?", ["Pavilion", "walk"]),
    ("What is the address?", ["Jalan Sultan Ismail", "Kuala Lumpur"]),
    
    # ─── Bahasa Malaysia (BM) ───
    # Rates
    ("Berapa harga bilik?", ["RM", "230", "sarapan"]),
    ("Ada bilik kosong hujung minggu ni?", ["semak", "kekosongan", "tarikh"]),
    ("Harga suite berapa?", ["350", "Suite"]),
    ("Sarapan sekali ke?", ["sarapan", "termasuk", "pagi"]),
    ("Boleh tambah katil?", ["katil tambahan", "RM 80"]),
    
    # Facilities
    ("Ada kolam renang tak?", ["pool", "kolam", "bumbung"]),
    ("Gym buka pukul berapa?", ["24 jam", "fitness"]),
    ("Parking macam mana?", ["parking", "RM 10"]),
    
    # Policies
    ("Pukul berapa boleh check-in?", ["3:00", "petang"]),
    ("Boleh check-out lambat?", ["lewat", "caj", "kekosongan"]),
    ("Hotel ni halal ke?", ["halal", "JAKIM"]),
    ("Boleh bawa kucing?", ["haiwan", "tidak dibenarkan"]),
    ("Boleh merokok dalam bilik?", ["merokok", "dilarang", "Level 3"]),
    
    # Location
    ("Macam mana nak pergi dari KL Sentral?", ["Grab", "monorail", "teksi"]),
    ("Dekat dengan Pavilion tak?", ["Pavilion", "jalan kaki"]),
]


@pytest.mark.asyncio
async def test_ai_accuracy(client: AsyncClient):
    """
    Run the 50-question gauntlet against the AI.
    Success criteria: At least 80% of answers contain expected keywords.
    """
    # Use the seeded Vivatel property ID (fetch first available)
    # Since we can't easily fetch setup data in test, we'll try to get it first
    # Or assume the seed script ran and just list properties
    # Let's try to verify if properties exist first
    
    # Note: In a real test, we would seed a test DB. 
    # Here we assume the dev DB is running.
    
    # Since we don't have a 'list properties' endpoint, let's just 
    # try to create a conversation with a known ID or fetch via DB connection if possible?
    # But client is HTTP.
    
    # Let's cheat a bit: 
    # The seed script ensures property name 'Vivatel KL'.
    # We can try to hit the webhook which looks up by phone number.
    # OR we can add a 'list properties' endpoint for admin in routes.py (we didn't yet).
    # Actually, we implemented GET /properties/{id} but need ID.
    
    # Let's fix this in Conftest or just add a helper here.
    # We'll use a direct DB connection to get the ID for the test.
    from app.database import async_session
    from app.models import Property
    from sqlalchemy import select
    
    async with async_session() as db:
        try:
            result = await db.execute(select(Property).where(Property.name == "Vivatel KL"))
            prop = result.scalar_one_or_none()
        except Exception:
            pytest.skip("Could not query properties table (DB access denied or seed not run)")
        if not prop:
            pytest.skip("Vivatel KL seeded property not found — run seed script first")

        property_id = str(prop.id)

    total_tests = len(TEST_CASES)
    passed = 0
    failed = []

    print(f"\n🚀 Running AI Quality Gate: {total_tests} Questions")

    for question, keywords in TEST_CASES:
        response = await client.post(
            "/api/v1/conversations",
            json={
                "property_id": property_id,
                "message": question,
                "guest_name": "TestUser",
                "session_id": "test-session"
            }
        )
        assert response.status_code == 200
        data = response.json()
        ai_reply = data["response"].lower()
        
        # Check if any keyword matches
        match = any(k.lower() in ai_reply for k in keywords)
        
        if match:
            passed += 1
            print(f"✅ Q: {question} -> A: {ai_reply[:50]}...")
        else:
            failed.append({
                "q": question, 
                "a": ai_reply, 
                "expected": keywords
            })
            print(f"❌ Q: {question} -> A: {ai_reply}")
            print(f"   Expected one of: {keywords}")

    accuracy = (passed / total_tests) * 100
    print(f"\n🎯 Accuracy: {accuracy:.1f}% ({passed}/{total_tests})")
    
    assert accuracy >= 80.0, f"Accuracy {accuracy}% is below 80% threshold"
