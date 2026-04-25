"""
WhatsApp Transport Abstraction Layer.
Controls whether we use Baileys (shadow/hybrid) or Meta Cloud API (Stage 3).
"""
from typing import Protocol, runtime_checkable
import structlog
import httpx

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


@runtime_checkable
class WhatsAppTransportInterface(Protocol):
    async def send_message(self, to: str, text: str) -> bool: ...
    async def get_session_status(self) -> str: ...


class BaileysTransport:
    """
    Shadow pilot (observe_only=True) and hybrid co-pilot (observe_only=False) transport.
    When observe_only=True, send_message() is a no-op that logs a warning.
    """
    def __init__(self, bridge_url: str, property_slug: str, observe_only: bool = False):
        self.bridge_url = bridge_url
        self.property_slug = property_slug
        self.observe_only = observe_only

    async def send_message(self, to: str, text: str) -> bool:
        if self.observe_only:
            logger.warning(
                "send_message_suppressed_shadow_pilot_mode",
                property_slug=self.property_slug,
                to=to[:8] + "...",
            )
            return False
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{self.bridge_url}/internal/send-message",
                    json={"property_slug": self.property_slug, "to": to, "text": text},
                    headers={"X-Internal-Secret": settings.internal_scheduler_secret or ""},
                )
                return resp.status_code == 200
        except Exception as e:
            logger.error("baileys_send_failed", error=str(e), property=self.property_slug)
            return False

    async def get_session_status(self) -> str:
        try:
            bridge_url = getattr(settings, 'baileys_bridge_url', None) or self.bridge_url
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{bridge_url}/qr/{self.property_slug}")
                data = resp.json()
                return data.get("status", "unknown")
        except Exception:
            return "unknown"


def get_whatsapp_transport(prop) -> "BaileysTransport | None":
    """Factory: returns the appropriate transport for a property."""
    bridge_url = getattr(settings, 'baileys_bridge_url', None) or "http://localhost:3001"
    if prop.shadow_pilot_mode:
        return BaileysTransport(bridge_url, prop.slug, observe_only=True)
    whatsapp_provider = getattr(prop, 'whatsapp_provider', 'meta')
    if whatsapp_provider == "baileys":
        return BaileysTransport(bridge_url, prop.slug, observe_only=False)
    # Meta/Twilio handled elsewhere
    return None
