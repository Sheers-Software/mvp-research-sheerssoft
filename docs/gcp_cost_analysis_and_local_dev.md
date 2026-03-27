# GCP Cost Analysis & Local Development Setup

**Date:** 2026-03-25
**Status:** Local dev stack built; GCP Cloud Run to be spun down.

---

## Why GCP Cloud Run Has Ongoing Costs

Both Cloud Run services (`nocturn-backend`, `nocturn-frontend`) are deployed and publicly accessible, even with `min-instances: 0` (scale-to-zero). Costs continue because:

### 1. `startup-cpu-boost: true` (Primary driver)
Cloud Run's CPU boost feature grants 2× the allocated CPU during container startup (cold start). Cold starts typically take 10–30 seconds for a Python/FastAPI app. Each cold start is charged at the boosted CPU rate, not the normal throttled rate.

| Config | Value |
|--------|-------|
| CPU limit | 1 vCPU |
| Memory | 1 GiB (backend), 512 MiB (frontend) |
| CPU throttling | enabled (throttled when idle) |
| Startup CPU boost | **enabled** (2× CPU during cold start) |
| Min instances | 0 (scale-to-zero) |
| Max instances | 5 (backend), 3 (frontend) |
| Ingress | all (publicly accessible from internet) |

### 2. Bot and Crawler Traffic (Compounding factor)
Both services are exposed at public URLs (`*.run.app`). GCP Cloud Run URLs are indexed by security scanners, web crawlers, and probing bots. Every external probe to a scaled-to-zero service triggers a cold start, which triggers the startup-cpu-boost charge. This creates a continuous trickle of cold-start compute costs from traffic you never initiated.

### 3. Secret Manager API Calls
Each backend cold start reads 15+ secrets from Secret Manager. GCP charges $0.06 per 10,000 API calls. With frequent cold starts from bot traffic, this accumulates.

### 4. Artifact Registry Storage
Two Docker images (~200 MB total) stored in Artifact Registry. Cost: ~$0.02/month. Negligible.

### Historical Context
Previous sessions noted the services were "spun down" (CLAUDE.md, 2026-03-23). They were **not actually deleted** — they remain deployed and continue to receive traffic and incur charges.

### Root Cause: Services Not Functional
After the Supabase migration (`c349fdf`), the `nocturn_app` Supabase role was not granted the necessary PostgreSQL privileges on the application tables. The backend connects to Supabase's PgBouncer (transaction mode, port 6543) with this restricted role, resulting in:
- `permission denied for table properties` on any data query
- `Internal Server Error` on all authenticated API endpoints
- The service appears healthy (`/health` returns 200) but cannot serve data

The Cloud Run deployment is effectively a broken service incurring ongoing costs.

---

## Local Development Setup

The local stack replaces GCP Cloud Run with local Docker containers:
- **PostgreSQL 16 + pgvector**: local database, full admin access, no RLS restrictions
- **Redis 7**: local session store and pub/sub
- **Backend**: same Dockerfile as GCP, but points to local postgres and GCP Secret Manager for API keys
- **Frontend**: same Dockerfile as GCP

### Prerequisites

```bash
# 1. Docker Desktop running
# 2. GCP authentication
gcloud auth application-default login
gcloud config set project nocturn-aai

# 3. Verify ADC credentials exist
ls $APPDATA/gcloud/application_default_credentials.json  # Windows
```

### Start Local Stack

```bash
cd D:/repos/mvp-research-sheerssoft
docker compose up -d --build
```

Services start on:
- Backend:  http://localhost:8000
- Frontend: http://localhost:3000
- Postgres: localhost:5433 (user: nocturn, pass: nocturn_dev, db: nocturn)
- Redis:    localhost:6380

### First-Time DB Setup and Seeding

On first `docker compose up`, the backend creates all tables via SQLAlchemy `create_all` (ENVIRONMENT=development). Then seed demo data:

```bash
cd backend
# Override DATABASE_URL to point to local docker postgres
DATABASE_URL=postgresql+asyncpg://nocturn:nocturn_dev@localhost:5433/nocturn python seed_demo_data.py
```

### How Secrets Work Locally

The docker-compose mounts your GCP Application Default Credentials into the container:
```
C:\Users\abasy\AppData\Roaming\gcloud\application_default_credentials.json
  → /gcp/credentials.json (inside container)
```

`config.py` uses these credentials to call GCP Secret Manager (`nocturn-ai-487207`) for all API keys (Gemini, OpenAI, JWT, Supabase, Twilio, Stripe, etc.).

The `DATABASE_URL` environment variable in docker-compose **overrides** the Secret Manager value, directing all DB traffic to the local postgres instead of Supabase. All other secrets still come from Secret Manager.

### Re-deploying to GCP

The local setup is deployment-identical to GCP. When ready to go live:

```bash
# 1. Re-create Cloud Run services
gcloud builds submit \
  --config=backend/cloudbuild.yaml \
  --project=nocturn-ai-487207 \
  --region=asia-southeast1 \
  --substitutions=COMMIT_SHA=$(git rev-parse HEAD) \
  .

# 2. Re-enable Cloud Scheduler jobs (when needed)
for job in nocturn-daily-report nocturn-followups nocturn-insights nocturn-keepalive; do
  gcloud scheduler jobs resume $job --location=asia-southeast1 --project=nocturn-aai
done
```

**Note before re-deploying to GCP:** Fix the Supabase `nocturn_app` role permissions issue. Either:
- `GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO nocturn_app;` in Supabase SQL editor
- Or switch the DATABASE_URL in Secret Manager to the Supabase postgres superuser URL

---

## Spinning Down GCP Cloud Run

After verifying local stack works:

```bash
# Delete Cloud Run services
gcloud run services delete nocturn-backend \
  --project=nocturn-ai-487207 --region=asia-southeast1 --quiet

gcloud run services delete nocturn-frontend \
  --project=nocturn-ai-487207 --region=asia-southeast1 --quiet

# Verify deletion
gcloud run services list --project=nocturn-aai
```

Cloud Scheduler jobs are already showing 0 items (no jobs to pause). Artifact Registry images can be kept for future deploys (cost: ~$0.02/month).

After deletion, the only recurring GCP costs will be:
- Secret Manager storage: ~$0.006/version × 15 secrets = ~$0.09/month
- Artifact Registry: ~$0.02/month
- **Total: ~$0.11/month** (effectively free)
