"""
AI Conversation Engine — the brain of the system.

Handles:
- Multi-turn conversation context
- Three behavioral modes: Concierge, Lead Capture, Handoff
- RAG-augmented responses using property knowledge base
- Bilingual support (EN/BM)
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from openai import AsyncOpenAI

from app.models import Conversation, Message, Lead, Property
from app.services import search_knowledge_base
from app.services.sanitizer import sanitize_guest_message
from app.config import get_settings

settings = get_settings()
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)


# ─────────────────────────────────────────────────────────────
# System Prompts — The personality and rules of the AI
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT_BASE = """You are the AI Concierge for {property_name}, designed to help guests book their stay.
Your goal is to be helpful, warm, and *efficient*. You want to get the guest key information quickly so they can book.

### KEY BEHAVIORS:
1.  **Be Concise**: Use short sentences. limit responses to 1-3 sentences max.
2.  **Be Revenue-Focused**: If a guest asks about rooms, *always* ask for their dates to give an accurate quote.
3.  **Stick to Facts**: ONLY use the PROPERTY KNOWLEDGE BASE below. If unsure, say: "Let me have our reservations team check that for you."
4.  **After Hours**: It is currently {after_hours_state}. If it is after hours (late night), be extra reassuring: "Our team is away, but I'm here to take down your details so they can contact you first thing in the morning."
5.  **Language**: Match the guest's language (English or Bahasa Malaysia).

### PROPERTY KNOWLEDGE BASE:
{knowledge_base_context}
"""

LEAD_CAPTURE_ADDENDUM = """
### ACTIVE LEAD CAPTURE MODE
The guest is interested. Your ONE Goal is to secure their details for the team.
Don't be passive. politely *guide* them to give you this info:
1.  **Name**
2.  **Dates of Stay**
3.  **Phone/Email** (if not already visible)

Example: "I can definitely check rates for you! What dates are you looking to stay?"
Example 2: "Perfect. Could I get your name to start a tentative booking?"
"""

HANDOFF_ADDENDUM = """
### HANDOFF MODE
The guest needs a human.
1.  **De-escalate**: "I understand."
2.  **Assure**: "I'm passing this full conversation to our Property Manager right now."
3.  **Close**: "They will contact you as soon as they are back online."
"""


def _detect_intent(message_text: str) -> str | None:
    """Quick keyword-based intent detection to guide AI mode transitions."""
    text_lower = message_text.lower()

    # Handoff triggers
    handoff_keywords = [
        "speak to someone", "talk to a person", "human", "real person",
        "complaint", "not happy", "dissatisfied", "manager",
        "bercakap dengan orang", "nak jumpa orang",
    ]
    if any(kw in text_lower for kw in handoff_keywords):
        return "handoff"

    # Booking intent triggers
    booking_keywords = [
        "book", "reserve", "available", "availability", "room for",
        "how much", "rates", "price", "tariff", "berapa harga",
        "nak tempah", "ada bilik", "kosong",
        "check in", "check-in", "stay",
    ]
    if any(kw in text_lower for kw in booking_keywords):
        return "lead_capture"

    return None


def _is_after_hours(property: Property) -> bool:
    """Check if current time is outside the property's operating hours."""
    if not property.operating_hours:
        return False

    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(
            property.operating_hours.get("timezone", "Asia/Kuala_Lumpur")
        )
        now = datetime.now(tz)
        start_hour = int(property.operating_hours.get("start", "09:00").split(":")[0])
        end_hour = int(property.operating_hours.get("end", "18:00").split(":")[0])
        return now.hour < start_hour or now.hour >= end_hour
    except Exception:
        return False


async def get_or_create_conversation(
    db: AsyncSession,
    property_id: uuid.UUID,
    guest_identifier: str,
    channel: str,
) -> Conversation:
    """
    Get an existing active conversation or create a new one.
    A conversation is considered active if it hasn't been resolved/expired.
    """
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.property_id == property_id,
            Conversation.guest_identifier == guest_identifier,
            Conversation.status == "active",
        )
        .options(
            selectinload(Conversation.messages),
            selectinload(Conversation.lead)
        )
        .order_by(Conversation.started_at.desc())
        .limit(1)
    )
    conversation = result.scalar_one_or_none()

    if conversation:
        return conversation

    # Get property to check after-hours
    prop_result = await db.execute(
        select(Property).where(Property.id == property_id)
    )
    prop = prop_result.scalar_one()

    conversation = Conversation(
        property_id=property_id,
        guest_identifier=guest_identifier,
        channel=channel,
        is_after_hours=_is_after_hours(prop),
    )
    db.add(conversation)
    await db.flush()
    # Refresh to ensure relationships (like lead) are loaded/mocked to avoid Greenlet error
    await db.refresh(conversation, ["lead"])
    return conversation


async def process_guest_message(
    db: AsyncSession,
    property_id: uuid.UUID,
    guest_identifier: str,
    channel: str,
    message_text: str,
    guest_name: str | None = None,
) -> dict:
    """
    Process an incoming guest message and generate an AI response.

    This is the main entry point for all channels (WhatsApp, Web, Email).

    Returns:
        dict with keys: response, conversation_id, mode, lead_created
    """
    # 1. Sanitize input (Audit R4)
    message_text = sanitize_guest_message(message_text)

    # 2. Get or create conversation
    conversation = await get_or_create_conversation(
        db, property_id, guest_identifier, channel
    )

    # Update conversation stats (Audit M1)
    conversation.last_message_at = datetime.now(timezone.utc)
    conversation.message_count += 1

    if guest_name and not conversation.guest_name:
        conversation.guest_name = guest_name

    # 2. Save guest message
    guest_msg = Message(
        conversation_id=conversation.id,
        role="guest",
        content=message_text,
        metadata_={"channel": channel},
    )
    db.add(guest_msg)
    await db.flush()

    # 3. Detect intent and update AI mode
    detected_intent = _detect_intent(message_text)
    if detected_intent:
        conversation.ai_mode = detected_intent

    # 4. Get property info
    prop_result = await db.execute(
        select(Property).where(Property.id == property_id)
    )
    prop = prop_result.scalar_one()

    # 5. RAG: Search knowledge base for relevant context
    kb_docs = await search_knowledge_base(db, property_id, message_text, limit=5)
    kb_context = "\n\n".join(
        f"[{doc.doc_type.upper()}] {doc.title}:\n{doc.content}"
        for doc in kb_docs
    ) if kb_docs else "No property information available yet."

    # 6. Build conversation history for LLM context
    # Use explicit select to avoid MissingGreenlet / lazy load issues
    msgs_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.sent_at.desc())  # Newest first
        .limit(10)
    )
    # Reverse to get chronological order
    recent_messages = list(msgs_result.scalars().all())[::-1]

    history = []
    # Wrap guest message in XML tags for robustness (Audit R4)
    for m in recent_messages:
        content = m.content
        role = "user"
        if m.role == "guest":
            content = f"<guest_message>{content}</guest_message>"
        elif m.role == "ai":
            role = "assistant"
        history.append({"role": role, "content": content})

    # 7. Build system prompt based on current AI mode
    operating_hours_str = "9am - 6pm"
    if prop.operating_hours:
        operating_hours_str = (
            f"{prop.operating_hours.get('start', '09:00')} - "
            f"{prop.operating_hours.get('end', '18:00')}"
        )
    
    after_hours_state = "during operating hours"
    if conversation.is_after_hours:
        after_hours_state = f"AFTER HOURS (Operating hours are {operating_hours_str})"
        
    system_prompt = SYSTEM_PROMPT_BASE.format(
        property_name=prop.name,
        after_hours_state=after_hours_state,
        knowledge_base_context=kb_context,
    )

    if conversation.ai_mode == "lead_capture":
        system_prompt += LEAD_CAPTURE_ADDENDUM
    elif conversation.ai_mode == "handoff":
        system_prompt += HANDOFF_ADDENDUM

    # 8. Call LLM
    start_time = datetime.now(timezone.utc)

    llm_response = await openai_client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_prompt},
            *history,
        ],
        max_tokens=300,  # Concise responses — 1-3 sentences
        temperature=0.7,
    )

    response_text = llm_response.choices[0].message.content.strip()
    end_time = datetime.now(timezone.utc)
    response_time_ms = int((end_time - start_time).total_seconds() * 1000)

    # 9. Save AI response
    ai_msg = Message(
        conversation_id=conversation.id,
        role="ai",
        content=response_text,
        metadata_={
            "response_time_ms": response_time_ms,
            "llm_tokens_used": llm_response.usage.total_tokens if llm_response.usage else 0,
            "mode": conversation.ai_mode,
            "model": settings.openai_model,
        },
    )
    db.add(ai_msg)

    # 10. Auto-extract lead info if in lead_capture mode
    lead_created = False
    if conversation.ai_mode == "lead_capture" and not conversation.lead:
        lead = await _try_extract_lead(
            db, conversation, prop, message_text, guest_identifier, channel
        )
        if lead:
            lead_created = True

    # 11. Handle handoff mode
    if conversation.ai_mode == "handoff":
        conversation.status = "handed_off"

    await db.flush()

    return {
        "response": response_text,
        "conversation_id": str(conversation.id),
        "mode": conversation.ai_mode,
        "is_after_hours": conversation.is_after_hours,
        "response_time_ms": response_time_ms,
        "lead_created": lead_created,
    }


async def _try_extract_lead(
    db: AsyncSession,
    conversation: Conversation,
    prop: Property,
    message_text: str,
    guest_identifier: str,
    channel: str,
) -> Lead | None:
    """
    Attempt to create a lead from the conversation.
    Uses a lightweight LLM call to extract structured info.
    """
    # Build the full conversation text
    # Explicitly fetch all messages
    msgs_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.sent_at)
    )
    messages = msgs_result.scalars().all()
    
    full_conversation = "\n".join(
        f"{msg.role}: {msg.content}" for msg in messages
    )

    extraction_response = await openai_client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract guest info from this hotel inquiry conversation. "
                    "Return ONLY a JSON object (no markdown) with keys: "
                    "guest_name (string or null), guest_email (string or null), "
                    "guest_phone (string or null), intent (one of: room_booking, "
                    "event, fb_inquiry, general), estimated_nights (number or null). "
                    "If info is not available, use null."
                ),
            },
            {"role": "user", "content": full_conversation},
        ],
        max_tokens=150,
        temperature=0,
    )

    try:
        import json
        raw = extraction_response.choices[0].message.content.strip()
        # Handle potential markdown code block wrapping
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        extracted = json.loads(raw)
    except (json.JSONDecodeError, IndexError):
        return None

    # Only create lead if we have at least a name or contact
    guest_name = extracted.get("guest_name")
    guest_phone = extracted.get("guest_phone")
    guest_email = extracted.get("guest_email")

    # Use channel-provided info as fallback
    if channel == "whatsapp" and not guest_phone:
        guest_phone = guest_identifier
    if channel == "email" and not guest_email:
        guest_email = guest_identifier

    if not guest_name and not guest_phone and not guest_email:
        return None

    # Estimate value based on intent and property ADR
    estimated_nights = extracted.get("estimated_nights") or 1
    estimated_value = Decimal(str(estimated_nights)) * prop.adr

    # Rule-based Lead Scoring
    intent = extracted.get("intent", "general")
    priority = "standard"
    flag_reason = None
    
    # 1. High Value Keywords
    high_value_keywords = ["wedding", "group", "corporate", "event", "conference"]
    if any(kw in message_text.lower() for kw in high_value_keywords):
        priority = "high_value"
        flag_reason = "Keyword match (Event/Group)"
        
    # 2. Stay Duration
    elif estimated_nights > 5:
        priority = "high_value"
        flag_reason = "Long stay (>5 nights)"
        
    # 3. Calculated Value
    elif estimated_value > (prop.adr * 3):
        # Allow override if value is significantly high even if short stay (e.g. multiple rooms implied? 
        # For now, simplistic check: if raw estimate is > 3x ADR. 
        # Actually logic is nights * ADR, so >3 nights is > 3x ADR.
        # Let's keep it simple: > 3 nights or high value custom quote
        priority = "high_value"
        flag_reason = "High estimated value"

    lead = Lead(
        conversation_id=conversation.id,
        property_id=conversation.property_id,
        guest_name=guest_name,
        guest_phone=guest_phone,
        guest_email=guest_email,
        intent=intent,
        estimated_value=estimated_value,
        priority=priority,
        flag_reason=flag_reason,
    )
    db.add(lead)
    conversation.guest_name = guest_name or conversation.guest_name

    return lead
