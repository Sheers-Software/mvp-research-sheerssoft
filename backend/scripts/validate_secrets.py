"""
validate_secrets.py
-------------------
Pre-flight validation script for GCP Secret Manager integration.

Usage:
    # From repo root:
    $env:ENVIRONMENT = "demo"    # trigger GCP fetch (demo or production)
    python backend/scripts/validate_secrets.py

Exits with code 0 if all required secrets are present and Twilio credentials
are accepted by the Twilio API.  Exits with code 1 on any failure.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx

REQUIRED: list[tuple[str, str]] = [
    ("gemini_api_key",       "GCP Secret → GEMINI_API_KEY"),
    ("twilio_account_sid",   "GCP Secret → TWILIO_ACCOUNT_SID"),
    ("twilio_auth_token",    "GCP Secret → TWILIO_AUTH_TOKEN"),
    ("twilio_phone_number",  "GCP Secret → TWILIO_PHONE_NUMBER"),
    ("database_url",         "GCP Secret → DATABASE_URL"),
    ("jwt_secret",           "GCP Secret → JWT_SECRET"),
]

OPTIONAL: list[tuple[str, str]] = [
    ("openai_api_key",           "GCP Secret → OPENAI_API_KEY"),
    ("sendgrid_api_key",         "GCP Secret → SENDGRID_API_KEY"),
    ("whatsapp_api_token",       "GCP Secret → WHATSAPP_API_TOKEN"),
    ("whatsapp_verify_token",    "GCP Secret → WHATSAPP_VERIFY_TOKEN"),
    ("whatsapp_phone_number_id", "GCP Secret → WHATSAPP_PHONE_NUMBER_ID"),
]


def _mask(value: str) -> str:
    """Show only first 4 characters then asterisks — safe for logging."""
    if len(value) <= 4:
        return "****"
    return value[:4] + "*" * min(len(value) - 4, 20)


async def validate_twilio_credentials(sid: str, token: str) -> bool:
    """
    Call Twilio's account fetch endpoint to confirm credentials are valid.
    No messages are sent.
    """
    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}.json"
    auth = (sid, token)
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, auth=auth)
            if resp.status_code == 200:
                data = resp.json()
                print(f"   ✅ Twilio credentials valid  |  Account status: {data.get('status', '?')}  |  SID: {sid[:10]}...")
                return True
            else:
                print(f"   ❌ Twilio API rejected credentials  |  HTTP {resp.status_code}: {resp.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ Twilio API request failed: {e}")
            return False


async def main() -> int:
    print("=" * 60)
    print("  Nocturn AI — Secret Validation Pre-flight Check")
    print("=" * 60)

    # Force Settings to load (triggers GCP fetch if environment=demo/production)
    from app.config import get_settings
    settings = get_settings()

    print(f"\n  Environment : {settings.environment}")
    print(f"  GCP Project : nocturn-ai-487207\n")

    # ── Required secrets ────────────────────────────────────────────────────
    print("── Required Secrets ───────────────────────────────────────────")
    all_required_ok = True
    for attr, label in REQUIRED:
        val = getattr(settings, attr, "")
        if val:
            print(f"  ✅ {attr.upper():<30} {_mask(val)}")
        else:
            print(f"  ❌ {attr.upper():<30} MISSING  ← {label}")
            all_required_ok = False

    # ── Optional secrets ─────────────────────────────────────────────────────
    print("\n── Optional Secrets ───────────────────────────────────────────")
    for attr, label in OPTIONAL:
        val = getattr(settings, attr, "")
        if val:
            print(f"  ✅ {attr.upper():<30} {_mask(val)}")
        else:
            print(f"  ⚠️  {attr.upper():<30} not set  (optional)")

    # ── Twilio live credential check ─────────────────────────────────────────
    print("\n── Twilio API Credential Check ────────────────────────────────")
    twilio_ok = False
    if settings.twilio_account_sid and settings.twilio_auth_token:
        twilio_ok = await validate_twilio_credentials(
            settings.twilio_account_sid,
            settings.twilio_auth_token,
        )
    else:
        print("   ⚠️  Skipped — TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN not loaded")

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    if all_required_ok and twilio_ok:
        print("  ✅ ALL CHECKS PASSED — ready for live demo / production")
        print("=" * 60)
        return 0
    else:
        failures = []
        if not all_required_ok:
            failures.append("one or more required secrets missing")
        if not twilio_ok:
            failures.append("Twilio credential check failed")
        print(f"  ❌ VALIDATION FAILED: {'; '.join(failures)}")
        print("     Check GCP Secret Manager for the missing secrets above.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
