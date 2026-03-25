"""
Async SQLAlchemy database engine and session management.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=not settings.is_production,
    pool_size=2,       # Reduced to fit Supabase free tier connection limits (60 max direct)
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections every 5 minutes to play nice with PgBouncer
    connect_args={"statement_cache_size": 0},  # Required for Supabase PgBouncer transaction mode
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Alias for background tasks that need standalone sessions
async_session_factory = async_session

from sqlalchemy import text


async def set_db_context(session: AsyncSession, property_id: str):
    """Sets the RLS context for the current session."""
    await session.execute(
        text(f"select set_config('app.current_property_id', '{property_id}', false)")
    )


async def get_db() -> AsyncSession:
    """FastAPI dependency that provides a database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
