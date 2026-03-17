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

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.services.scheduler import (
    delete_old_leads,
    generate_monthly_insights,
    process_automated_follow_ups,
    run_daily_reports,
)
from app.services.system_config import is_job_enabled

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
