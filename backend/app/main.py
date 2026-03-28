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
    # Wrapped in try/except: on Supabase the connecting role may not own the
    # tables (ALTER TABLE requires ownership). If the columns already exist
    # (prior run), the failure is harmless and the app continues normally.
    try:
        async with engine.begin() as conn:
            await conn.execute(text("""
                ALTER TABLE tenants
                    ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS assigned_account_manager VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    ADD COLUMN IF NOT EXISTS pilot_start_date TIMESTAMPTZ,
                    ADD COLUMN IF NOT EXISTS pilot_end_date TIMESTAMPTZ;
            """))
            await conn.execute(text("""
                ALTER TABLE users
                    ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ;
            """))
            await conn.execute(text("""
                ALTER TABLE tenant_memberships
                    ADD COLUMN IF NOT EXISTS accessible_property_ids JSONB;
            """))
            await conn.execute(text("""
                ALTER TABLE properties
                    ADD COLUMN IF NOT EXISTS audit_only_mode BOOLEAN NOT NULL DEFAULT FALSE,
                    ADD COLUMN IF NOT EXISTS shadow_pilot_start_date TIMESTAMPTZ,
                    ADD COLUMN IF NOT EXISTS shadow_pilot_phone VARCHAR(20);
            """))
            await conn.execute(text("""
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
            """))
            await conn.execute(text("""
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
            """))
            # audit_records is not property-scoped — disable RLS so the backend
            # service role can INSERT from the unauthenticated public endpoint.
            await conn.execute(text(
                "ALTER TABLE audit_records DISABLE ROW LEVEL SECURITY;"
            ))
            logger.info("Incremental column migrations applied")
    except Exception as migration_err:
        logger.warning(
            "Incremental DDL skipped — schema already up to date or insufficient privileges",
            error=str(migration_err),
        )

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
    version="0.5.1",
    dependencies=[],
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
