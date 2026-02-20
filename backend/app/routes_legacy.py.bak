"""
API routes for the Nocturn AI Inquiry Capture Engine.

Organized by the three user experiences:
- Guest channels: WhatsApp webhook, Web chat, Email webhook
- Staff: Conversation management, handoff
- GM: Analytics, leads, reports
"""

import json
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, BackgroundTasks, Form
import structlog
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Property, Conversation, Message, Lead, AnalyticsDaily, KBDocument
from app.schemas import (
    MessageRequest,
    ConversationResponse,
    WebChatStartRequest,
    LeadResponse,
    LeadUpdateRequest,
    PropertyResponse,
    PropertyCreateRequest,
    KBIngestRequest,
    KBIngestResponse,
    AnalyticsSummaryResponse,
)
from app.services.conversation import process_guest_message
from app.services import ingest_knowledge_base
from app.services.whatsapp import send_whatsapp_message
from app.services.email import send_email, notify_staff_handoff
from app.services.email import send_email, notify_staff_handoff, notify_staff_handoff_enhanced, normalize_email_message
from app.limiter import limiter
from app.auth import verify_jwt, verify_whatsapp_signature, verify_sendgrid_signature, check_property_access
from app.core.normalization import NormalizedMessage
from app.services.whatsapp import send_whatsapp_message, normalize_whatsapp_message
from app.services.analytics import get_realtime_stats

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1")


# ─────────────────────────────────────────────────────────────
# Guest Channels
# ─────────────────────────────────────────────────────────────

@router.get("/properties", response_model=List[PropertyResponse])
async def list_properties(
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """List all properties (for dashboard selection)."""
    # result = await db.execute(select(Property))
    # return result.scalars().all()
    # Pydantic validation error fix: return list of properties
    
    # We still need to set context or bypass if RLS blocks listing all properties?
    # But previous endpoint implementation didn't have special context logic.
    # Assuming RLS allows SELECT for property table or relying on admin privilege in DB.
    
    result = await db.execute(select(Property))
    return result.scalars().all()


@router.post("/webhook/whatsapp", response_model=None)
@limiter.limit("3000/minute")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    # Signature verification
    _: None = Depends(verify_whatsapp_signature)
):
    """
    WhatsApp Cloud API webhook receiver.
    Handles verification (GET) and incoming messages (POST).
    """
    body = await request.json()

    # 1. Normalize payload
    normalized_data = normalize_whatsapp_message(body)
    
    if not normalized_data:
        # Not a valid message (could be a status update or other event we don't handle yet)
        return {"status": "ignored"}

    # 2. Find property by WhatsApp Phone Number ID
    phone_number_id = normalized_data["metadata"].get("phone_number_id")
    
    prop_result = await db.execute(
        select(Property).where(Property.whatsapp_number == phone_number_id)
    )
    prop = prop_result.scalar_one_or_none()

    if not prop:
        logger.warning("WhatsApp webhook: Property not found", phone_id=phone_number_id)
        return {"status": "property_not_found"}

    # 3. Process in background
    background_tasks.add_task(
        _handle_whatsapp_message_async,
        property_id=prop.id,
        from_number=normalized_data["guest_identifier"],
        text=normalized_data["content"],
        guest_name=normalized_data["guest_name"]
    )

    return {"status": "processing"}


async def _handle_whatsapp_message_async(
    property_id: uuid.UUID,
    from_number: str,
    text: str,
    guest_name: str | None
):
    """
    Background task to process WhatsApp message and send reply.
    """
    # Create a new DB session for the background task
    from app.database import async_session, set_db_context
    
    async with async_session() as db:
        try:
            # Set RLS context for this property
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
            
            # Send response back via WhatsApp API
            response_text = result["response"]
            await send_whatsapp_message(to_number=from_number, message_text=response_text)
            
            # Notify staff if handoff triggered
            if result.get("mode") == "handoff":
                await notify_staff_handoff_enhanced(
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
                from_number=from_number
            )


@router.post("/webhook/email", response_model=None)
@limiter.limit("100/minute")
async def email_webhook(
    background_tasks: BackgroundTasks,
    subject: str = Form(None),
    text: str = Form(None),
    html: str = Form(None),
    to: str = Form(None),
    sender: str = Form(None),  # SendGrid sends 'from' as 'sender' or 'from' depending on config due to Python keyword? No, it sends 'from'.
    # But 'from' is a reserved keyword in Python.
    # FastAPI handles this via alias? No.
    # We need to access via request.form() because 'from' is a keyword.
    request: Request = None,
    # Verification (Optional but recommended)
    _ = Depends(verify_sendgrid_signature),
    db: AsyncSession = Depends(get_db)
):
    """
    SendGrid Inbound Parse webhook receiver.
    Parses multipart/form-data.
    """
    form_data = await request.form()
    
    # 1. Normalize
    normalized_data = normalize_email_message(dict(form_data))
    
    if not normalized_data:
        return {"status": "ignored"}
        
    # 2. Find property by To address
    # In normalized data, we put to_address in metadata
    to_address = normalized_data["metadata"].get("to_address")
    
    prop_result = await db.execute(
        select(Property).where(Property.notification_email == to_address)
    )
    prop = prop_result.scalar_one_or_none()
    
    if not prop:
        logger.warning("Email webhook: Property not found", to_address=to_address)
        return {"status": "no_property"}

    # 3. Process
    background_tasks.add_task(
        _handle_email_message_async,
        property_id=prop.id,
        from_address=normalized_data["guest_identifier"],
        subject=normalized_data["metadata"].get("subject"),
        text=normalized_data["content"], # content includes subject preamble
        guest_name=normalized_data["guest_name"]
    )

    return {"status": "processing"}


async def _handle_email_message_async(
    property_id: uuid.UUID,
    from_address: str, # renamed from guest_email to match usage
    subject: str,
    text: str, # this is now the full content
    guest_name: str | None
):
    """
    Background task to process inbound email and send reply.
    """
    from app.database import async_session, set_db_context
    
    async with async_session() as db:
        try:
            # Set RLS context
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
            
            # Send reply
            await send_email(
                to_email=from_address,
                subject=f"Re: {subject}",
                content=response_text
            )

            # Notify staff if handoff triggered
            if result.get("mode") == "handoff":
                await notify_staff_handoff_enhanced(
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


@router.post("/conversations", response_model=ConversationResponse)
@limiter.limit("20/minute")
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


# ─────────────────────────────────────────────────────────────
# Staff: Conversation Management
# ─────────────────────────────────────────────────────────────

@router.get("/properties/{property_id}/conversations")
async def list_conversations(
    property_id: str,
    status: str = Query(None, description="Filter by status"),
    after_hours: bool = Query(None, description="Filter after-hours only"),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    # Auth
    token: dict = Depends(check_property_access),
):
    """List conversations for a property (staff dashboard)."""
    query = (
        select(Conversation)
        .where(Conversation.property_id == uuid.UUID(property_id))
        .options(selectinload(Conversation.lead))
        .order_by(Conversation.started_at.desc())
        .limit(limit)
    )

    if status:
        query = query.where(Conversation.status == status)
    if after_hours is not None:
        query = query.where(Conversation.is_after_hours == after_hours)

    result = await db.execute(query)
    conversations = result.scalars().all()

    return [
        {
            "id": str(c.id),
            "channel": c.channel,
            "guest_name": c.guest_name,
            "guest_identifier": c.guest_identifier,
            "status": c.status,
            "ai_mode": c.ai_mode,
            "is_after_hours": c.is_after_hours,
            "started_at": c.started_at.isoformat(),
            "has_lead": c.lead is not None,
            "lead_intent": c.lead.intent if c.lead else None,
        }
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Get full conversation with all messages (for staff drill-down)."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == uuid.UUID(conversation_id))
        .options(
            selectinload(Conversation.messages),
            selectinload(Conversation.lead),
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "id": str(conv.id),
        "channel": conv.channel,
        "guest_name": conv.guest_name,
        "status": conv.status,
        "ai_mode": conv.ai_mode,
        "is_after_hours": conv.is_after_hours,
        "started_at": conv.started_at.isoformat(),
        "messages": [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "sent_at": m.sent_at.isoformat(),
                "metadata": m.metadata_,
            }
            for m in conv.messages
        ],
        "lead": {
            "id": str(conv.lead.id),
            "guest_name": conv.lead.guest_name,
            "intent": conv.lead.intent,
            "status": conv.lead.status,
            "estimated_value": float(conv.lead.estimated_value) if conv.lead.estimated_value else None,
        } if conv.lead else None,
    }


@router.post("/conversations/{conversation_id}/resolve")
async def resolve_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Staff resolves/closes a conversation."""
    result = await db.execute(
        select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv.status = "resolved"
    conv.ended_at = datetime.now(timezone.utc)
    await db.flush()
    return {"status": "resolved", "conversation_id": conversation_id}


@router.get("/analytics/dashboard")
async def get_dashboard_stats(
    user: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db)
):
    """
    Get real-time dashboard statistics.
    Includes:
    - Money Slide (Recovered Revenue)
    - Operations View (Active Inquiries, Response Time)
    """
    # Quick hack for MVP: Fetch the first property ID since we are single tenant per deployment usually
    result = await db.execute(select(Property).limit(1))
    prop = result.scalar_one_or_none()
    
    if not prop:
         raise HTTPException(status_code=404, detail="No property found")
         
    stats = await get_realtime_stats(db, prop.id)
    return stats


# ─────────────────────────────────────────────────────────────
# GM: Leads
# ─────────────────────────────────────────────────────────────

@router.get("/properties/{property_id}/leads", response_model=list[LeadResponse])
async def list_leads(
    property_id: str,
    status: str = Query(None),
    intent: str = Query(None),
    from_date: date = Query(None),
    to_date: date = Query(None),
    limit: int = Query(50, le=500),
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """List leads for a property (GM dashboard leads view)."""
    query = (
        select(Lead)
        .where(Lead.property_id == uuid.UUID(property_id))
        .order_by(Lead.captured_at.desc())
        .limit(limit)
    )

    if status:
        query = query.where(Lead.status == status)
    if intent:
        query = query.where(Lead.intent == intent)
    if from_date:
        query = query.where(Lead.captured_at >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        query = query.where(Lead.captured_at <= datetime.combine(to_date, datetime.max.time()))

    result = await db.execute(query)
    leads = result.scalars().all()

    return [
        LeadResponse(
            id=str(l.id),
            conversation_id=str(l.conversation_id),
            guest_name=l.guest_name,
            guest_phone=l.guest_phone,
            guest_email=l.guest_email,
            intent=l.intent,
            status=l.status,
            estimated_value=float(l.estimated_value) if l.estimated_value else None,
            captured_at=l.captured_at,
        )
        for l in leads
    ]


@router.patch("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    body: LeadUpdateRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Update a lead's status or notes."""
    result = await db.execute(
        select(Lead).where(Lead.id == uuid.UUID(lead_id))
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if body.status:
        lead.status = body.status
    if body.notes is not None:
        lead.notes = body.notes

    return LeadResponse(
        id=str(lead.id),
        conversation_id=str(lead.conversation_id),
        guest_name=lead.guest_name,
        guest_phone=lead.guest_phone,
        guest_email=lead.guest_email,
        intent=lead.intent,
        status=lead.status,
        estimated_value=float(lead.estimated_value) if lead.estimated_value else None,
        captured_at=lead.captured_at,
    )


# ─────────────────────────────────────────────────────────────
# GM: Analytics
# ─────────────────────────────────────────────────────────────

@router.get("/properties/{property_id}/analytics")
async def get_analytics(
    property_id: str,
    from_date: date = Query(None),
    to_date: date = Query(None),
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """
    Get analytics for a property over a date range.
    Used by the GM dashboard Money View and Operations View.
    """
    pid = uuid.UUID(property_id)

    if not from_date:
        from_date = date.today() - timedelta(days=30)
    if not to_date:
        to_date = date.today()

    # Get daily analytics
    result = await db.execute(
        select(AnalyticsDaily)
        .where(
            AnalyticsDaily.property_id == pid,
            AnalyticsDaily.report_date >= from_date,
            AnalyticsDaily.report_date <= to_date,
        )
        .order_by(AnalyticsDaily.report_date)
    )
    daily_records = result.scalars().all()

    # Aggregate totals
    totals = {
        "total_inquiries": sum(r.total_inquiries for r in daily_records),
        "after_hours_inquiries": sum(r.after_hours_inquiries for r in daily_records),
        "after_hours_responded": sum(r.after_hours_responded for r in daily_records),
        "leads_captured": sum(r.leads_captured for r in daily_records),
        "handoffs": sum(r.handoffs for r in daily_records),
        "estimated_revenue_recovered": float(
            sum(r.estimated_revenue_recovered for r in daily_records)
        ),
    }
    total_response_times = [
        float(r.avg_response_time_sec)
        for r in daily_records
        if r.avg_response_time_sec > 0
    ]
    totals["avg_response_time_sec"] = (
        sum(total_response_times) / len(total_response_times)
        if total_response_times
        else 0
    )

    # Daily breakdown for charts
    daily = [
        {
            "date": r.report_date.isoformat(),
            "total_inquiries": r.total_inquiries,
            "after_hours_inquiries": r.after_hours_inquiries,
            "leads_captured": r.leads_captured,
            "estimated_revenue_recovered": float(r.estimated_revenue_recovered),
            "channel_breakdown": r.channel_breakdown,
        }
        for r in daily_records
    ]

    return {
        "property_id": property_id,
        "period": {"from": from_date.isoformat(), "to": to_date.isoformat()},
        "totals": totals,
        "daily": daily,
    }


@router.get("/properties/{property_id}/analytics/live")
async def get_analytics_live(
    property_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """
    Get real-time analytics for the current day.
    """
    from app.services.analytics import get_realtime_stats
    stats = await get_realtime_stats(db, uuid.UUID(property_id))
    return stats


# ─────────────────────────────────────────────────────────────
# Auth Routes
# ─────────────────────────────────────────────────────────────

from fastapi.security import OAuth2PasswordRequestForm
from app.config import get_settings
from jose import jwt
from datetime import datetime, timedelta
from app.auth import check_property_access

@router.post("/auth/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint for dashboard access.
    MVP: Hardcoded admin check or check against properties.
    """
    settings = get_settings()
    # Simple hardcoded check for MVP
    user_ok = False
    
    # Check 1: Master Admin
    if form_data.username == settings.admin_user and form_data.password == settings.admin_password:
        user_ok = True
        
    # Check 2: Property Email (Optional, for later)
    # result = await db.execute(select(Property).where(Property.notification_email == form_data.username))
    # prop = result.scalar_one_or_none()
    # if prop and form_data.password == "password123": # Insecure for prod, ok for MVP demo
    #    user_ok = True

    if not user_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT
    access_token_expires = timedelta(hours=settings.jwt_expiry_hours)
    expire = datetime.utcnow() + access_token_expires
    
    to_encode = {
        "sub": form_data.username, 
        "exp": expire,
        "is_admin": True, # For now, all logins are admin
        "property_ids": ["*"] # Wildcard access for admin
    }
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    
    return {"access_token": encoded_jwt, "token_type": "bearer"}


# ─────────────────────────────────────────────────────────────
# Property Admin
# ─────────────────────────────────────────────────────────────

@router.post("/properties", response_model=PropertyResponse, status_code=201)
async def create_property(
    body: PropertyCreateRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Create a new property (tenant)."""
    from decimal import Decimal
    prop = Property(
        name=body.name,
        whatsapp_number=body.whatsapp_number,
        website_url=body.website_url,
        operating_hours=body.operating_hours,
        adr=Decimal(str(body.adr)),
        ota_commission_pct=Decimal(str(body.ota_commission_pct)),
    )
    db.add(prop)
    await db.flush()

    return PropertyResponse(
        id=str(prop.id),
        name=prop.name,
        whatsapp_number=prop.whatsapp_number,
        website_url=prop.website_url,
        adr=float(prop.adr),
        ota_commission_pct=float(prop.ota_commission_pct),
        created_at=prop.created_at,
    )


@router.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Get property details."""
    result = await db.execute(
        select(Property).where(Property.id == uuid.UUID(property_id))
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    return PropertyResponse(
        id=str(prop.id),
        name=prop.name,
        whatsapp_number=prop.whatsapp_number,
        website_url=prop.website_url,
        adr=float(prop.adr),
        ota_commission_pct=float(prop.ota_commission_pct),
        created_at=prop.created_at,
    )


@router.put("/properties/{property_id}/knowledge-base", response_model=KBIngestResponse)
async def upload_knowledge_base(
    property_id: str,
    body: KBIngestRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """Upload or replace a property's knowledge base."""
    pid = uuid.UUID(property_id)

    # Verify property exists
    result = await db.execute(select(Property).where(Property.id == pid))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Property not found")

    count = await ingest_knowledge_base(
        db=db,
        property_id=pid,
        documents=[doc.model_dump() for doc in body.documents],
    )

    return KBIngestResponse(documents_ingested=count, property_id=property_id)


# ─────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────

@router.get("/health")
@limiter.limit("100/minute")
async def health_check(request: Request, db: AsyncSession = Depends(get_db)):
    """Health check endpoint for container orchestrators."""
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}


# ─────────────────────────────────────────────────────────────
# Missing Endpoints (Audit Remediation)
# ─────────────────────────────────────────────────────────────

@router.post("/conversations/{conversation_id}/handoff")
async def handoff_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Explicitly trigger AI handoff."""
    result = await db.execute(
        select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv.ai_mode = "handoff"
    conv.status = "handoff"
    await db.flush()
    return {"status": "handed_off", "conversation_id": conversation_id}


@router.post("/conversations/{conversation_id}/takeover")
async def takeover_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Staff takes over conversation (pauses AI)."""
    result = await db.execute(
        select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv.ai_mode = "staff"
    conv.status = "active"
    await db.flush()
    return {"status": "staff_takeover", "conversation_id": conversation_id}


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Get individual lead details."""
    result = await db.execute(
        select(Lead).where(Lead.id == uuid.UUID(lead_id))
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    return LeadResponse(
        id=str(lead.id),
        conversation_id=str(lead.conversation_id),
        guest_name=lead.guest_name,
        guest_phone=lead.guest_phone,
        guest_email=lead.guest_email,
        intent=lead.intent,
        status=lead.status,
        estimated_value=float(lead.estimated_value) if lead.estimated_value else None,
        captured_at=lead.captured_at,
    )


@router.get("/properties/{property_id}/analytics/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    property_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """Get aggregated analytics summary (hero stats)."""
    pid = uuid.UUID(property_id)
    from_date = date.today() - timedelta(days=30)
    
    result = await db.execute(
        select(AnalyticsDaily)
        .where(
            AnalyticsDaily.property_id == pid,
            AnalyticsDaily.report_date >= from_date
        )
    )
    daily_records = result.scalars().all()
    
    avg_resp = 0
    if daily_records:
        resps = [float(r.avg_response_time_sec) for r in daily_records if r.avg_response_time_sec > 0]
        if resps:
            avg_resp = sum(resps) / len(resps)
            
    return AnalyticsSummaryResponse(
        total_inquiries=sum(r.total_inquiries for r in daily_records),
        after_hours_inquiries=sum(r.after_hours_inquiries for r in daily_records),
        after_hours_responded=sum(r.after_hours_responded for r in daily_records),
        leads_captured=sum(r.leads_captured for r in daily_records),
        handoffs=sum(r.handoffs for r in daily_records),
        avg_response_time_sec=avg_resp,
        estimated_revenue_recovered=float(sum(r.estimated_revenue_recovered for r in daily_records)),
        channel_breakdown={}
    )


@router.get("/properties/{property_id}/settings")
async def get_property_settings(
    property_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """Get property configuration."""
    result = await db.execute(
        select(Property).where(Property.id == uuid.UUID(property_id))
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    return {
        "id": str(prop.id),
        "operating_hours": prop.operating_hours,
        "knowledge_base_config": prop.knowledge_base_config,
        "timezone": prop.timezone,
        "plan_tier": prop.plan_tier,
        "is_active": prop.is_active,
    }


@router.post("/properties/{property_id}/onboard")
async def onboard_property(
    property_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """Trigger onboarding."""
    return {"status": "onboarded", "property_id": property_id}
