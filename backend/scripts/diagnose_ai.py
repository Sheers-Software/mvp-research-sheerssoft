import os
import asyncio
from google import genai
from openai import AsyncOpenAI
import structlog

structlog.configure()
logger = structlog.get_logger()


async def test_gemini(api_key: str, model_name: str):
    print(f"\n--- Testing Gemini ({model_name}) ---")
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=model_name, contents="test")
        print(f"✅ Gemini Success: {response.text[:50]}...")
    except Exception as e:
        print(f"❌ Gemini Failed: {e}")

    print("\n--- Listing Gemini Models ---")
    try:
        client = genai.Client(api_key=api_key)
        for m in client.models.list():
            if "generateContent" in m.supported_generation_methods:
                print(f"  - {m.name}")
    except Exception as e:
        print(f"❌ Gemini List Failed: {e}")


async def test_openai(api_key: str, model_name: str):
    print(f"\n--- Testing OpenAI ({model_name}) ---")
    try:
        client = AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5,
        )
        print(f"✅ OpenAI Success: {response.choices[0].message.content}...")
    except Exception as e:
        print(f"❌ OpenAI Failed: {e}")


async def main():
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not gemini_key:
        print("⚠️  GEMINI_API_KEY not set — skipping Gemini test")
    else:
        await test_gemini(gemini_key, gemini_model)

    if not openai_key:
        print("⚠️  OPENAI_API_KEY not set — skipping OpenAI test")
    else:
        await test_openai(openai_key, openai_model)


if __name__ == "__main__":
    asyncio.run(main())
