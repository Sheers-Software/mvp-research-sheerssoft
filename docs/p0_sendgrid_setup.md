# P0.3 — SendGrid Daily Email Report: Setup Runbook

**Status:** Completed 2026-03-17
**Purpose:** Unblock the daily 7:30am MYT email report to staff for Vivatel pilot.

---

## What was done

| Step | Action | Result |
|------|--------|--------|
| 1 | Added `SENDGRID_FROM_EMAIL` and `STAFF_NOTIFICATION_EMAIL` to `secrets_to_fetch` in `app/config.py` | Committed |
| 2 | Added `SENDGRID_API_KEY` (version 2) to GCP Secret Manager | `SG.n8MW...` |
| 3 | Created `SENDGRID_FROM_EMAIL` secret | `a.basyir@sheerssoft.com` |
| 4 | Created `STAFF_NOTIFICATION_EMAIL` secret | `a.basyir@sheerssoft.com` (temp — change to Zul's email after Vivatel closes) |
| 5 | Enabled Cloud Scheduler API | `cloudscheduler.googleapis.com` |
| 6 | Created 4 Cloud Scheduler jobs | See below |
| 7 | Deployed backend (Cloud Build) | Build `3c434aa0` — SUCCESS |

---

## Cloud Scheduler Jobs

All jobs in project `nocturn-ai-487207`, region `asia-southeast1`.

| Job name | Schedule (UTC) | MYT equivalent | Endpoint |
|----------|---------------|----------------|----------|
| `daily-report` | `30 23 * * *` | 7:30am | `POST /api/v1/internal/run-daily-report` |
| `run-followups` | `0 1 * * *` | 9:00am | `POST /api/v1/internal/run-followups` |
| `run-insights` | `0 18 * * *` | 2:00am | `POST /api/v1/internal/run-insights` |
| `db-keepalive` | `*/5 * * * *` | Every 5 min | `GET /api/v1/health` |

All POST jobs use header `X-Internal-Secret: <INTERNAL_SCHEDULER_SECRET>`.
The `db-keepalive` job prevents Supabase free-tier auto-pause (pauses after 1 week of no activity).

---

## Secrets in GCP Secret Manager

| Secret name | Value | Notes |
|-------------|-------|-------|
| `SENDGRID_API_KEY` | `SG.n8MW...` (version 2) | Full key in Secret Manager |
| `SENDGRID_FROM_EMAIL` | `a.basyir@sheerssoft.com` | Must match a verified SendGrid sender |
| `STAFF_NOTIFICATION_EMAIL` | `a.basyir@sheerssoft.com` | Update to `zul@vivatel.com.my` after pilot closes |

---

## Pending: Supabase Auto-Pause Fix

**Problem encountered:** Supabase free tier pauses projects after 1 week of inactivity. The database paused on 2026-03-17 (exactly 1 week after the 2026-03-10 deploy), causing `socket.gaierror: Name or service not known` on backend startup.

**Permanent fix:** The `db-keepalive` scheduler job (every 5 min) keeps the DB active going forward. The Supabase project must be manually unpaused once after each pause event.

**To unpause:**
1. Go to [supabase.com/dashboard](https://supabase.com/dashboard)
2. Select project `ramenghkpvipxijhfptp`
3. Click "Restore project" — takes ~1–2 min

---

## Test Command

After Supabase is unpaused, verify the daily report fires:

```bash
SECRET=$(gcloud secrets versions access latest --secret=INTERNAL_SCHEDULER_SECRET --project=nocturn-ai-487207)

curl -s -X POST \
  "https://nocturn-backend-owtn645vea-as.a.run.app/api/v1/internal/run-daily-report" \
  -H "X-Internal-Secret: ${SECRET}" \
  -H "Content-Type: application/json" \
  -d "{}"
```

**Expected response:** `{"status":"ok","reports_sent":1}`
**Expected outcome:** Email arrives at `a.basyir@sheerssoft.com` within 30 seconds.

---

## After Vivatel Pilot Closes

Update `STAFF_NOTIFICATION_EMAIL` to Zul's real email:

```bash
printf 'zul@vivatel.com.my' | \
  gcloud secrets versions add STAFF_NOTIFICATION_EMAIL \
    --data-file=- \
    --project=nocturn-ai-487207
```

Also set `Property.notification_email` directly on the Vivatel property row so it's hotel-specific:

```sql
UPDATE properties
SET notification_email = 'zul@vivatel.com.my'
WHERE slug = 'vivatel' OR name ILIKE '%vivatel%';
```

---

## SendGrid Sender Verification Reminder

The `SENDGRID_FROM_EMAIL` (`a.basyir@sheerssoft.com`) must be verified in SendGrid before any emails will send:

1. SendGrid dashboard → **Settings → Sender Authentication**
2. **Verify a Single Sender** → fill in `a.basyir@sheerssoft.com`
3. Click verification link in the email SendGrid sends
4. Status turns green ✓
