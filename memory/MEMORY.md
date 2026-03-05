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

## Pending Next Steps (Priority Order)

1. **Cloud Scheduler jobs** — create 4 jobs to replace APScheduler in production:
   - Daily report: `POST /api/v1/internal/run-daily-report` @ `30 7 * * *` MYT
   - Follow-ups: `POST /api/v1/internal/run-followups` @ `0 * * * *`
   - Monthly insights: `POST /api/v1/internal/run-insights` @ `0 8 1 * *`
   - DB keep-alive: `GET https://nocturn-backend-owtn645vea-as.a.run.app/api/v1/health` @ `0 12 */6 * *`
   - All internal jobs need header: `X-Internal-Secret: <value from Secret Manager>`

2. **Stripe live webhook** — add `https://nocturn-backend-owtn645vea-as.a.run.app/api/v1/billing/webhook` in Stripe dashboard, update `STRIPE_WEBHOOK_SECRET` in Secret Manager

3. **FERNET_ENCRYPTION_KEY** — generate and add to Secret Manager for PII field encryption

4. **Custom domain** (optional) — `api.sheerssoft.com` → backend, `app.sheerssoft.com` → frontend via Cloud Run domain mapping

5. **Supabase Pro upgrade** — before first paying tenant goes live ($25/month, eliminates auto-pause)

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
