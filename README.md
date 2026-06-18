# Nocturn AI — Zero-Integration AI Concierge for Solopreneurs

An instant, web-based AI lead capture tool designed for service-based solopreneurs and SMBs. Stop burning your Meta ad spend because you can't reply to WhatsApp leads instantly while you're busy working.

**The Pitch:** Paste your URL, get an AI trained on your business that answers your WhatsApp leads 24/7.

## Architecture

- **Backend:** Python 3.12 + FastAPI (async SQLAlchemy, asyncpg)
- **Frontend:** Next.js 14 + TypeScript
- **Database:** Supabase PostgreSQL 17 + pgvector — user `nocturn_app`
- **Auth:** Supabase Auth (magic links) + local JWT fallback
- **LLMs:** Google Gemini (primary), Anthropic Claude Haiku (secondary), OpenAI GPT-4o-mini (tertiary)
- **Channels:** WhatsApp (Meta Cloud API & Twilio), Web Chat Widget
- **WhatsApp Bridge:** Baileys (`@whiskeysockets/baileys` v6.7) linked-device bridge — for instant, frictionless connection without Meta approvals.
- **Billing:** Stripe ($29/mo flat fee)
- **Infra:** GCP Cloud Run, GCP Secret Manager

## Key Features

1. **"Paste URL, Get AI" Onboarding:** Frictionless, self-serve onboarding. Paste your website or Instagram URL, and Nocturn scrapes your services, prices, and FAQs to train your AI instantly.
2. **Interactive Demo Window:** Test your custom AI directly in the browser within 60 seconds before committing to a plan.
3. **Frictionless WhatsApp Link:** Connect your existing WhatsApp Business number in 30 seconds by scanning a QR code (via the Baileys linked-device bridge). No IT setup. No Meta API approvals.
4. **24/7 Lead Capture:** AI answers inquiries instantly, capturing contact details and booking intent while you sleep or serve other clients.
5. **Seamless Human Handoff:** If a lead requires human judgment, the AI flags it in your dashboard for priority follow-up.
6. **Product-Led Growth (PLG):** Built for high-velocity acquisition via Meta Ads. Low-touch, fully automated provisioning via `/welcome`.

## Business Model

- **Free Trial:** 7 Days fully featured.
- **Solopreneur Plan:** $29/month flat fee.
- **Zero Setup Fees.** 

## Getting Started

### Prerequisites

#### 1. GCP credentials (required for Secret Manager access)

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project nocturn-aai
```

#### 2. Secrets in GCP Secret Manager (`nocturn-ai-487207`)

All required secrets (Supabase, LLMs, Stripe, Fernet, SendGrid) are pulled dynamically from GCP Secret Manager at runtime.

### Launch (local Docker)

```bash
# Demo stack (backend :8001, frontend :3001)
docker-compose -f docker-compose.demo.yml up -d --build

# Seed demo data
docker exec <backend-container> python seed_demo_data.py
```

### Frictionless Onboarding Flow (The User Journey)

```
1. User clicks Meta Ad → Lands on Nocturn AI homepage.
2. Enters website URL.
3. System scrapes business context → provisions temporary KB.
4. User tests the AI in a browser chat widget.
5. "Aha!" Moment achieved in < 60 seconds.
6. User creates account, starts 7-Day Free Trial.
7. Scans WhatsApp QR code to connect their number.
8. Live.
```

## API Surface

| Prefix | Purpose |
|--------|---------|
| `POST /api/v1/onboarding/scrape-url` | Scrapes target URL to auto-generate KB |
| `POST /api/v1/onboarding/provision` | Automated self-serve account creation |
| `GET /api/v1/whatsapp/qr` | Fetch Baileys QR for instant connection |
| `POST /api/v1/auth/magic-link` | Passwordless login |
| `POST /api/v1/billing/checkout` | Stripe trial/checkout session |
| `GET /api/v1/properties/{id}/leads` | Fetch captured leads |

## Development

```bash
# Backend
pip install -r backend/requirements.txt
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm install && npm run dev
```

## Database & Supabase Notes

- **Hosted on Supabase** (ap-southeast-2).
- **Startup migrations:** `main.py` lifespan runs idempotent DDL on every cold start.
- **pgvector:** Used for RAG on the scraped knowledge base.

## LLM Fallback Chain

- Primary: **Gemini 2.5 Flash** (fastest, cheapest)
- Secondary: **Claude Haiku** 
- Tertiary: **GPT-4o-mini**
- Error resilience: If the AI pipeline fails, the system returns a safe, generic fallback asking the guest to hold for a human.
