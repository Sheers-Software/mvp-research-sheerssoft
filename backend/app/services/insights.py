"""
Insights service for determining guest sentiment and extracting common FAQs over time.
Used to generate the '30-Day Guest Insight Report' marketed to properties.
"""

import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from google import genai

from app.models import Conversation, Message
from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()

# Optional: Initialize Gemini client
gemini_client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

INSIGHT_SYSTEM_INSTRUCTION = """
Analyze the following batch of hotel guest inquiry transcripts from the last 30 days.
Extract the following insights into a clear, professional summary report:
1. Top 3 most frequently asked questions.
2. Top 3 common objections or reasons for handoff (e.g., "Price too high", "Requested early check-in not available").
3. Overall guest sentiment (Positive, Neutral, or Negative) with a one-paragraph summary.

Output format should be clean markdown that can be sent directly in an email block.
"""

async def compute_monthly_insights(
    db: AsyncSession,
    property_id: uuid.UUID,
    days_back: int = 30
) -> str | None:
    """
    Fetch all conversations over the last N days and run them through Gemini to
    extract high-level insights for the property manager.
    """
    if not gemini_client:
        logger.warning("Monthly Insights: Gemini API key not configured, skipping report.")
        return None

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)

    # 1. Fetch conversations from the last 30 days
    conv_result = await db.execute(
        select(Conversation.id)
        .where(
            Conversation.property_id == property_id,
            Conversation.started_at >= cutoff_date
        )
    )
    conversation_ids = [row[0] for row in conv_result.fetchall()]

    if not conversation_ids:
        return "Not enough data collected in the last 30 days to generate an insight report."

    # 2. Fetch messages for these conversations
    msg_result = await db.execute(
        select(Message)
        .where(Message.conversation_id.in_(conversation_ids))
        .order_by(Message.conversation_id, Message.sent_at)
    )
    messages = msg_result.scalars().all()

    # 3. Build a massive transcript block
    transcript_blocks = []
    current_conv = None
    current_block = []

    for msg in messages:
        if msg.conversation_id != current_conv:
            if current_block:
                transcript_blocks.append("\n".join(current_block))
            current_conv = msg.conversation_id
            current_block = [f"\n--- Conversation {current_conv} ---"]
        current_block.append(f"{msg.role}: {msg.content}")

    if current_block:
        transcript_blocks.append("\n".join(current_block))

    full_transcript = "\n".join(transcript_blocks)

    if len(full_transcript.split()) < 50:
        return "Insufficient conversational data to extract meaningful insights."

    # 4. Generate Insight Report using Gemini
    logger.info("Generating Monthly Insights Report", property_id=str(property_id), transcript_words=len(full_transcript.split()))
    try:
        from google.genai import types
        response = await gemini_client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=full_transcript,
            config=types.GenerateContentConfig(
                system_instruction=INSIGHT_SYSTEM_INSTRUCTION,
                temperature=0.3,
            )
        )
        return response.text.strip()
    except Exception as e:
        logger.error("Failed to generate insights report", property_id=str(property_id), error=str(e))
        return "Error analyzing transcripts. Please try again later."
