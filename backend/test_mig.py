import asyncio
import os
import sys

# Configure Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import get_settings

async def main():
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        try:
            await conn.execute(text("""
                ALTER TABLE properties
                    ADD COLUMN IF NOT EXISTS audit_only_mode BOOLEAN NOT NULL DEFAULT FALSE,
                    ADD COLUMN IF NOT EXISTS shadow_pilot_start_date TIMESTAMPTZ,
                    ADD COLUMN IF NOT EXISTS shadow_pilot_phone VARCHAR(20);
            """))
            print("SUCCESS")
        except Exception as e:
            print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())
