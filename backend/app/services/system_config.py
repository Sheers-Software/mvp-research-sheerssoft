"""
Platform system configuration service.

Provides scheduler job enable/disable controls stored in the system_config DB table.
Defaults: all notification jobs disabled in demo mode, enabled in production.
"""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

SCHEDULER_JOBS_KEY = "scheduler.jobs"

# Jobs that send notifications/emails — disabled in demo by default
NOTIFICATION_JOBS = ["daily_report", "followups", "insights"]

_DEFAULT_JOBS = {
    "daily_report": True,
    "followups": True,
    "insights": True,
    "cleanup": True,
    "weekly_audit_report": True,
}

_DEMO_DEFAULTS = {
    "daily_report": False,
    "followups": False,
    "insights": False,
    "cleanup": True,
    "weekly_audit_report": False,
}


async def ensure_system_config_table(conn):
    """Create system_config table if it doesn't exist (safe for all environments)."""
    await conn.execute(text("""
        CREATE TABLE IF NOT EXISTS system_config (
            key VARCHAR(255) PRIMARY KEY,
            value JSONB NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
    """))


async def seed_default_config(db: AsyncSession):
    """
    Seed scheduler.jobs config on first startup.
    Only inserts if the key doesn't already exist (never overwrites manual overrides).
    """
    from app.models import SystemConfig

    existing = await db.get(SystemConfig, SCHEDULER_JOBS_KEY)
    if existing is None:
        defaults = _DEMO_DEFAULTS if settings.is_demo else _DEFAULT_JOBS
        db.add(SystemConfig(key=SCHEDULER_JOBS_KEY, value=defaults))
        await db.commit()
        logger.info("Seeded scheduler config", defaults=defaults, environment=settings.environment)


async def get_jobs_config(db: AsyncSession) -> dict:
    """Return the current scheduler job enabled states."""
    from app.models import SystemConfig

    row = await db.get(SystemConfig, SCHEDULER_JOBS_KEY)
    if row:
        return dict(row.value)
    return _DEMO_DEFAULTS.copy() if settings.is_demo else _DEFAULT_JOBS.copy()


async def set_jobs_config(config: dict, db: AsyncSession):
    """Update scheduler job enabled states."""
    from app.models import SystemConfig

    row = await db.get(SystemConfig, SCHEDULER_JOBS_KEY)
    if row:
        row.value = config
        row.updated_at = datetime.now(timezone.utc)
    else:
        db.add(SystemConfig(key=SCHEDULER_JOBS_KEY, value=config))
    await db.commit()


async def is_job_enabled(job_name: str, db: AsyncSession) -> bool:
    """Check if a specific scheduler job is enabled."""
    config = await get_jobs_config(db)
    return bool(config.get(job_name, True))


# ─────────────────────────────────────────────────────────────
# Maintenance Mode
# ─────────────────────────────────────────────────────────────

MAINTENANCE_KEY = "maintenance_mode"

_DEFAULT_MAINTENANCE = {"enabled": False, "message": "", "eta": None}


async def get_maintenance_config(db: AsyncSession) -> dict:
    """Return the current maintenance mode config."""
    from app.models import SystemConfig
    row = await db.get(SystemConfig, MAINTENANCE_KEY)
    if row:
        return dict(row.value)
    return _DEFAULT_MAINTENANCE.copy()


async def set_maintenance_config(config: dict, db: AsyncSession):
    """Update maintenance mode config."""
    from app.models import SystemConfig
    row = await db.get(SystemConfig, MAINTENANCE_KEY)
    if row:
        row.value = config
        row.updated_at = datetime.now(timezone.utc)
    else:
        db.add(SystemConfig(key=MAINTENANCE_KEY, value=config))
    await db.commit()
