import asyncio
import uuid
import httpx
import json
import sys
import os

# Ensure we can import app models if needed, though mostly we will use API
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000/api/v1"
# We fetch property ID dynamically, but we need the phone number used in seed
DEMO_PHONE_ID = "601112223333" 

async def simulate_demo():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        print("\n🎬 STARTING DEMO SIMULATION 'The Grand Horizon'...\n")
        
        # 0. Authenticate (Admin)
        print("🔑 Step 0: Authenticating...")
        try:
            auth_resp = await client.post(f"{BASE_URL}/auth/token", data={
                "username": "admin",
                "password": "password123"
            })
            if auth_resp.status_code != 200:
                print(f"❌ Auth Failed: {auth_resp.status_code} - {auth_resp.text}")
                return
            token = auth_resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("   ✅ Authenticated.")
        except Exception as e:
            print(f"❌ Auth Error: {e}")
            return

        # 1. GET Property
        try:
            # Use authenticated headers
            resp = await client.get(f"{BASE_URL}/properties", headers=headers)
            if resp.status_code != 200:
                print(f"❌ API Error: {resp.status_code} - {resp.text}")
                return
            properties = resp.json()
            if not properties:
                print("❌ No properties found! Did you run start_demo.ps1?")
                return
            
            # Find Grand Horizon
            demo_prop = next((p for p in properties if "Grand Horizon" in p["name"]), None)
            if not demo_prop:
                print("❌ Grand Horizon Resort not found!")
                return
            
            prop_id = demo_prop["id"]
            print(f"✅ Step 1: Dashboard Loaded. Property: {demo_prop['name']} (ID: {prop_id})")
            print(f"   - ADR: {demo_prop['adr']}")
            print(f"   - Phone ID: {demo_prop['whatsapp_number']}")
            
            if demo_prop['whatsapp_number'] != DEMO_PHONE_ID:
                 print(f"⚠️ Warning: Demo Phone ID mismatch. Expected {DEMO_PHONE_ID}, got {demo_prop['whatsapp_number']}")
        except Exception as e:
             print(f"❌ API Error: {e}")
             return

        # 2. Live Chat Simulation (The "Magic")
        print("\n📱 Step 2: Simulating Live Guest Chat (WhatsApp)...")
        guest_phone = "60199887766" # New guest for live demo
        
        def make_payload(text):
            return {
              "entry": [{
                "changes": [{
                  "value": {
                    "metadata": { "phone_number_id": DEMO_PHONE_ID },
                    "contacts": [{ "profile": { "name": "Demo Guest" } }],
                    "messages": [{
                        "from": guest_phone,
                        "id": f"wamid.{uuid.uuid4()}",
                        "text": { "body": text },
                        "type": "text"
                    }]
                  }
                }]
              }]
            }

        # Message 1: Opening
        msg1 = "Hi, I'm John Doe. I'm looking for a venue for my wedding next year."
        print(f"   Guest: \"{msg1}\"")
        resp1 = await client.post(f"{BASE_URL}/webhook/whatsapp", json=make_payload(msg1))
        print(f"   Webhook Resp: {resp1.json()}")
        await asyncio.sleep(1)

        # Message 2: Context
        msg2 = "Maybe around 150 pax. Got package ah?" # Manglish check
        print(f"   Guest: \"{msg2}\"")
        resp2 = await client.post(f"{BASE_URL}/webhook/whatsapp", json=make_payload(msg2))
        print(f"   Webhook Resp: {resp2.json()}")
        
        print("\n⏳ Waiting 10s for AI processing...")
        await asyncio.sleep(10)

        # 3. Lead Capture Verification
        print("\n🕵️ Step 3: Verifying Lead Capture...")
        
        leads_resp = await client.get(f"{BASE_URL}/properties/{prop_id}/leads", headers=headers)
        if leads_resp.status_code != 200:
            print(f"❌ Leads API Error: {leads_resp.status_code} - {leads_resp.text}")
            return
            
        leads = leads_resp.json()
        if not isinstance(leads, list):
             print(f"❌ Leads API returned non-list: {leads}")
             print(leads)
             return

        # Find our guest
        new_lead = next((l for l in leads if l["guest_phone"] == guest_phone), None)
        
        if new_lead:
            print(f"   ✅ Lead Captured!")
            print(f"   - Name: {new_lead['guest_name']}")
            print(f"   - Intent: {new_lead['intent']}")
            print(f"   - Priority: {new_lead.get('priority')} (Expecting 'high_value' due to wedding)")
            print(f"   - Est. Value: {new_lead['estimated_value']}")
        else:
            print("   ❌ Lead NOT captured.")

        # 4. Handoff Scenario Check
        print("\n⚠️ Step 4: Checking Handoff Alerts...")
        # Check for the "Karen" scenario seeded earlier
        handoff_lead = next((l for l in leads if "Karen" in (l["guest_name"] or "")), None)
        # Or check conversations status
        
        convs_resp = await client.get(f"{BASE_URL}/properties/{prop_id}/conversations?status=pending_handoff", headers=headers)
        handoffs = convs_resp.json()
        
        if handoffs:
            print(f"   ✅ 'Action Required' Alert Active!")
            print(f"   - Pending Handoffs: {len(handoffs)}")
            print(f"   - Guest: {handoffs[0]['guest_name']} (Status: {handoffs[0]['status']})")
        else:
            print("   ❌ No pending handoffs found (Check seed data).")

        print("\n🏁 Demo Simulation Complete.")

if __name__ == "__main__":
    asyncio.run(simulate_demo())
