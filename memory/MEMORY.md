# Project Memory — Nocturn AI / SheersSoft

## GCP / Infrastructure

- **GCP Project**: `nocturn-ai-487207` (numeric: `343745766874`)
- **GCP ADC**: Run `gcloud auth application-default login` on each new machine
- **Supabase project ref**: `ramenghkpvipxijhfptp` → `https://ramenghkpvipxijhfptp.supabase.co`
- **Supabase status**: Free tier — auto-pauses after 7 days inactivity. Unpause from Supabase dashboard. Upgrade to Pro before first paying tenant.

## Live GCP Deployment (Cloud Run — asia-southeast1)

| Service | URL | Config |
|---------|-----|--------|
| **Backend** | `https://nocturn-backend-owtn645vea-as.a.run.app` | 1 vCPU, 1GB, min=1, CPU always-on, port 8080 |
| **Frontend** | `https://nocturn-frontend-owtn645vea-as.a.run.app` | 1 vCPU, 512MB, min=0, CPU-throttled, port 3000 |

- **Artifact Registry**: `asia-southeast1-docker.pkg.dev/nocturn-ai-487207/nocturn-ai/`
- **Cloud Run SA**: `nocturn-cloud-run@nocturn-ai-487207.iam.gserviceaccount.com`
- **Database on Cloud Run**: Supabase free tier (healthy, connected via Secret Manager URL)
- **Redis on Cloud Run**: In-memory fallback (no Memorystore; acceptable for pilot single-instance)
- **APScheduler**: Disabled in production (`ENVIRONMENT=production`). Cloud Scheduler jobs NOT yet created — this is the next infra task.
- **Deploy command**: `gcloud builds submit --config=backend/cloudbuild.yaml --project=nocturn-ai-487207 --region=asia-southeast1 --substitutions=COMMIT_SHA=$(git rev-parse HEAD) .`

## GCP Secret Manager — Full State

Secrets **confirmed in** Secret Manager (`nocturn-ai-487207`):
- `DATABASE_URL` (has BOM — stripped in config.py automatically)
- `GEMINI_API_KEY`, `OPENAI_API_KEY`
- `JWT_SECRET`, `JWT_ALGORITHM`, `JWT_EXPIRY_HOURS`
- `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET` (⚠️ currently local CLI secret — update after adding live Stripe webhook)
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`, `TWILIO_API_KEY_SID`, `TWILIO_API_KEY_SECRET`
- `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN`
- `INTERNAL_SCHEDULER_SECRET` (protects `/api/v1/internal/*` endpoints)
- `SUPABASE_ACCESS_TOKEN`

Secrets **still missing** (add from respective dashboards):
- `FERNET_ENCRYPTION_KEY` — generate: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- `ANTHROPIC_API_KEY` — from Anthropic console
- `SENDGRID_API_KEY` — from SendGrid dashboard
- `WHATSAPP_API_TOKEN`, `WHATSAPP_APP_SECRET` — from Meta developer console

## Stripe

- **Local listener secret** (dev only): stored as `STRIPE_WEBHOOK_SECRET` in Secret Manager
- **Live webhook URL**: `https://nocturn-backend-owtn645vea-as.a.run.app/api/v1/billing/webhook`
- **To go live**: Add endpoint in Stripe Dashboard → Developers → Webhooks. Copy new `whsec_`, then: `echo -n "whsec_..." | gcloud secrets versions add STRIPE_WEBHOOK_SECRET --data-file=- --project=nocturn-ai-487207`
- **Local listener** (Windows): `.\stripe_webhook_listen.ps1` (Stripe CLI installed via winget)
- **Stripe account**: Sheers Software Sdn Bhd sandbox (`acct_1RqmsMP5doWxcb8U`)
- **Test mode key**: stored in `C:\Users\abasy\.config\stripe\config.toml` (expires 2026-06-02)

## Database / Config Notes

- `database_url` default is `""` so Secret Manager loads Supabase URL; local fallback kicks in if SM unreachable
- BOM (`\ufeff`) stripped in `config.py` with `.strip().lstrip("\ufeff")`
- Config converts `postgresql://` → `postgresql+asyncpg://` AFTER Secret Manager fetch
- Pool: `pool_size=2, max_overflow=5` — fits Supabase free tier 60-connection limit
- `INTERNAL_SCHEDULER_SECRET` fetched from Secret Manager; protects Cloud Scheduler HTTP endpoints

## Docs State (17 Mar 2026)

- **Active docs** in `docs/`: prd.md (v2.0), architecture.md (v2.0), build_plan.md (v2.0), **product_gap.md (v1.0 — new)**, opportunity_2_playbook.md, AI_Inquiry_Capture_Gap_Analysis.md, gap_analysis.md, product_context.md, alignment.md, building-successful-saas-guide.md, revenue_methodology.md, cost_analysis.md, product_stories.md, product_manual.md, sales_demo_script.md, website_design_brief.md + operational docs (deployment, onboarding, user_guide, testing, sit_uat_guide, walkthrough_twilio_demo)
- **Archived** to `docs/archive/`: raw interview transcripts (Bernard, Shamsuridah, Shafar, Bob, Zul, Amsyar, Consultant), CRM_hotels.txt, blueprint_text.txt, .docx blueprint, architecture_audit.md, implementation_vs_saas_guide_audit.md, audit_remediation_walkthrough.md, product_alignment.md (duplicate of alignment.md)
- Key doc corrections: all docs now research-aligned — Gemini primary LLM, 768-dim embeddings, no SaaS infrastructure in customer scope, dormant infrastructure clearly labelled, revenue formula standardized to revenue_methodology.md canonical
- **product_gap.md**: "bridge/obstacle" analysis — 7 blockers to first payment, feature priority matrix (urgent/soon/drop), canonical revenue formula example for Vivatel
- **gtm_execution_plan.md (v1.0 — new)**: Complete workflow from current state to first paying customer across all business functions. 5 phases: Fix Gaps (Days 1–5), Activate Vivatel (6–12), Capture Evidence (13–30), Convert to Paid (28–35), Replicate (35–60), Scale to 10 (55–90). Includes 7 product tasks, Vivatel activation sequence, case study build, objection handling scripts, marketing alignment track, weekly review ritual, North Star Metric (GM dashboard logins), 90-day scorecard, and a stop-doing list.

## Architecture Changes Made This Session

1. **Redis graceful fallback** (`app/core/redis.py`): If Redis unavailable/localhost, all ops use in-memory dict with TTL. `publish()` is a no-op. No crash on startup.
2. **APScheduler disabled in production** (`app/main.py`): Only starts in dev/demo mode. Production uses Cloud Scheduler → HTTP calls to internal endpoints.
3. **Internal scheduler routes** (`app/routes/internal.py`): `POST /api/v1/internal/run-daily-report|run-followups|run-insights|cleanup-leads` — all require `X-Internal-Secret` header.
4. **Dockerfile** (`backend/Dockerfile`): Port changed to 8080 (`${PORT:-8080}`), gunicorn workers reduced to 2, startup period extended to 15s.
5. **Frontend Dockerfile**: `npm ci` (all deps including devDeps) in build stage — needed for TypeScript to compile `next.config.ts`.
6. **Frontend git tracking**: Was a stale gitlink (mode 160000). Fixed with `git rm --cached frontend && git add frontend/`.
7. **cloudbuild.yaml**: Full build→push→deploy pipeline for both backend and frontend. Backend: `--no-cpu-throttling`, Frontend: `--cpu-throttling`.

## Test State (as of last run)

- **test_billing.py**: 12/12 pass (7 original + 5 new subscription event tests; all mocked)
- **test_supabase.py**: 6/6 skip gracefully (auth tests need SERVICE_ROLE_KEY; DB tests skip when Supabase paused)
- **Other integration tests**: 14 fail (need running PostgreSQL — Docker or unpaused Supabase)
- `asyncio_mode = auto` in `pytest.ini` — required for pytest-asyncio

## Running Tests

```bash
# Always pass (no DB needed):
cd backend && pytest tests/test_billing.py -v

# Need unpaused Supabase:
cd backend && pytest tests/test_supabase.py -v

# Need Docker running:
docker-compose up -d
cd backend && pytest tests/test_channels.py -v
```

## Pending Next Steps (Priority Order — Blockers to First Payment)

1. **Dashboard home fix** — rebuild `frontend/src/app/dashboard/page.tsx` to show KPI cards (revenue, leads, inquiries) instead of onboarding checklist. The analytics data is at `/dashboard/analytics` — move it to the landing screen. **#1 critical gap.**

2. **Staff reply from dashboard** — add text input + send button to conversations view. Backend already supports `POST /api/v1/conversations/{id}/messages` with `role: "staff"`.

3. **Daily email report (production)** — (a) add `SENDGRID_API_KEY` to Secret Manager, (b) create Cloud Scheduler job: `POST /api/v1/internal/run-daily-report` @ `30 7 * * *` MYT with `X-Internal-Secret` header.

4. **FERNET_ENCRYPTION_KEY** — generate and add to Secret Manager: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

5. **"Lost" status filter** — add "Lost" chip to leads filter dropdown in `dashboard/leads/page.tsx`

6. **BM end-to-end test** — run 10 BM conversations via Twilio sandbox → Vivatel test number with native speaker review

7. **Vivatel KB population** — KB build session with Zul: collect rate card, FAQs, room types, facilities

8. **Cloud Scheduler jobs** (remaining 3): run-followups @ `0 * * * *`, run-insights @ `0 8 1 * *`, db-keepalive @ `0 12 */6 * *`

9. **Custom domain** (optional) — `api.sheerssoft.com` → backend, `app.sheerssoft.com` → frontend

10. **Supabase Pro upgrade** — before first paying tenant ($25/month, eliminates auto-pause)

**DO NOT** activate Stripe, Tenant SaaS hierarchy, Supabase Auth, SuperAdmin dashboard, or support chatbot until ≥3 paying tenants confirmed. See docs/product_gap.md Section 4.3.

## New PC Setup Checklist

```bash
# 1. Clone repo
git clone https://github.com/BasyirSheersComputer/mvp-research-sheerssoft.git
cd mvp-research-sheerssoft

# 2. Auth to GCP (gets ADC for Secret Manager access)
gcloud auth login
gcloud auth application-default login
gcloud config set project nocturn-ai-487207

# 3. Configure Docker for Artifact Registry
gcloud auth configure-docker asia-southeast1-docker.pkg.dev

# 4. Install Python deps
pip install -r backend/requirements.txt

# 5. Run mocked tests (no DB needed — confirm setup is correct)
cd backend && pytest tests/test_billing.py -v

# 6. Local dev server (loads secrets from GCP SM automatically)
cd backend && uvicorn app.main:app --reload --port 8000
```
