"""
Support routes — FAQ chatbot, support tickets, and live chat for tenant users.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
import structlog
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app.models import SupportTicket, Tenant, TenantMembership
from app.schemas import (
    SupportTicketCreateRequest, SupportTicketResponse,
    SupportTicketUpdateRequest, SupportChatRequest,
)

logger = structlog.get_logger()
router = APIRouter()


# ─────────────────────────────────────────────────────────────
# Support Chatbot
# ─────────────────────────────────────────────────────────────

@router.post("/support/chat")
async def support_chat(
    body: SupportChatRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Send a message to the Nocturn AI support chatbot.
    Uses the dedicated 'Nocturn AI Support' property's RAG engine.
    If conversation doesn't exist, starts a new one.
    """
    from app.models import Property, Conversation, Message

    # Find the Nocturn AI Support property
    stmt = select(Property).where(Property.slug == "nocturn-ai-support")
    result = await db.execute(stmt)
    support_property = result.scalar_one_or_none()

    if not support_property:
        # Graceful fallback if support property not provisioned yet
        return {
            "response": "Our support system is being set up. Please contact us directly via WhatsApp.",
            "conversation_id": None,
        }

    # Get or create conversation
    user_email = user.email if not isinstance(user, dict) else "admin@sheerssoft.com"
    user_name = user.full_name if not isinstance(user, dict) else "Admin"

    if body.conversation_id:
        conv_stmt = select(Conversation).where(Conversation.id == body.conversation_id)
        conv_result = await db.execute(conv_stmt)
        conversation = conv_result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(
            property_id=support_property.id,
            channel="support",
            guest_identifier=user_email,
            guest_name=user_name,
            status="active",
        )
        db.add(conversation)
        await db.flush()

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="guest",
        content=body.message,
    )
    db.add(user_msg)
    await db.flush()

    # Process through the AI conversation engine
    try:
        from app.services.conversation import process_message
        ai_response = await process_message(
            db=db,
            property_id=str(support_property.id),
            conversation_id=str(conversation.id),
            guest_message=body.message,
            guest_name=user_name,
            channel="support",
        )
        response_text = ai_response.get("response", "I'll connect you with our team.")
    except Exception as e:
        logger.error("Support chatbot AI error", error=str(e))
        response_text = (
            "I'm having trouble processing your request right now. "
            "Would you like me to connect you with a team member? "
            "Just say 'human' and I'll transfer you."
        )

    # Check for handoff requests
    handoff_keywords = ["human", "agent", "person", "help", "talk to someone", "real person"]
    if any(kw in body.message.lower() for kw in handoff_keywords):
        conversation.status = "handed_off"
        response_text = (
            "I'm connecting you with a SheersSoft team member. "
            "They'll respond shortly. Thank you for your patience!"
        )

    # Save AI response
    ai_msg = Message(
        conversation_id=conversation.id,
        role="ai",
        content=response_text,
    )
    db.add(ai_msg)
    conversation.message_count = (conversation.message_count or 0) + 2
    await db.commit()

    return {
        "response": response_text,
        "conversation_id": str(conversation.id),
        "status": conversation.status,
    }


# ─────────────────────────────────────────────────────────────
# Support Tickets
# ─────────────────────────────────────────────────────────────

@router.post("/support/tickets", response_model=SupportTicketResponse)
async def create_ticket(
    body: SupportTicketCreateRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Create a new support ticket."""
    # Get user's tenant
    user_id = user.id if not isinstance(user, dict) else uuid.UUID("00000000-0000-0000-0000-000000000000")

    if isinstance(user, dict):
        raise HTTPException(status_code=400, detail="Legacy admin cannot create tickets.")

    if not user.memberships:
        raise HTTPException(status_code=400, detail="User is not a member of any tenant.")

    tenant_id = user.memberships[0].tenant_id

    # Set priority based on tenant tier
    tenant_stmt = select(Tenant).where(Tenant.id == tenant_id)
    tenant_result = await db.execute(tenant_stmt)
    tenant = tenant_result.scalar_one_or_none()

    priority = body.priority
    if tenant and tenant.subscription_tier in ("independent", "premium"):
        # Bump priority for higher-tier tenants
        priority_map = {"low": "medium", "medium": "high"}
        priority = priority_map.get(priority, priority)

    ticket = SupportTicket(
        tenant_id=tenant_id,
        created_by_user_id=user_id,
        subject=body.subject,
        description=body.description,
        status="open",
        priority=priority,
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    return SupportTicketResponse(
        id=ticket.id,
        tenant_id=ticket.tenant_id,
        subject=ticket.subject,
        description=ticket.description,
        status=ticket.status,
        priority=ticket.priority,
        created_by_name=user.full_name,
        assigned_to_name=None,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
    )


@router.get("/support/tickets")
async def list_my_tickets(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """List the current user's support tickets."""
    if isinstance(user, dict):
        return []

    if not user.memberships:
        return []

    tenant_id = user.memberships[0].tenant_id

    stmt = (
        select(SupportTicket)
        .where(SupportTicket.tenant_id == tenant_id)
        .order_by(SupportTicket.created_at.desc())
        .limit(50)
    )
    result = await db.execute(stmt)
    tickets = result.scalars().all()

    return [
        SupportTicketResponse(
            id=t.id,
            tenant_id=t.tenant_id,
            subject=t.subject,
            description=t.description,
            status=t.status,
            priority=t.priority,
            created_by_name=None,
            assigned_to_name=None,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )
        for t in tickets
    ]


# ─────────────────────────────────────────────────────────────
# FAQ
# ─────────────────────────────────────────────────────────────

@router.get("/support/faq")
async def get_faq():
    """
    Return top FAQ entries for Nocturn AI.
    Sourced from ai.sheerssoft.com landing page.
    """
    return {
        "faqs": [
            {
                "question": "Do I need to integrate with my PMS (Opera, etc.)?",
                "answer": "No. Nocturn AI operates independently as a layer on top of your existing systems. We capture the inquiry and hand off the booking details to your team.",
            },
            {
                "question": "What happens to my existing WhatsApp conversations?",
                "answer": "Nocturn AI centralizes every WhatsApp conversation into a team inbox where anyone can see the history. Plus instant AI responses when nobody is available.",
            },
            {
                "question": "What happens after hours?",
                "answer": "Between 6PM and 9AM, Nocturn AI responds to every WhatsApp, email, and web inquiry. It captures guest intent, qualifies the lead, and queues it for your morning team.",
            },
            {
                "question": "Will guests know they're talking to AI?",
                "answer": "Our AI is trained specifically on YOUR property's tone. When a guest needs a human, it transfers instantly with full context.",
            },
            {
                "question": "How accurate is the AI?",
                "answer": "The AI only quotes information from your verified knowledge base. If it's unsure, it says: 'Let me connect you with our reservations team who can confirm the details.'",
            },
            {
                "question": "How long does setup take?",
                "answer": "48 hours from your first call to live. We handle the technical setup. Your team spends about 30 minutes sharing property information.",
            },
            {
                "question": "Is my data secure?",
                "answer": "All data is encrypted. Each property's data is fully isolated. We comply with Malaysia's PDPA requirements. Your guest data is YOUR data.",
            },
            {
                "question": "What happens after the 30-day pilot?",
                "answer": "You'll have hard data on revenue recovery. If the numbers speak, we discuss a simple monthly plan (no lock-in). If not, you walk away cost-free.",
            },
        ]
    }
