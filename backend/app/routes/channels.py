"""
Guest Channel routes — WhatsApp, Web Chat, Email webhooks.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, Form
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Property, Conversation
from app.schemas import (
    MessageRequest,
    ConversationResponse,
    WebChatStartRequest,
)
from app.services.conversation import process_guest_message, FALLBACK_RESPONSE
from app.services.whatsapp import send_whatsapp_message, normalize_whatsapp_message
from app.services.twilio_whatsapp import normalize_twilio_webhook, send_twilio_message
from app.services.email import send_email, notify_staff_handoff, normalize_email_message
from app.limiter import limiter
from app.auth import verify_whatsapp_signature, verify_sendgrid_signature, verify_twilio_signature

logger = structlog.get_logger()
router = APIRouter()

# Sent when a guest sends an image, audio, video, location, or other non-text message
_MEDIA_NOT_SUPPORTED_MSG = (
    "Hi! I can only read text messages. Please type your question and I'll be happy to help! 😊\n\n"
    "*(Maaf, saya hanya boleh membaca mesej teks. Sila taip soalan anda!)*"
)


# ─────────────────────────────────────────────────────────────
# WhatsApp
# ─────────────────────────────────────────────────────────────

@router.post("/webhook/whatsapp", response_model=None)
@limiter.limit("3000/minute")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_whatsapp_signature)
):
    """
    WhatsApp Cloud API webhook receiver.
    Handles verification (GET) and incoming messages (POST).
    """
    body = await request.json()

    normalized_data = normalize_whatsapp_message(body)
    if not normalized_data:
        return {"status": "ignored"}

    phone_number_id = normalized_data["metadata"].get("phone_number_id")
    prop_result = await db.execute(
        select(Property).where(Property.whatsapp_number == phone_number_id)
    )
    prop = prop_result.scalar_one_or_none()

    if not prop:
        logger.warning("WhatsApp webhook: Property not found", phone_id=phone_number_id)
        return {"status": "property_not_found"}

    # Non-text messages (images, audio, etc.) — send canned reply, skip AI
    if normalized_data["metadata"].get("is_unsupported_media"):
        background_tasks.add_task(
            _handle_unsupported_media_async,
            from_number=normalized_data["guest_identifier"],
            whatsapp_provider=prop.whatsapp_provider,
            twilio_from_number=prop.twilio_phone_number,
        )
        return {"status": "media_not_supported"}

    background_tasks.add_task(
        _handle_whatsapp_message_async,
        property_id=prop.id,
        from_number=normalized_data["guest_identifier"],
        text=normalized_data["content"],
        guest_name=normalized_data["guest_name"],
        whatsapp_provider=prop.whatsapp_provider,
        twilio_from_number=prop.twilio_phone_number,
    )

    return {"status": "processing"}


async def _handle_unsupported_media_async(
    from_number: str,
    whatsapp_provider: str,
    twilio_from_number: str | None,
):
    """Background task: reply to unsupported media (images, audio, etc.) with a canned message."""
    try:
        if whatsapp_provider == "twilio":
            await send_twilio_message(
                to_number=from_number,
                message_text=_MEDIA_NOT_SUPPORTED_MSG,
                from_number=twilio_from_number,
            )
        else:
            await send_whatsapp_message(to_number=from_number, message_text=_MEDIA_NOT_SUPPORTED_MSG)
    except Exception as e:
        logger.error(
            "Failed to send unsupported media reply",
            error=str(e),
            from_number=from_number,
        )


async def _handle_whatsapp_message_async(
    property_id: uuid.UUID,
    from_number: str,
    text: str,
    guest_name: str | None,
    whatsapp_provider: str = "meta",
    twilio_from_number: str | None = None,
):
    """Background task to process WhatsApp message and send reply."""
    from app.database import async_session, set_db_context

    async with async_session() as db:
        try:
            await set_db_context(db, str(property_id))

            result = await process_guest_message(
                db=db,
                property_id=property_id,
                guest_identifier=from_number,
                channel="whatsapp",
                message_text=text,
                guest_name=guest_name,
            )

            await db.commit()

            response_text = result["response"]

            # Route reply based on property configuration
            if whatsapp_provider == "twilio":
                await send_twilio_message(
                    to_number=from_number,
                    message_text=response_text,
                    from_number=twilio_from_number,
                )
            else:
                await send_whatsapp_message(to_number=from_number, message_text=response_text)

            if result.get("mode") == "handoff":
                await notify_staff_handoff(
                    property_id=str(property_id),
                    conversation_id=result["conversation_id"],
                    guest_identifier=from_number,
                    channel="whatsapp",
                    guest_name=guest_name,
                    conversation_summary=f"Last message: {text}\nAI Reply: {response_text}"
                )

        except Exception as e:
            logger.error(
                "Error processing WhatsApp message",
                error=str(e),
                property_id=str(property_id),
                from_number=from_number,
                exc_info=True,
            )
            # Best-effort fallback: ensure guest gets at least a reply
            try:
                if whatsapp_provider == "twilio":
                    await send_twilio_message(
                        to_number=from_number,
                        message_text=FALLBACK_RESPONSE,
                        from_number=twilio_from_number,
                    )
                else:
                    await send_whatsapp_message(to_number=from_number, message_text=FALLBACK_RESPONSE)
            except Exception as send_err:
                logger.error(
                    "Failed to send fallback reply after processing error",
                    error=str(send_err),
                    from_number=from_number,
                )


@router.get("/webhook/whatsapp")
async def whatsapp_verify(request: Request):
    """WhatsApp webhook verification (GET request from Meta)."""
    from app.config import get_settings
    settings = get_settings()

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        return int(challenge)

    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook/twilio/whatsapp", response_model=None)
@limiter.limit("3000/minute")
async def twilio_whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_twilio_signature)
):
    """
    Twilio WhatsApp API webhook receiver.
    """
    form_data = await request.form()
    
    normalized_data = normalize_twilio_webhook(dict(form_data))
    if not normalized_data:
        return {"status": "ignored"}

    to_number = normalized_data["metadata"].get("twilio_to_number")
    # Lookup the property by the Twilio Phone Number
    prop_result = await db.execute(
        select(Property).where(Property.twilio_phone_number == to_number)
    )
    prop = prop_result.scalar_one_or_none()

    if not prop:
        logger.warning("Twilio webhook: Property not found", to_number=to_number)
        return {"status": "property_not_found"}

    # Non-text messages (images, audio, etc.) — send canned reply, skip AI
    if normalized_data["metadata"].get("is_unsupported_media"):
        background_tasks.add_task(
            _handle_unsupported_media_async,
            from_number=normalized_data["guest_identifier"],
            whatsapp_provider="twilio",
            twilio_from_number=prop.twilio_phone_number,
        )
        return {"status": "media_not_supported"}

    background_tasks.add_task(
        _handle_whatsapp_message_async,
        property_id=prop.id,
        from_number=normalized_data["guest_identifier"],
        text=normalized_data["content"],
        guest_name=normalized_data["guest_name"],
        whatsapp_provider="twilio",
        twilio_from_number=prop.twilio_phone_number,
    )

    return {"status": "processing"}


# ─────────────────────────────────────────────────────────────
# Email
# ─────────────────────────────────────────────────────────────

@router.post("/webhook/email", response_model=None)
@limiter.limit("100/minute")
async def email_webhook(
    background_tasks: BackgroundTasks,
    subject: str = Form(None),
    text: str = Form(None),
    html: str = Form(None),
    to: str = Form(None),
    sender: str = Form(None),
    request: Request = None,
    _ = Depends(verify_sendgrid_signature),
    db: AsyncSession = Depends(get_db)
):
    """SendGrid Inbound Parse webhook receiver."""
    form_data = await request.form()

    normalized_data = normalize_email_message(dict(form_data))
    if not normalized_data:
        return {"status": "ignored"}

    to_address = normalized_data["metadata"].get("to_address")
    prop_result = await db.execute(
        select(Property).where(Property.notification_email == to_address)
    )
    prop = prop_result.scalar_one_or_none()

    if not prop:
        logger.warning("Email webhook: Property not found", to_address=to_address)
        return {"status": "no_property"}

    background_tasks.add_task(
        _handle_email_message_async,
        property_id=prop.id,
        from_address=normalized_data["guest_identifier"],
        subject=normalized_data["metadata"].get("subject"),
        text=normalized_data["content"],
        guest_name=normalized_data["guest_name"]
    )

    return {"status": "processing"}


async def _handle_email_message_async(
    property_id: uuid.UUID,
    from_address: str,
    subject: str,
    text: str,
    guest_name: str | None
):
    """Background task to process inbound email and send reply."""
    from app.database import async_session, set_db_context

    async with async_session() as db:
        try:
            await set_db_context(db, str(property_id))

            result = await process_guest_message(
                db=db,
                property_id=property_id,
                guest_identifier=from_address,
                channel="email",
                message_text=text,
                guest_name=guest_name,
            )

            await db.commit()

            response_text = result["response"]
            await send_email(
                to_email=from_address,
                subject=f"Re: {subject}",
                content=response_text
            )

            if result.get("mode") == "handoff":
                await notify_staff_handoff(
                    property_id=str(property_id),
                    conversation_id=result["conversation_id"],
                    guest_identifier=from_address,
                    channel="email",
                    guest_name=guest_name,
                    conversation_summary=f"Message: {text}\n\nAI Reply: {response_text}"
                )

        except Exception as e:
            logger.error(
                "Error processing email message",
                error=str(e),
                property_id=str(property_id),
                guest_email=from_address
            )


# ─────────────────────────────────────────────────────────────
# Web Chat Widget
# ─────────────────────────────────────────────────────────────

@router.post("/conversations", response_model=ConversationResponse)
@limiter.limit("500/minute")
async def web_chat_message(
    request: Request,
    body: WebChatStartRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Web chat widget endpoint.
    Handles both new conversations and follow-up messages.
    """
    property_id = uuid.UUID(body.property_id)
    session_id = body.session_id or str(uuid.uuid4())

    result = await process_guest_message(
        db=db,
        property_id=property_id,
        guest_identifier=f"web:{session_id}",
        channel="web",
        message_text=body.message,
        guest_name=body.guest_name,
    )

    return ConversationResponse(**result)


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=ConversationResponse,
)
@limiter.limit("60/minute")
async def web_chat_follow_up(
    request: Request,
    conversation_id: str,
    body: MessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """Follow-up message in an existing web chat conversation."""
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
    )
    conv = conv_result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    result = await process_guest_message(
        db=db,
        property_id=conv.property_id,
        guest_identifier=conv.guest_identifier,
        channel=conv.channel,
        message_text=body.message,
        guest_name=body.guest_name,
    )

    return ConversationResponse(**result)
