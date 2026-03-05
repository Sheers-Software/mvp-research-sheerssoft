import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def update_property():
    engine = create_async_engine('postgresql+asyncpg://demo:demo_password@localhost:5434/nocturn_demo')
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        result = await session.execute(text("""
            UPDATE properties 
            SET twilio_phone_number = '+14155238886', whatsapp_provider = 'twilio' 
            WHERE slug = 'sheers-hotel'
            RETURNING id, name, twilio_phone_number;
        """))
        await session.commit()
        for row in result:
            print(f'Successfully updated property: {row}')

if __name__ == "__main__":
    asyncio.run(update_property())
