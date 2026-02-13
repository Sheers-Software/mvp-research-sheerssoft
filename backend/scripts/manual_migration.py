import asyncio
from sqlalchemy import text
from app.database import engine

async def upgrade_db():
    async with engine.begin() as conn:
        print("Adding columns...")
        try:
            await conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'standard'"))
            await conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS flag_reason VARCHAR(255)"))
            await conn.execute(text("ALTER TABLE properties ADD COLUMN IF NOT EXISTS conversion_rate NUMERIC(5,2) DEFAULT 0.20"))
            print("Columns added successfully.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(upgrade_db())
