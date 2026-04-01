"""
Async SQLAlchemy database engine and session management.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from app.config import get_settings

settings = get_settings()

# NullPool: SQLAlchemy does not maintain its own connection pool.
# Each session opens a fresh connection and closes it on release.
# Supabase's Supavisor (PgBouncer-compatible) handles the actual pooling in
# transaction mode. SQLAlchemy's own pooling + PgBouncer transaction mode causes
# "prepared statement does not exist" errors because named prepared statements
# created on one server connection are not visible on another.
# statement_cache_size=0: disable asyncpg's client-side prepared statement cache
# so queries are sent as simple/unnamed statements instead of named prepared ones.
engine = create_async_engine(
    settings.database_url,
    echo=not settings.is_production,
    poolclass=NullPool,
    connect_args={"statement_cache_size": 0},
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
