# Nocturn AI — Hotel Inquiry Capture & Conversion Engine

An AI-powered hotel inquiry capture system that recovers revenue lost after hours, tracks granular ROI, and is a fully multi-tenant SaaS platform built by SheersSoft.

**v0.8.0** — ICP Qualification, Billing Wizard Step, Audit Comparison, FPX Payment Link, 3% Performance Fee Attribution. Open gaps reduced to 2 (1 P1 · 1 P2).

## Architecture

- **Backend:** Python 3.12 + FastAPI (async SQLAlchemy, asyncpg) — v0.8.0
- **Frontend:** Next.js 14 + TypeScript — v0.8.0
- **Database:** Supabase PostgreSQL 17 + pgvector — user `nocturn_app`, transaction pooler (port 6543, ap-southeast-2)
- **Auth:** Supabase Auth (magic links) + local JWT fallback
- **LLMs:** Google Gemini (primary), Anthropic Claude Haiku (secondary), OpenAI GPT-4o-mini (tertiary)
- **Channels:** WhatsApp (Meta Cloud API & Twilio), Web Chat Widget, Email (SendGrid)
- **Shadow Pilot:** Baileys (`@whiskeysockets/baileys` v6.7) linked-device bridge — observe-only, no messages sent
- **Billing:** Stripe (one-time setup fee + subscription management)
- **Infra:** GCP Cloud Run (backend + frontend + baileys-bridge), GCP Secret Manager (`nocturn-ai-487207`)
- **Secrets:** All credentials exclusively from GCP Secret Manager — no `.env` files, no Cloud SQL
- **PII Compliance:** Fernet field-level encryption (PDPA 2010), SHA-256 phone hashing, GDPR/PDPA right-to-delete endpoint

## Key Features

1. **Shadow Pilot (Baileys Linked Device):** Hotel GM scans a QR code in the admin panel. Nocturn adds itself as a second linked device on their real WhatsApp Business number — observe-only, zero messages sent to guests. 7 days of data: response times, after-hours unanswered intents, revenue leakage in RM. Day-7 automated email report + token-gated GM dashboard at `/shadow/[slug]?token=...`. Core sales mechanism for proving ROI before contract.
2. **AI Conversation Engine (RAG):** Answers guest inquiries using a per-property knowledge base, captures leads, and escalates to human staff when needed. Three behavioral modes: Concierge → Lead Capture → Handoff.
3. **Multi-Tenant SaaS Architecture:** Hotel groups (Tenants) own multiple Properties. Staff access is scoped per-property via TenantMembership roles (`owner` / `admin` / `staff`).
4. **Self-Service Onboarding Wizard (`/welcome`):** Six-step guided setup — confirm property details, enter knowledge base, verify channels, invite team, complete RM 999 setup payment, activate AI. No SheersSoft engineer required after provisioning.
5. **Tenant Management Portal (`/portal`):** Owner/admin layer for configuring the business — manage KB documents, team members (invite/remove), channel status, billing, and support tickets. Separate from the day-to-day operations dashboard.
6. **Gamified Onboarding Flow:** SuperAdmin provisions a new tenant in one API call — creates Tenant, Property, User (via Supabase Auth), TenantMembership, and OnboardingProgress. Magic link sent automatically. Channel setup runs asynchronously. Progress score 0–100.
7. **Stripe Billing:** One-time RM 999 setup fee + RM 199/month + 3% performance fee on confirmed bookings.
8. **SuperAdmin Platform Dashboard (`/admin`):** Global KPIs, tenant pipeline (Provisioned → Channels Setup → Live → Fully Onboarded), shadow pilot management, support ticket queue, application intake, service health dashboard.
9. **Property Dashboard (`/dashboard`):** Staff reply inbox, lead triage (with lost lead filtering), analytics with CSV/PDF export, settings, ROI metrics, AI insights (monthly guest topics + KB gap suggestions).
10. **Daily GM Report (9 AM Briefing):** Automated email every morning at 9:00 AM MYT: 4 KPI cards (Revenue Recovered, OTA Fees Saved, Inquiries Handled, Guest Sentiment), queued leads table, Gemini sentiment summary.
11. **Monthly Guest Insights Report:** Gemini pipeline processes 30 days of transcripts — sentiment, recurring objections, FAQs, KB gap suggestions.
12. **PII Encryption & PDPA Delete:** Fernet encryption on guest PII at rest. SHA-256 phone hashing for shadow pilot deduplication. Right-to-delete endpoint anonymizes all data.

## Business Model

| Component | Amount |
|-----------|--------|
| Setup fee (one-time) | RM 999 |
| Platform fee | RM 199/month |
| Performance fee | 3% on confirmed direct bookings |
| Revenue recovery guarantee | 30 days — if not proven, next month free |

## Getting Started

### Prerequisites

#### 1. GCP credentials (required for Secret Manager access)

```bash
gcloud auth login
gcloud auth application-default login
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
| `ADMIN_PASSWORD` | Secure password for legacy admin account |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` | Twilio Console |
| `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL`, `STAFF_NOTIFICATION_EMAIL` | SendGrid dashboard |
| `INTERNAL_SCHEDULER_SECRET` | `openssl rand -hex 32` |

Non-secret config (set in `.env.demo` or Cloud Run env vars, not in Secret Manager):

```
ENVIRONMENT=demo
BAILEYS_BRIDGE_URL=http://localhost:3001   # or Cloud Run URL in production
GEMINI_MODEL=gemini-2.5-flash
ALLOWED_ORIGINS=http://localhost:3001
```

### Launch (local Docker)

```bash
# Demo stack (backend :8001, frontend :3001)
docker-compose -f docker-compose.demo.yml up -d --build

# Seed main demo data (Vivatel KL hotel, 30 days analytics, 3 conversation scenarios)
docker exec <backend-container> python seed_demo_data.py

# Seed shadow pilot demo data (7-day synthetic observation, prints GM dashboard URL)
docker exec <backend-container> python seed_shadow_pilot_demo.py
```

```powershell
# Windows all-in-one (builds, seeds main + shadow pilot, prints GM dashboard URL)
.\start_live_demo.ps1
```

### Shadow Pilot — First Real Hotel

```
1. Admin panel → /admin/shadow-pilots → [+ New Shadow Pilot]
2. Enter: hotel phone, GM email, ADR, avg stay nights, operating hours
3. QR code displayed — GM scans with WhatsApp Business phone
4. Admin panel shows "● Connected"
5. Observe for 7 days (no action needed — zero messages sent)
6. Day-7: GM receives revenue leakage email + token-gated dashboard link
7. Day-8: SheersSoft AM calls with ROI proof → contract sign
```

### GCP Deployment

```bash
# Deploy all 3 services (backend + frontend + baileys-bridge)
gcloud builds submit \
  --config=backend/cloudbuild.yaml \
  --project=nocturn-ai-487207 \
  --region=asia-southeast1 \
  --substitutions=COMMIT_SHA=$(git rev-parse HEAD) \
  .

# After deploy: add BAILEYS_BRIDGE_URL to Secret Manager
echo -n "https://nocturn-baileys-bridge-<hash>-as.a.run.app" | \
  gcloud secrets create BAILEYS_BRIDGE_URL --data-file=- --project=nocturn-ai-487207
```

**Recreate Cloud Scheduler jobs after deploy:**

```bash
SECRET=$(gcloud secrets versions access latest --secret=INTERNAL_SCHEDULER_SECRET --project=nocturn-ai-487207)
BE=https://nocturn-backend-<hash>-as.a.run.app

# Shadow Pilot jobs (new)
gcloud scheduler jobs create http shadow-pilot-daily-aggregation \
  --schedule="0 0 * * *" --location=asia-southeast1 --project=nocturn-ai-487207 \
  --uri="$BE/api/v1/internal/run-shadow-pilot-aggregation" \
  --message-body='{}' --headers="X-Internal-Secret=$SECRET"

gcloud scheduler jobs create http shadow-pilot-weekly-report \
  --schedule="0 8 * * 1" --location=asia-southeast1 --project=nocturn-ai-487207 \
  --uri="$BE/api/v1/internal/run-shadow-pilot-weekly-report" \
  --message-body='{}' --headers="X-Internal-Secret=$SECRET"

# Standard jobs
gcloud scheduler jobs create http nocturn-daily-report \
  --schedule="0 9 * * *" --time-zone="Asia/Kuala_Lumpur" \
  --location=asia-southeast1 --project=nocturn-ai-487207 \
  --uri="$BE/api/v1/internal/run-daily-report" \
  --message-body='{}' --headers="X-Internal-Secret=$SECRET"

gcloud scheduler jobs create http nocturn-followups \
  --schedule="0 * * * *" --location=asia-southeast1 --project=nocturn-ai-487207 \
  --uri="$BE/api/v1/internal/run-followups" \
  --message-body='{}' --headers="X-Internal-Secret=$SECRET"

gcloud scheduler jobs create http nocturn-insights \
  --schedule="0 8 1 * *" --location=asia-southeast1 --project=nocturn-ai-487207 \
  --uri="$BE/api/v1/internal/run-insights" \
  --message-body='{}' --headers="X-Internal-Secret=$SECRET"

gcloud scheduler jobs create http nocturn-cleanup-leads \
  --schedule="0 3 * * 0" --location=asia-southeast1 --project=nocturn-ai-487207 \
  --uri="$BE/api/v1/internal/cleanup-leads" \
  --message-body='{}' --headers="X-Internal-Secret=$SECRET"

gcloud scheduler jobs create http nocturn-weekly-audit \
  --schedule="0 8 * * 1" --location=asia-southeast1 --project=nocturn-ai-487207 \
  --uri="$BE/api/v1/internal/run-weekly-audit-report" \
  --message-body='{}' --headers="X-Internal-Secret=$SECRET"
```

**Spin down:**
```bash
gcloud run services delete nocturn-backend --project=nocturn-ai-487207 --region=asia-southeast1 --quiet
gcloud run services delete nocturn-frontend --project=nocturn-ai-487207 --region=asia-southeast1 --quiet
gcloud run services delete nocturn-baileys-bridge --project=nocturn-ai-487207 --region=asia-southeast1 --quiet
```

**New machine setup:**
```bash
gcloud auth login && gcloud auth application-default login
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
  │   ├─ shadow_pilot_mode, shadow_pilot_session_active, shadow_pilot_start_date
  │   ├─ shadow_pilot_dashboard_token (30-day JWT for token-gated GM dashboard)
  │   ├─ adr, avg_stay_nights (revenue leakage formula inputs)
  │   └─ Conversations, Messages, Leads, KBDocuments, AnalyticsDaily
  │       ShadowPilotConversation (encrypted phone, intent, response times)
  │       ShadowPilotAnalyticsDaily (30+ daily metrics, revenue leakage)
  ├─ TenantMembership → role: "owner" | "admin" | "staff"
  └─ OnboardingProgress (per property, gamified 0–100 score)

User (1:1 with Supabase auth.users, is_superadmin for SheersSoft staff)
SupportTicket (tenant user → SheersSoft staff)
Application (public intake → converts to Tenant)
```

## API Surface

| Prefix | Purpose |
|--------|---------|
| `POST /api/v1/superadmin/shadow-pilots` | Provision shadow pilot (sets mode, triggers QR) |
| `GET /api/v1/superadmin/shadow-pilots/{id}/qr` | Fetch QR from Baileys bridge |
| `DELETE /api/v1/superadmin/shadow-pilots/{id}` | Stop pilot, disconnect session |
| `GET /api/v1/superadmin/shadow-pilots/{id}/analytics` | Daily analytics rows |
| `GET /api/v1/shadow/{slug}/summary?token=...` | Token-gated GM dashboard (no auth) |
| `POST /api/v1/internal/shadow-event` | Baileys bridge → message received/sent |
| `POST /api/v1/internal/shadow-session-status` | Session connected/disconnected |
| `POST /api/v1/internal/shadow-heartbeat` | 60s keepalive from bridge |
| `GET /api/v1/internal/shadow-active-properties` | Bridge startup discovery |
| `POST /api/v1/internal/run-shadow-pilot-aggregation` | Cloud Scheduler daily job |
| `POST /api/v1/internal/run-shadow-pilot-weekly-report` | Cloud Scheduler weekly job |
| `POST /api/v1/auth/token` | Legacy JWT login |
| `POST /api/v1/auth/magic-link` | Supabase magic link |
| `POST /api/v1/onboarding/provision-tenant` | One-click tenant provisioning |
| `GET /api/v1/onboarding/progress/{tenant_id}` | Onboarding score |
| `POST /api/v1/billing/checkout` | Stripe checkout session |
| `POST /api/v1/leads/{id}/payment-link` | Generate Stripe FPX payment link for a room booking lead |
| `GET /api/v1/superadmin/metrics` | Platform-wide KPIs |
| `GET /api/v1/superadmin/service-health` | 9-service health check |
| `GET /api/v1/portal/home` | Multi-property summary |
| `GET/POST/PUT/DELETE /api/v1/properties/{id}/kb` | KB document CRUD |
| `POST /api/v1/staff/reply` | Staff reply to guest |
| `POST /api/v1/webhook/whatsapp` | Meta WhatsApp webhook |
| `POST /api/v1/webhook/twilio/whatsapp` | Twilio WhatsApp webhook |
| `POST /api/v1/webhook/email` | SendGrid inbound email |
| `DELETE /api/v1/gdpr/delete-guest/{property_id}/{identifier}` | PDPA right-to-delete |
| `POST /api/v1/internal/run-daily-report` | Cloud Scheduler (X-Internal-Secret) |
| `POST /api/v1/internal/run-followups` | Cloud Scheduler |
| `POST /api/v1/internal/run-insights` | Cloud Scheduler |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, lifespan, DDL migrations
│   │   ├── config.py                # Settings — GCP Secret Manager + env vars
│   │   ├── models.py                # All ORM models (incl. ShadowPilotConversation/AnalyticsDaily)
│   │   ├── auth.py                  # JWT + check_property_access / check_tenant_access
│   │   ├── routes/
│   │   │   ├── internal.py          # Cloud Scheduler + Baileys bridge endpoints
│   │   │   ├── shadow_pilot_public.py  # Token-gated GM dashboard (no auth)
│   │   │   ├── superadmin.py        # Platform dashboard + shadow pilot management
│   │   │   ├── channels.py          # Guest channel webhooks (WhatsApp, Email, Web Chat)
│   │   │   ├── onboarding.py        # Tenant provisioning + onboarding wizard
│   │   │   ├── portal.py            # Tenant self-service (KB, team, channels)
│   │   │   ├── billing.py           # Stripe checkout + webhook
│   │   │   ├── staff.py             # Staff reply + conversation inbox
│   │   │   └── support.py           # Support chatbot + ticket CRUD
│   │   └── services/
│   │       ├── shadow_pilot_processor.py   # Baileys event handler (observe-only)
│   │       ├── shadow_pilot_classifier.py  # LLM intent classifier (7 intents, BM+EN)
│   │       ├── shadow_pilot_aggregator.py  # Daily rollup (30+ metrics, revenue leakage)
│   │       ├── shadow_pilot_reporter.py    # Weekly HTML email + token-gated dashboard data
│   │       ├── whatsapp_transport.py       # BaileysTransport (observe_only flag)
│   │       ├── conversation.py      # Core AI engine (RAG, 3 modes, bilingual EN/BM)
│   │       ├── analytics.py         # ROI metric calculations
│   │       ├── email.py             # SendGrid delivery
│   │       ├── pii_encryption.py    # Fernet field-level PII encryption
│   │       └── scheduler.py         # APScheduler (dev/demo) + Daily GM Report
│   ├── tests/
│   │   ├── test_shadow_pilot.py     # 26 tests: processor, classifier, aggregator, API, zero-reply gate
│   │   ├── test_ai_accuracy.py      # 50-question BM+EN accuracy gate (≥80% required)
│   │   ├── test_channels.py         # WhatsApp/Email webhook integration
│   │   ├── test_billing.py          # Stripe billing flows
│   │   └── ...
│   ├── seed_demo_data.py            # Main demo data (Vivatel KL, 3 scenarios, 30 days analytics)
│   ├── seed_shadow_pilot_demo.py    # 7-day synthetic shadow pilot data → prints GM dashboard URL
│   ├── rebuild_supabase.py          # Schema rebuild + RLS + GRANT nocturn_app
│   ├── cloudbuild.yaml              # GCP CI/CD: backend + frontend + baileys-bridge
│   └── requirements.txt
├── baileys-bridge/                  # Node.js TypeScript WhatsApp bridge (separate Cloud Run service)
│   ├── src/
│   │   ├── index.ts                 # Express API: start-session, stop-session, QR, health
│   │   ├── session-manager.ts       # Baileys socket management: QR, reconnect, heartbeat
│   │   └── event-forwarder.ts       # HTTP POST to FastAPI internal endpoints
│   ├── Dockerfile                   # node:20-alpine, min-instances=1 (persistent sessions)
│   └── package.json                 # @whiskeysockets/baileys v6.7
├── frontend/
│   └── src/app/
│       ├── admin/shadow-pilots/     # QR provisioning flow, session status badges
│       ├── shadow/[slug]/           # Token-gated GM dashboard (public, no login)
│       ├── admin/                   # SheersSoft internal ops portal (/admin)
│       ├── portal/                  # Tenant owner/admin portal (/portal)
│       ├── welcome/                 # Onboarding wizard (/welcome)
│       └── dashboard/               # Property staff operations (/dashboard)
├── docs/
│   ├── product_gap.md               # Gap analysis v3.0 — 2 open gaps (26 Apr 2026)
│   ├── shadow_pilot_spec.md         # Canonical implementation reference (1,332 lines)
│   ├── prd.md                       # PRD v2.5
│   ├── architecture.md              # Architecture v2.5 (incl. Baileys bridge)
│   └── build_plan.md                # Sprint 2.5 + 2.6 plan
├── .env.demo                        # Non-secret demo config (ENVIRONMENT, BAILEYS_BRIDGE_URL, etc.)
├── docker-compose.demo.yml          # Demo stack (Redis + backend + frontend)
├── start_live_demo.ps1              # Windows: build + seed main + seed shadow pilot + instructions
└── start_demo.ps1                   # Windows: quick local demo (no Docker)
```

## Revenue Leakage Formula

```
Daily leakage = (after_hours_unanswered_booking_intent × ADR × avg_stay_nights × 0.20 × 0.60)
              + (slow_response_booking_intent × ADR × avg_stay_nights × 0.15)

Weekly leakage = sum of 7 daily rows
Annualised     = weekly × 52
Net year-1 recovery = max(0, annualised × 0.60 − (RM 999 + RM 199 × 12))
```

Default ADR: RM 230. Default avg_stay_nights: 1.0. Conservative 60% discount applied.

## Development

```bash
# Backend
pip install -r backend/requirements.txt
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Tests
cd backend && pytest                                    # All tests
cd backend && pytest tests/test_shadow_pilot.py -v     # Shadow pilot suite (26 tests)
cd backend && pytest tests/test_ai_accuracy.py -v      # BM+EN accuracy gate (needs seeded DB)

# Seed (requires GCP ADC + DATABASE_URL in Secret Manager)
cd backend && python seed_demo_data.py
cd backend && python seed_shadow_pilot_demo.py          # Prints GM dashboard URL

# Schema rebuild (Supabase — run once after major schema changes)
cd backend && python rebuild_supabase.py
```

## Sprint Completion Status

- [x] **v0.4.0** — Self-Service Onboarding & Tenant Portal
- [x] **v0.5.0** — Local Dev Stack + Demo Readiness
- [x] **v0.5.1** — Infrastructure Hardening (GCP Secret Manager, LLM fallback chain)
- [x] **v0.5.3** — Daily GM Report (9 AM revenue briefing, Gemini sentiment)
- [x] **v0.5.4** — Document Alignment & Hybrid-First Refinement
- [x] **v0.6.0** — Shadow Pilot (Baileys Linked Device):
  - Baileys bridge as separate Cloud Run service (Node.js TypeScript, `min-instances=1`)
  - `ShadowPilotConversation` + `ShadowPilotAnalyticsDaily` models with 30+ metrics
  - Intent classifier (7 intents, EN + BM), after-hours detection, Fernet phone encryption
  - Daily aggregation job + weekly HTML report email (revenue leakage, sample convs, What-If)
  - Token-gated GM dashboard at `/shadow/[slug]?token=...` (no auth, 30-day JWT)
  - SuperAdmin panel: QR provisioning flow with 3s polling, session status badges
  - `seed_shadow_pilot_demo.py`: 7-day synthetic data for sales demos
  - 26-test suite covering processor, classifier, aggregator, API auth, zero-reply gate

- [x] **v0.6.1** — Gap Analysis & Production Hardening:
  - Full codebase audit against `nocturn_hybrid_value_flow.html` — 11 gaps documented in `docs/product_gap.md`
  - Shadow pilot DDL migrations applied to production Supabase (properties + 2 new tables)
  - All 8 Cloud Scheduler jobs enabled and verified (including 2 new shadow pilot jobs)
  - `BAILEYS_BRIDGE_URL` + `INTERNAL_SECRET` secrets added to GCP Secret Manager

- [x] **v0.7.0** — Hybrid Co-Pilot & Revenue Activation:
  - GAP-004: Day-7 report property-relative timing fix (verified in `shadow_pilot_reporter.py`)
  - GAP-006: Hybrid reply drafting sidebar in `/dashboard/conversations` (EN/BM toggles + AI Drafts)
  - GAP-010: Stripe RM 199/month recurring subscription wiring (webhook handling for lifecycle events)
  - GAP-003: KB self-service implemented in `/portal/kb/`
  - Reduced open gaps to 7 (0 P0 · 6 P1 · 1 P2)

- [x] **v0.8.0** — ICP Qualification & Revenue Activation:
  - GAP-001: `/apply` form captures ADR, monthly inquiry volume, star rating (Application model + DDL)
  - GAP-002: Welcome wizard expanded to 6 steps — Step 5 is RM 999 Stripe checkout with skip-for-now flow
  - GAP-005: AuditRecord linked to shadow pilot at provisioning; Day-7 email shows estimated vs observed leakage comparison
  - GAP-008: FPX/card direct booking payment link via Stripe PaymentLink — staff generates from conversations sidebar; `payment_link.completed` webhook confirms booking
  - GAP-009: 3% performance fee attribution — Lead + Tenant tracking, monthly APScheduler billing job, analytics dashboard card
  - Open gaps reduced to 2: GAP-007 (Google Sheet inventory) P1 · GAP-011 (30-day guarantee enforcement) P2

**Next — Sprint 2.8 (GAP-007 + Production Readiness):**
- GAP-007: Google Sheet inventory reader (2-min polling, gspread, inject into AI system prompt)
- Stripe `payment_method_types` configuration (verify FPX via Dashboard for current API version)
- BM 50-question accuracy test gate (≥80% required before first live client)

## Database & Supabase Notes

- **Hosted on Supabase** (`ramenghkpvipxijhfptp`, ap-southeast-2). App connects as `nocturn_app` via the transaction pooler (port 6543).
- **Startup migrations:** `main.py` lifespan runs idempotent DDL on every cold start — safe to restart.
- **Shadow pilot tables:** `shadow_pilot_conversations` and `shadow_pilot_analytics_daily` — created via in-code DDL migrations (not Alembic).
- **GRANT:** After schema rebuild, `rebuild_supabase.py` grants `SELECT, INSERT, UPDATE, DELETE` on all tables to `nocturn_app`.
- **pgvector:** `CREATE EXTENSION IF NOT EXISTS vector` runs at startup.
- **Connection pooling:** `pool_size=2, max_overflow=5, pool_recycle=300`.

## WhatsApp Notes

- **Shadow mode:** `BaileysTransport(observe_only=True)` — `send_message()` is a no-op that logs a warning. Used during 7-day pilot. Critical guarantee: zero messages ever sent to guests.
- **Non-text messages:** Images, audio, video, location → bilingual acknowledgement (EN + BM).
- **Error resilience:** If AI pipeline fails, guest receives a human-readable fallback response.
- **LLM fallback chain:** Gemini → Anthropic Claude Haiku → OpenAI → template string.
- **Bilingual responses:** All guest-facing error strings have EN and BM variants.
