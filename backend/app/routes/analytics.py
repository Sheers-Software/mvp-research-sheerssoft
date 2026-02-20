"""
Analytics routes — Dashboard data, daily analytics, live stats, summary.
"""

import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import AnalyticsDaily
from app.schemas import AnalyticsSummaryResponse
from app.auth import verify_jwt, check_property_access

logger = structlog.get_logger()
router = APIRouter()


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
    """Get real-time analytics for the current day."""
    from app.services.analytics import get_realtime_stats
    stats = await get_realtime_stats(db, uuid.UUID(property_id))
    return stats


@router.get("/properties/{property_id}/analytics/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    property_id: str,
    db: AsyncSession = Depends(get_db),
    token: dict = Depends(check_property_access),
):
    """Get aggregated analytics summary (hero stats for Money Slide)."""
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
