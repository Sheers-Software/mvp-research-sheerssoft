"""
Daily aggregation job for shadow pilot analytics.
Called by Cloud Scheduler via POST /api/v1/internal/run-shadow-pilot-aggregation
"""
from datetime import date, datetime, timezone, timedelta
from collections import Counter
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.models import ShadowPilotConversation, ShadowPilotAnalyticsDaily, Property

logger = structlog.get_logger()


async def run_daily_aggregation(db: AsyncSession, target_date: Optional[date] = None) -> dict:
    """Aggregate yesterday's conversations for all active shadow pilot properties."""
    if target_date is None:
        target_date = (datetime.now(timezone.utc) - timedelta(days=1)).date()

    props = list(await db.scalars(
        select(Property).where(
            Property.shadow_pilot_mode == True,
            Property.shadow_pilot_session_active == True,
        )
    ))
    results = []
    for prop in props:
        count = await _aggregate_property(db, prop, target_date)
        results.append({"property_id": str(prop.id), "conversations": count})
    return {"date": str(target_date), "properties": results}


async def _aggregate_property(db: AsyncSession, prop: Property, report_date: date) -> int:
    tz_name = prop.timezone or "Asia/Kuala_Lumpur"
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(tz_name)
    except Exception:
        import pytz
        tz = pytz.timezone(tz_name)

    # Fetch conversations whose first message falls on report_date in property-local time
    # Use a wide UTC window to account for any timezone offset (±14 hours max)
    all_convs = list(await db.scalars(
        select(ShadowPilotConversation).where(
            ShadowPilotConversation.property_id == prop.id,
            ShadowPilotConversation.first_guest_message_at >= datetime.combine(
                report_date, datetime.min.time()
            ).replace(tzinfo=timezone.utc) - timedelta(hours=24),
            ShadowPilotConversation.first_guest_message_at < datetime.combine(
                report_date, datetime.min.time()
            ).replace(tzinfo=timezone.utc) + timedelta(hours=48),
        )
    ))

    # Filter to exactly report_date in local time
    convs = [
        c for c in all_convs
        if c.first_guest_message_at.astimezone(tz).date() == report_date
    ]

    if not convs:
        return 0

    # Mark abandoned (24hr no reply)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    for c in convs:
        if c.first_staff_reply_at is None and c.first_guest_message_at < cutoff and c.status == "open":
            c.is_unanswered = True
            c.status = "abandoned"

    responded = [c for c in convs if c.first_staff_reply_at is not None]
    unanswered = [c for c in convs if c.first_staff_reply_at is None]
    after_hours = [c for c in convs if c.is_after_hours]
    ah_unanswered = [c for c in convs if c.is_after_hours and c.first_staff_reply_at is None]
    booking_intent = [c for c in convs if c.is_booking_intent]

    rt_values = [float(c.response_time_minutes) for c in responded if c.response_time_minutes]
    ah_rt = [float(c.response_time_minutes) for c in responded if c.is_after_hours and c.response_time_minutes]

    avg_rt = sum(rt_values) / len(rt_values) if rt_values else None
    avg_bh_rt_vals = [float(c.response_time_minutes) for c in responded if not c.is_after_hours and c.response_time_minutes]
    avg_bh_rt = sum(avg_bh_rt_vals) / len(avg_bh_rt_vals) if avg_bh_rt_vals else None
    avg_ah_rt = sum(ah_rt) / len(ah_rt) if ah_rt else None

    # Revenue calculations
    prop_adr = float(prop.adr or 230.0)
    prop_nights = float(prop.avg_stay_nights or 1.0)
    bi_unanswered = [c for c in ah_unanswered if c.is_booking_intent]
    slow_resp = [c for c in responded if c.is_booking_intent and c.response_time_minutes and float(c.response_time_minutes) > 240]

    rev_at_risk = len(bi_unanswered) * prop_adr * prop_nights * 0.20
    rev_conservative = rev_at_risk * 0.60
    ota_equiv = rev_conservative * 0.18
    slow_rev = len(slow_resp) * prop_adr * prop_nights * 0.15
    daily_leakage = rev_conservative + slow_rev

    # Hour-by-hour breakdown
    hour_counts = {str(h): 0 for h in range(24)}
    for c in convs:
        local_hour = c.first_guest_message_at.astimezone(tz).hour
        hour_counts[str(local_hour)] += 1

    peak_hour = int(max(hour_counts, key=lambda h: hour_counts[h])) if convs else None

    schedule = prop.operating_hours or {}
    open_h = 9
    close_h = 18
    ah_hours = {k: v for k, v in hour_counts.items() if not (open_h <= int(k) < close_h)}
    ah_peak = int(max(ah_hours, key=lambda h: ah_hours[h])) if any(v > 0 for v in ah_hours.values()) else None

    # Topics
    all_topics = [c.top_topic for c in convs if c.top_topic]
    unanswered_topics = [c.top_topic for c in ah_unanswered if c.top_topic]
    top_topics = [t for t, _ in Counter(all_topics).most_common(5)]
    top_unanswered = [t for t, _ in Counter(unanswered_topics).most_common(5)]

    langs = Counter(c.language_detected for c in convs if c.language_detected)
    total_lang = sum(langs.values()) or 1
    lang_breakdown = {k: round(v / total_lang, 2) for k, v in langs.items()}

    row_data = dict(
        total_inquiries=len(convs),
        after_hours_inquiries=len(after_hours),
        business_hours_inquiries=len(convs) - len(after_hours),
        booking_intent_inquiries=len(booking_intent),
        group_booking_inquiries=sum(1 for c in convs if c.is_group_booking),
        repeat_guest_contacts=sum(1 for c in convs if c.is_repeat_guest),
        responded_count=len(responded),
        unanswered_count=len(unanswered),
        after_hours_unanswered=len(ah_unanswered),
        after_hours_responded_next_day=sum(
            1 for c in responded if c.is_after_hours and c.response_time_minutes and float(c.response_time_minutes) > 480
        ),
        avg_response_time_minutes=avg_rt,
        avg_response_time_business_hours=avg_bh_rt,
        avg_response_time_after_hours=avg_ah_rt,
        response_time_over_1hr=sum(1 for t in rt_values if t > 60),
        response_time_over_4hr=sum(1 for t in rt_values if t > 240),
        response_time_over_8hr=sum(1 for t in rt_values if t > 480),
        response_time_over_24hr=sum(1 for t in rt_values if t > 1440),
        revenue_at_risk_total=rev_at_risk,
        revenue_at_risk_conservative=rev_conservative,
        ota_commission_equivalent=ota_equiv,
        slow_response_revenue_at_risk=slow_rev,
        daily_revenue_leakage=daily_leakage,
        peak_inquiry_hour=peak_hour,
        after_hours_peak_hour=ah_peak,
        inquiries_by_hour=hour_counts,
        top_inquiry_topics=top_topics,
        top_unanswered_topics=top_unanswered,
        booking_intent_rate=round(len(booking_intent) / len(convs), 4) if convs else 0,
        language_breakdown=lang_breakdown,
        computed_at=datetime.utcnow(),
    )

    existing = await db.scalar(
        select(ShadowPilotAnalyticsDaily).where(
            ShadowPilotAnalyticsDaily.property_id == prop.id,
            ShadowPilotAnalyticsDaily.report_date == report_date,
        )
    )
    if existing:
        for k, v in row_data.items():
            setattr(existing, k, v)
    else:
        db.add(ShadowPilotAnalyticsDaily(property_id=prop.id, report_date=report_date, **row_data))

    await db.commit()
    return len(convs)
