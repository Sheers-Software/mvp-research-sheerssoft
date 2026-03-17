# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered hotel inquiry capture and conversion engine. Handles guest conversations across WhatsApp (Meta Cloud API & Twilio), Web Chat, and Email channels. Captures leads after hours, provides ROI analytics, and escalates to human staff when needed. Now expanding into a multi-tenant SaaS with account management, onboarding workflows, and billing.

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

`next.config.ts` rewrites all `/api/*` requests to `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`). This means the frontend never calls the backend directly in production — set `NEXT_PUBLIC_API_URL` to the deployed backend URL. Uses `output: 'standalone'` for Docker deployment.

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

### Data Model Hierarchy

```
Tenant (billing entity — hotel group)
  ├─ subscription_tier: "pilot" | "boutique" | "independent" | "premium"
  ├─ subscription_status: "trialing" | "active" | "cancelled" | "past_due"
  ├─ stripe_customer_id (for billing)
  ├─ Property (one or many per tenant)
  │   ├─ tenant_id, slug, plan_tier, is_active, deleted_at
  │   └─ Conversations, Messages, Leads, KBDocuments, AnalyticsDaily
  ├─ TenantMembership (users linked to tenant with role)
  │   ├─ role: "owner" | "admin" | "staff"
  │   └─ accessible_property_ids: null=all properties, array=scoped
  └─ OnboardingProgress (per property — gamified milestone tracking)
      ├─ channel statuses: "pending" | "configuring" | "active" | "failed" | "skipped"
      └─ milestone flags: kb_populated, first_inquiry_received, first_lead_captured, etc.

User (1:1 with Supabase auth.users, is_superadmin flag for SheersSoft staff)
SupportTicket (tenant user → SheersSoft staff workflow)
Application (public intake at ai.sheerssoft.com/apply → converts to Tenant)
```

Every entity is scoped to `property_id` or `tenant_id`. JWT tokens carry `property_id`. Use `check_property_access()` from `auth.py` in routes touching property data; use `check_tenant_access()` for tenant-level routes.

### Key Backend Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app, lifespan, middleware wiring |
| `app/config.py` | `Settings` class — pydantic-settings + GCP Secret Manager fallback |
| `app/models.py` | All ORM models: Property, Conversation, Message, Lead, KBDocument, AnalyticsDaily, **Tenant, User, TenantMembership, OnboardingProgress, SupportTicket, Application** |
| `app/routes/channels.py` | Guest channel webhooks (WhatsApp Meta, Twilio, Email, Web Chat) |
| `app/routes/billing.py` | Stripe checkout session (one-time $150 setup fee) + webhook stub |
| `app/routes/onboarding.py` | SuperAdmin tenant provisioning, progress tracking, user invitation |
| `app/routes/superadmin.py` | Platform metrics, tenant CRUD, onboarding pipeline, tickets, applications |
| `app/routes/support.py` | Support chatbot (reuses AI engine), ticket CRUD, FAQ |
| `app/services/conversation.py` | Core AI engine — multi-turn context, 3 behavioral modes, bilingual (EN/BM), RAG |
| `app/services/__init__.py` | KB/RAG service — ingest docs, pgvector semantic search |
| `app/services/analytics.py` | ROI metric calculations — revenue recovered, cost savings |
| `app/services/channel_setup.py` | Async multi-channel orchestrator (WhatsApp/Email/Web widget setup) |
| `app/services/insights.py` | Monthly 30-day guest sentiment/FAQ extraction via Gemini |
| `app/services/stripe_service.py` | Stripe checkout session creation |
| `app/services/email.py` | Email delivery (SendGrid) — used by channel_setup, scheduler, onboarding |
| `app/services/pii_encryption.py` | Fernet field-level encryption for PII (PDPA compliance) |
| `app/services/circuit_breaker.py` | Circuit breaker for external service calls |
| `app/auth.py` | JWT auth + webhook signature verification + `check_property_access()` + `check_tenant_access()` |

### Conversation Engine (`services/conversation.py`)

Three behavioral modes managed per-conversation:
1. **Concierge** — answer questions warmly using RAG over KB
2. **Lead Capture** — extract guest name, phone, email, booking intent
3. **Handoff** — package context and escalate to human staff

`_call_llm()` orchestrates the LLM fallback chain. Each LLM call includes RAG-retrieved context from `KBDocument` using pgvector cosine distance on 768-dim embeddings.

### Tenant Provisioning Flow

```
SuperAdmin → POST /api/v1/onboarding/provision-tenant
  → Creates Tenant + Property + User (Supabase Auth Admin API) + TenantMembership + OnboardingProgress
  → Sends magic link to new user via Supabase
  → Background task: _setup_channels_async() (WhatsApp / Email / Web Widget)
    → Updates OnboardingProgress per channel
    → Emails account manager on failures
```

Onboarding progress score (0–100) computed from milestone flags, surfaced at `GET /api/v1/onboarding/progress/{tenant_id}`.

### Authentication & Authorization

**Current state (v0.3.0 — functional but incomplete, see `docs/auth_rbac_plan.md` for full plan):**

- **SuperAdmin** (`require_superadmin()`): checks `User.is_superadmin`; protects all `/superadmin` and `/onboarding` routes. Intended for SheersSoft internal staff only.
- **Tenant access** (`check_tenant_access()`): verifies `TenantMembership`; `is_superadmin` bypasses check
- **Property access** (`check_property_access()`): legacy JWT property_id matching
- **Supabase Auth**: Magic link via `POST /auth/v1/magiclink?redirect_to=...` → PKCE code exchange at `/auth/callback` (supabase-js) → backend issues own JWT via `POST /auth/supabase-callback`

**User planes — intended separation:**
1. **SheersSoft System Admin** (`is_superadmin=True`) → `/admin` portal
2. **Tenant Owner/Admin** (`TenantMembership.role=owner|admin`) → `/portal` (not yet built)
3. **Property Staff** (`TenantMembership.role=staff`) → `/dashboard`
4. **First-time invited user** (no membership yet) → `/welcome` onboarding wizard (not yet built)

**Known security gaps (P0 before first real client):**
- `SUPERADMIN_EMAILS` is currently in `cloudbuild.yaml` (should be in Secret Manager, not in repo)
- Legacy `admin/password123` hardcoded in config — development only, must be removed before client onboarding
- Auto-provisioning of unknown emails should be gated to invitation-only (currently creates a user record for any valid Supabase auth)
- `staff_tier` granularity within `role=staff` not yet implemented (manager vs revenue vs ops)

### Support Chatbot

`POST /api/v1/support/chat` routes through the core `process_message()` engine using a dedicated property with slug `"nocturn-ai-support"`. This property must exist in the database. Handoff detected via keyword matching ("human", "agent", etc.).

### WhatsApp Providers

`Property.whatsapp_provider` is `"meta"` or `"twilio"`. Routes in `channels.py` handle both; services `whatsapp.py` (Meta Cloud API) and `twilio_whatsapp.py` (Twilio Sandbox) implement each.

### Database

PostgreSQL 16 + pgvector. Async SQLAlchemy with `asyncpg`. All DB calls must be `async`. Migrations via Alembic (`backend/alembic/versions/`). Row-Level Security (RLS) enabled at the database level.

Pool is intentionally small (`pool_size=2, max_overflow=5`) to fit Supabase free-tier's 60-connection limit. `pool_recycle=300` keeps connections compatible with PgBouncer.

RLS context must be set at the start of any session that touches property-scoped data:
```python
await set_db_context(session, property_id)  # sets app.current_property_id for the session
```
Use `async_session_factory` (alias for `async_session`) when creating standalone sessions in background tasks.

### Analytics

`AnalyticsDaily` is pre-aggregated (one row per property per day). In development/demo, APScheduler (`services/scheduler.py`) runs jobs in-process. In production, APScheduler is **disabled** — Cloud Scheduler calls `POST /api/v1/internal/run-daily-report` etc. instead.

### Redis / Session / Realtime

`app/core/redis.py` has a graceful in-memory fallback. If `REDIS_URL` points to localhost or connection fails, all ops silently use a dict-based in-process store. Pub/sub is a no-op when Redis is unavailable. This means the app runs on Cloud Run without Memorystore for the pilot phase — sessions survive within a single instance but are not shared across instances.

### Internal Scheduler Endpoints

`app/routes/internal.py` — four `POST` endpoints called by Cloud Scheduler in production:
- `/api/v1/internal/run-daily-report`
- `/api/v1/internal/run-followups`
- `/api/v1/internal/run-insights`
- `/api/v1/internal/cleanup-leads`

All require `X-Internal-Secret` header matching `settings.internal_scheduler_secret` (loaded from GCP Secret Manager as `INTERNAL_SCHEDULER_SECRET`). Endpoints are excluded from OpenAPI docs (`include_in_schema=False`).

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
SUPABASE_URL=...          # optional; enables Supabase auth user creation + magic links
SUPABASE_SERVICE_ROLE_KEY=...
STRIPE_SECRET_KEY=...     # optional; needed for billing routes
```

For the demo stack, use `.env.demo` (already configured with Twilio/Gemini credentials).

**GCP Secret Manager state** (project `nocturn-ai-487207`): All critical secrets are stored — `DATABASE_URL` (has BOM, stripped automatically), `GEMINI_API_KEY`, `OPENAI_API_KEY`, `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET`, `JWT_SECRET`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, all Twilio keys, `INTERNAL_SCHEDULER_SECRET`. Still missing: `FERNET_ENCRYPTION_KEY`, `ANTHROPIC_API_KEY`, `SENDGRID_API_KEY`, `WHATSAPP_API_TOKEN`, `WHATSAPP_APP_SECRET`. Secrets stored with BOM (`\ufeff`) are stripped in `config.py` automatically.

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

Gemini requires role mapping before sending message history: `"assistant"` → `"model"`, `"user"` → `"user"` (using `google.genai.types.Content`). Anthropic requires the `system` prompt as a separate parameter, not in the messages array.

### Gemini embedding
`generate_embedding()` in `services/__init__.py` wraps the synchronous Gemini client in `asyncio.to_thread()`. Do not call `gemini_client.models.embed_content()` directly from async code.

### Bilingual responses
`FALLBACK_RESPONSE` and `FALLBACK_RESPONSE_BM` in `conversation.py` are the last-resort guest-facing strings in English and Bahasa Malaysia respectively. Any new guest-facing error message should have a BM variant.

## Testing

Tests are in `backend/tests/`. Uses `pytest-asyncio` with `asyncio_mode = auto` and `asyncio_default_fixture_loop_scope = function`.

`conftest.py` provides two auto-use fixtures:
- `client` — `httpx.AsyncClient` over `ASGITransport(app=app)`, no network involved
- `setup_db` — runs `Base.metadata.create_all` before every test (autouse)

Tests mock external service calls by patching module-level functions with `unittest.mock.AsyncMock` and `patch` (e.g., `patch("app.services.conversation.get_or_create_conversation", new_callable=AsyncMock)`). Use `app.dependency_overrides[dep_fn] = mock_fn` for FastAPI dependency injection overrides.

Tests that require seeded data (e.g., `test_ai_accuracy.py`) will skip if `seed_demo_data.py` has not been run first.

For integration testing against live channels, see `docs/sit_uat_guide.md` and `docs/testing_guide.md`.

## Production Deployment (GCP Cloud Run)

**Live URLs:**
- Backend: `https://nocturn-backend-owtn645vea-as.a.run.app`
- Frontend: `https://nocturn-frontend-owtn645vea-as.a.run.app`

**Deploy (manual trigger):**
```bash
gcloud builds submit \
  --config=backend/cloudbuild.yaml \
  --project=nocturn-ai-487207 \
  --region=asia-southeast1 \
  --substitutions=COMMIT_SHA=$(git rev-parse HEAD) \
  .
```

**CI/CD:** `backend/cloudbuild.yaml` defines the full pipeline: build backend → build frontend → push both to Artifact Registry → deploy backend Cloud Run → deploy frontend Cloud Run. Hook this to a Cloud Build GitHub trigger for automatic deploys on push to `main`.

**New PC setup:**
```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project nocturn-ai-487207
gcloud auth configure-docker asia-southeast1-docker.pkg.dev
```

**Stripe local webhook listener (Windows):**
```powershell
.\stripe_webhook_listen.ps1   # Stripe CLI installed at %LOCALAPPDATA%\Microsoft\WinGet\Packages\Stripe.StripeCli_*\
```
Run in a separate terminal. Copy the printed `whsec_` and add to Secret Manager as `STRIPE_WEBHOOK_SECRET`.

**Pending infra tasks:**
1. Create Cloud Scheduler jobs (daily-report, run-followups, run-insights, db-keepalive)
2. Add live Stripe webhook in Stripe dashboard → update `STRIPE_WEBHOOK_SECRET`
3. Add `FERNET_ENCRYPTION_KEY` to Secret Manager
4. Custom domain mapping (optional): `api.sheerssoft.com` / `app.sheerssoft.com`

## Documentation

- `docs/architecture.md` — detailed system design rationale
- `docs/prd.md` — product requirements
- `docs/walkthrough_twilio_demo.md` — step-by-step live demo guide
- `docs/testing_guide.md` / `docs/sit_uat_guide.md` — test procedures
- `memory/MEMORY.md` — persistent session memory: infra state, secrets, next steps, new PC setup
