"""
Daily Report generation and scheduling.
Handles generating the email body and sending it to property stakeholders.
"""

import asyncio
import json
import re
from datetime import datetime, timedelta, date, timezone
from decimal import Decimal

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, func, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import async_session
from app.models import Property, AnalyticsDaily, Lead, Conversation, Message, OnboardingProgress
from app.services.analytics import compute_all_properties_daily, compute_daily_analytics
from app.services.email import send_email

settings = get_settings()
logger = structlog.get_logger()

scheduler = AsyncIOScheduler()


async def _get_queued_leads(
    db: AsyncSession,
    property_id,
    report_date: date,
    limit: int = 5,
) -> list[dict]:
    """Fetch uncontacted leads captured on report_date for the GM leads queue."""
    day_start = datetime.combine(report_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    day_end = datetime.combine(report_date + timedelta(days=1), datetime.min.time()).replace(tzinfo=timezone.utc)

    result = await db.execute(
        select(Lead)
        .where(
            Lead.property_id == property_id,
            Lead.captured_at >= day_start,
            Lead.captured_at < day_end,
            Lead.status.in_(["new", "contacted"]),
            Lead.deleted_at.is_(None),
        )
        .order_by(Lead.priority.desc(), Lead.captured_at.asc())
        .limit(limit)
    )
    leads = result.scalars().all()

    _CHANNEL_LABELS = {
        "whatsapp": "WhatsApp",
        "email": "Email",
        "web": "Web Chat",
        "facebook": "Facebook",
        "instagram": "Instagram",
    }
    _INTENT_LABELS = {
        "room_booking": "Room Booking",
        "event": "Event / Conference",
        "fb_inquiry": "F&B Inquiry",
        "general": "General Inquiry",
    }

    return [
        {
            "name": lead.guest_name or "Unknown Guest",
            "channel": _CHANNEL_LABELS.get(lead.source_channel or "", lead.source_channel or "—"),
            "description": lead.notes or _INTENT_LABELS.get(lead.intent, lead.intent or "Inquiry"),
            "estimated_value": float(lead.estimated_value) if lead.estimated_value else 0.0,
            "priority": lead.priority or "standard",
        }
        for lead in leads
    ]


async def _compute_daily_sentiment(
    db: AsyncSession,
    property_id,
    report_date: date,
) -> tuple[int, str]:
    """
    Compute guest sentiment score (0-100%) and a brief summary for the report date.
    Uses Gemini when available; falls back to a metric-based heuristic.
    Returns (sentiment_pct, summary_text).
    """
    day_start = datetime.combine(report_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    day_end = datetime.combine(report_date + timedelta(days=1), datetime.min.time()).replace(tzinfo=timezone.utc)

    conv_result = await db.execute(
        select(Conversation.id, Conversation.status).where(
            Conversation.property_id == property_id,
            Conversation.started_at >= day_start,
            Conversation.started_at < day_end,
        )
    )
    rows = conv_result.fetchall()
    conversation_ids = [r[0] for r in rows]
    statuses = [r[1] for r in rows]

    if not conversation_ids:
        return 0, "No guest conversations were recorded for this period."

    # Heuristic: conversations resolved without needing human handoff = satisfied guests
    non_handoff = sum(1 for s in statuses if s != "handed_off")
    heuristic_score = min(99, int((non_handoff / max(1, len(statuses))) * 100))
    fallback_summary = (
        "Most guests received answers without requiring staff escalation. "
        "No unusual complaint patterns detected."
    )

    if not settings.gemini_api_key:
        return heuristic_score, fallback_summary

    try:
        from google import genai as _genai
        from google.genai import types as _gtypes

        gemini = _genai.Client(api_key=settings.gemini_api_key)

        msg_result = await db.execute(
            select(Message.content).where(
                Message.conversation_id.in_(conversation_ids[:30]),
                Message.role == "guest",
                Message.deleted_at.is_(None),
            ).limit(50)
        )
        guest_msgs = [r[0] for r in msg_result.fetchall()]

        if not guest_msgs or len(" ".join(guest_msgs).split()) < 15:
            return heuristic_score, fallback_summary

        transcript = "\n".join(f"- {m[:120]}" for m in guest_msgs[:40])
        prompt = (
            'Analyze these hotel guest messages and respond with JSON only:\n'
            '{"sentiment_score": <integer 0-100>, '
            '"summary": "<1-2 sentence summary of guest mood and top topics discussed>"}\n\n'
            f'Guest messages:\n{transcript}'
        )

        response = await gemini.aio.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=_gtypes.GenerateContentConfig(temperature=0.2),
        )
        text = (response.text or "").strip()
        match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            score = max(0, min(100, int(data.get("sentiment_score", heuristic_score))))
            summary = str(data.get("summary", fallback_summary)).strip()
            return score, summary or fallback_summary

    except Exception as exc:
        logger.warning("Daily sentiment compute failed, using heuristic", error=str(exc))

    return heuristic_score, fallback_summary


def _format_daily_report_email(
    prop: Property,
    stats: AnalyticsDaily,
    queued_leads: list[dict],
    sentiment_score: int,
    sentiment_summary: str,
) -> str:
    """Generate the Daily GM Report HTML email matching the product's 9 AM briefing promise."""

    ota_pct = float(prop.ota_commission_pct)
    revenue_val = float(stats.estimated_revenue_recovered)
    ota_saved_val = revenue_val * (ota_pct / 100)
    revenue_fmt = f"RM {revenue_val:,.0f}"
    ota_saved_fmt = f"RM {ota_saved_val:,.0f}"

    missed = max(0, stats.after_hours_inquiries - stats.after_hours_responded)
    # Handoffs = AI intentionally escalated — not "dropped", so dropped = 0
    dropped = 0

    # ── Leads queue rows ──────────────────────────────────────
    if queued_leads:
        lead_rows = "".join(
            f"""
            <tr style="border-bottom: 1px solid #f1f5f9;">
              <td style="padding: 10px 8px; font-weight: 600; color: #0f172a;">
                {lead['name']}
                {'<span style="background:#fef9c3;color:#92400e;font-size:10px;padding:2px 6px;border-radius:10px;margin-left:6px;font-weight:500;">HIGH VALUE</span>' if lead['priority'] == 'high_value' else ''}
              </td>
              <td style="padding: 10px 8px; color: #475569;">{lead['channel']}</td>
              <td style="padding: 10px 8px; color: #475569; max-width: 180px;">{lead['description'][:80]}</td>
              <td style="padding: 10px 8px; font-weight: 600; color: #0f172a; white-space: nowrap;">
                {'RM {:,.0f}'.format(lead['estimated_value']) if lead['estimated_value'] else '—'}
              </td>
            </tr>"""
            for lead in queued_leads
        )
        leads_section = f"""
        <div style="margin-bottom: 28px;">
          <h3 style="font-size: 15px; font-weight: 700; color: #0f172a; margin: 0 0 4px;">
            &#128205; Leads Queue
          </h3>
          <p style="font-size: 13px; color: #64748b; margin: 0 0 12px;">
            Review and follow up before noon — each lead is a booking in progress.
          </p>
          <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
            <thead>
              <tr style="background: #f8fafc; border-bottom: 2px solid #e2e8f0;">
                <th style="padding: 8px; text-align: left; color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">Guest</th>
                <th style="padding: 8px; text-align: left; color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">Channel</th>
                <th style="padding: 8px; text-align: left; color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">Request</th>
                <th style="padding: 8px; text-align: left; color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">Est. Value</th>
              </tr>
            </thead>
            <tbody>{lead_rows}</tbody>
          </table>
        </div>"""
    else:
        leads_section = """
        <div style="margin-bottom: 28px; background: #f8fafc; border-radius: 8px; padding: 16px; text-align: center; color: #64748b; font-size: 13px;">
          No new leads captured yesterday. The AI is listening 24/7 — check back tomorrow.
        </div>"""

    # ── Action required banner (if handoffs pending) ──────────
    action_banner = ""
    if stats.handoffs > 0:
        action_banner = f"""
        <div style="background: #fef2f2; border-left: 4px solid #ef4444; border-radius: 0 6px 6px 0; padding: 14px 16px; margin-bottom: 24px;">
          <strong style="color: #b91c1c;">&#9888;&#65039; Action Required:</strong>
          <span style="color: #7f1d1d;">
            {stats.handoffs} conversation{'s' if stats.handoffs != 1 else ''} {'are' if stats.handoffs != 1 else 'is'} waiting for staff attention.
            <a href="{settings.frontend_url}/dashboard" style="color: #b91c1c; font-weight: 600;">Open Dashboard &rarr;</a>
          </span>
        </div>"""

    # ── Channel breakdown rows ─────────────────────────────────
    breakdown = stats.channel_breakdown or {}
    channel_rows = "".join(
        f'<li style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #f1f5f9;font-size:13px;color:#475569;">'
        f'<span>{label}</span><strong style="color:#0f172a;">{breakdown.get(key, 0)}</strong></li>'
        for key, label in [("whatsapp", "WhatsApp"), ("web", "Web Chat"), ("email", "Email"),
                            ("facebook", "Facebook"), ("instagram", "Instagram")]
        if breakdown.get(key, 0) > 0
    ) or '<li style="padding:7px 0;font-size:13px;color:#94a3b8;">No channel data available</li>'

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1e293b;">
  <div style="max-width:620px;margin:24px auto;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

    <!-- Header -->
    <div style="background:#0f172a;padding:24px 28px;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
          <div style="font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Daily GM Report</div>
          <h1 style="margin:0;font-size:20px;color:#ffffff;font-weight:700;">{prop.name}</h1>
          <p style="margin:4px 0 0;font-size:13px;color:#94a3b8;">{stats.report_date.strftime('%A, %d %B %Y')} &nbsp;&middot;&nbsp; Your 9 AM Revenue Briefing</p>
        </div>
        <div style="text-align:right;">
          <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;">Nocturn AI</div>
          <div style="font-size:11px;color:#475569;">by SheersSoft</div>
        </div>
      </div>
    </div>

    <!-- 4 KPI cards -->
    <div style="background:#ffffff;padding:24px 28px 16px;border-bottom:1px solid #e2e8f0;">
      <table style="width:100%;border-collapse:collapse;">
        <tr>
          <td style="width:25%;padding:0 8px 0 0;vertical-align:top;">
            <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:14px 12px;text-align:center;">
              <div style="font-size:22px;font-weight:800;color:#15803d;">{revenue_fmt}</div>
              <div style="font-size:11px;font-weight:700;color:#166534;text-transform:uppercase;letter-spacing:0.5px;margin:4px 0 2px;">Revenue Recovered</div>
              <div style="font-size:11px;color:#16a34a;">{stats.leads_captured} lead{'s' if stats.leads_captured != 1 else ''} captured</div>
            </div>
          </td>
          <td style="width:25%;padding:0 8px;vertical-align:top;">
            <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:14px 12px;text-align:center;">
              <div style="font-size:22px;font-weight:800;color:#1d4ed8;">{ota_saved_fmt}</div>
              <div style="font-size:11px;font-weight:700;color:#1e40af;text-transform:uppercase;letter-spacing:0.5px;margin:4px 0 2px;">OTA Fees Saved</div>
              <div style="font-size:11px;color:#3b82f6;">vs. {ota_pct:.0f}% commission route</div>
            </div>
          </td>
          <td style="width:25%;padding:0 8px;vertical-align:top;">
            <div style="background:#fafafa;border:1px solid #e2e8f0;border-radius:10px;padding:14px 12px;text-align:center;">
              <div style="font-size:22px;font-weight:800;color:#0f172a;">{stats.total_inquiries}</div>
              <div style="font-size:11px;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.5px;margin:4px 0 2px;">Inquiries Handled</div>
              <div style="font-size:11px;color:#94a3b8;">{missed} missed &nbsp;&middot;&nbsp; {dropped} dropped</div>
            </div>
          </td>
          <td style="width:25%;padding:0 0 0 8px;vertical-align:top;">
            <div style="background:#fdf4ff;border:1px solid #e9d5ff;border-radius:10px;padding:14px 12px;text-align:center;">
              <div style="font-size:22px;font-weight:800;color:#7e22ce;">{sentiment_score}%</div>
              <div style="font-size:11px;font-weight:700;color:#6b21a8;text-transform:uppercase;letter-spacing:0.5px;margin:4px 0 2px;">Guest Sentiment</div>
              <div style="font-size:11px;color:#a855f7;">positive interactions</div>
            </div>
          </td>
        </tr>
      </table>
    </div>

    <!-- Body -->
    <div style="background:#ffffff;padding:24px 28px;">

      {action_banner}

      {leads_section}

      <!-- Guest Sentiment Summary -->
      <div style="margin-bottom:28px;">
        <h3 style="font-size:15px;font-weight:700;color:#0f172a;margin:0 0 8px;">&#129488; Guest Sentiment Summary</h3>
        <div style="background:#fdf4ff;border-left:4px solid #a855f7;border-radius:0 8px 8px 0;padding:14px 16px;font-size:13px;color:#3b0764;line-height:1.6;">
          {sentiment_summary}
        </div>
      </div>

      <!-- Channel Breakdown -->
      <div style="margin-bottom:24px;">
        <h3 style="font-size:15px;font-weight:700;color:#0f172a;margin:0 0 8px;">&#128202; Channel Breakdown</h3>
        <ul style="list-style:none;padding:0;margin:0;">{channel_rows}</ul>
      </div>

      <!-- CTA -->
      <div style="text-align:center;padding-top:8px;">
        <a href="{settings.frontend_url}/dashboard"
           style="display:inline-block;background:#0f172a;color:#ffffff;padding:13px 28px;text-decoration:none;border-radius:8px;font-weight:700;font-size:14px;">
          View Full Dashboard &rarr;
        </a>
      </div>

    </div>

    <!-- Footer -->
    <div style="background:#f8fafc;padding:16px 28px;border-top:1px solid #e2e8f0;text-align:center;font-size:11px;color:#94a3b8;">
      Generated by Nocturn AI Engine &nbsp;&middot;&nbsp; {prop.name} &nbsp;&middot;&nbsp;
      <a href="{settings.frontend_url}/dashboard" style="color:#94a3b8;">Manage notifications</a>
    </div>

  </div>
</body>
</html>"""
    return html


async def run_daily_reports(report_date: date | None = None):
    """
    Cron job: Generate and send the Daily GM Report for all active properties.
    Sent each morning at 9:00 AM MYT covering the previous day's activity.
    Includes: revenue recovered, OTA fees saved, inquiries handled, guest sentiment,
    queued leads table, and a Gemini-generated sentiment summary.
    """
    from app.database import async_session as _async_session
    from app.services.system_config import is_job_enabled as _is_job_enabled
    async with _async_session() as _db:
        if not await _is_job_enabled("daily_report", _db):
            logger.info("daily_report skipped — disabled via system config")
            return

    if report_date is None:
        report_date = date.today() - timedelta(days=1)

    logger.info("Starting daily GM report generation", report_date=report_date)

    async with async_session() as db:
        # Compute analytics for all properties
        analytics_records = await compute_all_properties_daily(db, report_date)

        for stats in analytics_records:
            res = await db.execute(select(Property).where(Property.id == stats.property_id))
            prop = res.scalar_one_or_none()
            if prop is None or not prop.is_active or prop.deleted_at is not None:
                continue

            # Gather leads queue and sentiment in parallel
            queued_leads, (sentiment_score, sentiment_summary) = await asyncio.gather(
                _get_queued_leads(db, prop.id, report_date),
                _compute_daily_sentiment(db, prop.id, report_date),
            )

            email_body = _format_daily_report_email(
                prop, stats, queued_leads, sentiment_score, sentiment_summary
            )
            subject = f"GM Report: {prop.name} — {report_date.strftime('%d %b %Y')}"

            recipient = prop.notification_email or settings.staff_notification_email
            if not recipient:
                logger.warning("daily_report: no recipient configured", property_id=str(prop.id))
                continue

            await send_email(
                to_email=recipient,
                subject=subject,
                content=email_body,
                is_html=True,
            )

            # Mark first_morning_report_sent milestone on OnboardingProgress
            try:
                op_res = await db.execute(
                    select(OnboardingProgress).where(
                        OnboardingProgress.property_id == prop.id,
                        OnboardingProgress.first_morning_report_sent.is_(False),
                    )
                )
                onboarding = op_res.scalar_one_or_none()
                if onboarding:
                    onboarding.first_morning_report_sent = True
                    await db.flush()
            except Exception as e:
                logger.warning("Could not mark first_morning_report_sent", error=str(e))

            logger.info(
                "Daily GM report sent",
                property=prop.name,
                recipient=recipient,
                leads_in_queue=len(queued_leads),
                sentiment_score=sentiment_score,
            )

        await db.commit()


async def delete_old_leads(db: AsyncSession = None):
    """
    Weekly job: Delete leads and conversations older than 90 days.
    Complies with PDPA/GDPR data retention policies and fits Supabase 500MB free tier limits.
    """
    from app.database import async_session
    from app.models import Lead, Conversation
    from sqlalchemy import delete

    # 90 days retention for Free Tier
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
    logger.info("Running data retention cleanup", cutoff_date=cutoff_date)

    async with async_session() as session:
        try:
            # 1. Delete old leads
            result_leads = await session.execute(
                delete(Lead).where(Lead.captured_at < cutoff_date)
            )
            deleted_leads = result_leads.rowcount

            # 2. Delete old conversations (cascades to messages)
            # define where clause for conversations
            result_convs = await session.execute(
                delete(Conversation).where(Conversation.started_at < cutoff_date)
            )
            deleted_convs = result_convs.rowcount

            await session.commit()
            logger.info(
                "Data retention cleanup complete",
                deleted_leads=deleted_leads,
                deleted_conversations=deleted_convs
            )

        except Exception as e:
            logger.error("Data retention job failed", error=str(e))
            await session.rollback()


async def process_automated_follow_ups(db: AsyncSession = None):
    """
    Hourly job: Check for active conversations that need 24h/72h/7d follow-ups.
    """
    from app.database import async_session, set_db_context
    from app.models import Conversation, Property
    from app.services.conversation import process_guest_message
    from app.services.whatsapp import send_whatsapp_message
    from app.services.twilio_whatsapp import send_twilio_message
    from app.services.email import send_email
    from app.services.system_config import is_job_enabled as _is_job_enabled

    async with async_session() as _db:
        if not await _is_job_enabled("followups", _db):
            logger.info("followups skipped — disabled via system config")
            return

    logger.info("Running automated follow-ups job")

    async with async_session() as session:
        try:
            now = datetime.now(timezone.utc)

            # Fetch all active conversations that haven't exhausted follow-ups
            result = await session.execute(
                select(Conversation, Property)
                .join(Property, Conversation.property_id == Property.id)
                .where(
                    Conversation.status == "active",
                    Conversation.follow_up_stage < 3
                )
            )

            pairs = result.all()

            for conv, prop in pairs:
                if not conv.last_interaction_at:
                    continue

                age_hours = (now - conv.last_interaction_at).total_seconds() / 3600.0

                target_stage = None
                if conv.follow_up_stage == 0 and age_hours >= 24:
                    target_stage = 1
                elif conv.follow_up_stage == 1 and age_hours >= 72:
                    target_stage = 2
                elif conv.follow_up_stage == 2 and age_hours >= 168:
                    target_stage = 3

                if target_stage:
                    try:
                        # Ensure RLS context is set for the tenant if needed
                        await set_db_context(session, str(prop.id))

                        conv.follow_up_stage = target_stage

                        # Process system triggered follow up
                        response = await process_guest_message(
                            db=session,
                            property_id=prop.id,
                            guest_identifier=conv.guest_identifier,
                            channel=conv.channel,
                            message_text="",  # System triggered
                            guest_name=conv.guest_name,
                            is_follow_up=True
                        )

                        await session.commit()

                        reply_text = response["response"]

                        # Deliver via correct channel integration
                        if conv.channel == "whatsapp":
                            if prop.whatsapp_provider == "twilio":
                                await send_twilio_message(
                                    to_number=conv.guest_identifier,
                                    message_text=reply_text,
                                    from_number=prop.twilio_phone_number
                                )
                            else:
                                await send_whatsapp_message(
                                    to_number=conv.guest_identifier,
                                    message_text=reply_text
                                )
                        elif conv.channel == "email":
                            await send_email(
                                to_email=conv.guest_identifier,
                                subject="Following up on your inquiry",
                                content=reply_text,
                                hotel_name=prop.name
                            )

                        logger.info("Sent follow-up", conversation_id=str(conv.id), stage=target_stage)

                    except Exception as e:
                        logger.error("Failed to send follow up", conversation_id=str(conv.id), error=str(e))
                        await session.rollback()

        except Exception as e:
            logger.error("Follow-up job failed", error=str(e))


async def generate_monthly_insights(db: AsyncSession = None):
    """
    Monthly job (1st of month): generate guest insight reports.
    """
    from app.database import async_session, set_db_context
    from app.models import Property
    from app.services.system_config import is_job_enabled as _is_job_enabled

    async with async_session() as _db:
        if not await _is_job_enabled("insights", _db):
            logger.info("insights skipped — disabled via system config")
            return
    from app.services.insights import compute_monthly_insights
    from app.services.email import send_email

    logger.info("Running monthly insights job")
    async with async_session() as session:
        try:
            # Get all properties
            result = await session.execute(select(Property))
            properties = result.scalars().all()

            for prop in properties:
                report_md = await compute_monthly_insights(session, prop.id, days_back=30)
                if not report_md:
                    continue

                # Simple HTML formatting
                html_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
                    <h2>&#128161; 30-Day Guest Insights: {prop.name}</h2>
                    <p>Here is your monthly intelligence report summarizing guest conversations:</p>
                    <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0;">
                        {report_md.replace(chr(10), '<br>')}
                    </div>
                </body>
                </html>
                """

                recipient = prop.notification_email or settings.staff_notification_email
                await send_email(
                    to_email=recipient,
                    subject=f"&#128161; Monthly Guest Insights: {prop.name}",
                    content=html_body,
                    is_html=True
                )
                logger.info("Sent monthly insights report", property_id=str(prop.id))
        except Exception as e:
            logger.error("Monthly insights job failed", error=str(e))


async def run_weekly_audit_report():
    """
    Weekly job (Monday 08:00 MYT) for shadow pilot properties.

    For each property with audit_only_mode=True, counts after-hours inquiries
    from the past 7 days and sends the GM a plain-language email:
    "Your hotel received X after-hours inquiries last week. Based on your ADR
    of RM Y, you left approximately RM Z on the table."

    This is the core value-delivery mechanism for Stage 2 of the sales funnel —
    the GM sees their own real data before we ask them to commit to Stage 3.
    """
    from sqlalchemy import select
    from app.models import Property, Conversation
    from app.database import async_session

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    async with async_session() as db:
        try:
            result = await db.execute(
                select(Property).where(
                    Property.audit_only_mode.is_(True),
                    Property.is_active.is_(True),
                    Property.deleted_at.is_(None),
                )
            )
            shadow_properties = result.scalars().all()

            if not shadow_properties:
                logger.info("weekly_audit_report: no shadow pilot properties found")
                return

            for prop in shadow_properties:
                try:
                    # Count after-hours conversations in the past 7 days
                    conv_result = await db.execute(
                        select(func.count()).where(
                            Conversation.property_id == prop.id,
                            Conversation.is_after_hours.is_(True),
                            Conversation.created_at >= week_ago,
                        )
                    )
                    after_hours_count = conv_result.scalar() or 0

                    # Count total conversations
                    total_result = await db.execute(
                        select(func.count()).where(
                            Conversation.property_id == prop.id,
                            Conversation.created_at >= week_ago,
                        )
                    )
                    total_count = total_result.scalar() or 0

                    # Revenue estimate: conservative (60% after-hours share × 20% conversion
                    # × ADR × 2 nights avg stay × 60% conservative discount)
                    adr = float(prop.adr) if prop.adr else 230.0
                    lost_bookings = after_hours_count * 0.20
                    revenue_estimate = lost_bookings * adr * 2.0 * 0.60

                    # Days since shadow pilot started (for context)
                    days_running = 7
                    if prop.shadow_pilot_start_date:
                        delta = datetime.now(timezone.utc) - prop.shadow_pilot_start_date.replace(
                            tzinfo=timezone.utc if prop.shadow_pilot_start_date.tzinfo is None else None
                        ) if prop.shadow_pilot_start_date.tzinfo is None else datetime.now(timezone.utc) - prop.shadow_pilot_start_date
                        days_running = max(1, min(delta.days, 7))

                    shadow_phone = prop.shadow_pilot_phone or "the test number"

                    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">

  <div style="background:#0f172a; color:white; padding:24px; border-radius:8px 8px 0 0; text-align:center;">
    <h2 style="margin:0;">Weekly Shadow Pilot Report</h2>
    <p style="margin:6px 0 0; opacity:0.75;">{prop.name} — Last 7 Days</p>
  </div>

  <div style="background:#f8fafc; border:1px solid #e2e8f0; border-top:0; padding:24px; border-radius:0 0 8px 8px;">

    <p style="font-size:16px;">
      Your hotel received <strong>{after_hours_count} after-hours {'inquiry' if after_hours_count == 1 else 'inquiries'}</strong>
      ({total_count} total) via {shadow_phone} over the past {days_running} days.
    </p>

    <div style="background:#fef9c3; border-left:4px solid #eab308; padding:16px; border-radius:4px; margin:16px 0;">
      <p style="margin:0; font-size:15px;">
        Based on your ADR of <strong>RM {adr:,.0f}</strong>, you left approximately
        <strong>RM {revenue_estimate:,.0f}</strong> on the table this week.
      </p>
      <p style="margin:8px 0 0; font-size:13px; color:#713f12;">
        (Conservative estimate: 20% inquiry-to-booking rate × 2-night avg stay × 60% confidence discount)
      </p>
    </div>

    <p>
      These are real guest inquiries that arrived when your front desk was unavailable.
      Each one was a potential booking that went unanswered.
    </p>

    <p style="color:#64748b; font-size:13px;">
      This shadow pilot runs silently — your guests on the main number are unaffected.
      When you're ready to turn on the AI and start capturing these bookings automatically,
      reply to this email or contact your account manager.
    </p>

  </div>

  <p style="text-align:center; color:#94a3b8; font-size:12px; margin-top:16px;">
    Nocturn AI by SheersSoft · Unsubscribe by replying STOP
  </p>

</body>
</html>"""

                    recipient = prop.notification_email or settings.staff_notification_email
                    if not recipient:
                        logger.warning("weekly_audit_report: no recipient for property", property_id=str(prop.id))
                        continue

                    await send_email(
                        to_email=recipient,
                        subject=f"📊 Shadow Pilot Week {days_running}d: {after_hours_count} after-hours inquiries — {prop.name}",
                        content=html_body,
                        is_html=True,
                    )
                    logger.info(
                        "weekly_audit_report sent",
                        property_id=str(prop.id),
                        property_name=prop.name,
                        after_hours_count=after_hours_count,
                        revenue_estimate=revenue_estimate,
                    )

                except Exception as e:
                    logger.error(
                        "weekly_audit_report: failed for property",
                        property_id=str(prop.id),
                        error=str(e),
                    )

        except Exception as e:
            logger.error("weekly_audit_report job failed", error=str(e))


async def start_scheduler():
    """Initialize and start the scheduler."""
    # Schedule daily GM report at configured time (default 9:00 AM MYT)
    trigger = CronTrigger(
        hour=settings.daily_report_hour,
        minute=settings.daily_report_minute,
        timezone=settings.timezone
    )

    scheduler.add_job(
        run_daily_reports,
        trigger=trigger,
        id="daily_reports",
        replace_existing=True
    )

    # Schedule data retention cleanup (Weekly on Sunday at 3am)
    scheduler.add_job(
        delete_old_leads,
        trigger=CronTrigger(day_of_week="sun", hour=3, minute=0, timezone=settings.timezone),
        id="data_retention",
        replace_existing=True
    )

    # Schedule automated follow ups (Hourly)
    scheduler.add_job(
        process_automated_follow_ups,
        trigger=CronTrigger(minute=0, timezone=settings.timezone),
        id="automated_follow_ups",
        replace_existing=True
    )

    # Schedule monthly guest insights (1st of month at 8:00 AM)
    scheduler.add_job(
        generate_monthly_insights,
        trigger=CronTrigger(day=1, hour=8, minute=0, timezone=settings.timezone),
        id="monthly_insights",
        replace_existing=True
    )

    # Schedule weekly audit report for shadow pilot properties (Monday 08:00 MYT)
    scheduler.add_job(
        run_weekly_audit_report,
        trigger=CronTrigger(day_of_week="mon", hour=8, minute=0, timezone=settings.timezone),
        id="weekly_audit_report",
        replace_existing=True
    )

    scheduler.start()
    logger.info(
        "Scheduler started",
        daily_report_time=f"{settings.daily_report_hour}:{settings.daily_report_minute:02d} {settings.timezone}"
    )

async def shutdown_scheduler():
    """Shutdown the scheduler."""
    scheduler.shutdown()
    logger.info("Scheduler shutdown")
