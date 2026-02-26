# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered hotel inquiry capture and conversion engine. Handles guest conversations across WhatsApp (Meta Cloud API & Twilio), Web Chat, and Email channels. Captures leads after hours, provides ROI analytics, and escalates to human staff when needed.

## Common Commands

### Backend (Python/FastAPI)

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run dev server
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run all tests
cd backend && pytest

# Run a single test file
cd backend && pytest tests/test_conversation.py -v

# Run a single test
cd backend && pytest tests/test_conversation.py::test_function_name -v

# Database migrations
cd backend && alembic upgrade head
cd backend && alembic revision --autogenerate -m "description"

# Seed demo data
cd backend && python seed_demo_data.py
```

### Frontend (Next.js)

```bash
cd frontend && npm install
cd frontend && npm run dev      # Dev server on port 3000
cd frontend && npm run build
cd frontend && npm run lint
```

### Docker

```bash
# Production/dev stack (ports: backend 8000, frontend 3000, postgres 5433, redis 6380)
docker-compose up -d --build

# Demo stack (ports: backend 8001, frontend 3001 — isolated DB and Redis)
docker-compose -f docker-compose.demo.yml up -d --build
```

### Live Demo (Windows)

```powershell
.\start_demo.ps1           # Standard demo
.\start_live_demo.ps1      # Live Twilio WhatsApp demo
```

## Architecture

### Request Flow

```
Guest (WhatsApp / Web Chat / Email)
  → FastAPI routes/channels.py  (webhook receive, rate limiting, signature verify)
  → services/conversation.py    (AI engine: context, RAG, behavioral mode)
  → LLM fallback chain          (Gemini → OpenAI GPT-4o-mini → Anthropic Claude Haiku → templates)
  → services/__init__.py        (RAG: pgvector semantic search against KBDocument)
  → Lead capture / escalation   (staff notification via Redis pub/sub)
  → Staff Dashboard             (Next.js: analytics, inbox, lead triage)
```

### Three Deployment Modes

Controlled by `ENVIRONMENT` env var:
- `development` — mock channels, console logging
- `demo` — real AI, simulated channels, pre-seeded 100+ conversation scenarios, uses `.env.demo`
- `production` — live integrations, secrets from GCP Secret Manager (`nocturn-ai-487207`)

### Credential Resolution Order

For API keys: env var → GCP Secret Manager fallback (production/demo only).

### Key Backend Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app, lifespan, middleware wiring |
| `app/config.py` | `Settings` class — pydantic-settings + GCP Secret Manager fallback |
| `app/models.py` | SQLAlchemy ORM: `Property`, `Conversation`, `Message`, `Lead`, `KBDocument`, `AnalyticsDaily` |
| `app/routes/channels.py` | Guest channel webhooks (WhatsApp Meta, Twilio, Email, Web Chat) |
| `app/services/conversation.py` | Core AI engine — multi-turn context, 3 behavioral modes, bilingual (EN/BM), RAG |
| `app/services/__init__.py` | KB/RAG service — ingest docs, pgvector semantic search |
| `app/services/analytics.py` | ROI metric calculations — revenue recovered, cost savings |
| `app/auth.py` | JWT auth + webhook signature verification |

### Conversation Engine (`services/conversation.py`)

Three behavioral modes managed per-conversation:
1. **Concierge** — answer questions warmly using RAG over KB
2. **Lead Capture** — extract guest name, phone, email, booking intent
3. **Handoff** — package context and escalate to human staff

`_call_llm()` orchestrates the LLM fallback chain. Each LLM call includes RAG-retrieved context from `KBDocument` using pgvector cosine distance on 768-dim embeddings.

### Multi-Tenancy

Every entity is scoped to `property_id`. Database-level Row-Level Security (RLS) is enabled. JWT tokens carry `property_id`. Use `check_property_access()` from `auth.py` in any route that touches property data.

### WhatsApp Providers

`Property.whatsapp_provider` is `"meta"` or `"twilio"`. Routes in `channels.py` handle both; services `whatsapp.py` (Meta Cloud API) and `twilio_whatsapp.py` (Twilio Sandbox) implement each.

### Database

PostgreSQL 16 + pgvector. Async SQLAlchemy with `asyncpg`. All DB calls must be `async`. Migrations via Alembic (`backend/alembic/versions/`).

### Analytics

`AnalyticsDaily` is pre-aggregated (one row per property per day). Background scheduler (`services/scheduler.py`) runs daily aggregation via APScheduler. Live stats endpoint reads directly from `Conversation`/`Message` tables.

## Configuration

Copy `.env.example` to `.env`. Key variables:

```
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://localhost:6380/0
GEMINI_API_KEY=...
OPENAI_API_KEY=...        # fallback LLM
ANTHROPIC_API_KEY=...     # fallback LLM
JWT_SECRET=...
ADMIN_USER=admin
ADMIN_PASSWORD=...
FERNET_ENCRYPTION_KEY=... # PII field-level encryption (PDPA)
```

For the demo stack, use `.env.demo` (already configured with Twilio/Gemini credentials).

## WhatsApp Channel — Key Patterns

### Message Flow (both Meta and Twilio)
Webhook → `normalize_*_message()` → property lookup → background task → `process_guest_message()` → `send_*_message()`

### Non-text message handling
Both `normalize_whatsapp_message` and `normalize_twilio_webhook` return `is_unsupported_media: True` in metadata when a guest sends an image/audio/video/location. `channels.py` detects this flag and dispatches `_handle_unsupported_media_async` which sends a canned bilingual reply without calling the AI.

### Error resilience
`_handle_whatsapp_message_async` catches all exceptions and attempts to send `FALLBACK_RESPONSE` (from `conversation.py`) to the guest so they are never left without a reply.

### Multi-tenant Twilio sender
`send_twilio_message()` accepts an optional `from_number` parameter. Always pass `prop.twilio_phone_number` from the property record — do not rely on the global `settings.twilio_phone_number` alone.

### LLM fallback chain
`_call_llm()` in `conversation.py` falls through Gemini → OpenAI → Anthropic → template string. Empty responses from any provider are treated as failures and fall through to the next provider.

### Gemini embedding
`generate_embedding()` in `services/__init__.py` wraps the synchronous Gemini client in `asyncio.to_thread()`. Do not call `gemini_client.models.embed_content()` directly from async code.

## Testing

Tests are in `backend/tests/`. Uses `pytest-asyncio` for async tests. The `pytest.ini` sets `asyncio_mode = auto`.

Tests that require seeded data (e.g., `test_ai_accuracy.py`) will skip if `seed_demo_data.py` has not been run first.

For integration testing against live channels, see `docs/sit_uat_guide.md` and `docs/testing_guide.md`.

## Documentation

- `docs/architecture.md` — detailed system design rationale
- `docs/prd.md` — product requirements
- `docs/walkthrough_twilio_demo.md` — step-by-step live demo guide
- `docs/testing_guide.md` / `docs/sit_uat_guide.md` — test procedures
