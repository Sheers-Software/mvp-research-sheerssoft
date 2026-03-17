# Product Gap Analysis
## Nocturn AI — What to Build, What to Drop, How to Get Paid
### Version 1.1 · 18 Mar 2026
### Cross-referenced with: prd.md v2.0, portal_architecture.md, gtm_execution_plan.md, workflow_zero_to_paid.md, revenue_methodology.md

---

## Current Status Snapshot

| Area | Status |
|------|--------|
| AI engine (WhatsApp, Web, BM/EN) | ✅ Live on Cloud Run |
| Dashboard home — KPI cards | ✅ Done (rebuilt, shows revenue/leads/inquiries) |
| Staff reply from dashboard | ✅ Done (conversations view has reply box) |
| "Lost" filter in leads | ✅ Done |
| Maintenance mode (backend + UI + banner) | ✅ Done — Phase 1.5 complete |
| Magic link auth (Supabase PKCE) | ✅ Done — superadmin restricted to `a.basyir@sheerssoft.com` |
| Daily email in production | ❌ Missing `SENDGRID_API_KEY` + Cloud Scheduler jobs |
| FERNET encryption key | ❌ Not in Secret Manager |
| BM end-to-end test (50 questions) | ❌ Not run |
| Vivatel KB population | ❌ Requires Zul session |
| Service health dashboard | ❌ Not built — Phase 1.5 next |
| Announcements system | ❌ Not built — Phase 1.5 |
| `/portal` tenant management layer | ❌ Not built — Phase 4 |
| `/welcome` onboarding wizard | ❌ Not built — Phase 4 |

---

## 1. The Situation

The codebase is at v0.3.1. The AI engine works. The backend is live on Cloud Run. The dashboard home shows revenue KPIs. Staff can reply to guests from the dashboard. **The remaining blockers to first payment are infra tasks (SendGrid key, Cloud Scheduler) and field work (BM test, Vivatel KB session) — no remaining product code is required to go to pilot.**

The portal architecture has been designed and Phase 1.5 (SheersSoft internal controls) is underway. This enables safe multi-tenant operation once Vivatel goes live.

---

## 2. The Bridge — Path to First Payment

```
Step 1: GM opens dashboard → SEES revenue ✅ DONE
Step 2: GM sees leads with full conversation context ✅ DONE
Step 3: Staff replies from dashboard → guest receives it on WhatsApp ✅ DONE
Step 4: GM gets email at 7am confirming last night's numbers ❌ BLOCKED (SendGrid + Scheduler)
Step 5: BM test passes ≥80% ❌ NOT RUN
Step 6: Vivatel KB populated ❌ NEEDS ZUL SESSION
Step 7: GM says "this is working" → invoice paid ← TARGET
```

---

## 3. Remaining Obstacles to First Payment

### Obstacle C: Daily Email Not Live in Production ← HIGHEST REMAINING PRIORITY

**Status:** SendGrid API key missing from Secret Manager. Cloud Scheduler jobs not created.

**Why this is still fatal:** The 7am daily email is the retention hook. A GM who doesn't log in daily still stays engaged because the email shows up in their inbox. Without it, the AI is invisible between demos.

**Fix (2 actions, ~2 hours):**
```bash
# Action 1: Add SendGrid API key
echo -n "SG.xxxx" | gcloud secrets versions add SENDGRID_API_KEY \
  --data-file=- --project=nocturn-ai-487207

# Action 2: Create all 4 Cloud Scheduler jobs
gcloud scheduler jobs create http nocturn-daily-report \
  --location=asia-southeast1 --schedule="30 7 * * *" \
  --time-zone="Asia/Kuala_Lumpur" \
  --uri="https://nocturn-backend-owtn645vea-as.a.run.app/api/v1/internal/run-daily-report" \
  --http-method=POST \
  --headers="X-Internal-Secret=<from Secret Manager INTERNAL_SCHEDULER_SECRET>" \
  --attempt-deadline=30s

# Plus: nocturn-followups (0 * * * *), nocturn-insights (0 8 1 * *), nocturn-keepalive (0 12 */6 * * GET /health)
```

---

### Obstacle D: PII Encryption Key Missing

**Status:** `FERNET_ENCRYPTION_KEY` not in Secret Manager. Encryption silently bypassed.

**Fix (30 min):**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
echo -n "<key>" | gcloud secrets versions add FERNET_ENCRYPTION_KEY \
  --data-file=- --project=nocturn-ai-487207
```
Redeploy after adding. Verify: new lead captured → phone field encrypted in DB.

---

### Obstacle E: BM Test Not Run

**Status:** BM logic exists and is untested end-to-end via real WhatsApp.

**Fix:** Run the 50-question suite from `docs/bm_test_suite.md` via Twilio sandbox → Vivatel test number. Must pass ≥80%. See `docs/bm_test_execution_plan.md` for execution steps.

---

### Obstacle F: Vivatel KB Empty

**Status:** No knowledge base ingested for Vivatel property. AI will hallucinate or give generic answers until this is done.

**Fix:** 90-minute session with Zul. Collect all 28 KB intake questions (see `docs/workflow_zero_to_paid.md` Stage 4). Ingest via:
```bash
python backend/scripts/ingest_kb.py --property-slug vivatel-kl --file vivatel_kb.md
```

---

## 4. Feature Priority Matrix

### 4.1 ✅ DONE — Blockers Cleared

| Feature | Completed |
|---------|-----------|
| Dashboard home → KPI cards (money slide) | ✅ v0.3.1 |
| Staff reply from dashboard conversations | ✅ v0.3.1 |
| "Lost" status filter in leads | ✅ v0.3.1 |
| Maintenance mode (backend + admin toggle + tenant banner) | ✅ v0.3.1 |
| Magic link auth — superadmin restricted to explicit email | ✅ v0.3.1 |

---

### 4.2 ❌ Still Needed Before Pilot (Infra + Field Work Only)

| Task | Type | Effort | Owner |
|------|------|--------|-------|
| Add `SENDGRID_API_KEY` to Secret Manager | Infra | 15 min | Ahmad Basyir |
| Create 4 Cloud Scheduler jobs | Infra | 45 min | Ahmad Basyir |
| Add `FERNET_ENCRYPTION_KEY` to Secret Manager + redeploy | Infra | 30 min | Ahmad Basyir |
| BM 50-question end-to-end test | Field test | Half day | Ahmad Basyir |
| Vivatel KB population session with Zul | Field work | 1 day | Ahmad Basyir + Zul |

**Total: ~2 days. No remaining product code blocks the pilot.**

---

### 4.3 Build Next — Phase 1.5 Internal Controls (Parallel with Pilot)

These protect the quality of the pilot and all subsequent relationships. Build while Vivatel is live so they're ready before the second tenant.

| Feature | Status | Priority | Effort |
|---------|--------|----------|--------|
| Maintenance mode | ✅ Done | — | — |
| Service health dashboard (`/admin/health`) | ❌ Not built | **Next** | 2 days |
| Announcements system (backend + admin + tenant banner) | ❌ Not built | After health | 3 days |

---

### 4.4 Build Before Phase 4 — Tenant Self-Service

These remove the per-tenant engineering time dependency. Required before onboarding the 3rd+ tenant without a SheersSoft engineer in the loop.

| Feature | Portal | When |
|---------|--------|------|
| `/portal` tenant home (multi-property summary) | `/portal` | 2nd paying tenant |
| KB management UI (add/edit/delete documents) | `/portal/kb` | 2nd paying tenant |
| `/welcome` onboarding wizard (5-step) | `/welcome` | 3rd tenant |
| Team management (invite + roles + property scope) | `/portal/team` | 3rd tenant |
| Channel status + retry UI | `/portal/channels` | 4th tenant |

---

### 4.5 Build at Scale (5+ Paying Tenants)

| Feature | Why Wait |
|---------|----------|
| Confirmed revenue field ("Mark as Booked") | Needs real booking data to be meaningful |
| `/dashboard/insights` — AI performance + KB gaps | Needs 30+ days of per-property data |
| Week-over-week comparison in daily email | Needs 14+ days of history |
| Billing portal (Stripe Customer Portal) | Manual invoicing until ≥10 tenants |
| Mobile-responsive dashboard | Desktop-first is fine for 3-4 star hotel GMs |
| `staff_tier` RBAC (manager/revenue/ops) | No tenant has asked for this yet |

---

### 4.6 Drop (Do Not Build in v1 — Reconfirmed)

| Feature | Why to Drop |
|---------|-------------|
| Gamified onboarding progress tracker | Replaced by KPI dashboard. No GM asked for this. |
| Application intake form (ai.sheerssoft.com/apply) | No inbound advertising driving traffic. |
| Support chatbot (nocturn-ai-support property) | Zero support tickets. Build when customer base justifies it. |
| Email channel inbound (SendGrid inbox) | Malaysian hotels use WhatsApp. Not validated. |
| Voice / image AI capabilities | No customer has asked. Don't add until core is proven. |
| F&B Intelligence (Opportunity #1) | Right direction, wrong timing. 5 paying customers first. |

**Note on items previously listed as "drop" that are NOW being built:**
- `SuperAdmin dashboard` — now `/admin` with maintenance + health + announcements. This is SheersSoft ops infrastructure, not a customer feature. Correct to build.
- `Supabase Auth` — magic link login is live and working. This was the right call.
- `TenantMembership hierarchy` — portal separation (`/portal` vs `/dashboard`) is the right architecture. Build Phase 4 when it unblocks scaling.

---

## 5. What "Getting Paid" Looks Like

### Direct Path (Vivatel Pilot)

```
Now (18 Mar) → 2 infra tasks (SendGrid + Scheduler + FERNET) → 2h
→ BM test (half day) → Vivatel KB session (1 day with Zul)
→ Deploy to production → Vivatel UAT (2 days supervised)
→ 7 days of real data → Pilot review call (Day 30) → Invoice
```

**Target: First invoice by Day 28–30 (mid-April 2026).**

### Next Priority After Pilot Launch

While monitoring Vivatel (days 8–14), build Phase 1.5 remaining items:
1. **Service health dashboard** — know before tenants know when a service degrades
2. **Announcements system** — communicate maintenance to tenants without personal WhatsApp

These are complete before the second tenant onboards, ensuring professional ops at scale.

---

## 6. The Revenue Formula (Canonical)

Per `revenue_methodology.md`:

```
Estimated Revenue Recovered = Sum of (lead nights × property ADR) × 20%
  where: lead nights defaults to 1 if not captured
         ADR defaults to property setting (Vivatel ~RM 230)
         20% = conservative conversion assumption

Cost Savings = AI-handled inquiries × 0.25 hrs × RM 25/hr
```

**Example (Vivatel, 30 days):**
- 20 after-hours leads × RM 230 ADR × 20% = **RM 920 estimated revenue recovered**
- 400 AI-handled inquiries × 0.25 hrs × RM 25 = **RM 2,500 cost savings**
- Total value: **RM 3,420/month** vs RM 1,500 subscription fee → 2.3× ROI

---

## 7. Decision Rule for New Feature Requests

1. **Does it unblock the first invoice?** → Build immediately.
2. **Does it protect the quality of the pilot?** → Build during pilot (Phase 1.5).
3. **Does it remove per-tenant engineering time?** → Build before 3rd tenant (Phase 4).
4. **Does it help retain/upsell 5+ paying properties?** → Build at scale.
5. **None of the above?** → Drop.

---

*v1.1 update: Obstacles A, B, and the Lost filter are resolved. Remaining blockers are infra tasks (2h) and field work (1.5 days) — no product code blocks the pilot. Phase 1.5 internal controls in progress.*
