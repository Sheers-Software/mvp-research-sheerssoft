# Product Gap Analysis
## Nocturn AI — What to Build, What to Drop, How to Get Paid
### Version 1.4 · 20 Apr 2026
### Cross-referenced with: prd.md v2.4, architecture.md v2.4, build_plan.md v2.4, portal_architecture.md, workflow_zero_to_paid.md, revenue_methodology.md

---

## Current Status Snapshot (as of 20 Apr 2026)

| Area | Status |
|------|--------|
| AI engine (WhatsApp Meta + Twilio, Web Chat, BM/EN) | ✅ Live (Cloud Run — GCP deploy paused since 23 Mar 2026) |
| Dashboard home — KPI cards (revenue/leads/inquiries) | ✅ Done (v0.3.1) |
| Staff reply from dashboard (conversations view) | ✅ Done (v0.3.1) |
| "Lost" filter in leads | ✅ Done (v0.3.1) |
| Maintenance mode (backend + admin toggle + tenant banner) | ✅ Done (v0.3.2) |
| Service health dashboard (`/admin/health`) | ✅ Done (v0.3.2) |
| Magic link auth (Supabase PKCE) | ✅ Done — superadmin restricted to `a.basyir@sheerssoft.com` |
| Daily email in production (SendGrid + 4 Cloud Scheduler jobs) | ✅ Done (v0.3.2) — Note: jobs deleted in 2026-03-23 GCP cleanup; recreate on next deploy |
| FERNET encryption key | ✅ Done — `FERNET_ENCRYPTION_KEY` confirmed in Secret Manager |
| Infra migration (Supabase-only DB, Secret Manager) | ✅ Done (v0.3.3) |
| `/portal` tenant management layer | ✅ Done (v0.4) — KB, team, channels, billing, support |
| `/welcome` onboarding wizard (5 steps) | ✅ Done (v0.4) |
| Role-based auth callback routing | ✅ Done (v0.4) |
| `/admin/kb-ingestion` tool | ✅ Done (v0.4) |
| Application intake form (`/apply`) | ✅ Done (v0.4) — primary GTM entry point |
| After-Hours Revenue Audit calculator (`/audit`) | ✅ Done (v0.5) |
| `AuditRecord` model + endpoints | ✅ Done (v0.5) |
| `/admin/tools/revenue-audit` admin tool | ✅ Done (v0.5) |
| `audit_only_mode` flag on Property | ✅ Done (v0.5) |
| Weekly audit email + `run_weekly_audit_report` scheduler job | ✅ Done (v0.5) |
| `/admin/shadow-pilots` provisioning page | ✅ Done (v0.5) |
| Announcements model (DB table + migration) | ✅ Model/table exists — backend routes in superadmin.py |
| **Hybrid AI Co-Pilot reply drafting UI** | ❌ Not built (Sprint 2.6) |
| **Google Sheet real-time inventory reader** | ❌ Not built (Sprint 2.6) |
| **FPX/DuitNow payment link generator in AI replies** | ❌ Not built (Sprint 2.6) |
| BM end-to-end test (50 questions) | ❌ Not run — **P0 blocker** |
| First pilot property KB not populated | ❌ Not done — **P0 field work** |

---

## 1. The Situation (20 Apr 2026)

The codebase is at **v0.5** (v0.5.2 per `main.py`). The shadow pilot infrastructure is complete — a SheersSoft AM can provision a shadow pilot for a prospect in 5 minutes from the admin panel, and the GM gets a real-data audit email on Day 7 automatically.

**The remaining gap to first paid client:**
1. Run the 50-question BM/Manglish test suite (half-day) — must pass ≥80%
2. Populate first pilot property KB (1-day field session)
3. Build Sprint 2.6 Hybrid Co-Pilot features (3–5 days dev) — converts shadow pilot → revenue-generating co-pilot

**Key hybrid model insight (20 Apr 2026):** The Meta Cloud API home-address verification blocker means we cannot auto-send via WhatsApp. The Hybrid Co-Pilot sidesteps this: AI drafts the reply in the dashboard, hotel staff sends via their existing WhatsApp Business App (multi-device). Hotels get 80% of the value today while Meta registration is resolved.

---

## 2. The Bridge — Path to First Revenue

```
Step 1: Shadow pilot provisioned → GM gets Day 7 audit email      ✅ INFRASTRUCTURE READY
Step 2: BM test passes ≥80%                                        ❌ NOT RUN (half-day)
Step 3: First pilot KB populated                                    ❌ NEEDS FIELD SESSION (1 day)
Step 4: Sprint 2.6 Hybrid Co-Pilot UI built                        ❌ NOT BUILT (2–3 days dev)
Step 5: Hotel tries co-pilot → AI drafts → staff sends → guest books ← TARGET
Step 6: GM sees "RM X recovered today" in morning report → signs up paid
```

---

## 3. Remaining Obstacles to First Payment

### Obstacle A: BM Test Not Run — ❌ FIELD WORK (P0)
**Status:** 50-question BM/Manglish test suite exists at `docs/bm_test_suite.md`. Execution plan at `docs/bm_test_execution_plan.md`. Not run end-to-end via real WhatsApp.

**Fix:** Run via Twilio sandbox. Must pass ≥80% before first client go-live.

---

### Obstacle B: Pilot Property KB Empty — ❌ FIELD WORK (P0)
**Status:** No KB ingested for first pilot property.

**Fix:** 90-minute session with GM/property contact. Ingest via `/admin/kb-ingestion` or:
```bash
python backend/scripts/ingest_kb.py --property-slug [slug] --file [property]_kb.md
```

---

### Obstacle C: Hybrid Co-Pilot Not Built — ❌ DEV (Sprint 2.6)
**Status:** Shadow pilot infrastructure shows GMs the problem. Hybrid co-pilot is how they experience the solution. Without it, the shadow pilot conversion asks GMs to still trust on faith.

**Required deliverables (Sprint 2.6):**
- Hybrid reply drafting UI in `/dashboard/conversations`: AI-drafted reply appears in sidebar when a guest message comes in. "Copy to WhatsApp" button + optional forward
- Google Sheet inventory reader: 2-minute polling of hotel's Google Sheet for room availability; injects into AI system prompt
- FPX/DuitNow link generator: when AI detects booking intent, embed a payment link in the draft
- Analytics update: "RM X recovered today (same-day vs OTA 30-day)" in daily GM report

---

### ~~Obstacle D: Cloud Scheduler Jobs Missing~~ — ✅ PARTIALLY RESOLVED
**Status:** Jobs were confirmed live (nocturn-daily-report, nocturn-followups, nocturn-insights, nocturn-keepalive, run-weekly-audit-report) but **deleted in 2026-03-23 GCP cleanup**. Must recreate on next production deploy.

---

### ~~Obstacle E: WHATSAPP_API_TOKEN missing~~ — ❌ STAGE 3 ONLY
**Status:** Not in Secret Manager. Not needed for Shadow Pilot (Twilio) or Hybrid Co-Pilot path. Required only for Stage 3 (full Meta Cloud API auto-send) after virtual office address verification is resolved.

---

## 4. Feature Priority Matrix

### 4.1 ✅ DONE — Everything Built Through v0.5

All items from `portal_architecture.md` Phases 1–5 are complete. Shadow pilot infrastructure (Sprint 2.5) is complete.

See `build_plan.md` Section "v0.5 — What Was Built" for the full feature list with ✅ status on every item.

---

### 4.2 ❌ Must Build Now (Sprint 2.6 — Hybrid Co-Pilot)

| Task | Type | Effort | Owner |
|------|------|--------|-------|
| Hybrid reply drafting sidebar in conversations view | Dev | 1 day | Ahmad Basyir |
| Google Sheet inventory reader (2-min polling) | Dev | 0.5 day | Ahmad Basyir |
| FPX/DuitNow payment link generator | Dev | 0.5 day | Ahmad Basyir |
| Daily GM report: "RM X recovered today" (hybrid-aware) | Dev | 0.5 day | Ahmad Basyir |
| BM 50-question end-to-end test | Field test | Half day | Ahmad Basyir |
| Pilot KB population session | Field work | 1 day | Ahmad Basyir |

**Total: ~4.5 days dev + 1.5 days field work. This is Sprint 2.6.**

---

### 4.3 Build Next — After First Pilot Live (Sprint 3+)

| Feature | When |
|---------|------|
| Day 7 AM notification to SheersSoft AM | Sprint 3 — completes the auto-conversion loop |
| Announcements system (UI: admin compose + tenant inbox banner) | Sprint 3 — backend model/table already exists |
| Confirmed revenue ("Mark as Booked") + actual revenue metric | After 30 days of pilot data |
| Week-over-week comparison in daily email | After 14+ days of data |
| `/dashboard/insights` — AI performance + KB gaps | After 30+ days of per-property data |

---

### 4.4 Build at Scale (5+ Paying Tenants)

| Feature | Why Wait |
|---------|----------|
| Billing portal (Stripe Customer Portal) | Manual invoicing until ≥10 tenants |
| Mobile-responsive dashboard | Desktop-first is fine for hotel GMs |
| `staff_tier` RBAC (manager/revenue/ops) | No tenant has asked for this yet |
| Meta Cloud API (Stage 3 full automation) | After virtual office address verified + 5 paying pilots |
| F&B Revenue Intelligence | 5 paying customers first |

---

### 4.5 Drop (Do Not Build in v1 — Reconfirmed)

| Feature | Why to Drop |
|---------|-------------|
| Automated PDF report generation for audit | Post-PMF. Text email is sufficient. |
| Voice / image AI capabilities | No customer has asked. Don't add. |
| Email channel inbound (SendGrid inbox) | Malaysian hotels use WhatsApp. Unvalidated. |
| Gamified onboarding progress tracker | Dashboard KPI cards replaced this. No GM asked. |
| F&B Intelligence, Guest Recognition KYC | Right direction, wrong timing. 5 paying customers first. |

> **Items previously listed as "Drop" that are now BUILT and ACTIVE:**
> - Application intake form (`/apply`) — primary GTM entry point
> - Shadow Pilot provisioning (`/admin/shadow-pilots`) — live
> - Tenant portal (`/portal`, `/welcome`) — live
> - Support chatbot property — architecture exists

---

## 5. What "Getting Paid" Looks Like

### Path A — Hybrid Co-Pilot (Primary, 7-day close)

```
Shadow pilot launched (Day 0) → Day 7 audit email → GM calls
  → Sprint 2.6 Hybrid Co-Pilot demo → KB + Google Sheet ingested (1 day)
  → Hotel tries co-pilot for 3 days → first direct booking closed
  → GM sees "RM X recovered today" in morning report
  → Invoice: RM 999 setup + RM 199/mo + 3% performance
```

### Path B — Full Auto (Stage 3, deferred)
After Hybrid proves ROI → virtual office address verified → Meta Cloud API registration → full auto-send.

---

## 6. The Revenue Formula (Canonical — Unchanged)

Per `revenue_methodology.md`:

```
Estimated Revenue Recovered = Sum of (lead nights × property ADR) × 20%
  where: lead nights defaults to 1 if not captured
         ADR defaults to property setting (target ~RM 230)
         20% = conservative conversion assumption

Cost Savings = AI-handled inquiries × 0.25 hrs × RM 25/hr
```

**Hybrid-specific update:** "Actual revenue recovered" will come from leads where staff sent an AI-drafted reply via WhatsApp Business App and the guest subsequently confirmed a booking. This is tracked via the "Mark as Booked" flow (Sprint 3 target).

---

## 7. Decision Rule for New Feature Requests

1. **Does it unblock the first hybrid co-pilot demo?** → Build immediately (Sprint 2.6).
2. **Does it protect the quality of the pilot?** → Build during pilot (Sprint 3).
3. **Does it remove per-tenant engineering time?** → Build before 3rd tenant.
4. **Does it help retain/upsell 5+ paying properties?** → Build at scale.
5. **None of the above?** → Drop.

---

*v1.4 update (20 Apr 2026): All portal, welcome wizard, shadow pilot, audit infrastructure confirmed ✅ complete. Application intake confirmed ✅ active. Three remaining gaps: BM test (P0 field work), pilot KB (P0 field work), Sprint 2.6 Hybrid Co-Pilot (3–5 days dev). Cloud Scheduler jobs must be recreated on next GCP deploy.*
