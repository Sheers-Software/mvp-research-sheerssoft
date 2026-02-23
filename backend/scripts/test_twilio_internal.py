import asyncio
import os
import sys

# Add backend directory to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import async_session
from app.models import Property
from sqlalchemy import select
from app.services.twilio_whatsapp import normalize_twilio_webhook
from app.routes.channels import _handle_whatsapp_message_async

async def run_test():
    # 1. Mock the Twilio webhook payload
    payload = {
        "From": "whatsapp:+1234567890",
        "To": "whatsapp:+0987654321",  # Replace with actual property Twilio number if known
        "Body": "Hello from internal test script",
        "ProfileName": "TestGuest"
    }
    
    normalized = normalize_twilio_webhook(payload)
    print(f"Normalized: {normalized}")
    
    async with async_session() as db:
        # Get any property to test with
        result = await db.execute(select(Property).limit(1))
        prop = result.scalar_one_or_none()
        
        if not prop:
            print("No property found in DB to test with.")
            return
            
        print(f"Testing against Property: {prop.name} (ID: {prop.id})")
        
        # 2. Call the background webhook handler directly (bypassing fastapi route/auth)
        try:
            await _handle_whatsapp_message_async(
                property_id=prop.id,
                from_number=normalized["guest_identifier"],
                text=normalized["content"],
                guest_name=normalized["guest_name"]
            )
            print("Successfully processed message!")
        except Exception as e:
            print(f"Error processing message: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
