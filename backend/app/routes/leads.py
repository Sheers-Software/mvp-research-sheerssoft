"""
Lead management routes — CRUD, CSV export.
"""

import csv
import io
import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
import structlog
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models import Lead
from app.schemas import LeadResponse, LeadUpdateRequest, LeadConvertRequest
from app.auth import verify_jwt, check_property_access
from app.services.stripe_service import create_fpx_payment_link

settings = get_settings()

logger = structlog.get_logger()
router = APIRouter()


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
            actual_revenue=float(l.actual_revenue) if l.actual_revenue else None,
            priority=l.priority,
            flag_reason=l.flag_reason,
            captured_at=l.captured_at,
        )
        for l in leads
    ]


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
        actual_revenue=float(lead.actual_revenue) if lead.actual_revenue else None,
        priority=lead.priority,
        flag_reason=lead.flag_reason,
        captured_at=lead.captured_at,
    )


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
        actual_revenue=float(lead.actual_revenue) if lead.actual_revenue else None,
        priority=lead.priority,
        flag_reason=lead.flag_reason,
        captured_at=lead.captured_at,
    )


@router.post("/leads/{lead_id}/convert", response_model=LeadResponse)
async def convert_lead(
    lead_id: str,
    body: LeadConvertRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Mark a lead as converted and record actual revenue."""
    result = await db.execute(
        select(Lead).where(Lead.id == uuid.UUID(lead_id))
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead.status = "converted"
    import decimal
    lead.actual_revenue = decimal.Decimal(str(body.actual_revenue))
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
        actual_revenue=float(lead.actual_revenue) if lead.actual_revenue else None,
        priority=lead.priority,
        flag_reason=lead.flag_reason,
        captured_at=lead.captured_at,
    )


@router.get("/properties/{property_id}/leads/export")
async def export_leads_csv(
    property_id: str,
    status: str = Query(None),
    intent: str = Query(None),
    from_date: date = Query(None),
    to_date: date = Query(None),
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """Export leads as CSV file."""
    query = (
        select(Lead)
        .where(Lead.property_id == uuid.UUID(property_id))
        .order_by(Lead.captured_at.desc())
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

    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Name", "Phone", "Email", "Intent", "Status",
        "Estimated Value (RM)", "Actual Revenue (RM)", "Priority", "Channel",
        "After Hours", "Captured At"
    ])

    for lead in leads:
        writer.writerow([
            lead.guest_name or "",
            lead.guest_phone or "",
            lead.guest_email or "",
            lead.intent or "",
            lead.status or "",
            float(lead.estimated_value) if lead.estimated_value else "",
            float(lead.actual_revenue) if lead.actual_revenue else "",
            lead.priority or "",
            lead.source_channel or "",
            "Yes" if lead.is_after_hours else "No",
            lead.captured_at.isoformat() if lead.captured_at else "",
        ])

    output.seek(0)
    filename = f"leads_{property_id}_{date.today().isoformat()}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


class PaymentLinkRequest(BaseModel):
    amount_rm: float
    description: str
    nights: int | None = None


@router.post("/leads/{lead_id}/payment-link")
async def generate_payment_link(
    lead_id: str,
    body: PaymentLinkRequest,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    """Generate a Stripe FPX payment link for a lead (direct booking)."""
    lead_result = await db.execute(
        select(Lead).where(Lead.id == uuid.UUID(lead_id))
    )
    lead = lead_result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    try:
        result = await create_fpx_payment_link(
            amount_rm=body.amount_rm,
            description=body.description,
            lead_id=lead_id,
            property_id=str(lead.property_id),
            success_url=f"{settings.frontend_url}/portal?booking_confirmed=true",
            cancel_url=f"{settings.frontend_url}/portal",
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    lead.payment_link_url = result["url"]
    lead.payment_link_stripe_id = result["payment_link_id"]
    lead.payment_link_expires_at = result["expires_at"]
    lead.facilitated_by_nocturn = True
    await db.commit()

    return {
        "payment_link_url": result["url"],
        "expires_at": result["expires_at"].isoformat(),
        "amount_rm": body.amount_rm,
        "description": body.description,
    }
