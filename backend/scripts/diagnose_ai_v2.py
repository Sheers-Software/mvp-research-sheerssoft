import os
import asyncio
from google import genai
from openai import AsyncOpenAI


async def diagnose():
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")

    results = []

    results.append("--- Gemini Diagnostic ---")
    if not gemini_key:
        results.append("⚠️  GEMINI_API_KEY not set — skipping")
    else:
        try:
            client = genai.Client(api_key=gemini_key)
            results.append("Listing available Gemini models:")
            for m in client.models.list():
                results.append(f"  - {m.name} (Methods: {m.supported_generation_methods})")
        except Exception as e:
            results.append(f"❌ Gemini List Failed: {e}")

    results.append("\n--- OpenAI Diagnostic ---")
    if not openai_key:
        results.append("⚠️  OPENAI_API_KEY not set — skipping")
    else:
        try:
            client = AsyncOpenAI(api_key=openai_key)
            results.append("Listing available OpenAI models:")
            models = await client.models.list()
            for m in models.data:
                results.append(f"  - {m.id}")
        except Exception as e:
            results.append(f"❌ OpenAI List Failed: {e}")

    output = "\n".join(results)
    print(output)

    output_path = os.getenv("DIAGNOSTIC_OUTPUT", "/app/scripts/diagnostic_results.txt")
    try:
        with open(output_path, "w") as f:
            f.write(output)
        print(f"\nResults written to {output_path}")
    except OSError as e:
        print(f"\nCould not write results to {output_path}: {e}")


if __name__ == "__main__":
    asyncio.run(diagnose())
