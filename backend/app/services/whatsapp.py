"""
WhatsApp Service — Send messages, templates, and read receipts via Meta Cloud API.

3-tier branching: demo (simulator) → dev (console log) → production (real API).
"""

import structlog
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import get_settings
from app.core.normalization import NormalizedMessage
from app.services.response_formatter import format_response

logger = structlog.get_logger()

GRAPH_API_BASE = "https://graph.facebook.com/v22.0"


async def send_whatsapp_message(to_number: str, message_text: str):
    """
    Sends a WhatsApp message with per-channel formatting.
    3-tier mode: demo → dev mock → production API.
    """
    settings = get_settings()

    # Format response for WhatsApp constraints
    formatted = format_response(message_text, "whatsapp")

    # Demo mode: use channel simulator
    if settings.is_demo:
        from app.services.channel_simulator import simulate_channel_send
        return await simulate_channel_send("whatsapp", to_number, formatted)

    # Dev mode: log to console
    if not settings.whatsapp_api_token or not settings.whatsapp_phone_number_id:
        if not settings.is_production:
            logger.info("MOCK_WHATSAPP", to=to_number, msg=formatted[:80])
            return {"status": "mock_sent"}

        logger.warning("WhatsApp credentials missing in production", to=to_number)
        return {"status": "skipped", "reason": "missing_credentials"}

    return await _send_text(to_number, formatted)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.HTTPStatusError),
)
async def _send_text(to_number: str, text: str) -> dict:
    """Send a plain text WhatsApp message with retry."""
    settings = get_settings()
    url = f"{GRAPH_API_BASE}/{settings.whatsapp_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_api_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        logger.info("WhatsApp sent", to=to_number, msg_id=data.get("messages", [{}])[0].get("id"))
        return data


async def send_whatsapp_template(
    to_number: str,
    template_name: str,
    language: str = "en",
    components: list = None,
):
    """
    Send a pre-approved WhatsApp template message.
    Used for booking confirmations, follow-ups, etc.
    """
    settings = get_settings()

    if settings.is_demo:
        from app.services.channel_simulator import simulate_channel_send
        return await simulate_channel_send("whatsapp", to_number, f"[Template: {template_name}]")

    if not settings.whatsapp_api_token or not settings.whatsapp_phone_number_id:
        logger.info("MOCK_TEMPLATE", to=to_number, template=template_name)
        return {"status": "mock_sent"}

    url = f"{GRAPH_API_BASE}/{settings.whatsapp_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_api_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
        },
    }
    if components:
        payload["template"]["components"] = components

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=10.0)
        response.raise_for_status()
        logger.info("WhatsApp template sent", to=to_number, template=template_name)
        return response.json()


async def mark_message_read(message_id: str):
    """Mark a received WhatsApp message as read (blue ticks)."""
    settings = get_settings()
    if not settings.whatsapp_api_token or not settings.whatsapp_phone_number_id:
        return

    url = f"{GRAPH_API_BASE}/{settings.whatsapp_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_api_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    }

    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, headers=headers, json=payload, timeout=5.0)
    except Exception as e:
        logger.warning("Failed to mark message as read", msg_id=message_id, error=str(e))


def normalize_whatsapp_message(payload: dict) -> dict:
    """
    Parse raw WhatsApp webhook payload into normalized structure.
    """
    try:
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return None

        msg = messages[0]
        from_number = msg.get("from")
        text_body = msg.get("text", {}).get("body")

        # Determine guest name
        contacts = value.get("contacts", [])
        guest_name = None
        if contacts:
            guest_name = contacts[0].get("profile", {}).get("name")

        # Get phone number ID for property lookup
        phone_number_id = value.get("metadata", {}).get("phone_number_id")

        if not from_number:
            return None

        # Handle non-text messages (images, audio, video, location, stickers, etc.)
        msg_type = msg.get("type", "text")
        if not text_body:
            if msg_type != "text":
                return {
                    "channel": "whatsapp",
                    "guest_identifier": from_number,
                    "guest_name": guest_name,
                    "content": None,
                    "metadata": {
                        "phone_number_id": phone_number_id,
                        "whatsapp_message_id": msg.get("id"),
                        "is_unsupported_media": True,
                        "media_type": msg_type,
                    },
                }
            return None

        return {
            "channel": "whatsapp",
            "guest_identifier": from_number,
            "guest_name": guest_name,
            "content": text_body,
            "metadata": {
                "phone_number_id": phone_number_id,
                "whatsapp_message_id": msg.get("id"),
            },
        }

    except Exception as e:
        logger.error("Error normalizing WhatsApp payload", error=str(e))
        return None
