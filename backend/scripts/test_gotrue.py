import asyncio
import httpx
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str

    class Config:
        env_file = ".env"

async def test_magic_link():
    settings = Settings()
    async with httpx.AsyncClient() as client:
        # TEST 1: Body
        url = f"{settings.supabase_url}/auth/v1/magiclink"
        print(f"Testing body payload to {url}")
        body = {
            "email": "a.basyir94@gmail.com",
            # "options": {"emailRedirectTo": "http://localhost:3001/body"}
        }
        resp = await client.post(
            f"{url}?redirect_to=http://localhost:3001/superquery",
            headers={"apikey": settings.supabase_anon_key, "Content-Type": "application/json"},
            json=body
        )
        print(resp.status_code, resp.text)

asyncio.run(test_magic_link())
