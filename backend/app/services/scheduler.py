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
                {(lambda: f"""
                <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin-bottom: 20px;">
                    <h3 style="margin: 0 0 5px; color: #b91c1c;">⚠️ Action Required</h3>
                    <p style="margin: 0; color: #7f1d1d;">
                        You have <strong>{stats.handoffs} conversation(s)</strong> waiting for staff attention.
                    </p>
                </div>
                """ if stats.handoffs > 0 else "")()}

                <div style="background-color: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 15px; margin-bottom: 20px;">
                    <h3 style="margin: 0 0 10px; color: #0369a1;">💰 Revenue Recovered</h3>
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

                <h3 style="border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; font-size: 16px;">📊 Channel Breakdown</h3>
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
            subject = f"📊 Daily Intelligence: {prop.name} - {report_date.strftime('%d %b %Y')}"
            
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
    Weekly job: Delete leads and conversations older than 2 years.
    Complies with PDPA/GDPR data retention policies.
    """
    from app.database import async_session
    from app.models import Lead, Conversation
    from sqlalchemy import delete

    # 2 years retention
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=730)
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
    
    scheduler.start()
    logger.info(
        "Scheduler started", 
        daily_report_time=f"{settings.daily_report_hour}:{settings.daily_report_minute:02d} {settings.timezone}"
    )

async def shutdown_scheduler():
    """Shutdown the scheduler."""
    scheduler.shutdown()
    logger.info("Scheduler shutdown")
