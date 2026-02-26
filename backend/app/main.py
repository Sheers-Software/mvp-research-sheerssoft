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

    # Ensure pgvector extension exists on startup
    from app.database import engine
    from sqlalchemy import text

    async with engine.begin() as conn:
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            logger.info("pgvector extension ready")
        except Exception:
            # Race condition: another worker already created it — safe to ignore
            logger.info("pgvector extension already exists (concurrent worker)")

    # Create tables if they don't exist (for development)
    if not settings.is_production:
        from app.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created (dev mode)")

    # Start scheduler
    await start_scheduler()

    yield

    # Shutdown scheduler
    await shutdown_scheduler()
    logger.info("Shutting down SheersSoft AI Engine")


app = FastAPI(
    title="SheersSoft AI Inquiry Capture Engine",
    description="AI-powered hotel inquiry capture and conversion system",
    version="0.1.0",
    dependencies=[],
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from app.middleware import TelemetryMiddleware
app.add_middleware(TelemetryMiddleware)

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
        "name": "SheersSoft AI Inquiry Capture Engine",
        "version": "0.1.0",
        "status": "running",
    }
