import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from sqlalchemy import text
from app.database import engine

async def main():
    async with engine.begin() as conn:
        try:
            await conn.execute(text("""
                ALTER TABLE properties
                    ADD COLUMN IF NOT EXISTS audit_only_mode BOOLEAN NOT NULL DEFAULT FALSE,
                    ADD COLUMN IF NOT EXISTS shadow_pilot_start_date TIMESTAMPTZ,
                    ADD COLUMN IF NOT EXISTS shadow_pilot_phone VARCHAR(20);
            """))
            print("Successfully added columns!")
        except Exception as e:
            print(f"FAILED to add columns: {e}")

if __name__ == "__main__":
    asyncio.run(main())
