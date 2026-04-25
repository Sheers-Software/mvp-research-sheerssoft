"""
AI Conversation Engine — the brain of the system.

Handles:
- Multi-turn conversation context
- Three behavioral modes: Concierge, Lead Capture, Handoff
- RAG-augmented responses using property knowledge base
- Bilingual support (EN/BM)
"""

import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

import structlog
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from openai import AsyncOpenAI
from google import genai

from app.models import Conversation, Message, Lead, Property
from app.services import search_knowledge_base
from app.services.sanitizer import sanitize_guest_message
from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

gemini_client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None
openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

# Template fallback when all LLMs fail
FALLBACK_RESPONSE = (
    "Thank you for your message! Our reservations team has been notified "
    "and will get back to you shortly. If you need immediate assistance, "
    "please call our front desk directly."
)
FALLBACK_RESPONSE_BM = (
    "Terima kasih atas mesej anda! Pasukan tempahan kami telah dimaklumkan "
    "dan akan menghubungi anda tidak lama lagi. Jika anda memerlukan bantuan "
    "segera, sila hubungi kaunter hadapan kami."
)


async def _call_llm(messages: list[dict], max_tokens: int = 512, temperature: float = 0.7) -> tuple:
    """
    Call LLM with automatic fallback.
    1. Try Gemini
    2. If Gemini fails, try Anthropic Claude Haiku
    3. If Anthropic fails, try OpenAI GPT-4o-mini
    4. If all fail, return template fallback response
    """
    # Attempt 1: Gemini
    if settings.gemini_api_key and gemini_client:
        try:
            from google.genai import types
            system_msg = ""
            gemini_contents = []

            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    # Map roles: 'assistant' -> 'model', 'user' -> 'user'
                    role = "model" if msg["role"] == "assistant" else "user"
                    gemini_contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=msg["content"])]
                        )
                    )

            # Since _call_llm is async, we use the async client 'aio'
            response = await gemini_client.aio.models.generate_content(
                model=settings.gemini_model,
                contents=gemini_contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_msg,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            text = response.text.strip() if response.text else ""
            if not text:
                logger.warning("Gemini returned empty response, trying fallback")
            else:
                return text, None, settings.gemini_model
        except Exception as e:
            logger.warning("Gemini LLM call failed, trying fallback", error=str(e))
    else:
        logger.warning("Gemini API key missing, skipping to fallback")

    # Attempt 2: Anthropic Claude Haiku
    if settings.anthropic_api_key:
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

            # Convert OpenAI format to Anthropic format
            system_msg = ""
            claude_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    claude_messages.append(msg)

            response = await client.messages.create(
                model=settings.anthropic_model,
                max_tokens=max_tokens,
                system=system_msg,
                messages=claude_messages,
            )
            return response.content[0].text.strip(), None, settings.anthropic_model
        except Exception as e:
            logger.warning("Anthropic LLM call failed, trying fallback", error=str(e))
    else:
        logger.warning("Anthropic API key missing, skipping to fallback")

    # Attempt 3: OpenAI
    if settings.openai_api_key and openai_client:
        try:
            response = await openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            content = response.choices[0].message.content
            if not content or not content.strip():
                logger.warning("OpenAI returned empty response, trying fallback")
            else:
                return content.strip(), response.usage, settings.openai_model
        except Exception as e:
            logger.warning("OpenAI LLM call failed, trying fallback", error=str(e))
    else:
        logger.warning("OpenAI API key missing, skipping to fallback")

    # Attempt 4: Template fallback
    logger.error("All LLM providers failed, using template fallback")
    return FALLBACK_RESPONSE, None, "fallback_template"


# ─────────────────────────────────────────────────────────────
# System Prompts — The personality and rules of the AI
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT_BASE = """You are the AI Concierge for {property_name}. You are NOT a generic chatbot — you are a knowledgeable, proactive hotel professional powered by advanced AI. You should respond the way a skilled reservations manager would: warmly, efficiently, and with contextual intelligence.

### CURRENT DATE & TIME:
{current_datetime}

### GUEST CONTEXT:
{guest_context}

### INFORMATION GATHERED SO FAR:
{lead_progress}

### INTELLIGENT BEHAVIOR RULES (CRITICAL — follow these precisely):

1. **IMPLICIT INFORMATION**: If the guest says "use this number", "you already have my number", "same number", or "you can reach me here" — look at GUEST CONTEXT above and CONFIRM the phone/email shown. NEVER re-ask for information you already have. Say: "Got it, I have your number as {guest_phone_placeholder} — is that correct?"

2. **DATE RESOLUTION**: ALWAYS convert relative dates to specific calendar dates using CURRENT DATE above:
   - "tomorrow" → calculate the exact date and state it ("That would be {tomorrow_date}")
   - "this weekend" → calculate Saturday-Sunday dates
   - "next Friday" → calculate the exact date
   - "for 3 nights from tomorrow" → calculate check-in AND check-out dates
   Never leave a date ambiguous. Always confirm: "So that's check-in on [DATE], check-out on [DATE] — [N] nights. Does that work?"

3. **PAX INFERENCE**: Extract number of guests from context clues:
   - "me and my wife" → 2 adults
   - "family of 4" → assume 2 adults + 2 children
   - "with the kids" → at least 2 adults + children, ask how many children
   - "couple" → 2 adults
   - "business trip" → likely 1 adult
   State your assumption: "I'll note that as 2 adults. Will any children be joining?"

4. **PROACTIVE ROOM SUGGESTIONS**: When a guest mentions their occasion or needs, recommend the BEST-FIT room from the PROPERTY KNOWLEDGE BASE:
   - Anniversary/honeymoon → suggest the most premium suite
   - Family → suggest family rooms or interconnecting rooms
   - Business → suggest rooms with work desk, wifi emphasis
   - Budget → suggest the best value option
   Don't just list rates. RECOMMEND: "For an anniversary, I'd suggest our Grand Suite — it has a private balcony and complimentary champagne."

5. **PRICE FRAMING**: When quoting rates, always provide context:
   - Include what's included (breakfast, wifi, pool, parking)
   - Show per-night AND total stay cost if dates are known
   - Compare value: "That's RM 380/night including breakfast for two — great value for a sea-view room."

6. **NO INTERROGATION**: NEVER ask more than 2 questions in a single message. Prioritize the most important missing info first. If you need name, dates, and pax — ask for dates first (the most time-sensitive), then name + pax together next.

7. **CONFIRMATION SUMMARIES**: Once you have all key details (name, dates, room, pax), summarize naturally:
   "Perfect! Let me confirm: [Name], [N] nights from [check-in] to [check-out], [Room Type] for [N adults]. I'll pass this to our reservations team and they'll send you a confirmation shortly!"

8. **PROACTIVE UPSELLS**: After handling the main query, offer ONE relevant add-on:
   - Airport pickup
   - Spa package
   - Dining reservation
   - Early check-in / late check-out
   Keep it brief: "By the way, we offer complimentary airport shuttle — would you like me to arrange that?"

9. **PARTIAL ANSWERS**: Extract implicit info without re-asking:
   - "I arrive on the 10am flight from KL" → check-in is that day, likely afternoon
   - "I'm checking out on Sunday" → calculate dates backward
   - "Just one night" → check-out = check-in + 1

10. **CONTEXTUAL MEMORY**: Review INFORMATION GATHERED SO FAR. NEVER re-ask for details already collected. If the guest provided their name 3 messages ago, use it — don't ask again.

### CORE BEHAVIORS:
- **Stick to Facts**: ONLY use the PROPERTY KNOWLEDGE BASE below. If unsure, say: "Let me check with our reservations team and get back to you."
- **After Hours**: It is currently {after_hours_state}. If after hours, reassure: "Our team is away for the night, but I'm here to take care of everything — they'll follow up first thing in the morning."
- **Language**: Match the guest's language (English or Bahasa Malaysia). If they switch, switch with them.

### BRAND PERSONA & VOCABULARY:
{brand_vocabulary_context}

### PROPERTY KNOWLEDGE BASE:
{knowledge_base_context}
"""

LEAD_CAPTURE_ADDENDUM = """
### ACTIVE LEAD CAPTURE MODE
The guest is interested. Your goal is to gather booking details efficiently — like a real reservations manager.

Check INFORMATION GATHERED SO FAR above. Only ask for what's MISSING:
1. **Name** — skip if already in GUEST CONTEXT or gathered earlier
2. **Dates of Stay** — resolve to specific dates, confirm check-in + check-out + number of nights
3. **Number of Guests** — infer from context when possible
4. **Room Preference** — suggest based on their stated needs
5. **Contact** — skip if phone/email is already in GUEST CONTEXT (WhatsApp number counts!)

{required_questions_context}

Remember: Maximum 2 questions per message. Lead with the most important missing piece.
"""

HANDOFF_ADDENDUM = """
### HANDOFF MODE
The guest needs a human. Handle this gracefully:
1. **Acknowledge**: "I completely understand, and I want to make sure you're taken care of."
2. **Assure**: "I'm flagging this conversation for our Property Manager right now, with all the details."
3. **Set expectations**: "They will reach out to you within [timeframe based on operating hours]. In the meantime, is there anything else I can note down for them?"
"""


def _detect_intent(message_text: str) -> str | None:
    """Nuanced intent detection with hospitality-specific categories."""
    text_lower = message_text.lower()

    # Handoff triggers — route to human immediately
    handoff_keywords = [
        "speak to someone", "talk to a person", "human", "real person",
        "complaint", "not happy", "dissatisfied", "manager",
        "refund", "cancel my booking", "cancel reservation",
        "bercakap dengan orang", "nak jumpa orang", "tak puas hati",
    ]
    if any(kw in text_lower for kw in handoff_keywords):
        return "handoff"

    # High-value lead triggers — skip concierge, go straight to capture
    high_value_keywords = [
        "wedding", "reception", "conference", "corporate event",
        "group booking", "block of rooms", "company retreat",
        "perkahwinan", "majlis", "korporat",
    ]
    if any(kw in text_lower for kw in high_value_keywords):
        return "lead_capture"

    # Standard booking intent triggers
    booking_keywords = [
        "book", "reserve", "available", "availability", "room for",
        "how much", "rates", "price", "tariff", "berapa harga",
        "nak tempah", "ada bilik", "kosong",
        "check in", "check-in", "stay", "tonight", "tomorrow",
        "this weekend", "next week",
        "honeymoon", "anniversary", "birthday", "getaway",
    ]
    if any(kw in text_lower for kw in booking_keywords):
        return "lead_capture"

    # Info queries — stay in concierge mode (don't push lead capture)
    # "spa", "restaurant", "parking", "wifi", "pool" etc.
    # Return None to keep current mode
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
    prop = prop_result.scalar_one_or_none()
    if not prop:
        raise ValueError(f"Property {property_id} not found")

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
    is_follow_up: bool = False,
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
    # Only update last_interaction_at if this is NOT an automated follow-up
    # meaning the guest actually replied, or a staff sent a real message
    if not is_follow_up:
        conversation.last_interaction_at = datetime.now(timezone.utc)
    conversation.message_count += 1

    if guest_name and not conversation.guest_name:
        conversation.guest_name = guest_name

    # 2. Save guest message (or system message if it's a follow up trigger without text from guest)
    if message_text:
        role = "ai" if is_follow_up else "guest"
        guest_msg = Message(
            conversation_id=conversation.id,
            role=role,
            content=message_text,
            metadata_={"channel": channel, "is_follow_up": is_follow_up},
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

    # 4b. Shadow Pilot / Audit-Only Mode — log message, skip AI response entirely.
    # The weekly audit report job reads from Conversations to generate the
    # "You received X after-hours inquiries" email. No reply is sent to the guest.
    if prop.audit_only_mode:
        await db.flush()
        logger.info(
            "audit_only_mode: message logged, AI response suppressed",
            property_id=str(property_id),
            conversation_id=str(conversation.id),
        )
        return {
            "response": None,
            "audit_only": True,
            "conversation_id": str(conversation.id),
            "mode": conversation.ai_mode,
            "is_after_hours": conversation.is_after_hours,
            "response_time_ms": 0,
            "lead_created": False,
        }

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
        .limit(15)  # Increased from 10 for longer conversations (weddings, events)
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
        
    brand_vocab_str = "Standard hotel professional and helpful."
    if prop.brand_vocabulary:
        brand_vocab_str = prop.brand_vocabulary
        
    # Build guest context from channel metadata
    import zoneinfo
    try:
        prop_tz = zoneinfo.ZoneInfo(
            prop.operating_hours.get("timezone", "Asia/Kuala_Lumpur") if prop.operating_hours else "Asia/Kuala_Lumpur"
        )
    except Exception:
        prop_tz = zoneinfo.ZoneInfo("Asia/Kuala_Lumpur")
    now_local = datetime.now(prop_tz)
    current_dt_str = now_local.strftime("%A, %B %d, %Y at %I:%M %p %Z")
    # Pre-compute tomorrow for the prompt placeholder
    tomorrow_local = now_local + timedelta(days=1)
    tomorrow_str = tomorrow_local.strftime("%A, %B %d")

    guest_context_parts = []
    guest_phone_for_prompt = "(not available)"
    if channel == "whatsapp" and guest_identifier:
        guest_context_parts.append(f"Channel: WhatsApp")
        guest_context_parts.append(f"Phone number: {guest_identifier}")
        guest_phone_for_prompt = guest_identifier
    elif channel == "email" and guest_identifier:
        guest_context_parts.append(f"Channel: Email")
        guest_context_parts.append(f"Email: {guest_identifier}")
    elif channel == "web":
        guest_context_parts.append(f"Channel: Website live chat")
    if conversation.guest_name:
        guest_context_parts.append(f"Name: {conversation.guest_name}")
    guest_context_str = "\n".join(guest_context_parts) if guest_context_parts else "No guest details known yet."

    # Build lead progress tracker from conversation history
    lead_progress_parts = []
    full_text = " ".join(m.content for m in recent_messages).lower()
    # Check what info has been gathered
    if conversation.guest_name:
        lead_progress_parts.append(f"- Name: {conversation.guest_name} ✓")
    else:
        lead_progress_parts.append("- Name: Not yet provided")
    if channel == "whatsapp" and guest_identifier:
        lead_progress_parts.append(f"- Phone: {guest_identifier} ✓ (from WhatsApp)")
    elif conversation.lead and conversation.lead.guest_phone:
        lead_progress_parts.append(f"- Phone: {conversation.lead.guest_phone} ✓")
    else:
        lead_progress_parts.append("- Phone: Not yet provided")
    # Check for date mentions in the conversation
    date_keywords = ["tonight", "tomorrow", "weekend", "next week", "monday", "tuesday",
                     "wednesday", "thursday", "friday", "saturday", "sunday",
                     "january", "february", "march", "april", "may", "june",
                     "july", "august", "september", "october", "november", "december",
                     "check in", "check-in", "night", "nights"]
    if any(kw in full_text for kw in date_keywords):
        lead_progress_parts.append("- Dates: Mentioned in conversation (confirm specifics)")
    else:
        lead_progress_parts.append("- Dates: Not yet discussed")
    # Check for pax mentions
    pax_keywords = ["wife", "husband", "family", "kids", "children", "couple",
                    "friend", "friends", "colleague", "alone", "solo", "adults"]
    if any(kw in full_text for kw in pax_keywords):
        lead_progress_parts.append("- Guests: Mentioned in conversation (confirm count)")
    else:
        lead_progress_parts.append("- Number of guests: Not yet discussed")
    lead_progress_str = "\n".join(lead_progress_parts)

    system_prompt = SYSTEM_PROMPT_BASE.format(
        property_name=prop.name,
        current_datetime=current_dt_str,
        guest_context=guest_context_str,
        lead_progress=lead_progress_str,
        guest_phone_placeholder=guest_phone_for_prompt,
        tomorrow_date=tomorrow_str,
        after_hours_state=after_hours_state,
        brand_vocabulary_context=brand_vocab_str,
        knowledge_base_context=kb_context,
    )

    if conversation.ai_mode == "lead_capture":
        required_qs_str = ""
        if prop.required_questions and len(prop.required_questions) > 0:
            qs_list = "\n".join(f"- {q}" for q in prop.required_questions)
            required_qs_str = f"Additionally, ensure you ask these REQUIRED QUESTIONS before passing to reservations:\n{qs_list}"
            
        system_prompt += LEAD_CAPTURE_ADDENDUM.format(required_questions_context=required_qs_str)
    elif conversation.ai_mode == "handoff":
        system_prompt += HANDOFF_ADDENDUM
        
    if is_follow_up:
        system_prompt += "\n\n### RE-ENGAGEMENT MODE\nThis guest has gone quiet. Your goal is to politely and warmly follow up. Keep it short, reference their previous interest, and ask if they still need help."

    # 8. Call LLM (with retry + fallback)
    start_time = datetime.now(timezone.utc)

    llm_messages = [
        {"role": "system", "content": system_prompt},
        *history,
    ]
    # Use lower temperature in lead capture for more focused, goal-oriented responses
    temp = 0.5 if conversation.ai_mode == "lead_capture" else 0.7
    response_text, usage, model_used = await _call_llm(
        llm_messages, max_tokens=800, temperature=temp
    )

    end_time = datetime.now(timezone.utc)
    response_time_ms = int((end_time - start_time).total_seconds() * 1000)

    logger.info(
        "LLM response generated",
        model=model_used,
        response_time_ms=response_time_ms,
        conversation_id=str(conversation.id),
    )

    # 9. Save AI response
    ai_msg = Message(
        conversation_id=conversation.id,
        role="ai",
        content=response_text,
        metadata_={
            "response_time_ms": response_time_ms,
            "llm_tokens_used": usage.total_tokens if usage else 0,
            "mode": conversation.ai_mode,
            "model": model_used,
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

    system_instruction = (
        "Extract guest info from this hotel inquiry conversation. "
        "Return ONLY a JSON object (no markdown) with keys: "
        "guest_name (string or null), guest_email (string or null), "
        "guest_phone (string or null), intent (one of: room_booking, "
        "event, fb_inquiry, general), estimated_nights (number or null). "
        "If info is not available, use null."
    )

    raw = None

    # Attempt 1: Gemini
    if settings.gemini_api_key and gemini_client:
        try:
            from google.genai import types
            response = await gemini_client.aio.models.generate_content(
                model=settings.gemini_model,
                contents=full_conversation,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0,
                    max_output_tokens=150,
                )
            )
            raw = response.text.strip()
        except Exception as e:
            logger.warning("Gemini lead extraction failed, trying fallback", error=str(e))

    # Attempt 2: OpenAI (Fallback)
    if not raw and settings.openai_api_key and openai_client:
        try:
            extraction_response = await openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": full_conversation},
                ],
                max_tokens=150,
                temperature=0,
            )
            raw = extraction_response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning("OpenAI lead extraction failed", error=str(e))

    if not raw:
        logger.warning("Lead extraction skipped: No LLM available or both failed")
        return None

    try:
        import json
        # Handle potential markdown code block wrapping
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
            if raw.startswith("json\n"):
                raw = raw[5:]
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        extracted = json.loads(raw)
    except Exception as e:
        logger.warning("Lead extraction LLM call failed", error=str(e))
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
        source_channel=channel,
        is_after_hours=conversation.is_after_hours,
        estimated_value=estimated_value,
        priority=priority,
        flag_reason=flag_reason,
    )
    db.add(lead)
    conversation.guest_name = guest_name or conversation.guest_name

    return lead


async def _call_llm_simple(prompt: str) -> str:
    """
    Simple single-turn LLM call returning raw text.
    Used by the shadow pilot classifier for intent detection.
    Tries Gemini first, then OpenAI, then raises if both fail.
    """
    import asyncio as _asyncio

    # Attempt 1: Gemini async client
    if settings.gemini_api_key and gemini_client:
        try:
            from google.genai import types as _types
            response = await gemini_client.aio.models.generate_content(
                model=settings.gemini_model,
                contents=[_types.Content(role="user", parts=[_types.Part.from_text(text=prompt)])],
                config=_types.GenerateContentConfig(temperature=0.0, max_output_tokens=256),
            )
            text = response.text.strip() if response.text else ""
            if text:
                return text
        except Exception as e:
            logger.debug("_call_llm_simple gemini failed", error=str(e))

    # Attempt 2: OpenAI
    if settings.openai_api_key and openai_client:
        try:
            resp = await openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=256,
                temperature=0.0,
            )
            text = resp.choices[0].message.content.strip()
            if text:
                return text
        except Exception as e:
            logger.debug("_call_llm_simple openai failed", error=str(e))

    raise RuntimeError("All LLM providers failed in _call_llm_simple")
