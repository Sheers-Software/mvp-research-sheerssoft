# Build Plan
## Nocturn AI — AI Inquiry Capture & Conversion Engine
### Version 2.5 · 24 Apr 2026
### Cross-referenced with: prd.md v2.5, architecture.md v2.5, shadow_pilot_spec.md v1.0, product_gap.md v1.4

---

## Status Snapshot (24 Apr 2026)

| # | Blocker | Status | Action |
|---|---------|--------|--------|
| 1 | Dashboard home shows revenue KPIs | ✅ RESOLVED v0.3.1 | — |
| 2 | Staff reply from dashboard | ✅ RESOLVED v0.3.1 | — |
| 3 | Daily email report (code + infra) | ✅ RESOLVED — Cloud Scheduler jobs deleted in 23 Mar cleanup | Recreate 5 jobs on next deploy |
| 4 | FERNET_ENCRYPTION_KEY | ✅ RESOLVED v0.3.2 | — |
| 5 | Infra migration to Supabase-only | ✅ RESOLVED v0.3.3 | — |
| 6 | /portal + /welcome wizard | ✅ RESOLVED v0.4 | — |
| 7 | Audit calculator + shadow pilot stubs | ✅ RESOLVED v0.5 | — |
| 8 | **BM/Manglish 50-question test** | ❌ FIELD WORK | Run test suite (≥80%). Half-day. |
| 9 | **Shadow pilot — Baileys linked device** | ❌ SPRINT 2.5 | Full implementation spec in shadow_pilot_spec.md |
| 10 | **WHATSAPP_API_TOKEN in Secret Manager** | ❌ STAGE 3 ONLY | Not needed until Stage 3. Skip for now. |

---

## Sprint 2.5 — Shadow Pilot Deep Implementation (CURRENT SPRINT)

**Goal:** Hotel GM scans one QR code. Nocturn observes their real WhatsApp for 7 days. GM receives an email on Day 7 with their exact revenue leakage in RM, a link to a live dashboard, and sample conversations from their own hotel. No new number promoted. No disruption to hotel operations.

**Duration:** 6 development days + 0.5 day infrastructure.

**Architecture change from previous plan:** The previous stub used a separate Twilio number (`shadow_pilot_phone` = Twilio number). This is replaced with Baileys linked device on the hotel's real number. The `shadow_pilot_phone` field now stores the hotel's real WhatsApp number for reference only — Baileys observes it directly via linked session. See architecture.md v2.5 Section 2.6.

---

### Day-by-Day Sprint 2.5 Plan

#### Day 1 — Baileys Bridge Service (Foundation)

| Task | Deliverable | Notes |
|---|---|---|
| Create `baileys-bridge/` Node.js project | `package.json`, `tsconfig.json`, `Dockerfile` | Use `@whiskeysockets/baileys` v6.7. TypeScript strict mode. |
| Implement `SessionManager` | `session-manager.ts` — starts/stops sessions, emits QR, handles reconnect | Full implementation in shadow_pilot_spec.md Section 4.3 |
| Implement `EventForwarder` | `event-forwarder.ts` — POSTs events to FastAPI backend | POST to `/api/v1/internal/shadow-event` with `X-Internal-Secret` |
| Implement Express API | `index.ts` — `/internal/start-session`, `/internal/stop-session`, `/qr/:slug` | Loads active sessions from backend on startup |
| Local test | Scan QR with a test WhatsApp number, send/receive 3 messages, verify events reach FastAPI | Use `ngrok` for local webhook in dev |

**Quality gate:** QR renders → scan → session connected → send a test message → event received by FastAPI mock endpoint. End-to-end in < 60 seconds.

---

#### Day 2 — Database Models + Migration

| Task | Deliverable | Notes |
|---|---|---|
| Alembic migration: Property model additions | `shadow_pilot_mode`, `shadow_pilot_start_date`, `shadow_pilot_phone`, `shadow_pilot_session_active`, `shadow_pilot_session_last_seen`, `shadow_pilot_dashboard_token`, `shadow_pilot_dashboard_token_expires`, `avg_stay_nights` | Incremental ALTER — safe on live DB. See shadow_pilot_spec.md Section 3.1. |
| New model: `ShadowPilotConversation` | `backend/app/models/shadow_pilot.py` + Alembic migration | All fields per shadow_pilot_spec.md Section 3.2 |
| New model: `ShadowPilotAnalyticsDaily` | Same file, separate class + Alembic migration | All fields per shadow_pilot_spec.md Section 3.3 |
| Add indexes | `idx_spc_property_id`, `idx_spc_first_message`, `idx_spc_is_after_hours`, `idx_spc_is_unanswered`, `idx_spc_phone_hash` | Defined in shadow_pilot_spec.md Section 3.2 |
| Migrate existing data | SQL: `UPDATE properties SET shadow_pilot_mode = audit_only_mode WHERE audit_only_mode = TRUE` | Keep `audit_only_mode` — still used by hybrid co-pilot |
| Test migrations | Run Alembic up/down on local Supabase | Verify rollback works cleanly |

**Quality gate:** `alembic upgrade head` runs clean. `alembic downgrade -1` runs clean. Both new tables exist with correct columns and indexes.

---

#### Day 3 — FastAPI Shadow Pilot Processor

| Task | Deliverable | Notes |
|---|---|---|
| New file: `shadow_pilot_processor.py` | `handle_message_received()` + `handle_message_sent()` | Full implementation in shadow_pilot_spec.md Section 5.1 |
| New file: `shadow_pilot_classifier.py` | `classify_intent()` — returns (intent, confidence, topic, language) | Full implementation in shadow_pilot_spec.md Section 5.2 |
| WhatsApp transport abstraction update | `get_transport()` returns `BaileysTransport(observe_only=True)` when `shadow_pilot_mode=True` | Ensures zero messages sent during shadow mode |
| New internal endpoints | `POST /api/v1/internal/shadow-event`, `POST /api/v1/internal/shadow-session-status`, `POST /api/v1/internal/shadow-heartbeat`, `GET /api/v1/internal/shadow-active-properties` | All require `X-Internal-Secret`. Add to `internal.py` router. |
| Unit tests | `test_shadow_processor.py` — test `handle_message_received` creates correct record, `handle_message_sent` computes correct response_time_minutes, after-hours flag correct, `observe_only=True` never sends | Pytest. Cover edge cases: duplicate events, media messages, unanswered after 24hr. |

**Quality gates:**
- [ ] `handle_message_received` with `shadow_pilot_mode=False` → no-op (returns immediately)
- [ ] `handle_message_received` with `shadow_pilot_mode=True` → `ShadowPilotConversation` created
- [ ] `handle_message_sent` with matching conversation → `response_time_minutes` computed correctly
- [ ] `handle_message_sent` with no matching conversation → no crash, silent ignore
- [ ] After-hours flag: message at 11 PM property local time → `is_after_hours=True`
- [ ] Intent: "ada bilik tak?" → `is_booking_intent=True`
- [ ] `get_transport()` with `shadow_pilot_mode=True` → `send_message()` returns False without calling bridge

---

#### Day 4 — Daily Aggregation + Revenue Computation

| Task | Deliverable | Notes |
|---|---|---|
| New file: `shadow_pilot_aggregator.py` | `run_daily_aggregation()` — computes all 30+ metrics per property per day | Full implementation in shadow_pilot_spec.md Section 5.3 |
| Internal endpoint | `POST /api/v1/internal/run-shadow-pilot-aggregation` | Calls `run_daily_aggregation()`. Requires `X-Internal-Secret`. |
| Revenue formula implementation | `revenue_at_risk_conservative = booking_intent_unanswered × ADR × avg_stay_nights × 0.20 × 0.60` | Default ADR: RM 230. Default avg_stay_nights: 1.0. Both configurable per property. |
| `ShadowPilotWeeklyRollup` dataclass | `backend/app/services/shadow_pilot_reporter.py` | Computed on-demand from 7 days of `ShadowPilotAnalyticsDaily`. See shadow_pilot_spec.md Section 3.4. |
| `compute_weekly_rollup()` function | Aggregates 7 daily rows into one rollup + selects 3–5 sample abandoned conversations | Used by both weekly report email and token-gated dashboard API |
| Unit tests | `test_shadow_aggregator.py` — verify revenue formula, metric counts, edge case: 0 conversations, edge case: all conversations unanswered | Pytest. Test with 20 fixture conversations. |

**Quality gates:**
- [ ] 0 conversations → aggregation runs clean (no crash, all metrics = 0)
- [ ] 5 booking-intent after-hours unanswered conversations at ADR 230 → `revenue_at_risk_conservative = 5 × 230 × 1.0 × 0.20 × 0.60 = RM 138`
- [ ] Conversations open > 24hr → `status = "abandoned"`, `is_unanswered = True`
- [ ] `peak_inquiry_hour` correctly identifies the hour with most activity
- [ ] `inquiries_by_hour` has exactly 24 keys ("0" through "23")

---

#### Day 5 — Weekly Report Email + GM Dashboard API

**Part A: Weekly Report Email**

| Task | Deliverable | Notes |
|---|---|---|
| Email template | `backend/app/templates/shadow_pilot_weekly_report.html` | Full spec in shadow_pilot_spec.md Section 8. Inline CSS (email-safe). Max-width 600px. |
| `send_weekly_report_email()` | Renders template with `ShadowPilotWeeklyRollup` + sends via SendGrid | Subject line: `[Hotel Name]: You left RM X on the table this week.` |
| 24-hour bar chart (HTML/CSS) | Rendered inline in email — no external image dependency | Use HTML `<div>` bars with inline height styles computed from `inquiries_by_hour`. Two colours: green (business hours), red (after-hours). |
| Sample conversations section | Renders 3–5 `sample_abandoned_conversations` from rollup | Phone numbers masked: `+60XXXXX12`. Show time, topic, preview, estimated value, response status. |
| AM notification | After GM email sends: POST to Slack webhook (or log to a dedicated `sheers_notifications` table if Slack not set up) | Message: "Shadow pilot Day 7: [Hotel Name]. [X] unanswered inquiries. RM [leakage] leakage. Call GM today: [GM email]" |
| `run_shadow_pilot_weekly_report()` function | Checks all active shadow pilots, fires report for any where `days_active % 7 == 0` | Uses `compute_weekly_rollup()`. See shadow_pilot_spec.md Section 9. |
| Internal endpoint | `POST /api/v1/internal/run-shadow-pilot-weekly-report` | Called by Cloud Scheduler. Requires `X-Internal-Secret`. |

**Part B: Token-Gated GM Dashboard API**

| Task | Deliverable | Notes |
|---|---|---|
| Dashboard token generation | On shadow pilot provisioning: generate signed JWT (`property_id`, `type: "shadow_dashboard"`, `exp: now + 30 days`). Store in `Property.shadow_pilot_dashboard_token`. | HS256, signed with `SECRET_KEY`. |
| API endpoint | `GET /api/v1/shadow/{property_slug}/summary?token={jwt}` | Validates JWT. Returns `ShadowPilotWeeklyRollup` + last 7 `ShadowPilotAnalyticsDaily` rows. No Supabase auth — token only. |
| Token embedded in weekly report email | CTA button URL = `/shadow/[slug]?token=[token]` | Regenerated on each weekly report send if old token near expiry. |

**Quality gates:**
- [ ] Email renders correctly at 375px width (mobile)
- [ ] Email renders correctly at 600px width (desktop)
- [ ] Subject line shows correct RM figure
- [ ] Sample conversations section shows 3–5 rows with masked phone numbers
- [ ] HTML bar chart renders without any external image/CDN dependency
- [ ] AM notification fires within 60 seconds of GM email send
- [ ] Token-gated dashboard API returns 401 for invalid token
- [ ] Token-gated dashboard API returns 401 for expired token (>30 days)
- [ ] Token-gated dashboard API returns correct rollup for valid token

---

#### Day 6 — Admin Panel + Token-Gated Frontend Page

**Part A: Updated /admin/shadow-pilots**

| Task | Deliverable | Notes |
|---|---|---|
| Provisioning form update | Add fields: `avg_stay_nights`, `operating_hours` (start/end time). Remove `twilio_number` field (no longer needed). | Operating hours used for after-hours flag. |
| QR code display step | After form submit → modal transitions to QR display. Polls `GET /superadmin/shadow-pilots/{id}/qr` every 3 seconds. Shows QR as `<img src="data:image/png;base64,...">`. | On status `"connected"`: replace QR with green "✓ Connected to [Hotel Name]'s WhatsApp" message. |
| Active pilots list update | Show: hotel name, session status (connected/disconnected), days active, 7-day inquiry count, 7-day leakage (RM). | Poll session status every 30 seconds. |
| Disconnect button | `DELETE /api/v1/superadmin/shadow-pilots/{id}` → confirmation modal → stops Baileys session. | Show warning: "This will disconnect the observation session. Hotel's WhatsApp continues working normally." |

**Part B: New /shadow/[slug] Page (Token-Gated GM Dashboard)**

| Task | Deliverable | Notes |
|---|---|---|
| Next.js page: `frontend/app/shadow/[slug]/page.tsx` | Fetches `/api/v1/shadow/{slug}/summary?token={token}` (token from URL query param). No auth middleware — token-only route. | Server component for initial data fetch. |
| Hero KPI section | 6 cards: total inquiries / after-hours unanswered / weekly leakage / avg after-hours response / annualised leakage / booking intent rate | Large numbers. Clean layout. Matches brand. |
| Hour-by-hour chart | Recharts `BarChart` (already a project dependency). 24 bars. Green = business hours. Red = after-hours. X-axis: hours. Y-axis: inquiry count. | No new chart library needed. |
| Response time breakdown | Stacked bar: `<30min | 1-4hr | 4-8hr | 8-24hr | Unanswered`. Shows distribution of all conversations. | |
| Sample abandoned conversations table | 3–5 rows: time, topic, preview, estimated value, response status | Phone numbers masked. |
| "What If" comparison | Two-column table: "This week (actual)" vs "With Nocturn AI (projected)". Response time, unanswered count, revenue. | |
| CTA section | Prominent button: "Start 48-Hour Implementation — RM 999" → `/apply`. | Include the 30-day guarantee copy. |
| Error state | Invalid/expired token → clean error page: "This report link has expired. Contact ahmad@sheerssoft.com to request a new link." | No error stack traces exposed. |

**Quality gates:**
- [ ] `/shadow/[slug]?token=[valid_jwt]` → page loads with correct data, < 3 seconds
- [ ] `/shadow/[slug]?token=[invalid]` → clean error page
- [ ] All 6 hero KPIs visible above the fold on mobile (375px)
- [ ] CTA button visible without scrolling on desktop
- [ ] QR code appears in admin modal within 5 seconds of provisioning
- [ ] Session status updates to "Connected" in admin panel within 60 seconds of scan

---

#### Day 6.5 — Infrastructure & Cloud Scheduler

| Task | Deliverable | Notes |
|---|---|---|
| Update `cloudbuild.yaml` | Add Baileys bridge build + deploy steps | See architecture.md v2.5 Section 9.2 |
| Add secrets to GCP Secret Manager | `BAILEYS_BRIDGE_URL` | Value: Cloud Run URL of the bridge service (known after first deploy) |
| Create Cloud Scheduler jobs | `shadow-pilot-daily-aggregation` (0 0 * * *) and `shadow-pilot-weekly-report` (0 8 * * 1) | Add `X-Internal-Secret` header. Both jobs target the FastAPI backend. |
| Recreate the 5 deleted Cloud Scheduler jobs | `run-daily-report`, `run-followups`, `run-insights`, `cleanup-leads`, `run-weekly-audit-report` | These were deleted in the 23 Mar GCP cleanup. Must recreate on next deploy. |
| End-to-end integration test | Provision a test shadow pilot using a personal WhatsApp number. Send 5 test messages (mix of after-hours and business-hours). Verify: conversations created, after-hours flags correct, manual trigger of aggregation job produces correct `ShadowPilotAnalyticsDaily` row, manual trigger of weekly report sends correct email. | Full pipeline test. |

---

### Sprint 2.5 Quality Gates (All Must Pass Before Sprint 2.6 Starts)

**Observation pipeline:**
- [ ] Hotel GM scans QR → session established → confirmation in admin panel (< 60 seconds)
- [ ] Incoming guest message → `ShadowPilotConversation` created (< 5 seconds)
- [ ] Staff reply → `response_time_minutes` computed correctly
- [ ] After-hours flag set correctly (test: send message at 11 PM property local time)
- [ ] Booking intent classified correctly on 3 BM and 3 EN test messages
- [ ] **Zero messages sent to any guest during shadow_pilot_mode=True** (verified by checking Baileys bridge send logs — should be empty)
- [ ] Session auto-reconnects within 10 seconds of simulated drop

**Aggregation:**
- [ ] Daily aggregation runs clean for a property with 0 conversations
- [ ] Daily aggregation produces correct all 30+ metrics for a property with 20 test conversations
- [ ] Revenue formula produces expected RM figure (cross-check manually)
- [ ] `unanswered_count` matches manual count after 24hr window

**Report & dashboard:**
- [ ] Weekly report email delivers to GM test inbox
- [ ] Email renders correctly on mobile (375px) and desktop (600px)
- [ ] SheersSoft AM notification fires within 60 seconds of report send
- [ ] Token-gated dashboard loads at `/shadow/[slug]?token=[valid_jwt]`
- [ ] All 6 hero KPIs visible above the fold on mobile
- [ ] CTA links to `/apply`

---

## Sprint 2.6 — Hybrid AI Co-Pilot (Following Sprint)

**Goal:** Hotels get AI-drafted replies in the dashboard. Staff copy the draft into WhatsApp Business App and send. No Meta API required. Google Sheet inventory sync for live availability. FPX/DuitNow payment link in every booking-intent reply.

**Estimated duration:** 4.5 development days.

| Task | Effort | Deliverable |
|---|---|---|
| Hybrid reply drafting sidebar in `/dashboard/conversations` | 1 day | AI draft appears in right panel when a new guest message arrives. "Copy to WhatsApp" button. Staff edits + sends. |
| Google Sheet inventory reader (2-min polling) | 0.5 day | Polls hotel's linked Google Sheet. Room availability injected into AI system prompt. No PMS needed. |
| FPX/DuitNow payment link generator | 0.5 day | When AI detects booking intent, embed payment link in draft. Guest can pay direct. |
| "RM X recovered today" in daily GM report | 0.5 day | Hybrid-aware analytics: tracks conversations where staff sent AI-drafted reply + guest subsequently booked. |
| BM 50-question end-to-end test | 0.5 day field | Run via WhatsApp sandbox. Must pass ≥80%. **P0 gate before any live co-pilot.** |
| First pilot KB population session | 1 day field | 90-min session with hotel GM/property contact. Ingest via `/admin/kb-ingestion`. |

**Sprint 2.6 quality gates (all must pass before first client goes live):**
- [ ] BM/Manglish test suite passes ≥80%
- [ ] AI draft appears in dashboard within 5 seconds of guest message
- [ ] "Copy to WhatsApp" copies the exact draft text to clipboard
- [ ] Google Sheet polling updates AI context within 2 minutes of sheet edit
- [ ] FPX link included in draft when `is_booking_intent = True`
- [ ] Daily GM report shows "RM X recovered via co-pilot" metric

---

## Post-Sprint Roadmap

### Sprint 3 — After First Pilot Live

| Feature | Why |
|---|---|
| Day 7 AM auto-notification (Slack → WhatsApp) | Closes the shadow pilot → co-pilot conversion loop without manual tracking |
| Announcements system (compose + tenant banner) | Backend model/table already exists. Frontend compose UI missing. |
| "Mark as Booked" confirmed revenue in dashboard | GMs want to mark a lead converted with actual RM value for the case study data |
| Week-over-week comparison in daily email | 14+ days of pilot data needed first |

### Sprint 4+ — At Scale (5+ Paying Tenants)

| Feature | Release Condition |
|---|---|
| Stripe billing activation | ≥3 paying tenants confirmed and manually invoiced |
| Meta Cloud API full auto-send (Stage 3) | Virtual office address verified + 5 paying pilots |
| Official BSP migration (Wati or 360dialog) | After Meta registration completes |
| Mobile-responsive dashboard | First hotel GM requests it |
| `/dashboard/insights` — AI performance + KB gaps | ≥30 days of pilot data per property |
| RBAC staff tiers (manager / revenue / ops) | No tenant has asked for this yet |

---

## Go-Live Checklists

### Shadow Pilot Go-Live (per new prospect) — Updated v2.5

| # | Item | Verified |
|---|---|---|
| 1 | Property record created in `/admin` with correct ADR, avg_stay_nights, operating hours, GM email | |
| 2 | Shadow pilot provisioned via `/admin/shadow-pilots` | |
| 3 | QR code displayed in admin panel | |
| 4 | Hotel GM (or owner) scans QR on their WhatsApp Business phone | |
| 5 | Admin panel shows "Connected" for this property | |
| 6 | `shadow_pilot_mode = True` confirmed in property record | |
| 7 | `shadow_pilot_start_date` recorded correctly | |
| 8 | Test: send a WhatsApp message to hotel's number from a different phone → verify `ShadowPilotConversation` created (< 5 seconds) in Supabase | |
| 9 | Test: send a reply FROM the hotel's number → verify `response_time_minutes` computed | |
| 10 | Test: **verify NO auto-reply sent to the test number** | |
| 11 | Calendar reminder set for Day 7 call | |
| 12 | Day 7 weekly report email tested in staging before pilot starts | |
| 13 | Token-gated dashboard URL saved and tested | |

### Hybrid Co-Pilot Go-Live (per new property) — Unchanged

| # | Item |
|---|---|
| 1 | Property KB fully populated (rooms, rates, facilities, FAQs, policies) |
| 2 | Google Sheet inventory link provided and polling confirmed |
| 3 | `shadow_pilot_mode = False`, `audit_only_mode = False` confirmed in property record |
| 4 | `whatsapp_provider = "baileys"` set (same Baileys session from shadow pilot, now active) |
| 5 | BM/Manglish 50-question test suite passed at ≥80% |
| 6 | GM notification email set for daily reports |
| 7 | Cloud Scheduler jobs confirmed active |
| 8 | 30-day revenue recovery guarantee communicated to GM |

---

## Cost Budget (Updated — v2.5)

| Item | Cost / Month | Notes |
|---|---|---|
| Cloud Run (backend + dashboard) | RM 200–400 | Existing |
| Cloud Run (Baileys bridge) | RM 50–100 | New. Min 1 instance, 512MB. ~RM 70/month at min capacity. |
| Cloud Storage (session persistence) | RM 5–10 | For `/sessions` volume at scale. Free tier covers pilot. |
| Supabase PostgreSQL | RM 0 (free tier) | Two new tables add negligible storage. |
| Google Gemini (intent classification) | RM 20–50 | ~100 intent classifications/day across all active pilots. Minimal. |
| OpenAI GPT-4o-mini (co-pilot drafts) | RM 300–600 | Unchanged |
| SendGrid | RM 100–200 | +weekly pilot report emails (minimal volume) |
| **Total** | **RM 675–1,360** | **vs. RM 22,500 MRR at 10 properties = 85–97% gross margin** |

---

## Definition of Done — Sprint 2.5

Sprint 2.5 is complete when ALL of the following are true:

- [ ] Hotel GM scans one QR code from the admin panel and Nocturn begins observing their real WhatsApp in < 60 seconds
- [ ] Incoming guest messages are logged as `ShadowPilotConversation` records within 5 seconds
- [ ] Staff replies are observed and `response_time_minutes` computed correctly
- [ ] **Zero messages sent to any guest at any point** (verified end-to-end)
- [ ] After-hours flag, booking intent, and response time tracking all produce correct values on test data
- [ ] Daily aggregation job produces all 30+ metrics correctly
- [ ] Revenue leakage formula produces the correct RM figure
- [ ] Weekly report email delivers with correct figures, sample conversations, and CTA
- [ ] Token-gated GM dashboard loads and shows correct data
- [ ] SheersSoft AM notification fires on Day 7 report send
- [ ] Admin panel shows QR → connected → session status correctly
- [ ] All existing tests continue to pass (no regressions)
- [ ] Cloud Scheduler jobs for aggregation and weekly report created and verified (HTTP 200)

---

*v2.5 changes: Sprint 2.5 fully rewritten from stub to complete day-by-day implementation plan. Shadow pilot architecture changed from Twilio secondary number to Baileys linked device on hotel's real WhatsApp. Sprint 2.6 (Hybrid Co-Pilot) unchanged — still the following sprint. Infrastructure cost updated to include Baileys bridge container.*
