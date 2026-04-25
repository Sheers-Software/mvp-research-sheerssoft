"""
Nocturn AI Inquiry Capture & Conversion Engine
Main FastAPI application.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.config import get_settings

settings = get_settings()

from app.routes import router
from app.websockets import router as ws_router
from app.services.scheduler import start_scheduler, shutdown_scheduler
from app.limiter import limiter

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info(
        "Starting SheersSoft AI Engine",
        environment=settings.environment,
    )

    # Ensure pgvector extension and system_config table exist
    from app.database import engine, async_session
    from sqlalchemy import text

    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        logger.info("pgvector extension ready")

    # Create tables if they don't exist (for development/demo)
    if not settings.is_production:
        from app.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created (dev/demo mode)")
    else:
        # In production, only ensure system_config table exists (no full create_all)
        from app.services.system_config import ensure_system_config_table
        try:
            async with engine.begin() as conn:
                await ensure_system_config_table(conn)
        except Exception as sc_err:
            logger.warning("system_config table setup skipped", error=str(sc_err))

    # Apply incremental column migrations (idempotent — safe on every startup).
    # Each is wrapped in try/except because the production connecting role (nocturn_app via PgBouncer)
    # may lack DDL ownership. If they silently fail, the dedicated `migrate.py` step in Cloud Build
    # is responsible for logging the failures. If they already exist, it is harmless.
    
    migrations = [
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
            """
        ),
        (
            "users_last_login",
            """
            ALTER TABLE users
                ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ;
            """
        ),
        (
            "tenant_memberships_property_ids",
            """
            ALTER TABLE tenant_memberships
                ADD COLUMN IF NOT EXISTS accessible_property_ids JSONB;
            """
        ),
        (
            "properties_shadow_pilot",
            """
            ALTER TABLE properties
                ADD COLUMN IF NOT EXISTS audit_only_mode BOOLEAN NOT NULL DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS shadow_pilot_start_date TIMESTAMPTZ,
                ADD COLUMN IF NOT EXISTS shadow_pilot_phone VARCHAR(20);
            """
        ),
        (
            "properties_shadow_pilot_v2",
            """
            ALTER TABLE properties
                ADD COLUMN IF NOT EXISTS shadow_pilot_mode BOOLEAN NOT NULL DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS shadow_pilot_session_active BOOLEAN NOT NULL DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS shadow_pilot_session_last_seen TIMESTAMPTZ,
                ADD COLUMN IF NOT EXISTS shadow_pilot_dashboard_token TEXT,
                ADD COLUMN IF NOT EXISTS shadow_pilot_dashboard_token_expires TIMESTAMPTZ,
                ADD COLUMN IF NOT EXISTS avg_stay_nights NUMERIC(5,2) NOT NULL DEFAULT 1.0;
            UPDATE properties SET shadow_pilot_mode = audit_only_mode WHERE audit_only_mode = TRUE AND shadow_pilot_mode = FALSE;
            """
        ),
        (
            "create_shadow_pilot_conversations",
            """
            CREATE TABLE IF NOT EXISTS shadow_pilot_conversations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
                guest_phone_encrypted TEXT NOT NULL,
                guest_phone_hash VARCHAR(64) NOT NULL,
                guest_name VARCHAR(255),
                first_guest_message_at TIMESTAMPTZ NOT NULL,
                last_guest_message_at TIMESTAMPTZ NOT NULL,
                first_staff_reply_at TIMESTAMPTZ,
                last_staff_reply_at TIMESTAMPTZ,
                response_time_minutes NUMERIC(10,2),
                is_after_hours BOOLEAN NOT NULL DEFAULT FALSE,
                is_unanswered BOOLEAN NOT NULL DEFAULT FALSE,
                is_booking_intent BOOLEAN NOT NULL DEFAULT FALSE,
                is_group_booking BOOLEAN NOT NULL DEFAULT FALSE,
                is_repeat_guest BOOLEAN NOT NULL DEFAULT FALSE,
                intent VARCHAR(50),
                intent_confidence NUMERIC(5,4),
                top_topic VARCHAR(100),
                message_count_guest INTEGER NOT NULL DEFAULT 1,
                message_count_staff INTEGER NOT NULL DEFAULT 0,
                language_detected VARCHAR(20),
                estimated_value_rm NUMERIC(10,2),
                status VARCHAR(20) NOT NULL DEFAULT 'open',
                first_guest_message_preview VARCHAR(500),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_spc_property_id ON shadow_pilot_conversations(property_id);
            CREATE INDEX IF NOT EXISTS idx_spc_first_message ON shadow_pilot_conversations(first_guest_message_at);
            CREATE INDEX IF NOT EXISTS idx_spc_property_after_hours ON shadow_pilot_conversations(property_id, is_after_hours);
            CREATE INDEX IF NOT EXISTS idx_spc_property_unanswered ON shadow_pilot_conversations(property_id, is_unanswered);
            CREATE INDEX IF NOT EXISTS idx_spc_phone_hash ON shadow_pilot_conversations(property_id, guest_phone_hash);
            """
        ),
        (
            "create_shadow_pilot_analytics_daily",
            """
            CREATE TABLE IF NOT EXISTS shadow_pilot_analytics_daily (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
                report_date DATE NOT NULL,
                total_inquiries INTEGER NOT NULL DEFAULT 0,
                after_hours_inquiries INTEGER NOT NULL DEFAULT 0,
                business_hours_inquiries INTEGER NOT NULL DEFAULT 0,
                booking_intent_inquiries INTEGER NOT NULL DEFAULT 0,
                group_booking_inquiries INTEGER NOT NULL DEFAULT 0,
                repeat_guest_contacts INTEGER NOT NULL DEFAULT 0,
                responded_count INTEGER NOT NULL DEFAULT 0,
                unanswered_count INTEGER NOT NULL DEFAULT 0,
                after_hours_unanswered INTEGER NOT NULL DEFAULT 0,
                after_hours_responded_next_day INTEGER NOT NULL DEFAULT 0,
                avg_response_time_minutes NUMERIC(10,2),
                avg_response_time_business_hours NUMERIC(10,2),
                avg_response_time_after_hours NUMERIC(10,2),
                response_time_over_1hr INTEGER NOT NULL DEFAULT 0,
                response_time_over_4hr INTEGER NOT NULL DEFAULT 0,
                response_time_over_8hr INTEGER NOT NULL DEFAULT 0,
                response_time_over_24hr INTEGER NOT NULL DEFAULT 0,
                revenue_at_risk_total NUMERIC(12,2) NOT NULL DEFAULT 0,
                revenue_at_risk_conservative NUMERIC(12,2) NOT NULL DEFAULT 0,
                ota_commission_equivalent NUMERIC(12,2) NOT NULL DEFAULT 0,
                slow_response_revenue_at_risk NUMERIC(12,2) NOT NULL DEFAULT 0,
                daily_revenue_leakage NUMERIC(12,2) NOT NULL DEFAULT 0,
                peak_inquiry_hour INTEGER,
                after_hours_peak_hour INTEGER,
                inquiries_by_hour JSONB,
                inquiries_by_day_of_week JSONB,
                top_inquiry_topics JSONB,
                top_unanswered_topics JSONB,
                booking_intent_rate NUMERIC(5,4),
                language_breakdown JSONB,
                computed_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(property_id, report_date)
            );
            CREATE INDEX IF NOT EXISTS idx_spad_property_date ON shadow_pilot_analytics_daily(property_id, report_date);
            """
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
            """
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
            """
        ),
        (
            "audit_records_disable_rls",
            "ALTER TABLE audit_records DISABLE ROW LEVEL SECURITY;"
        )
    ]

    for name, sql in migrations:
        try:
            async with engine.begin() as conn:
                await conn.execute(text(sql))
        except Exception as e:
            logger.debug(f"Incremental DDL skipped [{name}]: schema already up to date or insufficient privileges", error=str(e))
    
    logger.info("Incremental column migrations sweep completed")

    # Seed default scheduler config (no-op if already seeded)
    from app.services.system_config import seed_default_config
    try:
        async with async_session() as db:
            await seed_default_config(db)
    except Exception as seed_err:
        logger.warning("Scheduler config seed skipped", error=str(seed_err))

    # Start APScheduler only in dev/demo — production uses Cloud Scheduler
    # calling /api/v1/internal/* endpoints (CPU-throttled Cloud Run).
    if not settings.is_production:
        await start_scheduler()

    yield

    if not settings.is_production:
        await shutdown_scheduler()
    logger.info("Shutting down SheersSoft AI Engine")


app = FastAPI(
    title="Nocturn AI — Inquiry Capture & Conversion Engine",
    description="AI-powered hotel inquiry capture and conversion system by SheersSoft",
    version="0.5.4",
    dependencies=[],
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Ensure ALL unhandled exceptions return JSON (not Starlette's plain-text "Internal Server Error")
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", path=str(request.url), error=str(exc), exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

from app.middleware import TelemetryMiddleware, MaintenanceModeMiddleware
app.add_middleware(TelemetryMiddleware)
app.add_middleware(MaintenanceModeMiddleware)

# CORS — allow all origins in dev, restrict in production
if settings.is_production:
    origins = settings.allowed_origins.split(",")
else:
    # In development, list explicit localhost ports to allow credentials
    origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "*" # Allow generic for now to support file:// or random test origins
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)
app.include_router(ws_router)

# Mount static files (for widget.js) - Pointing to sibling frontend directory
import os
frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend/public")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
else:
    logger.warning("Frontend public directory not found, static files disabled", path=frontend_path)


@app.get("/")
async def root():
    return {
        "name": "Nocturn AI — Inquiry Capture & Conversion Engine",
        "version": "0.2.0",
        "status": "running",
    }
