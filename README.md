# SheersSoft AI Inquiry Capture & Conversion Engine

An AI-powered hotel inquiry capture system that recovers revenue lost after hours and tracks granular ROI.

## Architecture

- **Backend:** Python 3.12 + FastAPI
- **Frontend:** Next.js 14 + TypeScript + TailwindCSS
- **Database:** PostgreSQL 16 + pgvector (Semantic AI Search)
- **LLMs:** Google Gemini (Primary), OpenAI GPT-4o-mini & Anthropic (Fallbacks)
- **Channels:** WhatsApp (Meta Cloud API & Twilio), Web Chat Widget, Email (SendGrid)

## Key Features

1. **AI Conversation Engine (RAG):** Answers guest inquiries using a knowledge-base, captures leads, and hands off complex issues seamlessly.
2. **"Paste & Go" Integrations Setup:** Zero code changes required for integrating Meta, Twilio, SendGrid, and AI credentials. Configured entirely via GCP Secret Manager.
3. **Demo Mode Orchestrator:** Fully isolated environment running on simulated channel data with 100+ native conversation scenarios for flawless sales pitches without touching production. 
4. **Operations Tuning:** Revenue managers can tune AI personas, set required screening questions, and input front desk hourly wages directly via the Dashboard Settings interface.
5. **Advanced Analytics & Export:** 
   - Real-time pipeline calculation estimating Gross Revenue Recovered and Ops Cost Savings.
   - Broad time-scaling filters (Daily, Weekly, Monthly, Quarterly, Yearly, Custom).
   - Generates CSV tabular spreadsheets and exports Canvas-rendered visual PDF reports in-browser.

## Getting Started

1. **Setup Integrations (Phase 0):** Push API keys for Gemini, OpenAI, WhatsApp, Twilio, and SendGrid to GCP Secret Manager (project `nocturn-ai-487207`). See `.env.example` for the list of required secret keys.
2. **Launch the Real Application:**
   ```powershell
   docker-compose up -d --build
   ```
3. **Launch the Local Simulated Demo Stack:**
   ```powershell
   .\start_demo.ps1
   ```
   *Note: This starts an entirely separate stack (`docker-compose.demo.yml`) with pre-seeded demo properties and mock conversations, accessible at port `3001`.*

4. **Launch the Live Interactive Sales Demo Stack:**
   ```powershell
   .\start_live_demo.ps1
   ```
   *Prerequisites:*
   - Push Twilio credentials (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`) to GCP Secret Manager (`nocturn-ai-487207`).
   - Start a Cloudflare Tunnel: `cloudflared tunnel --url http://localhost:8001`
   - Configure the Twilio WhatsApp Sender webhook to: `https://<tunnel-url>/api/v1/webhook/twilio/whatsapp`
   - After seeding, patch the demo property's `twilio_phone_number` in the database if GCP ADC is unavailable inside Docker.

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── database.py          # Async SQLAlchemy engine
│   │   ├── models.py            # Database tables
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routes/              # Modular API endpoints
│   │   └── services/            # Core logic, LLMs, integrations, RAG
│   ├── scripts/
│   │   ├── seed_demo_data.py    # Database seeder for demo state
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                    # Next.js 14 Dashboard
├── scripts/                     # External Powershell & Node workflow scripts
├── docs/                        # Research & technical playbooks
├── docker-compose.yml           # Production & Dev Stack
└── docker-compose.demo.yml      # Isolated Demo Stack
```

## Sprint Completion Status

Everything from the blueprint has been fully implemented:

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

## WhatsApp Channel — Reliability Notes

The following hardening was applied to ensure a consistent guest experience:

- **Non-text messages handled gracefully:** Guests who send images, audio, video, or location pins now receive a bilingual acknowledgement (*"I can only read text messages / Saya hanya boleh membaca mesej teks"*) instead of being silently ignored.
- **Fallback reply on processing errors:** If the AI pipeline or database fails mid-message, the guest still receives a human-readable fallback message rather than seeing no response at all.
- **Multi-tenant Twilio sender fixed:** Outbound Twilio messages now use each property's registered `twilio_phone_number` as the sender, not a shared global value.
- **Empty LLM response protection:** A blank response from Gemini or OpenAI now falls through to the next provider in the chain (Gemini → OpenAI → Anthropic → template) instead of being saved as an empty AI message.
- **Gemini embedding no longer blocks the event loop:** The synchronous Gemini embedding call is now run via `asyncio.to_thread()`, keeping response latency predictable under concurrent load.
- **Weekly data retention job fixed:** A missing `timezone` import in the scheduler would have caused the PDPA/GDPR cleanup job to crash with a `NameError`; this is now resolved.
