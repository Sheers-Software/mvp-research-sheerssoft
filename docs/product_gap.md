# Product Gap Analysis
## Nocturn AI — Codebase vs Hybrid Value Flow
### Version 3.0 · 26 Apr 2026
### Source: Live codebase audit against `nocturn_hybrid_value_flow.html` (Hybrid Co-Pilot Value Delivery & Capture Flow)

---

## Summary

| Phase | Alignment | P0 Gaps | P1 Gaps | P2 Gaps |
|-------|-----------|---------|---------|---------|
| Phase 1 — Acquisition | 100% | 0 | 0 | 0 |
| Phase 2 — Onboarding | 100% | 0 | 0 | 0 |
| Phase 3 — Shadow Pilot | 100% | 0 | 0 | 0 |
| Phase 4 — Hybrid Co-Pilot | 85% | 0 | 1 | 0 |
| Phase 5 — Conversion | 80% | 0 | 0 | 1 |

**Total open gaps: 2** — 0 P0 · 1 P1 · 1 P2

---

## Phase 1 — Acquisition

### GAP-001 · [RESOLVED v0.8.0] `/apply` form ICP qualification fields · **P1**

**Status:** Implemented. `frontend/src/app/apply/page.tsx` now captures `adr_estimate` (RM, number), `monthly_inquiry_volume` (integer), and `star_rating` (1–5 select). `backend/app/models.py` Application model updated. Schema passthrough added. DDL startup migration added.

---

## Phase 2 — Onboarding

### GAP-002 · [RESOLVED v0.8.0] Welcome wizard billing step · **P1**

**Status:** Implemented. `frontend/src/app/welcome/page.tsx` is now 6 steps (was 5). Step 5 is the RM 999 setup fee Stripe checkout (`apiPost /billing/checkout`). URL param handling for `?paid=true` and `?step=N` (Stripe redirect return). "Skip for now" advances to Step 6 with a pending-payment yellow banner. Go Live moved to Step 6.

---

## Phase 3 — Shadow Pilot

### GAP-004 · [RESOLVED] Day-7 report is now property-relative · **P0**
**Current state:** Verified in `backend/app/services/shadow_pilot_reporter.py`. The system now correctly checks `days_active >= 7` and uses `shadow_pilot_report_sent_at` to ensure the report is sent exactly once per pilot, relative to its start date.

---

### GAP-005 · [RESOLVED v0.8.0] AuditRecord ↔ shadow pilot data connected · **P1**

**Status:** Implemented. `Property.audit_estimated_monthly_leakage_rm` (Numeric 12,2) added with DDL migration. Shadow pilot provisioning in `superadmin.py` now looks up the matching `AuditRecord` (by email or hotel name) and stores the estimated leakage on the property. `shadow_pilot_reporter.py` now computes an estimated vs observed comparison and renders it as a prominent callout box in the Day-7 email, immediately above the data table.

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

### GAP-008 · [RESOLVED v0.8.0] FPX / DuitNow payment link · **P1**

**Status:** Implemented using Stripe PaymentLink with FPX + card support (Malaysia-native via Stripe). `Lead` model now has 7 payment tracking fields (`payment_link_url`, `payment_link_stripe_id`, `payment_link_expires_at`, `payment_confirmed_at`, `confirmed_booking_amount_rm`, `facilitated_by_nocturn`, `performance_fee_rm`). `Tenant.performance_fee_balance_rm` added. New endpoint `POST /api/v1/leads/{id}/payment-link` generates a Stripe PaymentLink and persists it to the lead. `payment_link.completed` webhook handler confirms booking, computes 3% fee, and accumulates on tenant. Conversations UI shows "DIRECT BOOKING PAYMENT" section in the AI draft sidebar when `lead.intent === 'room_booking'`.

---

### GAP-009 · [RESOLVED v0.8.0] 3% performance fee attribution and tracking · **P1**

**Status:** Implemented. Attribution flows from `payment_link.completed` webhook → `Lead.facilitated_by_nocturn` + `Lead.performance_fee_rm` → `Tenant.performance_fee_balance_rm`. Monthly APScheduler job (`run_monthly_performance_fee_billing`) runs on the 1st of each month (UTC midnight = 08:00 MYT) and posts accumulated fees as Stripe InvoiceItem, then resets the balance. Analytics endpoint and dashboard now surface "Performance fee accrued" metric card (RM value, `minimumFractionDigits: 2`).

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

## Resolved Gaps (v0.8.0 Update — 26 Apr 2026)

- **GAP-001**: `/apply` form now captures ADR, monthly inquiry volume, star rating.
- **GAP-002**: Welcome wizard Step 5 is RM 999 Stripe checkout (6-step wizard).
- **GAP-005**: AuditRecord linked to shadow pilot; Day-7 email shows pre/post comparison.
- **GAP-008**: FPX/card Stripe PaymentLink flow — generate, send, confirm via webhook.
- **GAP-009**: 3% performance fee attribution, monthly billing job, analytics card.

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
| GAP-007 | Google Sheet inventory reader missing | 1 day |

**Total P1: 1 day dev**

---

### P2 — Before scale (operational overhead at > 5 clients)

| ID | Gap | Effort |
|----|-----|--------|
| GAP-011 | 30-day guarantee has no enforcement code | 0.5 day |

**Total P2: 0.5 day dev**

---

## What is well-aligned

The following components from the value flow are fully implemented and production-verified (as of 26 Apr 2026):

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
- `/apply` ICP qualification (ADR, monthly inquiry volume, star rating) — v0.8.0
- Welcome wizard 6-step billing flow (RM 999 Stripe checkout) — v0.8.0
- AuditRecord ↔ shadow pilot leakage comparison in Day-7 email — v0.8.0
- FPX/card direct booking payment link (Stripe PaymentLink) — v0.8.0
- 3% performance fee attribution, monthly Stripe billing job — v0.8.0
