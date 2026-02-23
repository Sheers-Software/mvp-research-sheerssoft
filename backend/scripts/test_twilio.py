import asyncio
import os
import sys

# Add backend directory to sis path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.twilio_whatsapp import send_twilio_message
from app.config import get_settings

async def test_twilio():
    settings = get_settings()
    
    # We will test using explicit numbers here to ensure the logic flows
    # Ensure credentials are set for Twilio (temporarily mock for the script if they aren't loaded)
    
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        print("ERROR: Twilio credentials not fully loaded in settings.")
        print(f"SID Loaded: {'Yes' if settings.twilio_account_sid else 'No'}")
        print(f"Token Loaded: {'Yes' if settings.twilio_auth_token else 'No'}")
        return

    print(f"Using Environment: {settings.environment}")
    print(f"Loaded Twilio SID: {settings.twilio_account_sid[:5]}...")
    
    # We need a phone number to test with. For now, we will just print success that the config is loaded
    # and we can reach the point of calling Twilio.
    # To actually test sending, we'd need a verified Sandbox number or registered sender.
    
    print("\nTwilio integration script loaded successfully. To genuinely test sending, provide a valid 'to' number.")
    print("For now, this confirms the application environment can parse the Twilio configuration.")

if __name__ == "__main__":
    asyncio.run(test_twilio())
