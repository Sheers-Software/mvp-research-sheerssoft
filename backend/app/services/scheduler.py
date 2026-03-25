"""
Daily Report generation and scheduling.
Handles generating the email body and sending it to property stakeholders.
"""

import asyncio
from datetime import datetime, timedelta, date, timezone
from decimal import Decimal

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, func, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import async_session
from app.models import Property, AnalyticsDaily
from app.services.analytics import compute_all_properties_daily, compute_daily_analytics
from app.services.email import send_email

settings = get_settings()
logger = structlog.get_logger()

scheduler = AsyncIOScheduler()


def _format_daily_report_email(prop: Property, stats: AnalyticsDaily) -> str:
    """Generate HTML email body for the daily report."""
    
    # Format currency
    revenue = f"RM {stats.estimated_revenue_recovered:,.2f}"
    commission_saved = f"RM {stats.estimated_revenue_recovered * (prop.ota_commission_pct / 100):,.2f}"
    
    # Calculate response rate
    response_rate = 0
    if stats.after_hours_inquiries > 0:
        response_rate = (stats.after_hours_responded / stats.after_hours_inquiries) * 100
    
    # Simple HTML template
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #0f172a; color: white; padding: 20px; text-align: center;">
                <h2 style="margin: 0;">{prop.name}</h2>
                <p style="margin: 5px 0 0; opacity: 0.8;">Daily Intelligence Report • {stats.report_date.strftime('%A, %d %b %Y')}</p>
            </div>
            
            <div style="padding: 20px;">
                {(lambda: f'''
                <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin-bottom: 20px;">
                    <h3 style="margin: 0 0 5px; color: #b91c1c;">&#9888; Action Required</h3>
                    <p style="margin: 0; color: #7f1d1d;">
                        You have <strong>{stats.handoffs} conversation(s)</strong> waiting for staff attention.
                    </p>
                </div>
                ''' if stats.handoffs > 0 else "")()}

                <div style="background-color: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 15px; margin-bottom: 20px;">
                    <h3 style="margin: 0 0 10px; color: #0369a1;">&#128176; Revenue Recovered</h3>
                    <div style="display: flex; justify-content: space-between; align-items: baseline;">
                        <span style="font-size: 24px; font-weight: bold; color: #0f172a;">{revenue}</span>
                        <span style="font-size: 14px; color: #64748b;">Est. Value (After Hours)</span>
                    </div>
                    <div style="margin-top: 5px; font-size: 13px; color: #0369a1;">
                        Saved approx. <strong>{commission_saved}</strong> in OTA commissions
                    </div>
                    <div style="margin-top: 5px; font-size: 11px; color: #64748b;">
                        *Estimated based on 20% lead-to-booking conversion rate
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #0f172a;">{stats.after_hours_inquiries}</div>
                        <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">After-Hours Inquiries</div>
                    </div>
                    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #0f172a;">{int(response_rate)}%</div>
                        <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Auto-Response Rate</div>
                    </div>
                    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #0f172a;">{stats.leads_captured}</div>
                        <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Leads Captured</div>
                    </div>
                    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #0f172a;">{stats.handoffs}</div>
                        <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Staff Handoffs</div>
                    </div>
                </div>

                <h3 style="border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; font-size: 16px;">&#128202; Channel Breakdown</h3>
                <ul style="list-style: none; padding: 0;">
                    <li style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f5f9;">
                        <span>WhatsApp</span>
                        <strong>{stats.channel_breakdown.get('whatsapp', 0)}</strong>
                    </li>
                    <li style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f5f9;">
                        <span>Web Chat</span>
                        <strong>{stats.channel_breakdown.get('web', 0)}</strong>
                    </li>
                    <li style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f5f9;">
                        <span>Email</span>
                        <strong>{stats.channel_breakdown.get('email', 0)}</strong>
                    </li>
                </ul>

                <div style="margin-top: 30px; text-align: center;">
                    <a href="{settings.website_url if hasattr(settings, 'website_url') else '#'}" style="background-color: #0f172a; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">View Full Dashboard</a>
                </div>
            </div>
            
            <div style="background-color: #f8fafc; padding: 15px; text-align: center; font-size: 12px; color: #94a3b8;">
                <p>Generated by Nocturn AI Engine for {prop.name}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


async def run_daily_reports(report_date: date | None = None):
    """
    Cron job: Generate and send daily reports for all properties.
    Default: run for yesterday.
    """
    from app.database import async_session as _async_session
    from app.services.system_config import is_job_enabled as _is_job_enabled
    async with _async_session() as _db:
        if not await _is_job_enabled("daily_report", _db):
            logger.info("daily_report skipped — disabled via system config")
            return

    if report_date is None:
        report_date = date.today() - timedelta(days=1)

    logger.info("Starting daily report generation", report_date=report_date)
    
    async with async_session() as db:
        # Compute analytics
        analytics_records = await compute_all_properties_daily(db, report_date)
        
        # Send emails
        for stats in analytics_records:
            # Re-fetch property to get name/details (optimization: could be joined in analytics query)
            from sqlalchemy import select
            res = await db.execute(select(Property).where(Property.id == stats.property_id))
            prop = res.scalar_one()
            
            # Generate email
            email_body = _format_daily_report_email(prop, stats)
            subject = f"&#128202; Daily Intelligence: {prop.name} - {report_date.strftime('%d %b %Y')}"
            
            # Send to property notification email (if configured) or staff email
            recipient = prop.notification_email or settings.staff_notification_email
            
            await send_email(
                to_email=recipient,
                subject=subject,
                content=email_body,
                is_html=True
            )
            
            logger.info("Daily report sent", property=prop.name, recipient=recipient)
            

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
    # Schedule daily report at configured time (default 7:30 AM)
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
