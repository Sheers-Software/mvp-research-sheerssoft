"""
Integration Registry — centralized health check and status for all external integrations.
Surfaces in the dashboard Settings page so teams can see what's connected.
"""

from app.config import get_settings

settings = get_settings()


def get_integration_status() -> dict:
    """
    Returns the configuration status of all external integrations.
    Used by the Settings page to show what's connected vs. mocked.
    """
    return {
        "mode": settings.environment,
        "integrations": {
            "gemini": {
                "name": "Gemini (Primary LLM)",
                "configured": bool(settings.gemini_api_key),
                "required": True,
                "setup_guide": "docs/setup/gemini.md",
                "description": "Powers the AI conversation engine. Required for all modes.",
            },
            "openai": {
                "name": "OpenAI (Fallback 1)",
                "configured": bool(settings.openai_api_key),
                "required": False,
                "setup_guide": "docs/setup/openai.md",
                "description": "First fallback if Gemini fails.",
            },
            "anthropic": {
                "name": "Anthropic (Claude Haiku)",
                "configured": bool(settings.anthropic_api_key),
                "required": False,
                "setup_guide": "docs/setup/openai.md",
                "description": "Automatic fallback if OpenAI fails. Optional but recommended.",
            },
            "whatsapp": {
                "name": "WhatsApp Business API",
                "configured": bool(settings.whatsapp_api_token) and bool(settings.whatsapp_phone_number_id),
                "required": False,
                "mock_active": not bool(settings.whatsapp_api_token),
                "setup_guide": "docs/setup/whatsapp.md",
                "description": "Live WhatsApp messaging via Meta Cloud API.",
                "credentials_needed": [
                    {"key": "WHATSAPP_API_TOKEN", "set": bool(settings.whatsapp_api_token)},
                    {"key": "WHATSAPP_PHONE_NUMBER_ID", "set": bool(settings.whatsapp_phone_number_id)},
                    {"key": "WHATSAPP_APP_SECRET", "set": bool(settings.whatsapp_app_secret)},
                    {"key": "WHATSAPP_VERIFY_TOKEN", "set": bool(settings.whatsapp_verify_token)},
                ],
            },
            "sendgrid": {
                "name": "SendGrid Email",
                "configured": bool(settings.sendgrid_api_key),
                "required": False,
                "mock_active": not bool(settings.sendgrid_api_key),
                "setup_guide": "docs/setup/sendgrid.md",
                "description": "Email replies and daily reports via SendGrid.",
                "credentials_needed": [
                    {"key": "SENDGRID_API_KEY", "set": bool(settings.sendgrid_api_key)},
                    {"key": "SENDGRID_FROM_EMAIL", "set": bool(settings.sendgrid_from_email)},
                    {"key": "SENDGRID_WEBHOOK_PUBLIC_KEY", "set": bool(settings.sendgrid_webhook_public_key)},
                ],
            },
            "encryption": {
                "name": "PII Encryption (Fernet)",
                "configured": bool(settings.fernet_encryption_key),
                "required": False,
                "description": "Field-level encryption for guest PII (PDPA compliance).",
            },
        },
    }
