"""Test embedding with various model names and SDK approaches."""
import sys, os
sys.path.insert(0, "/app")
os.environ.setdefault("SQLALCHEMY_SILENCE_UBER_WARNING", "1")
from app.config import get_settings
s = get_settings()

print(f"API key prefix: {s.gemini_api_key[:12]}...")
print(f"Configured model: {s.gemini_embedding_model}")
print()

# Test 1: google-genai SDK with various model names
from google import genai
print(f"google-genai SDK version: {genai.__version__}")
c = genai.Client(api_key=s.gemini_api_key)

models_to_try = [
    "models/text-embedding-004",
    "text-embedding-004",
    "models/embedding-001",
    "embedding-001",
]

for model in models_to_try:
    try:
        r = c.models.embed_content(model=model, contents="test embedding")
        print(f"  SDK {model}: OK dim={len(r.embeddings[0].values)}")
        break
    except Exception as e:
        err = str(e)[:120]
        print(f"  SDK {model}: FAIL - {err}")

# Test 2: Direct REST API calls
import httpx
print()
print("--- REST API Tests ---")
for ver in ["v1", "v1beta"]:
    for model in ["text-embedding-004", "embedding-001"]:
        url = f"https://generativelanguage.googleapis.com/{ver}/models/{model}:embedContent?key={s.gemini_api_key}"
        payload = {"content": {"parts": [{"text": "test embedding query"}]}}
        try:
            r = httpx.post(url, json=payload, timeout=15)
            if r.status_code == 200:
                data = r.json()
                dim = len(data["embedding"]["values"])
                print(f"  REST {ver}/{model}: OK dim={dim}")
            else:
                err_msg = r.json().get("error", {}).get("message", "")[:100]
                print(f"  REST {ver}/{model}: {r.status_code} - {err_msg}")
        except Exception as e:
            print(f"  REST {ver}/{model}: ERR - {str(e)[:100]}")

# Test 3: Try listing available models
print()
print("--- Available Embedding Models ---")
try:
    for ver in ["v1", "v1beta"]:
        url = f"https://generativelanguage.googleapis.com/{ver}/models?key={s.gemini_api_key}"
        r = httpx.get(url, timeout=15)
        if r.status_code == 200:
            models = r.json().get("models", [])
            embed_models = [m["name"] for m in models if "embed" in m.get("name", "").lower()]
            print(f"  {ver} embedding models: {embed_models}")
        else:
            print(f"  {ver}: {r.status_code} - {r.text[:100]}")
except Exception as e:
    print(f"  ERR: {str(e)[:100]}")
