# Nocturn AI — Hotel Inquiry Capture & Conversion Engine

An AI-powered hotel inquiry capture system that recovers revenue lost after hours, tracks granular ROI, and is a fully multi-tenant SaaS platform built by SheersSoft.

## Architecture

- **Backend:** Python 3.11 + FastAPI (async SQLAlchemy, asyncpg)
- **Frontend:** Next.js 14 + TypeScript
- **Database:** PostgreSQL 16 + pgvector (Supabase-hosted)
- **Auth:** Supabase Auth (magic links) + local JWT fallback
- **LLMs:** Google Gemini (primary), OpenAI GPT-4o-mini & Anthropic Claude Haiku (fallbacks)
- **Channels:** WhatsApp (Meta Cloud API & Twilio), Web Chat Widget, Email (SendGrid)
- **Billing:** Stripe (one-time setup fee + subscription management)
- **Infra:** GCP Cloud Run (backend + frontend), GCP Secret Manager (`nocturn-ai-487207`), Cloud Scheduler (4 jobs)
- **PII Compliance:** Fernet field-level encryption (PDPA 2010), GDPR/PDPA right-to-delete endpoint

## Key Features

1. **AI Conversation Engine (RAG):** Answers guest inquiries using a per-property knowledge base, captures leads, and escalates to human staff when needed. Three behavioral modes: Concierge → Lead Capture → Handoff.
2. **Multi-Tenant SaaS Architecture:** Hotel groups (Tenants) own multiple Properties. Staff access is scoped per-property via TenantMembership roles (`owner` / `admin` / `staff`).
3. **Gamified Onboarding Flow:** SuperAdmin provisions a new tenant in one API call — creates Tenant, Property, User (via Supabase Auth), TenantMembership, and OnboardingProgress. Magic link sent automatically. Channel setup runs asynchronously. Progress score 0–100.
4. **Stripe Billing:** One-time $150 setup fee via Stripe Checkout. Webhook activates tenant subscription on payment.
5. **SuperAdmin Platform Dashboard (`/admin`):** Global KPIs, tenant pipeline (Provisioned → Channels Setup → Live → Fully Onboarded), support ticket queue, application intake from `ai.sheerssoft.com/apply`, service health dashboard, system announcements.
6. **Property Dashboard (`/dashboard`):** Staff reply inbox, lead triage (with lost lead filtering), analytics with CSV/PDF export, settings, ROI metrics.
7. **Maintenance Mode & Announcements:** SheersSoft can toggle platform maintenance (with ETA message) and broadcast typed announcements (maintenance / incident / feature / billing) scoped by tier or individual tenant.
8. **Service Health Dashboard:** 9 parallel health checks (DB, Redis, Gemini, OpenAI, Anthropic, SendGrid, Twilio, Meta WhatsApp, Supabase) with 20s cache and auto-refresh.
9. **Support Chatbot:** Reuses the core AI engine on a dedicated `nocturn-ai-support` property. Detects handoff intent and escalates to SheersSoft staff.
10. **Automated Follow-up Engine:** AI re-engages cold leads at 24h, 72h, and 7-day intervals.
11. **Monthly Guest Insights Report:** Gemini pipeline processes 30 days of transcripts — sentiment, recurring objections, FAQs.
12. **PII Encryption & PDPA Delete:** Fernet encryption on guest PII fields at rest. Right-to-delete endpoint anonymizes all data for a guest identifier.

## Getting Started

### Prerequisites — Push to GCP Secret Manager

All credentials go into GCP Secret Manager project `nocturn-ai-487207`. Run `gcloud auth application-default login` for local ADC.

| Secret | Where to get it |
|--------|----------------|
| `DATABASE_URL` | Supabase dashboard → Project Settings → Database → Connection String |
| `GEMINI_API_KEY` | Google AI Studio |
| `OPENAI_API_KEY` | OpenAI platform |
| `SUPABASE_URL` | Supabase dashboard → Project Settings → API |
| `SUPABASE_ANON_KEY` | Same |
| `SUPABASE_SERVICE_ROLE_KEY` | Same |
| `STRIPE_API_KEY` | Stripe dashboard → Developers → API keys |
| `STRIPE_WEBHOOK_SECRET` | Stripe dashboard → Developers → Webhooks |
| `JWT_SECRET` | Supabase dashboard → Project Settings → API → JWT Secret |
| `FERNET_ENCRYPTION_KEY` | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` | Twilio Console |
| `SENDGRID_API_KEY` | SendGrid dashboard |
| `INTERNAL_SCHEDULER_SECRET` | Any random string — used to authenticate Cloud Scheduler → Cloud Run calls |

### Launch (local)

```bash
# Production / dev stack (backend :8000, frontend :3000, postgres :5433, redis :6380)
docker-compose up -d --build

# Demo stack — isolated DB and Redis (backend :8001, frontend :3001)
docker-compose -f docker-compose.demo.yml up -d --build
```

```powershell
# Windows demo scripts
.\start_demo.ps1           # Standard demo
.\start_live_demo.ps1      # Live Twilio WhatsApp demo (requires Cloudflare Tunnel)
```

### GCP Deployment

**Current state:** Cloud Run services are spun down to save cost. Scheduler jobs are paused. Images are cached locally at commit `cf9e34c1ce009e8726f162cc7edce41048835a04`.

**Spin up (deploy and resume):**
```bash
# 1. Build + deploy both services
gcloud builds submit \
  --config=backend/cloudbuild.yaml \
  --project=nocturn-ai-487207 \
  --region=asia-southeast1 \
  --substitutions=COMMIT_SHA=$(git rev-parse HEAD) \
  .

# 2. Resume Cloud Scheduler jobs
for job in nocturn-daily-report nocturn-followups nocturn-insights nocturn-keepalive; do
  gcloud scheduler jobs resume $job --location=asia-southeast1 --project=nocturn-ai-487207
done
```

**Spin down (save cost):**
```bash
# Pause Scheduler jobs
for job in nocturn-daily-report nocturn-followups nocturn-insights nocturn-keepalive; do
  gcloud scheduler jobs pause $job --location=asia-southeast1 --project=nocturn-ai-487207
done

# Delete Cloud Run services (redeploy via cloudbuild to restore)
gcloud run services delete nocturn-backend --project=nocturn-ai-487207 --region=asia-southeast1 --quiet
gcloud run services delete nocturn-frontend --project=nocturn-ai-487207 --region=asia-southeast1 --quiet
```

**New machine setup:**
```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project nocturn-ai-487207
gcloud auth configure-docker asia-southeast1-docker.pkg.dev
```

## Data Model

```
Tenant (billing entity — hotel group)
  ├─ subscription_tier: "pilot" | "boutique" | "independent" | "premium"
  ├─ subscription_status: "trialing" | "active" | "cancelled" | "past_due"
  ├─ stripe_customer_id
  ├─ Property (one or many per tenant)
  │   └─ Conversations, Messages, Leads, KBDocuments, AnalyticsDaily
  ├─ TenantMembership → role: "owner" | "admin" | "staff"
  └─ OnboardingProgress (per property, gamified 0–100 score)

User (1:1 with Supabase auth.users, is_superadmin for SheersSoft staff)
SupportTicket (tenant user → SheersSoft staff)
Application (public intake → converts to Tenant)
Announcement (type: maintenance/incident/feature/billing, scoped by tier or tenant)
SystemConfig (key-value store for maintenance mode, platform settings)
```

## API Surface

| Prefix | Purpose |
|--------|---------|
| `POST /api/v1/auth/token` | Legacy JWT login |
| `POST /api/v1/auth/magic-link` | Supabase magic link |
| `POST /api/v1/onboarding/provision-tenant` | One-click tenant provisioning (superadmin) |
| `GET /api/v1/onboarding/progress/{tenant_id}` | Gamified onboarding score |
| `POST /api/v1/billing/checkout` | Stripe checkout session |
| `POST /api/v1/billing/webhook` | Stripe webhook (activates tenant) |
| `GET /api/v1/superadmin/metrics` | Platform-wide KPIs |
| `GET /api/v1/superadmin/tenants` | Tenant list + CRUD |
| `GET /api/v1/superadmin/pipeline` | Onboarding kanban pipeline |
| `GET /api/v1/superadmin/service-health` | 9-service health check dashboard |
| `GET/POST/PATCH /api/v1/superadmin/announcements` | Announcement broadcast CRUD |
| `GET /api/v1/superadmin/system-config` | Platform-wide config (maintenance mode) |
| `GET /api/v1/announcements/active` | Active announcements for authenticated tenant |
| `GET /api/v1/system/info` | Environment info + maintenance status (no auth) |
| `POST /api/v1/staff/reply` | Staff reply to a guest conversation |
| `POST /api/v1/support/chat` | Support chatbot |
| `POST /api/v1/applications` | Public application intake |
| `POST /api/v1/webhook/whatsapp` | Meta WhatsApp webhook |
| `POST /api/v1/webhook/twilio/whatsapp` | Twilio WhatsApp webhook |
| `POST /api/v1/webhook/email` | SendGrid inbound email |
| `DELETE /api/v1/gdpr/delete-guest/{property_id}/{identifier}` | PDPA right-to-delete |
| `POST /api/v1/internal/run-daily-report` | Cloud Scheduler trigger (auth: X-Internal-Secret) |
| `POST /api/v1/internal/run-followups` | Cloud Scheduler trigger |
| `POST /api/v1/internal/run-insights` | Cloud Scheduler trigger |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, lifespan, startup migrations
│   │   ├── config.py                # Settings + GCP Secret Manager fallback
│   │   ├── database.py              # Async SQLAlchemy engine + RLS context
│   │   ├── models.py                # All ORM models
│   │   ├── schemas.py               # Pydantic request/response schemas
│   │   ├── auth.py                  # JWT + check_property_access / check_tenant_access
│   │   ├── routes/
│   │   │   ├── admin.py             # Property CRUD, settings, system/info, announcements/active
│   │   │   ├── billing.py           # Stripe checkout + webhook
│   │   │   ├── channels.py          # Guest channel webhooks (WhatsApp, Email, Web Chat)
│   │   │   ├── internal.py          # Cloud Scheduler endpoints (X-Internal-Secret)
│   │   │   ├── onboarding.py        # Tenant provisioning + progress tracking
│   │   │   ├── staff.py             # Staff reply + conversation inbox
│   │   │   ├── superadmin.py        # Platform dashboard, tenants, service-health, announcements CRUD
│   │   │   └── support.py           # Support chatbot + ticket CRUD
│   │   ├── services/
│   │   │   ├── conversation.py      # Core AI engine (RAG, 3 modes, bilingual EN/BM)
│   │   │   ├── analytics.py         # ROI metric calculations
│   │   │   ├── channel_setup.py     # Async multi-channel orchestrator
│   │   │   ├── circuit_breaker.py   # Circuit breaker for external calls
│   │   │   ├── email.py             # SendGrid delivery
│   │   │   ├── insights.py          # Monthly 30-day transcript analysis
│   │   │   ├── integration_registry.py # Integration status checks
│   │   │   ├── pii_encryption.py    # Fernet field-level PII encryption
│   │   │   ├── scheduler.py         # APScheduler (dev/demo only)
│   │   │   ├── stripe_service.py    # Stripe checkout session
│   │   │   └── system_config.py     # Maintenance mode DB config
│   │   └── core/
│   │       └── redis.py             # Redis client with in-memory fallback
│   ├── tests/
│   ├── alembic/                     # DB migrations
│   ├── cloudbuild.yaml              # GCP Cloud Build CI/CD pipeline
│   └── requirements.txt
├── frontend/
│   └── src/app/
│       ├── admin/                   # SheersSoft internal ops portal
│       │   ├── announcements/       # Announcement broadcast management
│       │   ├── health/              # Service health dashboard
│       │   ├── system/              # Maintenance mode toggle
│       │   ├── tenants/             # Tenant management
│       │   ├── pipeline/            # Onboarding pipeline kanban
│       │   └── tickets/             # Support ticket queue
│       └── dashboard/               # Property staff dashboard
│           ├── conversations/       # Guest inbox + staff reply
│           ├── leads/               # Lead triage + lost lead filter
│           ├── analytics/           # ROI metrics, CSV/PDF export
│           └── settings/            # Property configuration
├── docs/                            # Architecture, PRD, testing guides, build plan
├── docker-compose.yml               # Production / dev stack
└── docker-compose.demo.yml          # Isolated demo stack
```

## Development

```bash
# Backend
pip install -r backend/requirements.txt
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Tests
cd backend && pytest                           # All tests
cd backend && pytest tests/test_billing.py -v  # Billing (no DB required)
cd backend && pytest tests/test_supabase.py -v # Supabase live (requires GCP ADC)

# Database migrations
cd backend && alembic upgrade head
cd backend && alembic revision --autogenerate -m "description"

# Seed demo data
cd backend && python seed_demo_data.py
```

## Sprint Completion Status

- [x] Phase 0: Integration Credential Architecture
- [x] Phase 1: Backend Hardening
- [x] Phase 2: Demo Mode Orchestration & Seed Scripting
- [x] Phase 3: Staff Dashboard & KPI Construction
- [x] Phase 4: Web Chat Widget Polish
- [x] Phase 5: Multi-Channel Live Integrations (WhatsApp, Web, Email)
- [x] Phase 6: Security & PDPA Governance
- [x] Phase 7: Production Containerization
- [x] Phase 8: Multi-Tenant Security Auditing
- [x] Phase 9: AI Personas, Brand Scripting, Metrics Tracking
- [x] Phase 10: Live Metric and Operations End-to-End Validation
- [x] Phase 11: Advanced Analytics — Date Filtering, CSV & PDF Reporting
- [x] Phase 12: Live WhatsApp Demo via Twilio (Approved Sender + Cloudflare Tunnel)
- [x] Phase 13: WhatsApp Reliability & Consistency Hardening
- [x] Phase 14: Gap Resolution — Automated Follow-ups, Revenue Tracking, Monthly AI Briefings
- [x] Phase 15: Multi-Tenant SaaS — Stripe Billing, Supabase Auth, Onboarding Flow, SuperAdmin Dashboard
- [x] Phase 16: Auth & Integration Hardening — Magic Link Redirect, SendGrid SMTP, Tenant Detail Dashboard, Twilio Sandbox Linking
- [x] Phase 1.5: Internal Controls — Maintenance Mode, Service Health Dashboard, Announcements System

## Database & Supabase Notes

- **Hosted on Supabase** (`ramenghkpvipxijhfptp`). `DATABASE_URL` loaded from GCP Secret Manager — no hardcoded credentials.
- **Free tier pause:** Supabase free tier projects auto-pause after 7 days of inactivity. Unpause from the Supabase dashboard.
- **Startup migrations:** `main.py` lifespan runs idempotent `CREATE TABLE IF NOT EXISTS` / `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` DDL on every cold start — safe to restart repeatedly.
- **Connection pooling:** `pool_size=2, max_overflow=5, pool_recycle=300` to fit Supabase free tier's 60-connection limit.
- **RLS:** Row-Level Security enabled. Call `set_db_context(session, property_id)` at the start of any session touching property-scoped data.
- **Migrations:** Managed via Alembic. For DDL-heavy operations against the pooler, use `npx supabase db push` with the Supabase CLI.
- **Custom SMTP:** Supabase Auth uses SendGrid SMTP (`smtp.sendgrid.net:465`) to bypass free-tier email rate limits.

## WhatsApp Channel Notes

- **Non-text messages:** Images, audio, video, and location pins receive a bilingual acknowledgement (EN + BM) instead of being silently ignored.
- **Error resilience:** If the AI pipeline fails, the guest still receives a human-readable fallback response.
- **Multi-tenant sender:** Outbound messages use each property's registered `twilio_phone_number` — not a shared global value.
- **LLM fallback chain:** Blank or failed responses fall through: Gemini → OpenAI → Anthropic → template string.
- **Gemini embeddings:** Synchronous Gemini embedding call wrapped in `asyncio.to_thread()` — do not call directly from async code.
- **Bilingual responses:** All guest-facing error strings have both English and Bahasa Malaysia variants (`FALLBACK_RESPONSE` / `FALLBACK_RESPONSE_BM`).
