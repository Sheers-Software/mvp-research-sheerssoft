"""
Shadow Pilot Weekly Report — Rollup computation and email delivery.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, timezone, timedelta
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.models import Property, ShadowPilotAnalyticsDaily, ShadowPilotConversation
from app.services.email import send_email

logger = structlog.get_logger()

NOCTURN_ANNUAL_COST = 999 + 199 * 12  # Setup + 12 months subscription


@dataclass
class ShadowPilotWeeklyRollup:
    property_id: uuid.UUID
    property_name: str
    gm_email: str
    period_start: date
    period_end: date
    days_observed: int
    total_inquiries: int
    after_hours_inquiries: int
    booking_intent_inquiries: int
    responded_count: int
    unanswered_count: int
    after_hours_unanswered: int
    avg_response_time_minutes: float
    avg_response_time_after_hours: float
    response_time_over_4hr: int
    response_time_over_24hr: int
    weekly_revenue_leakage: float
    ota_commission_equivalent: float
    annualised_revenue_leakage: float
    nocturn_year_1_net_recovery: float
    peak_inquiry_hour: int
    top_inquiry_topics: list
    top_unanswered_topics: list
    inquiries_by_hour_aggregate: dict
    sample_abandoned_conversations: list
    dashboard_token: Optional[str] = None
    dashboard_url: Optional[str] = None


async def compute_weekly_rollup(
    db: AsyncSession,
    prop: Property,
    report_end: date,
) -> ShadowPilotWeeklyRollup:
    period_start = report_end - timedelta(days=6)

    rows = list(await db.scalars(
        select(ShadowPilotAnalyticsDaily).where(
            ShadowPilotAnalyticsDaily.property_id == prop.id,
            ShadowPilotAnalyticsDaily.report_date >= period_start,
            ShadowPilotAnalyticsDaily.report_date <= report_end,
        ).order_by(ShadowPilotAnalyticsDaily.report_date)
    ))

    def s(attr, default=0):
        return sum(getattr(r, attr) or default for r in rows)

    def avg(attr):
        vals = [float(getattr(r, attr)) for r in rows if getattr(r, attr) is not None]
        return sum(vals) / len(vals) if vals else 0.0

    total = s("total_inquiries")
    unanswered = s("unanswered_count")
    ah_unanswered = s("after_hours_unanswered")
    weekly_leakage = s("daily_revenue_leakage")
    ota_equiv = s("ota_commission_equivalent")
    annualised = weekly_leakage * 52
    net_recovery = max(0.0, annualised * 0.60 - NOCTURN_ANNUAL_COST)

    # Aggregate hour chart
    hour_agg = {str(h): 0 for h in range(24)}
    for r in rows:
        if r.inquiries_by_hour:
            for h, cnt in r.inquiries_by_hour.items():
                hour_agg[str(h)] = hour_agg.get(str(h), 0) + cnt

    peak_hour = int(max(hour_agg, key=lambda h: hour_agg[h])) if rows else 0

    # Topics from most recent non-empty row
    all_topics: list = []
    unanswered_topics: list = []
    for r in reversed(rows):
        if r.top_inquiry_topics:
            all_topics = r.top_inquiry_topics
            break
    for r in reversed(rows):
        if r.top_unanswered_topics:
            unanswered_topics = r.top_unanswered_topics
            break

    # Sample abandoned conversations
    samples = list(await db.scalars(
        select(ShadowPilotConversation).where(
            ShadowPilotConversation.property_id == prop.id,
            ShadowPilotConversation.is_after_hours == True,
            ShadowPilotConversation.status == "abandoned",
            ShadowPilotConversation.first_guest_message_at >= datetime.combine(
                period_start, datetime.min.time()
            ).replace(tzinfo=timezone.utc),
        ).order_by(ShadowPilotConversation.estimated_value_rm.desc().nullslast()).limit(5)
    ))

    sample_convs = []
    for c in samples:
        sample_convs.append({
            "time_received": c.first_guest_message_at.strftime("%I:%M %p"),
            "topic": c.top_topic or "General inquiry",
            "intent": c.intent or "general",
            "estimated_value_rm": float(c.estimated_value_rm or 0),
            "preview": (c.first_guest_message_preview or "")[:100],
            "response": "Never" if c.status == "abandoned" else "Delayed",
        })

    gm_email = prop.notification_email or ""

    # Dashboard token/URL
    token = prop.shadow_pilot_dashboard_token
    from app.config import get_settings
    settings = get_settings()
    dashboard_url = f"{settings.frontend_url}/shadow/{prop.slug}?token={token}" if token else None

    return ShadowPilotWeeklyRollup(
        property_id=prop.id,
        property_name=prop.name,
        gm_email=gm_email,
        period_start=period_start,
        period_end=report_end,
        days_observed=len(rows),
        total_inquiries=total,
        after_hours_inquiries=s("after_hours_inquiries"),
        booking_intent_inquiries=s("booking_intent_inquiries"),
        responded_count=s("responded_count"),
        unanswered_count=unanswered,
        after_hours_unanswered=ah_unanswered,
        avg_response_time_minutes=avg("avg_response_time_minutes"),
        avg_response_time_after_hours=avg("avg_response_time_after_hours"),
        response_time_over_4hr=s("response_time_over_4hr"),
        response_time_over_24hr=s("response_time_over_24hr"),
        weekly_revenue_leakage=weekly_leakage,
        ota_commission_equivalent=ota_equiv,
        annualised_revenue_leakage=annualised,
        nocturn_year_1_net_recovery=net_recovery,
        peak_inquiry_hour=peak_hour,
        top_inquiry_topics=all_topics,
        top_unanswered_topics=unanswered_topics,
        inquiries_by_hour_aggregate=hour_agg,
        sample_abandoned_conversations=sample_convs,
        dashboard_token=token,
        dashboard_url=dashboard_url,
    )


async def send_weekly_report_email(prop: Property, rollup: ShadowPilotWeeklyRollup) -> bool:
    if not rollup.gm_email:
        logger.warning("shadow_report_no_email", property=prop.name)
        return False

    subject = f"{prop.name}: You left RM {rollup.weekly_revenue_leakage:,.0f} on the table this week. Here's the proof."

    # Audit vs observed comparison line
    estimated_rm = float(prop.audit_estimated_monthly_leakage_rm or 0)
    observed_7d_rm = float(rollup.weekly_revenue_leakage)
    observed_monthly_projection = observed_7d_rm * (30 / 7)

    if estimated_rm > 0:
        variance_pct = ((observed_monthly_projection - estimated_rm) / estimated_rm) * 100
        if abs(variance_pct) < 5:
            comparison_line = f"Your pre-pilot estimate was RM {estimated_rm:,.0f}/month — your real data confirms this."
        elif observed_monthly_projection > estimated_rm:
            comparison_line = (
                f"You estimated RM {estimated_rm:,.0f}/month at risk on the calculator. "
                f"Your 7-day data projects RM {observed_monthly_projection:,.0f}/month — "
                f"you were underestimating by {variance_pct:.0f}%."
            )
        else:
            comparison_line = (
                f"You estimated RM {estimated_rm:,.0f}/month at risk. "
                f"Your 7-day data projects RM {observed_monthly_projection:,.0f}/month — "
                f"this is your confirmed minimum recoverable amount."
            )
    else:
        comparison_line = None

    # Build 24-hour bar chart HTML
    max_count = max(rollup.inquiries_by_hour_aggregate.values()) or 1
    bars_html = ""
    for h in range(24):
        cnt = rollup.inquiries_by_hour_aggregate.get(str(h), 0)
        pct = int((cnt / max_count) * 100)
        is_ah = h < 9 or h >= 18
        color = "#E24B4A" if is_ah else "#1D9E75"
        bars_html += (
            f'<div style="display:inline-block;width:3.5%;margin:0 0.2%;vertical-align:bottom;">'
            f'<div style="height:{pct}px;background:{color};min-height:2px;"></div>'
            f'<div style="font-size:9px;color:#888;text-align:center;">{h}</div></div>'
        )

    # Sample conversations HTML
    samples_html = ""
    for sc in rollup.sample_abandoned_conversations[:5]:
        samples_html += (
            f'<tr>'
            f'<td style="padding:8px 12px;font-size:12px;color:#666;">{sc["time_received"]}</td>'
            f'<td style="padding:8px 12px;font-size:12px;">{sc["intent"].replace("_", " ").title()}</td>'
            f'<td style="padding:8px 12px;font-size:12px;color:#888;">"{sc["preview"][:80]}..."</td>'
            f'<td style="padding:8px 12px;font-size:12px;font-weight:600;color:#1D9E75;">RM {sc["estimated_value_rm"]:,.0f}</td>'
            f'<td style="padding:8px 12px;font-size:12px;color:#E24B4A;">{sc["response"]}</td>'
            f'</tr>'
        )

    ah_resp_hrs = round(rollup.avg_response_time_after_hours / 60, 1) if rollup.avg_response_time_after_hours else 0

    dashboard_btn = ""
    if rollup.dashboard_url:
        dashboard_btn = (
            f'<div style="text-align:center;margin:24px 0;">'
            f'<a href="{rollup.dashboard_url}" style="background:#1D9E75;color:white;padding:14px 28px;'
            f'text-decoration:none;border-radius:6px;font-weight:600;font-size:14px;">VIEW YOUR FULL DASHBOARD</a>'
            f'</div>'
        )

    body = f"""
<div style="font-family:-apple-system,sans-serif;color:#1a1a1a;max-width:600px;margin:0 auto;">
  <div style="background:#0e0e10;color:white;padding:24px 28px;border-radius:8px 8px 0 0;">
    <div style="font-size:11px;color:#1D9E75;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;">Nocturn AI · Shadow Pilot Report</div>
    <div style="font-size:22px;font-weight:500;">{prop.name}</div>
    <div style="font-size:13px;color:#888;margin-top:4px;">WhatsApp Performance · {rollup.period_start.strftime('%d %b')} – {rollup.period_end.strftime('%d %b %Y')}</div>
  </div>

  <div style="background:#fff;border:1px solid #e8e8e8;border-top:none;padding:24px 28px;">
    <p style="font-size:14px;line-height:1.6;">This week, your WhatsApp received <strong>{rollup.total_inquiries}</strong> inquiries.</p>
    <p style="font-size:14px;line-height:1.6;">Your team responded to <strong>{rollup.responded_count}</strong> of them.</p>
    <p style="font-size:14px;line-height:1.6;">The other <strong>{rollup.unanswered_count}</strong> went unanswered.</p>

    <div style="background:#FFF5F5;border:1px solid #FFD5D5;border-radius:6px;padding:16px 20px;margin:20px 0;">
      <div style="font-size:11px;color:#888;font-weight:600;text-transform:uppercase;margin-bottom:4px;">Revenue Leaked This Week</div>
      <div style="font-size:28px;font-weight:600;color:#E24B4A;">RM {rollup.weekly_revenue_leakage:,.0f}</div>
      <div style="font-size:11px;color:#888;margin-top:2px;">Conservative estimate — 40% discount applied</div>
    </div>

    {f'<div style="background:#F0F4FF;border:1px solid #C7D3F7;border-radius:6px;padding:14px 18px;margin:16px 0;font-size:13px;color:#1e2d6b;line-height:1.6;">{comparison_line}</div>' if comparison_line else ''}

    <table style="width:100%;border-collapse:collapse;font-size:13px;margin:20px 0;">
      <tr style="background:#f8f8f8;">
        <td style="padding:10px 14px;font-weight:600;border:1px solid #eee;">After-hours inquiries</td>
        <td style="padding:10px 14px;border:1px solid #eee;">{rollup.after_hours_inquiries}</td>
      </tr>
      <tr>
        <td style="padding:10px 14px;font-weight:600;border:1px solid #eee;">After-hours — no response</td>
        <td style="padding:10px 14px;border:1px solid #eee;">{rollup.after_hours_unanswered}</td>
      </tr>
      <tr style="background:#f8f8f8;">
        <td style="padding:10px 14px;font-weight:600;border:1px solid #eee;">Avg after-hours response time</td>
        <td style="padding:10px 14px;border:1px solid #eee;">{ah_resp_hrs} hrs</td>
      </tr>
      <tr>
        <td style="padding:10px 14px;font-weight:600;border:1px solid #eee;">Responses taking >4 hrs</td>
        <td style="padding:10px 14px;border:1px solid #eee;">{rollup.response_time_over_4hr}</td>
      </tr>
    </table>

    <div style="font-size:12px;font-weight:600;color:#555;text-transform:uppercase;margin:20px 0 10px;">When It Happened — Inquiries by Hour</div>
    <div style="padding:8px 0;">{bars_html}</div>

    <div style="font-size:12px;font-weight:600;color:#555;text-transform:uppercase;margin:20px 0 10px;">What They Were Asking (Unanswered)</div>
    <table style="width:100%;border-collapse:collapse;">
      <thead>
        <tr style="background:#f8f8f8;font-size:11px;color:#888;">
          <th style="padding:8px 12px;text-align:left;">Time</th>
          <th style="padding:8px 12px;text-align:left;">Type</th>
          <th style="padding:8px 12px;text-align:left;">Preview</th>
          <th style="padding:8px 12px;text-align:left;">Est. Value</th>
          <th style="padding:8px 12px;text-align:left;">Response</th>
        </tr>
      </thead>
      <tbody>{samples_html}</tbody>
    </table>

    <div style="background:#F0FAF5;border:1px solid #C3E8D9;border-radius:6px;padding:16px 20px;margin:24px 0;">
      <div style="font-size:13px;font-weight:600;color:#0F6E56;margin-bottom:8px;">If Nocturn AI Had Been Active This Week</div>
      <div style="font-size:13px;line-height:1.8;">
        All {rollup.after_hours_inquiries} after-hours inquiries answered instantly<br>
        Response time: under 30 seconds (vs your current {ah_resp_hrs} hrs)<br>
        Est. RM {rollup.weekly_revenue_leakage * 0.6:,.0f} in captured direct bookings<br>
        RM 0 in OTA commissions paid on those bookings<br>
        Your team wakes up to {rollup.unanswered_count} warm leads, not silence
      </div>
    </div>

    <div style="background:#f8f8f8;border-radius:6px;padding:16px 20px;margin:20px 0;">
      <div style="font-size:12px;font-weight:600;text-transform:uppercase;color:#888;margin-bottom:8px;">Projected Annual Impact</div>
      <div style="font-size:13px;line-height:1.8;">
        Weekly leakage x 52 weeks = <strong>RM {rollup.annualised_revenue_leakage:,.0f}</strong><br>
        Nocturn AI annual cost = <strong>RM {NOCTURN_ANNUAL_COST:,}</strong><br>
        Net Year-1 Recovery = <strong style="color:#1D9E75;">RM {rollup.nocturn_year_1_net_recovery:,.0f}</strong>
      </div>
    </div>

    {dashboard_btn}

    <p style="font-size:13px;color:#888;text-align:center;">Or reply to this email to speak with Ahmad Basyir directly.</p>
  </div>

  <div style="background:#f8f8f8;border:1px solid #e8e8e8;border-top:none;padding:12px 28px;border-radius:0 0 8px 8px;">
    <p style="font-size:11px;color:#999;margin:0;">Sheers Software Sdn Bhd · SSM 202501033756</p>
  </div>
</div>"""

    await send_email(
        to_email=rollup.gm_email,
        subject=subject,
        content=body,
        is_html=True,
        hotel_name="Nocturn AI",
    )
    return True


async def run_shadow_pilot_weekly_reports(db: AsyncSession) -> dict:
    """
    Check all shadow pilots and send report when property-relative Day 7 is reached.

    Logic (runs daily via Cloud Scheduler):
    - First report: send once when days_active >= 7 and shadow_pilot_report_sent_at is None.
      Marks shadow_pilot_report_sent_at so subsequent runs skip this property.
    - Subsequent weekly reports: send when days_active is a multiple of 7 AFTER the first
      report was already sent (Day 14, 21, 28...).
    """
    today = datetime.now(timezone.utc).date()
    props = list(await db.scalars(
        select(Property).where(Property.shadow_pilot_mode == True)
    ))
    sent = []
    for prop in props:
        if not prop.shadow_pilot_start_date:
            continue
        days_active = (today - prop.shadow_pilot_start_date.date()).days
        if days_active < 7:
            continue

        is_first_report = prop.shadow_pilot_report_sent_at is None
        is_weekly_followup = (
            not is_first_report
            and days_active > 7
            and days_active % 7 == 0
        )

        if not (is_first_report or is_weekly_followup):
            continue

        rollup = await compute_weekly_rollup(db, prop, today)
        ok = await send_weekly_report_email(prop, rollup)
        if ok:
            sent.append(prop.name)
            await _notify_sheers_am(prop, rollup)
            if is_first_report:
                prop.shadow_pilot_report_sent_at = datetime.now(timezone.utc)
                await db.commit()

    return {"sent_count": len(sent), "properties": sent}


async def _notify_sheers_am(prop: Property, rollup: ShadowPilotWeeklyRollup) -> None:
    """Send internal notification to SheersSoft AM."""
    days_active = (datetime.now(timezone.utc).date() - prop.shadow_pilot_start_date.date()).days
    subject = f"[ACTION] Shadow Pilot Day {days_active}: {prop.name}"
    body = (
        f"Shadow pilot Day {days_active} report sent for <strong>{prop.name}</strong>.<br><br>"
        f"<strong>Call the GM today:</strong> {rollup.gm_email}<br><br>"
        f"Key stats:<br>"
        f"- Unanswered inquiries: {rollup.unanswered_count}<br>"
        f"- After-hours unanswered: {rollup.after_hours_unanswered}<br>"
        f"- Weekly leakage: RM {rollup.weekly_revenue_leakage:,.0f}<br>"
        f"- Annualised leakage: RM {rollup.annualised_revenue_leakage:,.0f}<br><br>"
        f'<em>"You had {rollup.unanswered_count} inquiries you never answered. '
        f'Want to activate Nocturn AI on your number today?"</em>'
    )
    try:
        await send_email(
            to_email="basyir@sheerssoft.com",
            subject=subject,
            content=body,
            is_html=True,
            hotel_name="Nocturn AI System",
        )
    except Exception as e:
        logger.warning("am_notify_failed", error=str(e))
