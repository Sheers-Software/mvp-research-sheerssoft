#!/usr/bin/env python3
"""
Standalone migration runner — applies all incremental DDL to Supabase.

Designed to run as a Cloud Build step using DATABASE_URL secret.
Uses asyncpg directly (bypassing SQLAlchemy) with statement_cache_size=0
to work properly with Supabase PgBouncer in transaction mode.

Usage:
    python migrate.py
"""
import asyncio
import asyncpg
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# All DDL migrations in order — IDEMPOTENT (safe to re-run)
MIGRATIONS = [
    (
        "tenants_stripe_columns",
        """
        ALTER TABLE tenants
            ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255),
            ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR(255),
            ADD COLUMN IF NOT EXISTS assigned_account_manager VARCHAR(255),
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS pilot_start_date TIMESTAMPTZ,
            ADD COLUMN IF NOT EXISTS pilot_end_date TIMESTAMPTZ;
        """,
    ),
    (
        "users_last_login",
        """
        ALTER TABLE users
            ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ;
        """,
    ),
    (
        "tenant_memberships_property_ids",
        """
        ALTER TABLE tenant_memberships
            ADD COLUMN IF NOT EXISTS accessible_property_ids JSONB;
        """,
    ),
    (
        "properties_shadow_pilot",
        """
        ALTER TABLE properties
            ADD COLUMN IF NOT EXISTS audit_only_mode BOOLEAN NOT NULL DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS shadow_pilot_start_date TIMESTAMPTZ,
            ADD COLUMN IF NOT EXISTS shadow_pilot_phone VARCHAR(20);
        """,
    ),
    (
        "create_announcements",
        """
        CREATE TABLE IF NOT EXISTS announcements (
            id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            type             VARCHAR(20) NOT NULL,
            status           VARCHAR(20) NOT NULL DEFAULT 'draft',
            title            VARCHAR(255) NOT NULL,
            body             TEXT NOT NULL,
            target_type      VARCHAR(20) NOT NULL DEFAULT 'all',
            target_tier      VARCHAR(20),
            target_tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
            scheduled_at     TIMESTAMPTZ,
            resolved_at      TIMESTAMPTZ,
            send_email       BOOLEAN NOT NULL DEFAULT FALSE,
            created_by       UUID REFERENCES users(id),
            created_at       TIMESTAMPTZ DEFAULT NOW(),
            updated_at       TIMESTAMPTZ DEFAULT NOW()
        );
        """,
    ),
    (
        "create_audit_records",
        """
        CREATE TABLE IF NOT EXISTS audit_records (
            id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            hotel_name             VARCHAR(255),
            contact_name           VARCHAR(255),
            email                  VARCHAR(255),
            phone                  VARCHAR(30),
            room_count             INTEGER NOT NULL,
            adr                    NUMERIC(10,2) NOT NULL,
            daily_msgs             NUMERIC(8,1) NOT NULL,
            front_desk_close       VARCHAR(10) NOT NULL DEFAULT '22:00',
            ota_commission_rate    NUMERIC(5,2) NOT NULL DEFAULT 18.0,
            revenue_lost_monthly   NUMERIC(12,2) NOT NULL,
            ota_commission_monthly NUMERIC(12,2) NOT NULL,
            total_monthly_leakage  NUMERIC(12,2) NOT NULL,
            annual_leakage         NUMERIC(12,2) NOT NULL,
            conservative_annual    NUMERIC(12,2) NOT NULL,
            roi_multiple           NUMERIC(8,1) NOT NULL,
            source                 VARCHAR(20) NOT NULL DEFAULT 'web',
            status                 VARCHAR(20) NOT NULL DEFAULT 'submitted',
            notes                  TEXT,
            created_at             TIMESTAMPTZ DEFAULT NOW(),
            updated_at             TIMESTAMPTZ DEFAULT NOW()
        );
        """,
    ),
    (
        "audit_records_disable_rls",
        "ALTER TABLE audit_records DISABLE ROW LEVEL SECURITY;",
    ),
]


async def run_migrations():
    # Prefer DATABASE_URL_ADMIN (postgres superuser) if available,
    # fall back to DATABASE_URL (nocturn_app — requires prior GRANT)
    db_url = os.environ.get("DATABASE_URL_ADMIN") or os.environ.get("DATABASE_URL", "")

    if not db_url:
        # Try fetching from GCP Secret Manager via the app's config
        try:
            from app.config import get_settings
            db_url = get_settings().database_url
        except Exception as e:
            log.error("Cannot determine DATABASE_URL: %s", e)
            sys.exit(1)

    # Strip asyncpg driver prefix if present
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://").strip().lstrip("\ufeff")

    log.info("Connecting to database (PgBouncer-safe mode)…")
    try:
        conn = await asyncpg.connect(db_url, statement_cache_size=0, timeout=15)
    except Exception as e:
        log.error("Connection failed: %s", e)
        sys.exit(1)

    passed, failed, skipped = 0, 0, 0
    for name, sql in MIGRATIONS:
        try:
            await conn.execute(sql.strip())
            log.info("  ✓ %s", name)
            passed += 1
        except asyncpg.InsufficientPrivilegeError as e:
            log.warning("  ⚠ %s — permission denied (run as postgres once manually): %s", name, e)
            skipped += 1
        except Exception as e:
            log.error("  ✗ %s — %s", name, e)
            failed += 1

    await conn.close()

    log.info("\nMigration summary: %d passed, %d skipped (permissions), %d failed", passed, skipped, failed)

    if failed > 0:
        log.error("Migration had failures — aborting deploy")
        sys.exit(1)

    log.info("All migrations complete ✓")


if __name__ == "__main__":
    asyncio.run(run_migrations())
