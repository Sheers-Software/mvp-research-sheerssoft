"""
After-Hours Revenue Audit endpoints.

Public:
  POST /audit/calculate    — instant calculation (no save, no auth)
  POST /audit/submit       — save audit record + trigger email (no auth)

SuperAdmin:
  GET  /audit/records      — list all audit submissions
  GET  /audit/records/{id} — single record detail
  PATCH /audit/records/{id} — update status / notes
"""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_superadmin
from app.database import get_db
from app.limiter import limiter
from app.models import AuditRecord

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit")

# ─── Constants ───────────────────────────────────────────────────────────────

AFTER_HOURS_SHARE = 0.60       # 60% of msgs arrive after hours
CONVERSION_RATE = 0.20          # 20% of after-hours msgs would have converted
AVG_STAY_NIGHTS = 2.0           # Malaysian domestic traveler average
OTA_DISPLACEMENT = 0.65         # 65% of unanswered guests book OTA instead
CONSERVATIVE_DISCOUNT = 0.60    # Final number discounted to 60% for credibility
MONTHLY_SUBSCRIPTION_RM = 499.0  # Boutique tier — used for ROI calc

# Daily message estimates by room count band when user picks "I don't know"
ROOM_TO_MSGS: list[tuple[int, int, float]] = [
    (20, 40, 7.5),
    (40, 80, 15.0),
    (80, 150, 30.0),
    (150, 9999, 50.0),
]

# Front-desk closure hour presets (24h)
CLOSURE_HOUR_MAP = {
    "20:00": 20,
    "21:00": 21,
    "22:00": 22,
    "23:00": 23,
    "00:00": 24,
    "24h": 0,  # 0 means 24-hour coverage → no dark window
}


# ─── Schemas ─────────────────────────────────────────────────────────────────

class AuditInputs(BaseModel):
    room_count: int
    adr: float                    # Average Daily Rate in RM
    daily_msgs: float | None = None   # None → derive from room_count
    front_desk_close: str = "22:00"   # "20:00"|"21:00"|"22:00"|"23:00"|"00:00"|"24h"
    ota_commission_rate: float = 18.0  # percentage, e.g. 18.0


class AuditResults(BaseModel):
    # Inputs echoed back
    room_count: int
    adr: float
    daily_msgs_used: float
    after_hours_msgs_per_day: float
    monthly_after_hours_msgs: float
    lost_bookings_per_month: float
    avg_stay_nights: float
    # Revenue figures
    revenue_lost_monthly: float
    ota_commission_monthly: float
    total_monthly_leakage: float
    annual_leakage: float
    conservative_annual: float
    # ROI
    annual_net_recovery: float    # conservative_annual - subscription cost
    roi_multiple: float


class AuditSubmitRequest(BaseModel):
    inputs: AuditInputs
    contact_name: str
    hotel_name: str
    email: str
    phone: str | None = None


class AuditRecordResponse(BaseModel):
    id: str
    hotel_name: str | None
    contact_name: str | None
    email: str | None
    phone: str | None
    room_count: int
    adr: float
    daily_msgs: float
    front_desk_close: str
    ota_commission_rate: float
    revenue_lost_monthly: float
    ota_commission_monthly: float
    total_monthly_leakage: float
    annual_leakage: float
    conservative_annual: float
    roi_multiple: float
    status: str
    notes: str | None
    source: str
    created_at: str


class AuditStatusUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None


# ─── Calculation logic ────────────────────────────────────────────────────────

def _derive_daily_msgs(room_count: int) -> float:
    for lo, hi, estimate in ROOM_TO_MSGS:
        if lo <= room_count < hi:
            return estimate
    return 50.0


def _calculate(inputs: AuditInputs) -> AuditResults:
    daily_msgs = inputs.daily_msgs if inputs.daily_msgs else _derive_daily_msgs(inputs.room_count)

    close_hour = CLOSURE_HOUR_MAP.get(inputs.front_desk_close, 22)
    if close_hour == 0:
        # 24-hour front desk — still some dark window (night audit only, 2am-7am)
        # Use 20% instead of 60% for partial after-hours share
        after_hours_share = 0.20
    else:
        after_hours_share = AFTER_HOURS_SHARE

    after_hours_msgs_per_day = daily_msgs * after_hours_share
    monthly_after_hours = after_hours_msgs_per_day * 30
    lost_bookings = monthly_after_hours * CONVERSION_RATE

    revenue_lost_monthly = lost_bookings * inputs.adr * AVG_STAY_NIGHTS
    ota_bookings_monthly = lost_bookings * OTA_DISPLACEMENT
    ota_commission_monthly = ota_bookings_monthly * inputs.adr * AVG_STAY_NIGHTS * (inputs.ota_commission_rate / 100)

    total_monthly = revenue_lost_monthly + ota_commission_monthly
    annual_leakage = total_monthly * 12
    conservative_annual = annual_leakage * CONSERVATIVE_DISCOUNT
    annual_subscription = MONTHLY_SUBSCRIPTION_RM * 12
    annual_net_recovery = conservative_annual - annual_subscription
    roi_multiple = conservative_annual / annual_subscription if annual_subscription > 0 else 0

    return AuditResults(
        room_count=inputs.room_count,
        adr=inputs.adr,
        daily_msgs_used=daily_msgs,
        after_hours_msgs_per_day=round(after_hours_msgs_per_day, 1),
        monthly_after_hours_msgs=round(monthly_after_hours, 0),
        lost_bookings_per_month=round(lost_bookings, 1),
        avg_stay_nights=AVG_STAY_NIGHTS,
        revenue_lost_monthly=round(revenue_lost_monthly, 0),
        ota_commission_monthly=round(ota_commission_monthly, 0),
        total_monthly_leakage=round(total_monthly, 0),
        annual_leakage=round(annual_leakage, 0),
        conservative_annual=round(conservative_annual, 0),
        annual_net_recovery=round(annual_net_recovery, 0),
        roi_multiple=round(roi_multiple, 1),
    )


# ─── Public endpoints ─────────────────────────────────────────────────────────

@router.post("/calculate", response_model=AuditResults, summary="Calculate audit (no save)")
@limiter.limit("60/minute")
async def calculate_audit(request: Request, inputs: AuditInputs):
    """
    Instant calculation. No auth required, nothing saved.
    Frontend calls this on every input change for live preview.
    """
    return _calculate(inputs)


@router.post("/submit", response_model=dict, summary="Submit audit and save lead")
@limiter.limit("5/minute")
async def submit_audit(
    request: Request,
    body: AuditSubmitRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Saves the audit record with contact info.
    No auth required — this is the public lead-gate endpoint.
    """
    results = _calculate(body.inputs)

    record = AuditRecord(
        hotel_name=body.hotel_name,
        contact_name=body.contact_name,
        email=body.email,
        phone=body.phone,
        room_count=body.inputs.room_count,
        adr=body.inputs.adr,
        daily_msgs=results.daily_msgs_used,
        front_desk_close=body.inputs.front_desk_close,
        ota_commission_rate=body.inputs.ota_commission_rate,
        revenue_lost_monthly=results.revenue_lost_monthly,
        ota_commission_monthly=results.ota_commission_monthly,
        total_monthly_leakage=results.total_monthly_leakage,
        annual_leakage=results.annual_leakage,
        conservative_annual=results.conservative_annual,
        roi_multiple=results.roi_multiple,
        source="web",
        status="submitted",
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    logger.info(
        f"Audit submitted: {body.hotel_name} ({body.email}) — "
        f"RM {results.conservative_annual:,.0f}/yr conservative leakage"
    )

    # TODO: trigger SendGrid email with PDF report
    # TODO: send Slack notification to SheersSoft

    return {
        "id": str(record.id),
        "results": results.model_dump(),
        "message": "Audit submitted successfully",
    }


# ─── SuperAdmin endpoints ─────────────────────────────────────────────────────

@router.get("/records", summary="List all audit records (superadmin)")
async def list_audit_records(
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_superadmin),
):
    result = await db.execute(
        select(AuditRecord).order_by(desc(AuditRecord.created_at))
    )
    records = result.scalars().all()

    return [
        AuditRecordResponse(
            id=str(r.id),
            hotel_name=r.hotel_name,
            contact_name=r.contact_name,
            email=r.email,
            phone=r.phone,
            room_count=r.room_count,
            adr=float(r.adr),
            daily_msgs=float(r.daily_msgs),
            front_desk_close=r.front_desk_close,
            ota_commission_rate=float(r.ota_commission_rate),
            revenue_lost_monthly=float(r.revenue_lost_monthly),
            ota_commission_monthly=float(r.ota_commission_monthly),
            total_monthly_leakage=float(r.total_monthly_leakage),
            annual_leakage=float(r.annual_leakage),
            conservative_annual=float(r.conservative_annual),
            roi_multiple=float(r.roi_multiple),
            status=r.status,
            notes=r.notes,
            source=r.source,
            created_at=r.created_at.isoformat(),
        )
        for r in records
    ]


@router.get("/records/{record_id}", summary="Get single audit record (superadmin)")
async def get_audit_record(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_superadmin),
):
    result = await db.execute(
        select(AuditRecord).where(AuditRecord.id == uuid.UUID(record_id))
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Audit record not found")

    return AuditRecordResponse(
        id=str(record.id),
        hotel_name=record.hotel_name,
        contact_name=record.contact_name,
        email=record.email,
        phone=record.phone,
        room_count=record.room_count,
        adr=float(record.adr),
        daily_msgs=float(record.daily_msgs),
        front_desk_close=record.front_desk_close,
        ota_commission_rate=float(record.ota_commission_rate),
        revenue_lost_monthly=float(record.revenue_lost_monthly),
        ota_commission_monthly=float(record.ota_commission_monthly),
        total_monthly_leakage=float(record.total_monthly_leakage),
        annual_leakage=float(record.annual_leakage),
        conservative_annual=float(record.conservative_annual),
        roi_multiple=float(record.roi_multiple),
        status=record.status,
        notes=record.notes,
        source=record.source,
        created_at=record.created_at.isoformat(),
    )


@router.patch("/records/{record_id}", summary="Update audit record status/notes (superadmin)")
async def update_audit_record(
    record_id: str,
    body: AuditStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_superadmin),
):
    result = await db.execute(
        select(AuditRecord).where(AuditRecord.id == uuid.UUID(record_id))
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Audit record not found")

    if body.status is not None:
        record.status = body.status
    if body.notes is not None:
        record.notes = body.notes
    record.updated_at = datetime.utcnow()

    await db.commit()
    return {"ok": True}
