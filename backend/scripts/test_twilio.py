"""
test_twilio.py
--------------
End-to-end WhatsApp send test via Twilio.

Usage:
    # From repo root — requires a real Twilio sandbox verified recipient:
    $env:ENVIRONMENT = "demo"
    $env:TO_NUMBER   = "+60XXXXXXXXX"   # Your phone number (verified in Twilio sandbox)
    python backend/scripts/test_twilio.py

The script will send a real WhatsApp test message from the configured Twilio
sandbox/sender number to TO_NUMBER and print the resulting Twilio Message SID.

Prerequisites:
  - TWILIO_ACCOUNT_SID loaded (env or GCP Secret Manager)
  - TWILIO_AUTH_TOKEN loaded
  - TWILIO_PHONE_NUMBER loaded (the Twilio sandbox / sender number)
  - TO_NUMBER env var set to a Twilio sandbox–verified phone number
"""

import asyncio
import os
import sys
import importlib.util

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import twilio_whatsapp directly to avoid triggering services/__init__.py
# which has a top-level 'from google import genai' that fails on local machines
# without the full ml stack installed.
_spec = importlib.util.spec_from_file_location(
    "twilio_whatsapp",
    os.path.join(os.path.dirname(__file__), "..", "app", "services", "twilio_whatsapp.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
send_twilio_message = _mod.send_twilio_message

from app.config import get_settings


async def run():
    settings = get_settings()

    print("── Twilio E2E Send Test ─────────────────────────────────────")
    print(f"  Environment  : {settings.environment}")

    # Credential checks
    missing = []
    if not settings.twilio_account_sid:
        missing.append("TWILIO_ACCOUNT_SID")
    if not settings.twilio_auth_token:
        missing.append("TWILIO_AUTH_TOKEN")
    if not settings.twilio_phone_number:
        missing.append("TWILIO_PHONE_NUMBER")

    if missing:
        print(f"\n  ❌ Missing credentials: {', '.join(missing)}")
        print("     Run validate_secrets.py first to diagnose the issue.")
        sys.exit(1)

    print(f"  SID          : {settings.twilio_account_sid[:10]}...")
    print(f"  From         : {settings.twilio_phone_number}")

    to_number = os.environ.get("TO_NUMBER", "").strip()
    if not to_number:
        print("\n  ❌ TO_NUMBER env var not set.")
        print("     Set it to a Twilio-sandbox-verified number, e.g.:")
        print("     $env:TO_NUMBER = \"+60XXXXXXXXX\"")
        sys.exit(1)

    print(f"  To           : {to_number}\n")

    result = await send_twilio_message(
        to_number=to_number,
        message_text=(
            "✅ *Nocturn AI — Test Message*\n\n"
            "This is a live Twilio WhatsApp send test from the backend.\n"
            "If you received this, the full stack is working correctly!"
        ),
        from_number=settings.twilio_phone_number,
    )

    if result.get("status") in ("mock_sent", "skipped"):
        print(f"  ⚠️  Message was NOT actually sent (mode: {result})")
        print("     Ensure ENVIRONMENT=demo or production and credentials are set.")
    else:
        sid = result.get("sid", "unknown")
        status = result.get("status", "unknown")
        print(f"  ✅ Message sent!  SID: {sid}  |  Status: {status}")


if __name__ == "__main__":
    asyncio.run(run())
