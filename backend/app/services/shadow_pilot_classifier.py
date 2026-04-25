"""
Lightweight intent classifier for shadow pilot messages.
Uses the existing LLM chain with a minimal, fast prompt.
"""
import json
from typing import Tuple
import structlog

logger = structlog.get_logger()

CLASSIFY_PROMPT = """You are classifying a WhatsApp message sent to a Malaysian hotel.

Message: "{message}"

Classify into EXACTLY ONE intent:
- room_booking (wants to book a room)
- rate_query (asking about rates/prices)
- availability_check (asking if rooms available on specific dates)
- group_booking (booking for 5+ people or event)
- facilities_inquiry (pool, gym, parking, breakfast, etc.)
- complaint (dissatisfied guest)
- general (anything else)

Also extract:
- topic: short label max 4 words in English
- language: "bm", "en", or "mixed"
- confidence: 0.0-1.0

Respond in JSON only:
{{"intent": "...", "topic": "...", "language": "...", "confidence": 0.0}}"""


async def classify_intent(message: str) -> Tuple[str, float, str, str]:
    """Returns (intent, confidence, topic, language)."""
    if not message.strip():
        return ("general", 0.5, "unknown", "unknown")
    try:
        from app.services.conversation import _call_llm_simple
        raw = await _call_llm_simple(CLASSIFY_PROMPT.format(message=message[:300]))
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
            if raw.startswith("json\n"):
                raw = raw[5:]
        result = json.loads(raw)
        return (
            result.get("intent", "general"),
            float(result.get("confidence", 0.5)),
            result.get("topic", "unknown"),
            result.get("language", "unknown"),
        )
    except Exception as e:
        logger.debug("shadow_classify_failed", error=str(e))
        return ("general", 0.0, "unknown", "unknown")
