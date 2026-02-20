"""
Channel Simulator — In demo mode, simulates channel sends (WhatsApp, email)
by storing them in Redis for dashboard display instead of sending to real APIs.
"""

import json
import uuid
from datetime import datetime, timezone

import structlog

from app.config import get_settings
from app.core.redis import get_redis

logger = structlog.get_logger()
settings = get_settings()

# Redis key prefix and TTL for simulated messages
DEMO_CHANNEL_KEY = "demo:channel_log"
DEMO_CHANNEL_TTL = 3600  # 1 hour


async def simulate_channel_send(
    channel: str,
    to: str,
    message: str,
    property_id: str = None,
    guest_name: str = None,
) -> dict:
    """
    In demo mode, simulates sending a channel message.
    Stores the message in Redis so the dashboard can display it.

    Returns a simulated success response.
    """
    if not settings.is_demo:
        logger.warning("Channel simulator called outside demo mode")
        return {"status": "error", "reason": "not_in_demo_mode"}

    entry = {
        "id": str(uuid.uuid4()),
        "channel": channel,
        "to": to,
        "message": message[:500],  # Truncate for storage
        "property_id": property_id,
        "guest_name": guest_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "simulated",
    }

    try:
        redis = await get_redis()
        # Push to a list (most recent first)
        await redis.client.lpush(DEMO_CHANNEL_KEY, json.dumps(entry))
        # Trim to keep only last 100 messages
        await redis.client.ltrim(DEMO_CHANNEL_KEY, 0, 99)
        # Set TTL on the key
        await redis.client.expire(DEMO_CHANNEL_KEY, DEMO_CHANNEL_TTL)
    except Exception as e:
        # If Redis is unavailable, just log — don't break the demo
        logger.warning("Channel simulator Redis storage failed", error=str(e))

    logger.info(
        "DEMO_CHANNEL_SIMULATED",
        channel=channel,
        to=to,
        message_preview=message[:50],
    )

    return {
        "status": "simulated",
        "channel": channel,
        "message_id": entry["id"],
    }


async def get_simulated_messages(limit: int = 50) -> list[dict]:
    """
    Retrieve recent simulated channel messages for dashboard display.
    """
    try:
        redis = await get_redis()
        raw_messages = await redis.client.lrange(DEMO_CHANNEL_KEY, 0, limit - 1)
        return [json.loads(msg) for msg in raw_messages]
    except Exception as e:
        logger.warning("Failed to retrieve simulated messages", error=str(e))
        return []


async def clear_simulated_messages():
    """Clear all simulated messages (used when re-seeding demo)."""
    try:
        redis = await get_redis()
        await redis.client.delete(DEMO_CHANNEL_KEY)
    except Exception:
        pass
