import asyncio
from app.database import engine
from app.models import Base
from sqlalchemy import text
import structlog

logger = structlog.get_logger()

async def reset_database():
    """Drops all tables and recreates them from models.py."""
    print("Dropping all tables...")
    async with engine.begin() as conn:
        # Drop all tables, cascade to dependencies
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    
    print("Recreating tables from models...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database reset complete.")

if __name__ == "__main__":
    asyncio.run(reset_database())
