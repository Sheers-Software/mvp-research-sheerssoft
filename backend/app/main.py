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
        async with engine.begin() as conn:
            await ensure_system_config_table(conn)

    # Apply incremental column migrations (safe to run on every startup)
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
        logger.info("Incremental column migrations applied")

    # Seed default scheduler config (no-op if already seeded)
    from app.services.system_config import seed_default_config
    async with async_session() as db:
        await seed_default_config(db)

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
    version="0.3.0",
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
