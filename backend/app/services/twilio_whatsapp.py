"""
Twilio WhatsApp Service — Send messages, templates, and normalize webhooks via Twilio API.

Includes Live Demo Routing override to ensure real demonstration devices bypass the channel simulator.
"""

import httpx
import structlog
from urllib.parse import urlencode
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import get_settings
from app.services.response_formatter import format_response

logger = structlog.get_logger()

TWILIO_API_BASE = "https://api.twilio.com/2010-04-01/Accounts"


async def send_twilio_message(to_number: str, message_text: str, from_number: str | None = None):
    """
    Sends a WhatsApp message via Twilio with per-channel formatting.
    Includes Live Demo Routing override.

    Args:
        to_number: The guest's phone number (e.g. "+601112345678").
        message_text: The plain-text reply to send.
        from_number: The property's Twilio WhatsApp number. Falls back to
                     the global TWILIO_PHONE_NUMBER setting if not supplied.
    """
    settings = get_settings()
    formatted = format_response(message_text, "whatsapp")

    # Resolve the sender number
    resolved_from = from_number or settings.twilio_phone_number

    # If demo mode, check if we should override and send to a real device
    if settings.is_demo:
        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            from app.services.channel_simulator import simulate_channel_send
            return await simulate_channel_send("twilio_whatsapp", to_number, formatted)

        logger.info("Demo Mode Override: Sending real Twilio message to device", to=to_number)

    # Dev mode: log to console if credentials missing
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        if not settings.is_production:
            logger.info("MOCK_TWILIO_WHATSAPP", to=to_number, from_=resolved_from, msg=formatted[:80])
            return {"status": "mock_sent"}

        logger.warning("Twilio credentials missing in production", to=to_number)
        return {"status": "skipped", "reason": "missing_credentials"}

    if not resolved_from:
        logger.error("No Twilio sender number configured", to=to_number)
        return {"status": "skipped", "reason": "missing_from_number"}

    return await _send_twilio_text(to_number, formatted, resolved_from)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.HTTPStatusError),
)
async def _send_twilio_text(to_number: str, text: str, from_number: str) -> dict:
    """Send a plain text WhatsApp message via Twilio."""
    settings = get_settings()
    url = f"{TWILIO_API_BASE}/{settings.twilio_account_sid}/Messages.json"

    # Twilio requires WhatsApp numbers to be prefixed with "whatsapp:"
    if not to_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_number}"
    if not from_number.startswith("whatsapp:"):
        from_number = f"whatsapp:{from_number}"

    payload = {
        "To": to_number,
        "From": from_number,
        "Body": text,
    }

    auth = (settings.twilio_account_sid, settings.twilio_auth_token)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, auth=auth, headers=headers, data=payload, timeout=10.0)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(
                "Twilio API Error",
                status_code=response.status_code,
                response_body=response.text,
                error=str(e),
                payload={k: v for k, v in payload.items() if k != "Body"},
            )
            raise e

        data = response.json()
        logger.info("Twilio WhatsApp sent", to=to_number, from_=from_number, msg_sid=data.get("sid"))
        return data


def normalize_twilio_webhook(form_data: dict) -> dict:
    """
    Parse raw Twilio webhook payload into normalized structure.
    """
    try:
        from_number = form_data.get("From", "")
        to_number = form_data.get("To", "")
        text_body = form_data.get("Body", "")
        profile_name = form_data.get("ProfileName", None)
        message_sid = form_data.get("MessageSid", "")

        # Twilio sends numbers formatted like "whatsapp:+1234567890"
        if from_number.startswith("whatsapp:"):
            from_number = from_number.replace("whatsapp:", "")
        if to_number.startswith("whatsapp:"):
            to_number = to_number.replace("whatsapp:", "")

        if not from_number or not text_body:
            return None

        return {
            "channel": "whatsapp",
            "guest_identifier": from_number,
            "guest_name": profile_name,
            "content": text_body,
            "metadata": {
                "twilio_message_sid": message_sid,
                "twilio_to_number": to_number,  # Useful for Property lookup
            },
        }

    except Exception as e:
        logger.error("Error normalizing Twilio payload", error=str(e))
        return None
