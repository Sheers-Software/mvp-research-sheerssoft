import asyncio
from datetime import date
from app.database import async_session
from app.services.analytics import compute_all_properties_daily

async def main():
    print("Computing daily analytics for all properties...")
    async with async_session() as db:
        await compute_all_properties_daily(db, date.today())
        await db.commit()
    print("Analytics computation complete.")

if __name__ == "__main__":
    asyncio.run(main())
