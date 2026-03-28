# Nocturn AI — Hotel Inquiry Capture & Conversion Engine

An AI-powered hotel inquiry capture system that recovers revenue lost after hours, tracks granular ROI, and is a fully multi-tenant SaaS platform built by SheersSoft.

**v0.5.1** — Infrastructure hardening: GCP Secret Manager project ID corrected, LLM fallback chain updated (Gemini → Claude Haiku → GPT-4o-mini), Docker frontend proxy fixed, Anthropic API key provisioned.

## Architecture

- **Backend:** Python 3.12 + FastAPI (async SQLAlchemy, asyncpg) — v0.5.1
- **Frontend:** Next.js 14 + TypeScript
- **Database:** Supabase PostgreSQL 17 + pgvector — user `nocturn_app`, transaction pooler (port 6543, ap-southeast-2)
- **Auth:** Supabase Auth (magic links) + local JWT fallback
- **LLMs:** Google Gemini (primary), Anthropic Claude Haiku (secondary), OpenAI GPT-4o-mini (tertiary)
- **Channels:** WhatsApp (Meta Cloud API & Twilio), Web Chat Widget, Email (SendGrid)
- **Billing:** Stripe (one-time setup fee + subscription management)
- **Infra:** GCP Cloud Run (backend + frontend), GCP Secret Manager (`nocturn-ai-487207`)
- **Secrets:** All credentials exclusively from GCP Secret Manager — no `.env` files, no Cloud SQL
- **PII Compliance:** Fernet field-level encryption (PDPA 2010), GDPR/PDPA right-to-delete endpoint

## Key Features

1. **AI Conversation Engine (RAG):** Answers guest inquiries using a per-property knowledge base, captures leads, and escalates to human staff when needed. Three behavioral modes: Concierge → Lead Capture → Handoff.
2. **Multi-Tenant SaaS Architecture:** Hotel groups (Tenants) own multiple Properties. Staff access is scoped per-property via TenantMembership roles (`owner` / `admin` / `staff`).
3. **Self-Service Onboarding Wizard (`/welcome`):** Five-step guided setup for new clients — confirm property details, enter knowledge base (rooms, rates, FAQs, policies), verify channels, invite team, activate AI. No SheersSoft engineer required after provisioning.
4. **Tenant Management Portal (`/portal`):** Owner/admin layer for configuring the business — manage KB documents, team members (invite/remove), channel status, billing, and support tickets. Separate from the day-to-day operations dashboard.
5. **Gamified Onboarding Flow:** SuperAdmin provisions a new tenant in one API call — creates Tenant, Property, User (via Supabase Auth), TenantMembership, and OnboardingProgress. Magic link sent automatically. Channel setup runs asynchronously. Progress score 0–100.
6. **Stripe Billing:** One-time $150 setup fee via Stripe Checkout. Webhook activates tenant subscription on payment.
7. **SuperAdmin Platform Dashboard (`/admin`):** Global KPIs, tenant pipeline (Provisioned → Channels Setup → Live → Fully Onboarded), support ticket queue, application intake from `ai.sheerssoft.com/apply`, service health dashboard, system announcements, KB ingestion tool.
8. **Property Dashboard (`/dashboard`):** Staff reply inbox, lead triage (with lost lead filtering), analytics with CSV/PDF export, settings, ROI metrics, AI insights (monthly guest topics + KB gap suggestions).
7. **Maintenance Mode & Announcements:** SheersSoft can toggle platform maintenance (with ETA message) and broadcast typed announcements (maintenance / incident / feature / billing) scoped by tier or individual tenant.
8. **Service Health Dashboard:** 9 parallel health checks (DB, Redis, Gemini, OpenAI, Anthropic, SendGrid, Twilio, Meta WhatsApp, Supabase) with 20s cache and auto-refresh.
9. **Support Chatbot:** Reuses the core AI engine on a dedicated `nocturn-ai-support` property. Detects handoff intent and escalates to SheersSoft staff.
10. **Automated Follow-up Engine:** AI re-engages cold leads at 24h, 72h, and 7-day intervals.
11. **Monthly Guest Insights Report:** Gemini pipeline processes 30 days of transcripts — sentiment, recurring objections, FAQs.
12. **PII Encryption & PDPA Delete:** Fernet encryption on guest PII fields at rest. Right-to-delete endpoint anonymizes all data for a guest identifier.

## Getting Started

### Prerequisites

#### 1. GCP credentials (required for Secret Manager access)

All secrets are loaded exclusively from GCP Secret Manager at startup. No `.env` files are used.

```bash
gcloud auth login
gcloud auth application-default login   # creates ADC credentials mounted into containers
gcloud config set project nocturn-aai
```

#### 2. Secrets in GCP Secret Manager (`nocturn-ai-487207`)

| Secret | Where to get it |
|--------|----------------|
| `DATABASE_URL` | Supabase dashboard → Connect → Transaction pooler URI |
| `GEMINI_API_KEY` | Google AI Studio |
| `OPENAI_API_KEY` | OpenAI platform |
| `SUPABASE_URL` | Supabase dashboard → Project Settings → API |
| `SUPABASE_ANON_KEY` | Same |
| `SUPABASE_SERVICE_ROLE_KEY` | Same |
| `STRIPE_API_KEY` | Stripe dashboard → Developers → API keys |
| `STRIPE_WEBHOOK_SECRET` | Stripe dashboard → Developers → Webhooks |
| `JWT_SECRET` | Supabase dashboard → Project Settings → API → JWT Secret |
| `FERNET_ENCRYPTION_KEY` | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `ADMIN_PASSWORD` | Set a secure password for the legacy admin account |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` | Twilio Console |
| `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL`, `STAFF_NOTIFICATION_EMAIL` | SendGrid dashboard |
| `INTERNAL_SCHEDULER_SECRET` | `openssl rand -hex 32` |

### Launch (local Docker)

GCP ADC credentials are mounted into the backend container automatically. The local stack spins up its own postgres (port 5433) + redis (port 6380) — no Supabase dependency for local dev.

```bash
# Local dev stack (backend :8000, frontend :3000, postgres :5433, redis :6380)
docker compose up -d --build

# Demo stack
docker-compose -f docker-compose.demo.yml up -d --build
```

```powershell
# Windows demo scripts
.\start_demo.ps1           # Standard demo
.\start_live_demo.ps1      # Live Twilio WhatsApp demo (requires Cloudflare Tunnel)
```

### GCP Deployment

**Current state (as of 2026-03-29):** Re-deploying from v0.5.1. Artifact Registry (`nocturn-ai`) is active. Secret Manager has all critical secrets. Cloud Run services will be recreated by the deploy command below.

**Deploy (spin up):**
```bash
gcloud builds submit \
  --config=backend/cloudbuild.yaml \
  --project=nocturn-ai-487207 \
  --region=asia-southeast1 \
  --substitutions=COMMIT_SHA=$(git rev-parse HEAD) \
  .
```

After deploy, recreate Cloud Scheduler jobs if needed:
```bash
# Daily report (7:30am KL time)
gcloud scheduler jobs create http nocturn-daily-report \
  --location=asia-southeast1 --project=nocturn-ai-487207 \
  --schedule="30 7 * * *" --time-zone="Asia/Kuala_Lumpur" \
  --uri="https://nocturn-backend-<hash>-as.a.run.app/api/v1/internal/run-daily-report" \
  --message-body='{}' --headers="X-Internal-Secret=<INTERNAL_SCHEDULER_SECRET>"
```

**Spin down (save cost):**
```bash
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
| `GET /api/v1/portal/home` | Multi-property summary for tenant owner/admin |
| `GET /api/v1/portal/team` | List team members for tenant |
| `DELETE /api/v1/portal/team/{id}` | Remove team member |
| `GET /api/v1/portal/channels` | Channel status + web widget embed code per property |
| `GET/POST/PUT/DELETE /api/v1/properties/{id}/kb` | KB document CRUD (tenant self-service) |
| `POST /api/v1/properties/{id}/kb/ingest-wizard` | Structured bulk KB ingestion (rooms/FAQs/policies) |
| `POST /api/v1/onboarding/complete/{property_id}` | Activate property (finish onboarding wizard) |
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
│   │   ├── config.py                # Settings — GCP Secret Manager only, no .env fallback
│   │   ├── database.py              # Async SQLAlchemy engine + RLS context
│   │   ├── models.py                # All ORM models
│   │   ├── schemas.py               # Pydantic request/response schemas
│   │   ├── auth.py                  # JWT + check_property_access / check_tenant_access
│   │   ├── routes/
│   │   │   ├── admin.py             # Property CRUD, settings, system/info, announcements/active
│   │   │   ├── billing.py           # Stripe checkout + webhook
│   │   │   ├── channels.py          # Guest channel webhooks (WhatsApp, Email, Web Chat)
│   │   │   ├── internal.py          # Cloud Scheduler endpoints (X-Internal-Secret)
│   │   │   ├── onboarding.py        # Tenant provisioning, progress tracking, onboarding/complete
│   │   │   ├── portal.py            # Tenant self-service: home, team, channels, KB CRUD, KB wizard
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
│       ├── admin/                   # SheersSoft internal ops portal (/admin)
│       │   ├── announcements/       # Announcement broadcast management
│       │   ├── health/              # Service health dashboard
│       │   ├── kb-ingestion/        # KB setup tool for client properties
│       │   ├── system/              # Maintenance mode toggle
│       │   ├── tenants/             # Tenant management + detail
│       │   ├── pipeline/            # Onboarding pipeline kanban
│       │   └── tickets/             # Support ticket queue
│       ├── portal/                  # Tenant owner/admin portal (/portal)
│       │   ├── kb/[propertyId]/     # KB document management (tabbed by category)
│       │   ├── team/                # Team management + invite
│       │   ├── channels/            # Channel status + web widget embed code
│       │   ├── properties/          # Property list + add property
│       │   ├── billing/             # Subscription tier + Stripe checkout
│       │   └── support/             # Support ticket submit/view
│       ├── welcome/                 # Onboarding wizard (/welcome — 5 steps)
│       └── dashboard/               # Property staff operations (/dashboard)
│           ├── conversations/       # Guest inbox + staff reply
│           ├── insights/            # Monthly AI insights + KB gap suggestions
│           ├── leads/               # Lead triage + lost lead filter
│           ├── analytics/           # ROI metrics, CSV/PDF export
│           └── settings/            # Property configuration
├── docs/                            # Architecture, PRD, testing guides, build plan
├── scripts/
│   └── deploy_gcp.ps1               # Manual Cloud Run deploy (no Cloud SQL)
├── docker-compose.yml               # Production / dev stack (Supabase DB, no local postgres)
└── docker-compose.demo.yml          # Demo stack (Supabase DB, no local postgres)
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

# Database migrations (against Supabase — requires GCP ADC for DATABASE_URL)
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
- [x] Phase 1.6: Infra Migration — Supabase-only DB, GCP Secret Manager–only secrets, Cloud SQL removed
- [x] **v0.4.0: Self-Service Onboarding & Tenant Portal** — `/welcome` wizard, `/portal` owner layer, KB self-service, role-based auth routing, generic ICP (not Vivatel-specific)
- [x] **v0.5.0: Local Dev Stack + Demo Readiness** — local postgres/redis in docker-compose, google-genai SDK upgrade, gemini-embedding-001, RAG threshold fix, shadow pilot infrastructure (audit_only_mode, weekly audit report, /admin/shadow-pilots)
- [x] **v0.5.1: Infrastructure Hardening** — GCP Secret Manager project ID corrected (nocturn-ai-487207), cloudbuild.yaml SA fixed, LLM fallback chain reordered (Haiku as secondary), Docker frontend proxy URL fixed (backend:8080), Anthropic API key provisioned, WhatsApp GTM lead pipeline (10k leads, 330 WhatsApp-ready)

## Database & Supabase Notes

- **Hosted on Supabase** (`ramenghkpvipxijhfptp`, ap-southeast-2). App connects as `nocturn_app` via the transaction pooler (port 6543). `DATABASE_URL` is stored in GCP Secret Manager — never in `.env` files.
- **Free tier pause:** Supabase free tier projects auto-pause after 7 days of inactivity. Unpause from the Supabase dashboard before running locally or deploying.
- **pgvector:** Enabled natively on Supabase. `CREATE EXTENSION IF NOT EXISTS vector` runs at startup (idempotent).
- **Startup migrations:** `main.py` lifespan runs idempotent `CREATE TABLE IF NOT EXISTS` / `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` DDL on every cold start — safe to restart repeatedly.
- **Connection pooling:** `pool_size=2, max_overflow=5, pool_recycle=300` to fit Supabase free tier's 60-connection limit.
- **RLS:** Row-Level Security enabled. Call `set_db_context(session, property_id)` at the start of any session touching property-scoped data.
- **Migrations:** Managed via Alembic. Run `alembic upgrade head` with GCP ADC active to apply migrations against Supabase.
- **Custom SMTP:** Supabase Auth uses SendGrid SMTP (`smtp.sendgrid.net:465`) to bypass free-tier email rate limits.

## WhatsApp Channel Notes

- **Non-text messages:** Images, audio, video, and location pins receive a bilingual acknowledgement (EN + BM) instead of being silently ignored.
- **Error resilience:** If the AI pipeline fails, the guest still receives a human-readable fallback response.
- **Multi-tenant sender:** Outbound messages use each property's registered `twilio_phone_number` — not a shared global value.
- **LLM fallback chain:** Blank or failed responses fall through: Gemini → Anthropic Claude Haiku → OpenAI → template string.
- **Gemini embeddings:** Synchronous Gemini embedding call wrapped in `asyncio.to_thread()` — do not call directly from async code.
- **Bilingual responses:** All guest-facing error strings have both English and Bahasa Malaysia variants (`FALLBACK_RESPONSE` / `FALLBACK_RESPONSE_BM`).
