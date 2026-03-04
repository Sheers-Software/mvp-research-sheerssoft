# SheersSoft AI Inquiry Capture & Conversion Engine

An AI-powered hotel inquiry capture system that recovers revenue lost after hours, tracks granular ROI, and is now a fully multi-tenant SaaS platform.

## Architecture

- **Backend:** Python 3.11 + FastAPI (async SQLAlchemy, asyncpg)
- **Frontend:** Next.js + TypeScript + TailwindCSS
- **Database:** PostgreSQL 16 + pgvector (Supabase-hosted)
- **Auth:** Supabase Auth (magic links) + local JWT fallback
- **LLMs:** Google Gemini (Primary), OpenAI GPT-4o-mini & Anthropic Claude (Fallbacks)
- **Channels:** WhatsApp (Meta Cloud API & Twilio), Web Chat Widget, Email (SendGrid)
- **Billing:** Stripe (one-time setup fee + subscription management)
- **Secrets:** GCP Secret Manager (`nocturn-ai-487207`) — all API keys resolved via ADC

## Key Features

1. **AI Conversation Engine (RAG):** Answers guest inquiries using a property knowledge base, captures leads, and hands off complex issues seamlessly.
2. **Multi-Tenant SaaS Architecture:** Hotel groups (Tenants) can own multiple Properties. Staff access is scoped per-property via TenantMembership roles (`owner` / `admin` / `staff`).
3. **Gamified Onboarding Flow:** SuperAdmin provisions a new tenant in one API call — creates Tenant, Property, User (via Supabase Auth), TenantMembership, and OnboardingProgress. Sends magic link automatically. Channel setup runs asynchronously. Progress score (0–100) surfaced in dashboard.
4. **Stripe Billing:** One-time $150 setup fee via Stripe Checkout. Webhook activates tenant subscription on payment completion.
5. **SuperAdmin Platform Dashboard:** Global platform metrics, tenant pipeline (Provisioned → Channels Setup → Live → Fully Onboarded), support ticket queue, application intake from `ai.sheerssoft.com/apply`.
6. **Support Chatbot:** Reuses the core AI engine on a dedicated `nocturn-ai-support` property. Detects handoff intent and escalates to SheersSoft staff.
7. **"Paste & Go" Integrations Setup:** Zero code changes required. All API keys configured entirely via GCP Secret Manager.
8. **Demo Mode Orchestrator:** Fully isolated environment with 100+ pre-seeded conversation scenarios.
9. **Advanced Analytics & Export:** Revenue recovered, cost savings, CSV export, canvas-rendered PDF reports, broad time-scale filters.
10. **Automated Follow-up Engine:** AI re-engages cold leads at 24h, 72h, and 7-day intervals.
11. **Monthly Guest Insights Report:** RAG pipeline processes 30 days of transcripts to compile sentiment, recurring objections, and FAQs.

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

### Launch

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

**Live WhatsApp demo prerequisites:**
- Push Twilio credentials to GCP Secret Manager
- Start a Cloudflare Tunnel: `cloudflared tunnel --url http://localhost:8001`
- Configure the Twilio WhatsApp Sender webhook to: `https://<tunnel-url>/api/v1/webhook/twilio/whatsapp`

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
| `POST /api/v1/support/chat` | Support chatbot |
| `POST /api/v1/applications` | Public application intake |
| `POST /api/v1/webhook/whatsapp` | Meta WhatsApp webhook |
| `POST /api/v1/webhook/twilio/whatsapp` | Twilio WhatsApp webhook |
| `POST /api/v1/webhook/email` | SendGrid inbound email |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings + GCP Secret Manager resolution
│   │   ├── database.py          # Async SQLAlchemy engine + RLS context
│   │   ├── models.py            # All ORM models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # JWT + check_property_access / check_tenant_access
│   │   ├── routes/
│   │   │   ├── billing.py       # Stripe checkout + webhook
│   │   │   ├── onboarding.py    # Tenant provisioning + progress
│   │   │   ├── superadmin.py    # Platform dashboard + pipeline
│   │   │   ├── support.py       # Support chatbot + tickets
│   │   │   └── channels.py      # Guest channel webhooks
│   │   └── services/
│   │       ├── conversation.py  # Core AI engine (RAG, 3 modes, bilingual)
│   │       ├── stripe_service.py
│   │       ├── channel_setup.py
│   │       └── insights.py
│   ├── tests/
│   │   ├── test_billing.py      # Stripe tests (7/7 pass, fully mocked)
│   │   ├── test_supabase.py     # Supabase connectivity (live, skips gracefully)
│   │   └── ...
│   ├── supabase/                # Supabase CLI local dev config
│   ├── cloudbuild.yaml          # GCP Cloud Build CI/CD
│   └── requirements.txt
├── frontend/                    # Next.js Dashboard
├── docs/                        # Architecture, PRD, testing guides
├── docker-compose.yml           # Production / dev stack
└── docker-compose.demo.yml      # Isolated demo stack
```

## Development

```bash
# Backend
pip install -r backend/requirements.txt
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Tests
cd backend && pytest                          # All tests
cd backend && pytest tests/test_billing.py -v # Billing (no DB required)
cd backend && pytest tests/test_supabase.py -v # Supabase live (requires GCP ADC)

# Migrations
cd backend && alembic upgrade head
cd backend && alembic revision --autogenerate -m "description"
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
- [x] Phase 9: AI Personas, Brand Scripting, Metrics Tracking Additions
- [x] Phase 10: Live Metric and Operations End-to-End Validation
- [x] Phase 11: Advanced Analytics Date Filtering, CSV & PDF Reporting
- [x] Phase 12: Live WhatsApp Demo via Twilio (Approved Sender + Cloudflare Tunnel)
- [x] Phase 13: WhatsApp Reliability & Consistency Hardening
- [x] Phase 14: Gap Resolution (Automated Follow-ups, Revenue Tracking, Monthly AI Briefings)
- [x] Phase 15: Multi-Tenant SaaS — Stripe Billing, Supabase Auth, Onboarding Flow, SuperAdmin Dashboard

## Database & Supabase Notes

- **Hosted on Supabase** (`ramenghkpvipxijhfptp`). `DATABASE_URL` is loaded from GCP Secret Manager; no hardcoded credentials.
- **Free tier pause:** Supabase free tier projects auto-pause after 7 days of inactivity. Unpause from the Supabase dashboard to restore DB connectivity.
- **Connection:** Uses Supabase's Session Pooler when direct connection is unavailable. Set `sslmode=require` in the URL.
- **Migrations:** Managed via Alembic. For DDL-heavy migrations against the pooler, use `npx supabase db push` with the Supabase CLI.
- **RLS:** Row-Level Security is enabled. Call `set_db_context(session, property_id)` at the start of any session touching property-scoped data.

## WhatsApp Channel — Reliability Notes

- **Non-text messages handled gracefully:** Images, audio, video, and location pins receive a bilingual acknowledgement instead of being silently ignored.
- **Fallback reply on errors:** If the AI pipeline fails mid-message, the guest still receives a human-readable fallback response.
- **Multi-tenant Twilio sender:** Outbound messages use each property's registered `twilio_phone_number`, not a shared global value.
- **Empty LLM response protection:** Blank responses fall through to the next provider (Gemini → OpenAI → Anthropic → template).
- **Gemini embedding non-blocking:** The synchronous Gemini embedding call is wrapped in `asyncio.to_thread()`.
