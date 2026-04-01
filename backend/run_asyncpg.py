import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

import asyncpg
from app.config import get_settings

async def main():
    settings = get_settings()
    poolUrl = settings.database_url.replace("+asyncpg", "")
    print(f"Connecting to {poolUrl.split('@')[1]}...")
    try:
        conn = await asyncpg.connect(poolUrl, statement_cache_size=0)
        await conn.execute("""
            ALTER TABLE properties
                ADD COLUMN IF NOT EXISTS audit_only_mode BOOLEAN NOT NULL DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS shadow_pilot_start_date TIMESTAMPTZ,
                ADD COLUMN IF NOT EXISTS shadow_pilot_phone VARCHAR(20);
        """)
        print("Successfully added columns!")
        await conn.close()
    except Exception as e:
        print(f"FAILED to add columns: {e}")

if __name__ == "__main__":
    asyncio.run(main())
