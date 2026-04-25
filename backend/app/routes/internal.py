"""
Internal scheduler endpoints — called by Cloud Scheduler (GCP) in production.

These replace APScheduler cron jobs so Cloud Run can run with CPU-throttled
mode (no always-on CPU cost). Each endpoint is protected by a shared secret
header: X-Internal-Secret.

Cloud Scheduler job targets:
  POST /api/v1/internal/run-daily-report    (daily 07:30 Asia/Kuala_Lumpur)
  POST /api/v1/internal/run-followups       (hourly)
  POST /api/v1/internal/run-insights        (1st of month 08:00)
  POST /api/v1/internal/cleanup-leads       (weekly Sunday 03:00)
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.services.scheduler import (
    delete_old_leads,
    generate_monthly_insights,
    process_automated_follow_ups,
    run_daily_reports,
    run_weekly_audit_report,
)
from app.services.system_config import is_job_enabled
from app.services.shadow_pilot_processor import handle_message_received, handle_message_sent
from app.services.shadow_pilot_aggregator import run_daily_aggregation
from app.services.shadow_pilot_reporter import run_shadow_pilot_weekly_reports

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/internal")
settings = get_settings()


def _verify(x_internal_secret: str | None):
    expected = settings.internal_scheduler_secret
    if not expected:
        raise HTTPException(status_code=503, detail="Internal scheduler secret not configured")
    if x_internal_secret != expected:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/run-daily-report", include_in_schema=False)
async def run_daily_report(
    x_internal_secret: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Triggered by Cloud Scheduler — runs daily analytics + email report."""
    _verify(x_internal_secret)
    if not await is_job_enabled("daily_report", db):
        logger.info("daily_report job skipped — disabled via system config")
        return {"status": "skipped", "reason": "disabled"}
    try:
        await run_daily_reports()
        return {"status": "ok", "job": "daily_reports"}
    except Exception as exc:
        logger.error("Daily report job failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/run-followups", include_in_schema=False)
async def run_followups(
    x_internal_secret: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Triggered by Cloud Scheduler — processes automated lead follow-up emails."""
    _verify(x_internal_secret)
    if not await is_job_enabled("followups", db):
        logger.info("followups job skipped — disabled via system config")
        return {"status": "skipped", "reason": "disabled"}
    try:
        await process_automated_follow_ups()
        return {"status": "ok", "job": "automated_follow_ups"}
    except Exception as exc:
        logger.error("Follow-up job failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/run-insights", include_in_schema=False)
async def run_insights(
    x_internal_secret: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Triggered by Cloud Scheduler — generates monthly guest insights report."""
    _verify(x_internal_secret)
    if not await is_job_enabled("insights", db):
        logger.info("insights job skipped — disabled via system config")
        return {"status": "skipped", "reason": "disabled"}
    try:
        await generate_monthly_insights()
        return {"status": "ok", "job": "monthly_insights"}
    except Exception as exc:
        logger.error("Insights job failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/run-weekly-audit-report", include_in_schema=False)
async def run_weekly_audit_report_endpoint(
    x_internal_secret: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Triggered by Cloud Scheduler — sends weekly shadow pilot audit emails."""
    _verify(x_internal_secret)
    if not await is_job_enabled("weekly_audit_report", db):
        logger.info("weekly_audit_report job skipped — disabled via system config")
        return {"status": "skipped", "reason": "disabled"}
    try:
        await run_weekly_audit_report()
        return {"status": "ok", "job": "weekly_audit_report"}
    except Exception as exc:
        logger.error("Weekly audit report job failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/cleanup-leads", include_in_schema=False)
async def cleanup_leads(
    x_internal_secret: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Triggered by Cloud Scheduler — removes leads past data retention window."""
    _verify(x_internal_secret)
    if not await is_job_enabled("cleanup", db):
        logger.info("cleanup job skipped — disabled via system config")
        return {"status": "skipped", "reason": "disabled"}
    try:
        await delete_old_leads()
        return {"status": "ok", "job": "data_retention"}
    except Exception as exc:
        logger.error("Cleanup job failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ─────────────────────────────────────────────────────────────
# Shadow Pilot Bridge Endpoints
# ─────────────────────────────────────────────────────────────


class ShadowEventPayload(BaseModel):
    event_type: str  # "message.received" | "message.sent"
    property_slug: str
    sender_jid: str
    message_id: str
    content_preview: Optional[str] = None
    timestamp_unix: int
    has_media: bool = False


class ShadowSessionStatusPayload(BaseModel):
    property_slug: str
    status: str
    qr_base64: Optional[str] = None


class ShadowHeartbeatPayload(BaseModel):
    property_slug: str


@router.post("/shadow-event", include_in_schema=False)
async def shadow_event_endpoint(
    payload: ShadowEventPayload,
    x_internal_secret: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Receives message events from Baileys bridge."""
    _verify(x_internal_secret)
    if payload.event_type == "message.received":
        await handle_message_received(
            db=db,
            property_slug=payload.property_slug,
            sender_jid=payload.sender_jid,
            message_id=payload.message_id,
            content_preview=payload.content_preview,
            timestamp_ms=payload.timestamp_unix,
            has_media=payload.has_media,
        )
    elif payload.event_type == "message.sent":
        await handle_message_sent(
            db=db,
            property_slug=payload.property_slug,
            recipient_jid=payload.sender_jid,
            message_id=payload.message_id,
            timestamp_ms=payload.timestamp_unix,
        )
    return {"status": "ok"}


@router.post("/shadow-session-status", include_in_schema=False)
async def shadow_session_status(
    payload: ShadowSessionStatusPayload,
    x_internal_secret: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Updates Baileys session connection status for a property."""
    _verify(x_internal_secret)
    from app.models import Property
    prop = await db.scalar(select(Property).where(Property.slug == payload.property_slug))
    if prop:
        prop.shadow_pilot_session_active = (payload.status == "connected")
        prop.shadow_pilot_session_last_seen = datetime.now(timezone.utc)
        await db.commit()
    return {"status": "ok"}


@router.post("/shadow-heartbeat", include_in_schema=False)
async def shadow_heartbeat(
    payload: ShadowHeartbeatPayload,
    x_internal_secret: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Receives periodic heartbeat from Baileys bridge to confirm session is alive."""
    _verify(x_internal_secret)
    from app.models import Property
    prop = await db.scalar(select(Property).where(Property.slug == payload.property_slug))
    if prop:
        prop.shadow_pilot_session_last_seen = datetime.now(timezone.utc)
        await db.commit()
    return {"status": "ok"}


@router.get("/shadow-active-properties", include_in_schema=False)
async def shadow_active_properties(
    x_internal_secret: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Returns all properties currently in shadow_pilot_mode for bridge discovery."""
    _verify(x_internal_secret)
    from app.models import Property
    props = list(await db.scalars(
        select(Property).where(Property.shadow_pilot_mode == True)
    ))
    return {
        "properties": [
            {"slug": p.slug, "shadow_pilot_phone": p.shadow_pilot_phone}
            for p in props if p.slug
        ]
    }


@router.post("/run-shadow-pilot-aggregation", include_in_schema=False)
async def run_shadow_pilot_aggregation(
    x_internal_secret: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Triggered by Cloud Scheduler — aggregates daily shadow pilot conversation metrics."""
    _verify(x_internal_secret)
    try:
        result = await run_daily_aggregation(db)
        return {"status": "ok", "job": "shadow_pilot_aggregation", "result": result}
    except Exception as exc:
        logger.error("Shadow pilot aggregation failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/run-shadow-pilot-weekly-report", include_in_schema=False)
async def run_shadow_pilot_weekly_report(
    x_internal_secret: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Triggered by Cloud Scheduler — sends weekly shadow pilot reports to GMs."""
    _verify(x_internal_secret)
    try:
        result = await run_shadow_pilot_weekly_reports(db)
        return {"status": "ok", "job": "shadow_pilot_weekly_report", "result": result}
    except Exception as exc:
        logger.error("Shadow pilot weekly report failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
