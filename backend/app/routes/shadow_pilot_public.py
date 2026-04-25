"""
Shadow Pilot Public Routes — Token-gated GM dashboard.
No session auth — JWT token in query param only.
"""
import jwt
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Property, ShadowPilotAnalyticsDaily
from app.config import get_settings
from app.services.shadow_pilot_reporter import compute_weekly_rollup

router = APIRouter()



@router.get("/shadow/{property_slug}/summary")
async def get_shadow_summary(
    property_slug: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Token-gated shadow pilot summary for GM dashboard.
    No session auth required — token-only verification.

    Token is validated BEFORE the property DB lookup so that invalid/expired
    tokens always return 401, never 404 (which would leak slug existence).
    """
    settings = get_settings()
    # Validate token structure and expiry before touching the DB
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Dashboard link has expired. Contact ahmad@sheerssoft.com for a new link.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid dashboard token.")

    if payload.get("type") != "shadow_dashboard":
        raise HTTPException(status_code=401, detail="Invalid token type.")

    prop = await db.scalar(select(Property).where(Property.slug == property_slug))
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found.")

    # Verify token belongs to this property
    if str(payload.get("property_id")) != str(prop.id):
        raise HTTPException(status_code=403, detail="Token does not match property.")

    today = datetime.now(timezone.utc).date()
    rollup = await compute_weekly_rollup(db, prop, today)

    daily_rows = list(await db.scalars(
        select(ShadowPilotAnalyticsDaily).where(
            ShadowPilotAnalyticsDaily.property_id == prop.id,
        ).order_by(ShadowPilotAnalyticsDaily.report_date.desc()).limit(7)
    ))

    return {
        "property_name": prop.name,
        "property_slug": prop.slug,
        "shadow_pilot_start_date": prop.shadow_pilot_start_date.isoformat() if prop.shadow_pilot_start_date else None,
        "rollup": {
            "period_start": rollup.period_start.isoformat(),
            "period_end": rollup.period_end.isoformat(),
            "days_observed": rollup.days_observed,
            "total_inquiries": rollup.total_inquiries,
            "after_hours_inquiries": rollup.after_hours_inquiries,
            "booking_intent_inquiries": rollup.booking_intent_inquiries,
            "responded_count": rollup.responded_count,
            "unanswered_count": rollup.unanswered_count,
            "after_hours_unanswered": rollup.after_hours_unanswered,
            "avg_response_time_minutes": rollup.avg_response_time_minutes,
            "avg_response_time_after_hours": rollup.avg_response_time_after_hours,
            "response_time_over_4hr": rollup.response_time_over_4hr,
            "response_time_over_24hr": rollup.response_time_over_24hr,
            "weekly_revenue_leakage": rollup.weekly_revenue_leakage,
            "ota_commission_equivalent": rollup.ota_commission_equivalent,
            "annualised_revenue_leakage": rollup.annualised_revenue_leakage,
            "nocturn_year_1_net_recovery": rollup.nocturn_year_1_net_recovery,
            "peak_inquiry_hour": rollup.peak_inquiry_hour,
            "top_inquiry_topics": rollup.top_inquiry_topics,
            "top_unanswered_topics": rollup.top_unanswered_topics,
            "inquiries_by_hour": rollup.inquiries_by_hour_aggregate,
            "sample_abandoned_conversations": rollup.sample_abandoned_conversations,
        },
        "daily_rows": [
            {
                "date": r.report_date.isoformat(),
                "total_inquiries": r.total_inquiries,
                "after_hours_unanswered": r.after_hours_unanswered,
                "daily_revenue_leakage": float(r.daily_revenue_leakage or 0),
                "avg_response_time_minutes": float(r.avg_response_time_minutes or 0),
            }
            for r in reversed(daily_rows)
        ],
    }
