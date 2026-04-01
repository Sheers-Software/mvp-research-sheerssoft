import asyncio
import asyncpg
import os
from app.config import get_settings

async def check_db():
    settings = get_settings()
    db_url = settings.database_url
    # Strip asyncpg driver prefix
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    print(f"Connecting to {db_url.split('@')[-1]}...")
    try:
        conn = await asyncpg.connect(db_url)
        rows = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        print("Tables found in 'public' schema:")
        for row in rows:
            print(f" - {row['table_name']}")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
