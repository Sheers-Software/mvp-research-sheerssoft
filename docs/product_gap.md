# Product Gap Analysis
## Nocturn AI — Codebase vs Hybrid Value Flow
### Version 2.0 · 25 Apr 2026
### Source: Live codebase audit against `nocturn_hybrid_value_flow.html` (Hybrid Co-Pilot Value Delivery & Capture Flow)

---

## Summary

| Phase | Alignment | P0 Gaps | P1 Gaps | P2 Gaps |
|-------|-----------|---------|---------|---------|
| Phase 1 — Acquisition | 80% | 0 | 1 | 0 |
| Phase 2 — Onboarding | 90% | 0 | 1 | 0 |
| Phase 3 — Shadow Pilot | 90% | 0 | 1 | 0 |
| Phase 4 — Hybrid Co-Pilot | 70% | 0 | 3 | 0 |
| Phase 5 — Conversion | 80% | 0 | 0 | 1 |

**Total open gaps: 7** — 0 P0 · 6 P1 · 1 P2

---

## Phase 1 — Acquisition

### GAP-001 · `/apply` form missing ICP qualification fields · **P1**

**Flow spec:** The application form captures "property type, star rating, WhatsApp number, ADR, monthly inquiry volume — ICP data captured at intake."

**Current state:** `frontend/src/app/apply/page.tsx` captures hotel name, contact name, email, phone (optional), room count (optional), inquiry channels (multi-select), and a freetext notes field. ADR, star rating, and monthly inquiry volume are absent entirely.

**Impact:** The revenue leakage formula requires ADR and monthly inquiry volume to produce a meaningful pre-sales projection. Without them, the admin cannot pre-qualify the economics of a prospect at intake — they must conduct a separate discovery call before provisioning. The self-qualifying loop described in Phase 1 is broken: the GM proves ROI on the `/audit` calculator but that data never flows through to the application record.

**Exact fix:**
- `frontend/src/app/apply/page.tsx` — add three fields: `adr_estimate` (number, RM), `monthly_inquiry_volume` (integer), `star_rating` (1–5 select).
- `backend/app/models.py` — add `adr_estimate NUMERIC(10,2)`, `monthly_inquiry_volume INTEGER`, `star_rating SMALLINT` to `Application` model.
- `backend/app/routes/superadmin.py` — include new fields in application create/read schemas.
- Pre-populate ADR on the shadow pilot provisioning form from the application record at provisioning time.

**Estimated effort:** 0.25 day

---

## Phase 2 — Onboarding

### GAP-002 · Welcome wizard billing step is absent · **P1**

**Flow spec:** 5-step wizard covers "channels, team roster, notification preferences, billing details" — billing details is an explicit step.

**Current state:** `frontend/src/app/welcome/page.tsx` has 5 steps: (1) welcome/property name, (2) knowledge base entry, (3) channel status, (4) invite team, (5) go-live summary. No billing details step exists. Stripe checkout is reachable only via `POST /api/v1/billing/checkout` — there is no wizard entry point.

**Impact:** A hotel completing the full welcome wizard exits without entering billing information. The RM 999 setup fee is never collected during onboarding. Billing is a manual follow-up action requiring the admin to re-engage the client separately after the wizard is complete.

**Exact fix:**
- `frontend/src/app/welcome/page.tsx` — replace Step 5 (go-live summary) with a billing step that calls `POST /api/v1/billing/checkout` for the RM 999 setup fee Stripe session. Move go-live to a post-payment confirmation screen.
- Alternatively: insert billing as Step 4, shift team invite to Step 5, make go-live the final screen after payment confirmed via webhook.

**Estimated effort:** 0.5 day

---

## Phase 3 — Shadow Pilot

### GAP-004 · [RESOLVED] Day-7 report is now property-relative · **P0**
**Current state:** Verified in `backend/app/services/shadow_pilot_reporter.py`. The system now correctly checks `days_active >= 7` and uses `shadow_pilot_report_sent_at` to ensure the report is sent exactly once per pilot, relative to its start date.

---

### GAP-005 · AuditRecord and shadow pilot data are disconnected pipelines · **P1**

**Flow spec:** Day-7 email delivers "Real data from their own property" — implying a before/after comparison.

**Current state:** `AuditRecord` captures the pre-sales self-assessment from the `/audit` calculator (estimated RM lost/month based on GM's own inputs). `ShadowPilotAnalyticsDaily` captures actual observed data. The Day-7 report shows shadow pilot data only. The two pipelines are never joined.

**Impact:** The most compelling sales narrative — "You estimated RM X at risk on the calculator. Your real 7-day data shows RM Y actually leaking — you underestimated it" — is never rendered. The comparison between the GM's self-reported estimate and the observed evidence is a psychological anchor that makes the value proposition undeniable. Currently, the Day-7 email is a data dump without the "you were right" moment.

**Exact fix:**
- At shadow pilot provisioning time (`POST /api/v1/superadmin/shadow-pilots`), look up the `AuditRecord` for the hotel (match on email or `converted_to_tenant_id`) and store `estimated_monthly_leakage_rm` on the `Property` (new column).
- In `shadow_pilot_reporter.py` report template, include a comparison row: "Your pre-pilot estimate: RM X/month" vs "Observed 7-day leakage: RM Y (annualised: RM Z)".

**Files to change:** `backend/app/routes/superadmin.py` (shadow pilot provision), `backend/app/models.py` (Property), `backend/app/services/shadow_pilot_reporter.py`.

**Estimated effort:** 0.5 day

---

## Phase 4 — Hybrid Co-Pilot

### GAP-006 · [RESOLVED] Hybrid reply drafting sidebar implemented · **P0**
**Current state:** Verified in `frontend/src/app/dashboard/conversations/page.tsx`. The conversations inbox now features an AI Draft sidebar with EN/BM toggles and one-click "Use this draft" functionality.

---

### GAP-007 · Google Sheet inventory reader is not implemented · **P1**

**Flow spec:** "Polls hotel's Google Sheet for live room availability (2-minute refresh cycle). Injects into system prompt."

**Current state:** No Google Sheets integration exists anywhere in the backend. Room availability is static — whatever was last ingested into `KBDocument` is the only source of truth. Grep for "sheets", "gsheet", "google.oauth2", "gspread" returns zero matches.

**Impact:** Without live inventory, the AI will quote availability for sold-out rooms. For the first live hotel, one incident of a guest being told a room is available when it is not destroys staff trust and kills adoption immediately. This is the most common and most damaging failure mode for AI assistants in hospitality.

**Exact fix:**
1. `backend/app/models.py` — add `google_sheet_inventory_url TEXT` to `Property`.
2. New `backend/app/services/inventory_reader.py` — uses `gspread` (service account auth). Fetches the sheet, parses room availability rows, stores as structured JSON cache on property (or Redis key with 2-min TTL).
3. `backend/app/services/conversation.py` — in the system prompt builder, inject current inventory cache: "Available rooms as of {time}: {room_list}. Do NOT quote unavailable rooms."
4. `backend/app/services/scheduler.py` — add a 2-minute polling job (dev/demo) and a Cloud Scheduler endpoint (production) for inventory refresh.
5. `frontend/src/app/portal/` — add Google Sheet URL field to property settings.

**Estimated effort:** 1 day

---

### GAP-008 · FPX / DuitNow payment link generator is not implemented · **P1**

**Flow spec:** "AI detects booking signal → FPX / DuitNow payment link auto-embedded in draft reply. Guest gets a frictionless direct payment path."

**Current state:** Stripe card-only integration exists for SheersSoft's billing relationship with hotels. No FPX or DuitNow integration exists for the hotel-to-guest booking payment flow. Grep for "fpx", "duitnow", "toyyibpay", "billplz", "ipay88" returns zero matches.

**Impact:** Stripe card payment has very low penetration among Malaysian hotel guests, who default to FPX (online banking) or DuitNow QR for local transactions. Without a Malaysia-native payment method, the booking journey breaks at payment. The guest reverts to OTA. The 3% performance fee is uncollectable. This is the gap between "inquiry handled" and "direct booking confirmed."

**Exact fix:**
1. Integrate Stripe's FPX support via `PaymentIntents` (lowest friction given existing Stripe setup) — FPX is available in Malaysia via Stripe.
2. New `backend/app/services/payment_link.py` — generates a Stripe PaymentIntent with `payment_method_types=["fpx"]` for a given amount (ADR × nights) and returns a hosted payment URL.
3. In the hybrid draft endpoint (GAP-006), when `intent=room_booking` is detected, include a payment link in the draft.
4. `backend/app/models.py` (Lead) — add `payment_link_url TEXT`, `confirmed_booking_amount_rm NUMERIC(10,2)`, `payment_reference VARCHAR(255)`.

**Estimated effort:** 1 day

---

### GAP-009 · 3% performance fee has no attribution or tracking mechanism · **P1**

**Flow spec:** "Only on confirmed, Nocturn-facilitated bookings. Aligned incentive."

**Current state:** `Lead` model has `converted BOOLEAN` and `converted_at TIMESTAMPTZ` but no flag for whether the conversion was Nocturn-facilitated vs organic, no confirmed booking amount, and no performance fee accumulation. `Tenant` has billing fields but no `performance_fee_balance_rm`.

**Impact:** The 3% performance fee is unmeasurable from the system. It either goes uncollected, requires hotel self-reporting (unenforceable), or requires manual reconciliation per billing cycle. As client count grows this becomes operationally intractable. The aligned incentive — Sheers earns only when the hotel earns — cannot function without attribution data.

**Exact fix:**
1. `backend/app/models.py` (Lead) — add `facilitated_by_nocturn BOOLEAN DEFAULT FALSE`, `confirmed_booking_amount_rm NUMERIC(10,2)`, `performance_fee_rm NUMERIC(10,2)` (computed as `amount × 0.03`).
2. `backend/app/models.py` (Tenant) — add `performance_fee_balance_rm NUMERIC(12,2) DEFAULT 0` (running total for current billing period).
3. When staff sends a reply via the hybrid sidebar and the guest subsequently confirms via payment link, set `facilitated_by_nocturn=True` and `confirmed_booking_amount_rm`.
4. Monthly billing job: include `performance_fee_balance_rm` as a line item in the Stripe invoice, then reset to 0.

**Files to change:** `backend/app/models.py`, `backend/app/routes/staff.py`, `backend/app/services/stripe_service.py`.

**Estimated effort:** 0.5 day

---

## Phase 5 — Conversion

### GAP-010 · [RESOLVED] Stripe subscription billing is wired · **P0**
**Current state:** Verified in `backend/app/routes/billing.py`. Subscriptions are now fully implemented with webhook handling for `customer.subscription.created`, `updated`, and `deleted` events.

---

### GAP-011 · 30-day revenue recovery guarantee has no enforcement code · **P2**

**Flow spec:** "30-day guarantee waives next month if it didn't. The math closes itself."

**Current state:** The guarantee is stated in business model documentation only. No corresponding field, threshold check, or waiver logic exists in the codebase. `Tenant` has `pilot_start_date` and `pilot_end_date` but no `guarantee_threshold_rm`, no `pilot_revenue_recovered_rm`, and no `guarantee_invoked` flag.

**Impact:** When the first hotel invokes the guarantee, SheersSoft must manually waive the next Stripe invoice. Manageable at 1–2 clients. Operationally untenable at 20+. More importantly, there is no automated signal to the account manager that a pilot is underperforming and approaching guarantee territory before Day 30.

**Exact fix:**
1. `backend/app/models.py` (Tenant) — add `guarantee_threshold_rm NUMERIC(10,2)` (default: cost of Nocturn for the month = RM 199), `pilot_revenue_recovered_rm NUMERIC(10,2) DEFAULT 0`, `guarantee_invoked BOOLEAN DEFAULT FALSE`.
2. Daily report job (`scheduler.py`) — accumulate `analytics.revenue_recovered` since `pilot_start_date` into `pilot_revenue_recovered_rm`.
3. At Day 28, if `pilot_revenue_recovered_rm < guarantee_threshold_rm`, send an internal alert to the AM: "Hotel X pilot underperforming — may invoke guarantee."
4. At Day 30, if threshold not met and hotel requests waiver, auto-apply a 100% Stripe discount coupon to next invoice and set `guarantee_invoked=True`.

**Estimated effort:** 0.5 day

---

## Resolved Gaps (v0.6.0 Update)

- **GAP-003**: KB self-service implemented in `/portal/kb/`.
- **GAP-004**: Day-7 report logic updated to be property-relative.
- **GAP-006**: Hybrid reply drafting sidebar added to dashboard.
- **GAP-010**: Stripe subscription billing fully wired in backend.

## Sprint Prioritisation

### P0 — All P0 gaps resolved in v0.6.0

| ID | Gap | Effort |
|----|-----|--------|
| - | (No open P0 gaps) | - |

**Total P0: 0 days dev**

---

### P1 — Before second client (blocks revenue model and adoption)

| ID | Gap | Effort |
|----|-----|--------|
| GAP-001 | `/apply` missing ADR + monthly inquiry volume | 0.25 day |
| GAP-002 | Welcome wizard missing billing step | 0.5 day |
| GAP-005 | AuditRecord ↔ shadow pilot data disconnected | 0.5 day |
| GAP-007 | Google Sheet inventory reader missing | 1 day |
| GAP-008 | FPX/DuitNow payment link missing | 1 day |
| GAP-009 | 3% performance fee has no attribution | 0.5 day |

**Total P1: 3.75 days dev**

---

### P2 — Before scale (operational overhead at > 5 clients)

| ID | Gap | Effort |
|----|-----|--------|
| GAP-011 | 30-day guarantee has no enforcement code | 0.5 day |

**Total P2: 0.5 day dev**

---

## What is well-aligned

The following components from the value flow are fully implemented and production-verified (as of 25 Apr 2026):

- Shadow pilot core — processor, classifier, aggregator, reporter, Baileys bridge (v0.6.0)
- AI engine — `conversation.py`, RAG, bilingual EN/BM, 3 behavioral modes
- After-hours intent detection + revenue leakage formula
- Follow-up engine — Day 1/3/7 automated sequences
- Daily 9 AM GM report — revenue recovered, OTA fees saved, guest sentiment
- Monthly insights — Gemini 30-day transcript analysis
- PDPA encryption — Fernet + SHA-256 phone hashing
- `/audit` calculator (public, self-serve)
- `/apply` intake form (functional, needs ADR fields)
- `/admin/shadow-pilots` provisioning with QR flow
- `/welcome` onboarding wizard (5 steps, functional)
- `/portal` tenant self-management (KB, team, channels, billing pages)
- All 8 Cloud Scheduler jobs enabled in production
- 3 Cloud Run services live (`nocturn-backend`, `nocturn-frontend`, `baileys-bridge`)
