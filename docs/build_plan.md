# Build Plan
## Nocturn AI — AI Inquiry Capture & Conversion Engine
### Version 2.3 · 25 Mar 2026 · Original Ship Date: 11 Mar 2026
### Aligned with [product_context.md](./product_context.md) · Steered by [building-successful-saas-guide.md](./building-successful-saas-guide.md)
### Cross-referenced with: [portal_architecture.md](./portal_architecture.md), [product_gap.md](./product_gap.md) v1.2, [prd.md](./prd.md) v2.1
### Implementation Status: v0.5.0 · All GCP compute spun down — ready for next deploy

---

## Remaining Blockers to Pilot Go-Live (as of 23 Mar 2026)

P0 product code is **complete**. The remaining blockers are infra tasks and field work only.

| # | Blocker | Status | Action Required |
|---|---------|--------|-----------------|
| 1 | **Dashboard home shows onboarding checklist, not revenue** | ✅ **RESOLVED** — v0.3.1. Dashboard home shows KPI cards as the landing screen. | — |
| 2 | **Staff cannot reply from dashboard** | ✅ **RESOLVED** — v0.3.1. Reply box live in conversations view, replies forwarded to WhatsApp/web. | — |
| 3 | **Daily email report blocked in production** | ✅ **RESOLVED** — `SENDGRID_API_KEY` + `SENDGRID_FROM_EMAIL` in Secret Manager. 4 Cloud Scheduler jobs created and verified. Note: deleted in 2026-03-23 GCP cleanup — recreate on next deploy. | Recreate 4 Cloud Scheduler jobs on next production deploy. |
| 4 | **`FERNET_ENCRYPTION_KEY` missing** | ✅ **RESOLVED** — Key confirmed in Secret Manager. PII encryption active. | — |
| 5 | **Bilingual (BM) responses untested end-to-end** | ❌ **FIELD WORK** — 50-question test suite written but not run. Half-day. **P0 blocker — must pass ≥80% before first client go-live.** | Run via Twilio sandbox. Must pass ≥80% (see `docs/bm_test_execution_plan.md`). |
| 6 | **Pilot property KB not populated** | ❌ **FIELD WORK** — No KB ingested for first pilot property. 1 day on-site or via admin KB ingestion tool. | KB session: collect rate card, room types, FAQs, policies. Ingest via `/admin/kb-ingestion` or `python backend/scripts/ingest_kb.py`. |
| 7 | **"Lost" status missing from leads filter UI** | ✅ **RESOLVED** — v0.3.1. Lost filter live in leads view. | — |
| 8 | **Tenant self-service portal not built** | ✅ **RESOLVED** — v0.4. Full `/portal` + `/welcome` wizard shipped. | — |
| 9 | **Shadow Pilot infrastructure** | ✅ **SPRINT 2.5 BUILT** — All dev items complete. One infra item remains: Cloud Scheduler job for `/run-weekly-audit-report` (create on next GCP deploy). Day 7 AM notification not yet built. | Create Cloud Scheduler job on next deploy. Build AM notification (see Sprint 2.5 below). |
| 10 | **`WHATSAPP_API_TOKEN` and `WHATSAPP_APP_SECRET` missing from Secret Manager** | ❌ **INFRA** — Required for Meta Cloud API in production. Shadow pilots use Twilio (already configured). Blocks Stage 3 (full product) for first client. | Add to GCP Secret Manager before first Stage 3 client go-live. |

---

## v0.5 — After-Hours Revenue Audit + GCP Production (Current Sprint)

### What Was Built

| Feature | Status |
|---------|--------|
| Public audit calculator at `/audit` (frontend) | ✅ Complete |
| `AuditRecord` model + `audit_records` table | ✅ Complete |
| `POST /audit/calculate` (public, 60/min rate limit) | ✅ Complete |
| `POST /audit/submit` (public, 5/min rate limit) | ✅ Complete |
| `GET/PATCH /audit/records` (superadmin pipeline) | ✅ Complete |
| `/admin/tools/revenue-audit` internal tool | ✅ Complete |
| `ENVIRONMENT=production` in `cloudbuild.yaml` | ✅ Complete |
| `test_ai_accuracy` graceful skip on DB permission error | ✅ Complete |
| `audit_only_mode` + shadow pilot fields on `Property` model | ✅ Complete |
| AI bypass in `conversation.py` when `audit_only_mode=True` | ✅ Complete |
| Weekly audit email (`run_weekly_audit_report` scheduler + internal endpoint) | ✅ Complete |
| `/admin/shadow-pilots` provisioning page | ✅ Complete |
| Dark → light theme migration (globals.css, all pages) | ✅ Complete |
| GCP project ID fix (`nocturn-ai-487207` → `nocturn-aai`) across all configs | ✅ Complete |

---

## Sprint 2.5 — Shadow Pilot Infrastructure (Mostly Complete)

> **Goal:** Complete the three-stage sales funnel. A SheersSoft AM can provision a shadow pilot for a prospect in 5 minutes from the admin panel. The GM gets a real-data audit email on Day 7 automatically.

| Task | Owner | Deliverable | Status |
|------|-------|-------------|--------|
| `audit_only_mode`, `shadow_pilot_start_date`, `shadow_pilot_phone` on `Property` model | Dev | Alembic migration + `main.py` incremental ALTER | ✅ Built |
| Skip AI response when `audit_only_mode = True` | Dev | In `conversation.py` `process_guest_message()`: if `property.audit_only_mode`, log message, return without calling LLM | ✅ Built |
| Weekly audit email template | Dev | SendGrid HTML email: "Your hotel received X after-hours inquiries. Based on your ADR of RM Y, you left approximately RM Z on the table this week." | ✅ Built |
| `run_weekly_audit_report` scheduler job | Dev | `services/scheduler.py` + `POST /api/v1/internal/run-weekly-audit-report` — queries AnalyticsDaily for all `audit_only_mode=True` properties, computes leakage, sends GM email | ✅ Built |
| Cloud Scheduler job for weekly audit email | Infra | 1 new Cloud Scheduler job targeting `/api/v1/internal/run-weekly-audit-report` weekly | ❌ Not created — add on next GCP deploy |
| Shadow pilot provisioning in `/admin` | Dev | `/admin/shadow-pilots` page: create shadow pilot (property name, GM email, ADR, Twilio number), sets `audit_only_mode=True`, records `shadow_pilot_start_date` | ✅ Built |
| Day 7 auto-notification to SheersSoft AM | Dev | When weekly audit email sends, also POST to internal Slack webhook (or log prominently) so AM knows to call same day | ❌ Not built |

**Quality Gates:**
- [ ] Shadow pilot property created via admin → incoming Twilio messages logged → NO AI response sent
- [ ] AnalyticsDaily correctly aggregates `is_after_hours` count for `audit_only_mode` properties
- [ ] Weekly audit email sends with correct inquiry count + RM calculation
- [ ] AM notification fires same day as audit email

---

## v0.4 — Self-Service Onboarding & Portal (Previous Sprint)

### What Was Built

| Feature | Status |
|---------|--------|
| `/portal` layout + home page (multi-property summary) | ✅ Complete |
| `/portal/kb/[propertyId]` — KB self-management | ✅ Complete |
| `/portal/team` — Team member management + invite | ✅ Complete |
| `/portal/channels` — Channel status + widget embed code | ✅ Complete |
| `/portal/properties` — Property list + add property | ✅ Complete |
| `/portal/billing` — Subscription tier + Stripe checkout | ✅ Complete |
| `/portal/support` — Support ticket submit/view | ✅ Complete |
| `/welcome` — 5-step onboarding wizard | ✅ Complete |
| Backend `GET /portal/home` | ✅ Complete |
| Backend `GET /portal/team`, `DELETE /portal/team/{id}` | ✅ Complete |
| Backend `GET /portal/channels` | ✅ Complete |
| Backend `GET/POST/PUT/DELETE /properties/{id}/kb` | ✅ Complete |
| Backend `POST /properties/{id}/kb/ingest-wizard` | ✅ Complete |
| Backend `POST /onboarding/complete/{property_id}` | ✅ Complete |
| Backend `GET /announcements/active` (tenant-facing) | ✅ Complete |
| Auth callback: role-based routing | ✅ Complete |
| `/auth/me` returns role + onboarding_completed | ✅ Complete |
| `/dashboard/insights` page | ✅ Complete |
| Dashboard layout: Insights nav + Portal link for owners | ✅ Complete |
| `/admin/kb-ingestion` tool for SheersSoft operators | ✅ Complete |

---

## 1. Plan Overview

**Objective:** Ship a production-ready AI inquiry capture engine in **28 calendar days** (4 sprints × 7 days) and deploy the first live pilot at a hotel property in Malaysia.

**Constraints:**
- 2-person team (1 Lead Dev, 1 Product/Dev hybrid)
- Sprint 1 AI Core is already built and functional (current codebase)
- First paying customer target: within **21 days of pilot go-live** (see `gtm_execution_plan.md` Phase 3)
- Budget: bootstrapped — optimize for cloud cost efficiency

**Survival imperatives (from Principal Engineer playbook):**
- **Ship fast, learn faster.** Weekly or bi-weekly deployments. Feature flags for safe production testing.
- **Technical founder:** 3–5 customer calls/week. Non-negotiable. Cannot build great products from a conference room.
- **Metrics from day one.** Activation rate, retention cohorts, North Star Metric. Track churn reasons for every lost customer.
- **Refactoring cadence:** One refactoring sprint every 4–5 feature sprints. Document TODOs with business thresholds.

**What's Already Done (Sprint 1 — Complete):**
- [x] FastAPI backend with async SQLAlchemy
- [x] PostgreSQL 16 + pgvector for knowledge base (768-dim Gemini embeddings)
- [x] AI conversation engine (LLM + RAG pipeline): Gemini → OpenAI → Anthropic → template fallback chain
- [x] Property + Conversation + Message + Lead + Analytics data models
- [x] Basic API endpoints (conversations, messages, properties, leads, analytics)
- [x] Pilot KB seeded (demo data)
- [x] Docker Compose local dev environment
- [x] Cloud Run deployment pipeline (Cloud Build, not GitHub Actions)
- [x] Rate limiting (SlowAPI)
- [x] Multi-tenant property isolation

---

## 2. Sprint Plan

### Sprint 2: Channels — "Give the Brain a Mouth" (Days 8–14)

> **Goal:** A guest can message on WhatsApp, website, or email and get an AI response. Staff can take over when needed.

| Day | Task | Owner | Deliverable | Dependencies |
|-----|------|-------|-------------|--------------|
| **8** | [x] WhatsApp Business API registration & verification | Product | Verified WhatsApp Business account | Meta Business verification ready |
| **8–9** | [x] WhatsApp webhook receiver (incoming messages) | Dev | `POST /api/v1/webhook/whatsapp` & `twilio/whatsapp` — receives and verifies Meta/Twilio webhooks | Meta API credentials |
| **9–10** | [x] WhatsApp message sender (outbound replies) | Dev | AI response → formatted → sent via WhatsApp Cloud/Twilio API | Webhook receiver done |
| **8–10** | [x] Web chat widget (embeddable JS) | Dev | `<script src="...">` → floating chat bubble → WebSocket conversation | Can be parallel with WhatsApp |
| **10–11** | [x] Widget ↔ Backend WebSocket integration | Dev | Real-time message exchange between widget and conversation engine | Widget UI + backend WebSocket endpoint |
| **11–12** | [x] Email intake webhook (SendGrid Inbound Parse) | Dev | `POST /api/v1/webhook/email` → parsed email → AI response → reply | SendGrid account configured |
| **12–13** | [x] Human handoff detection + notification | Dev | AI detects "talk to someone" / low confidence → flags conversation → publishes to Redis | Conversation engine |
| **13** | [x] Channel-specific response formatting | Dev | WhatsApp: short messages, no markdown. Email: formatted HTML. Web: rich text. | All channels working |
| **14** | [x] **Sprint 2 Integration Test** | Both | Twilio and regular Meta integrated properly with webhooks processing and replying to channels. | All above |

**Quality Gates:**
- [x] WhatsApp round-trip conversation works (send message → receive AI response)
- [ ] **Bahasa Malaysia Support**: System correctly identifies and responds in BM. ⚠️ *Implemented but not end-to-end tested. **50-question BM/Manglish test suite must pass at ≥80% before pilot go-live** (see PRD F1 acceptance criteria and gtm_execution_plan.md Phase 0, Task P0.6). Re-run before each new property onboarded.*
- [x] Web widget loads on a test page and handles a 5-message conversation
- [x] Email → AI response → reply email with thread preserved
- [x] Human handoff triggers and context is packaged correctly

**Key Risk:** WhatsApp Business API approval can take 1–7 days. **Mitigation:** Apply on Day 8 morning. Build against the test sandbox while waiting. If approval is delayed, pilot launches with web widget + email only.

---

### Sprint 3: Dashboard + Analytics + Reports — "Show the Money" (Days 15–21)

> **Goal:** A GM logs in and sees: *"Last night you received 23 inquiries. We answered 21 in <30s. 14 leads captured. Estimated RM 3,220 recovered."*

| Day | Task | Owner | Deliverable | Dependencies |
|-----|------|-------|-------------|--------------|
| **15** | Observability: OpenTelemetry + metrics + alerts | Dev | Request latency (P50/P95/P99), error rate, 70% capacity alerts | — |
| **15** | Staff Dashboard: project scaffold + auth | Dev | Next.js app with JWT login. Property-scoped access. | Backend auth endpoints (exist) |
| **15–16** | Live Conversations view | Dev | Real-time list of active conversations. Click to view messages. Status indicators (active/handed_off/resolved). | WebSocket from backend |
| **16–17** | Handoff Queue UI | Dev | Staff sees pending handoffs with context summary. "Take Over" button. Staff reply input in conversation detail — replies forwarded to guest via original channel (WhatsApp/web). ✅ Done v0.3.1. | Handoff flow (Sprint 2) |
| **17–18** | GM Analytics Dashboard + Dashboard Home | Dev | Key metrics: total inquiries, after-hours %, response time, leads captured, estimated revenue recovered. Time-series charts. Dashboard home (`/dashboard`) shows revenue KPI cards as the landing screen. ✅ Done v0.3.1. | Analytics aggregation service |
| **18** | Analytics aggregation CRON job | Dev | Daily job: aggregate conversations → `analytics_daily` table. Compute estimated revenue. | Data models (exist) |
| **18** | Product analytics instrumentation | Dev | Amplitude/Mixpanel: activation events, feature usage. North Star Metric: inquiries → leads → revenue. | — |
| **18–19** | Lead Management view | Dev | Sortable/filterable table: leads with name, phone, email, intent, status, value, channel, timestamp. Click-to-view conversation. Status update (new→contacted→converted→lost). CSV export. | Lead data (exists) |
| **19–20** | Automated daily email report | Dev | Scheduled job (7:00am property-local-time). Email to GM: yesterday's metrics, week-over-week comparison. HTML template. ⚠️ *BLOCKED in production: requires `SENDGRID_API_KEY` in Secret Manager + Cloud Scheduler job created.* | SendGrid outbound + analytics data |
| **20** | Dashboard UI polish | Product | Color palette, typography, responsive design. The GM should WANT to open this every morning. Big numbers. Clean layout. | All views built |
| **21** | **Sprint 3 Integration Test** | Both | Generate 100 simulated conversations across all channels. Verify: dashboard shows correct totals, charts render, leads are accurate, daily report sends. | All above |

**Quality Gates:**
- [x] Dashboard loads in < 3 seconds
- [x] Analytics numbers match raw conversation data (seed_dashboard_demo.py generates 100+ scenarios)
- [✓] Daily email confirmed working — `SENDGRID_API_KEY` in Secret Manager, Cloud Scheduler jobs created and verified. Jobs deleted in 2026-03-23 cleanup; recreate on next deploy.
- [x] Lead export to CSV works with all fields
- [x] Handoff queue shows real-time updates via polling

**Design Requirement — The "Money Slide":**

The GM dashboard hero section must display:

```
┌─────────────────────────────────────────────────────────┐
│                    Yesterday · 10 Feb 2026              │
│                                                         │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│   │   47    │  │   21    │  │   14    │  │ RM 3,220│  │
│   │Inquiries│  │After-Hrs│  │ Leads   │  │Recovered│  │
│   │ Handled │  │Recovered│  │Captured │  │ Revenue │  │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘  │
│                                                         │
│   Avg Response: 18s    Handoff Rate: 12%                │
│   ▓▓▓▓▓▓▓▓▓▓░░ 88% handled by AI                      │
└─────────────────────────────────────────────────────────┘
```

This is not optional. This screen sells the product.

---

### Sprint 4: Polish + Deploy + Pilot Launch — "Make It Bulletproof" (Days 22–28)

> **Goal:** First pilot property is live. AI is answering real guest inquiries. Dashboard shows real data. GM gets daily reports.

| Day | Task | Owner | Deliverable | Dependencies |
|-----|------|-------|-------------|--------------|
| **22** | Error handling & retry logic | Dev | Graceful LLM failures (fallback to template responses). Webhook retry handling. Circuit breaker for external APIs. | All services |
| **22–23** | Property onboarding flow | Dev | Create property → ingest KB (markdown/JSON) → link WhatsApp → get widget snippet → go live. **Target: supports "Live in 48 hours"** (Day 1: KB build + channel connect; Day 2: live). SheersSoft team handles KB build; hotel spends ~30 min on channel setup. | Backend onboard endpoint |
| **23** | Multi-tenant security audit | Dev | Verify: Property A cannot see Property B's data. RLS enforced. Vector search scoped. Test with 2+ properties. Must pass before any new client goes live. | Data isolation code |
| **24** | PDPA compliance implementation | Dev | PII encryption at field level. Data retention auto-purge. Privacy policy page. Consent flow on widget. Right-to-delete endpoint. | Security requirements |
| **24** | Churn tracking: exit reason capture | Dev | When customer churns: capture reason (product, price, budget, competitor). >5% monthly = product problem. | — |
| **24–25** | Load testing | Dev | Simulate 500 concurrent conversations. Verify Cloud Run auto-scales. Identify and fix bottlenecks. Measure P50/P95/P99 latency. | Production-like environment |
| **25–26** | Pilot UAT (User Acceptance Testing) | Product | Deploy to production. Pilot client team tests for 2 days with real scenarios. Collect feedback. | All features complete |
| **26–27** | Bug fixes from UAT | Dev | Address blockers found during pilot testing. | UAT feedback |
| **27** | Property onboarding guide + FAQ | Product | One-pager: how to get started, what the AI can/can't do, how to update KB, how to read reports. | Onboarding flow finalized |
| **28** | **🎉 FIRST PILOT GO LIVE** | Both | First pilot property's WhatsApp + website widget are live with real guests. Dashboard is online. GM receives first daily report the next morning. | All above |

**Quality Gates:**
- [x] Graceful fallback for LLM failures (template response sent to guest)
- [x] Zero data leakage in multi-tenant audit (RLS + property_id scoping verified)
- [x] PII encrypted at rest (Fernet field-level encryption on phone/email)
- [ ] 500 concurrent conversations load test — pending
- [ ] P95 response latency < 5 seconds — pending formal measurement
- [ ] First pilot client team accepts the product (no critical bugs) — pilot scheduling in progress
- [ ] First daily report email received by GM — pending first pilot go-live

**Go-Live Checklist (per new client):**

| # | Item | Notes |
|---|------|-------|
| 1 | Property KB fully populated (rooms, rates, facilities, FAQs, policies) | Via `/admin/kb-ingestion` or client self-serves via `/portal/kb` |
| 2 | WhatsApp Business number verified and linked | Meta Business verification required; Twilio sandbox for testing |
| 3 | Widget script installed on client website | One `<script>` tag; most hotel sites are WordPress |
| 4 | SendGrid inbound parse configured for client email | Forward reservations email to SendGrid parse address |
| 5 | Operating hours configured (affects after-hours tagging) | Set in property settings |
| 6 | GM notification email set (daily reports) | Confirm recipient before Cloud Scheduler jobs are active |
| 7 | Cloud Run deployed and accessible | Spun down as of 2026-03-23; redeploy via `gcloud builds submit` |
| 8 | GCP Secret Manager secrets loaded | All critical secrets present. Still missing (optional): `ANTHROPIC_API_KEY`, `WHATSAPP_API_TOKEN`, `WHATSAPP_APP_SECRET` |
| 9 | Cloud Scheduler jobs created | Deleted during 2026-03-23 GCP cleanup — recreate on next production deploy |
| 10 | BM/Manglish 50-question test suite passed at ≥80% | One-time P0 gate; re-run before each new property if AI engine has changed |
| 11 | Stripe webhook configured | Not required for pilot — manual invoicing. Activate when ≥3 paying tenants confirmed. |
| 12 | Rollback plan documented (disable AI, revert to manual) | Maintenance mode toggle available from `/admin/system` |
| 13 | Shadow pilot complete (if using Stage 2 funnel path) | Day 7 audit email sent, GM has seen real inquiry data, Day 7 call completed before requesting Meta API registration |
| 14 | `audit_only_mode` confirmed False before full product launch | Verify in admin panel. If still True, AI will not respond to guests. |

**Shadow Pilot Go-Live Checklist (per prospect):**

| # | Item |
|---|------|
| 1 | Twilio shadow number provisioned and set as `shadow_pilot_phone` on Property |
| 2 | Property created with `audit_only_mode = True` |
| 3 | GM instructed to promote shadow number (WhatsApp bio, email footer, signage) |
| 4 | `shadow_pilot_start_date` recorded |
| 5 | Calendar reminder for Day 7 call set |
| 6 | Day 7 audit email tested in staging before prospect goes live |

---

## 2.5 SaaS Infrastructure — Activation Status

> This infrastructure was not in the original 28-day plan but was shipped in v0.2–v0.3 as forward investment. Full activation details in PRD Section 9.2 and `portal_architecture.md`.

| Feature | Status | Notes |
|---------|--------|-------|
| Tenant + TenantMembership + OnboardingProgress models | ✅ Active (internal) | Used by `/admin` provisioning. Not customer-facing until Phase 4. |
| Supabase Auth (magic links, admin API) | ✅ Active | Magic link login live. Superadmin restricted to `a.basyir@sheerssoft.com`. |
| SuperAdmin dashboard (`/admin`) — ops portal | ✅ Active | Maintenance mode, scheduler config, service health, tenant management. SheersSoft-internal only. |
| SuperAdmin provisioning (`/api/v1/onboarding/provision-tenant`) | ✅ Active (manual) | Used by SheersSoft engineers to provision new tenants. |
| Internal scheduler endpoints | ✅ Active (code ready) | Endpoints live and verified (HTTP 200). Cloud Scheduler jobs **deleted** during 2026-03-23 GCP cleanup — must recreate on next deploy. |
| Circuit breaker for external calls | ✅ Active | Used in production. |
| Graceful Redis fallback (in-memory dict) | ✅ Active | Enables Cloud Run without Memorystore for pilot phase. |
| Maintenance mode middleware | ✅ Active | Toggle from `/admin/system`. 30s in-process cache. Tenant banner on `/dashboard`. |
| Service health dashboard (`/admin/health`) | ✅ Active | 9 parallel checks, 20s cache, 30s auto-refresh frontend. |
| PII field-level encryption (Fernet) | ✅ Active | `FERNET_ENCRYPTION_KEY` confirmed in Secret Manager. |
| Monthly Gemini-powered guest insights | ✅ Built | Activate via Cloud Scheduler when pilot data ≥30 days. |
| Stripe billing — checkout + webhook stub | ❌ Dormant | Activate when pilot-to-paid conversion proven; manual invoicing until then. |
| Support chatbot + ticket CRUD | ✅ Active | `/portal/support` live. Backend ticket CRUD active. |
| Application intake form | ❌ Dormant | Activate when inbound demand justifies self-serve signup. |
| Tenant self-service portal (`/portal`, `/welcome`) | ✅ Active | Built in v0.4. Full portal + 5-step onboarding wizard live. |

**Pending infra to complete before scaling:**
1. ✅ `FERNET_ENCRYPTION_KEY`, `SENDGRID_API_KEY` confirmed in Secret Manager
2. ✅ Cloud SQL removed — database migrated to Supabase (`nocturn_app` user, transaction pooler)
3. ✅ GCP Secret Manager is the sole source of all secrets (no .env fallbacks)
4. ⚠️ **Recreate Cloud Scheduler jobs** on next production deploy (deleted 2026-03-23)
5. Add `ANTHROPIC_API_KEY`, `WHATSAPP_API_TOKEN`, `WHATSAPP_APP_SECRET` to Secret Manager when available
6. Create 4 Cloud Scheduler jobs on next deploy
3. Configure live Stripe webhook → update `STRIPE_WEBHOOK_SECRET`
4. Custom domain mapping (optional): `api.sheerssoft.com` / `app.sheerssoft.com`

---

## 3. Ongoing Rituals (Non-Negotiable)

| Ritual | Cadence | Owner | Notes |
|--------|---------|-------|-------|
| **Customer calls** | 3–5 per week | Technical founder | You cannot build great products from a conference room. |
| **Refactoring sprint** | Every 4–5 feature sprints | Dev | Address technical debt. Document TODOs with business thresholds. |
| **Deployments** | Weekly or bi-weekly | Dev | Feature flags: deploy code without releasing features. Test in production safely. |
| **Churn review** | Every lost customer | Product | Capture exit reason. >5% monthly churn = product problem. |
| **Unit economics review** | Monthly | Product | LTV:CAC, payback period. Stop scaling if CAC > LTV/3. |

---

## 4. Post-Launch: 10-Customer Expansion (Days 29–60)

### Week 1-2: Shadow Pilots Running

| Action | Goal |
|---|---|
| Run audit outreach to 10 prospects (audit calculator link as first touch) | 3–5 audit submissions in first week |
| Convert 3 audit submissions to shadow pilots | 3 shadow pilots active simultaneously |
| Provision shadow Twilio numbers for each | Each prospect has real inquiry data collecting |

### Week 3-4: First Shadow → Full Conversions

| Action | Goal |
|---|---|
| Day 7 calls for first shadow pilots | Each GM reviews their own inquiry data |
| Initiate Meta Cloud API registration for converted prospects | 2-4 day approval window begins |
| Build first property KBs using actual questions from shadow pilot data | KB built from real questions → high AI accuracy from Day 1 |
| First full product clients go live | Real AI responses, real leads captured |

### Week 5-6: Prove It and Case Study

| Action | Goal |
|---|---|
| Capture first 7 days of full-product data | Real numbers: inquiries, after-hours recovery, leads |
| Build the first case study one-pager | Formula: shadow pilot volume × conversion rate × ADR = actual recovery. Do NOT publish estimates. |
| Activate referral pipeline | Referrals convert 10× better than cold outreach. Ask at Day 7 call. |
| Run more audit outreach using shadow pilot data as social proof | "Hotel X had 14 after-hours messages last week on a shadow number — here's their RM figure." |

---

## 5. Cost Budget (Monthly at 10 Properties)

| Item | Cost / Month | Notes |
|------|-------------|-------|
| Cloud Run (backend + dashboard) | RM 200–400 | Auto-scaling, min 1 instance |
| ~~Cloud SQL~~ | RM 0 | **Removed** — replaced by Supabase free tier. No Cloud SQL cost. |
| Cloud Memorystore (Redis) | RM 0 (pilot) / RM 150–250 (scale) | Not needed until >1 Cloud Run instance. In-memory fallback active for pilot. |
| OpenAI GPT-4o-mini | RM 300–600 | ~20,000 conversations total |
| WhatsApp Business API | RM 1,000–2,000 | ~$0.03-0.05 per conversation × 10 properties |
| SendGrid | RM 100–200 | Inbound parse + outbound reports |
| Domain + SSL + CDN | RM 50 | Widget hosting |
| **Total** | **RM 2,100–4,000** | **vs. RM 22,500 MRR = 82–91% gross margin** |

---

## 6. Risk Register & Mitigations

| # | Risk | Probability | Impact | Mitigation | Owner |
|---|------|-------------|--------|------------|-------|
| 1 | WhatsApp API approval delayed >7 days | Medium | High | Apply Day 8. Pilot with web widget + email first. | Product |
| 2 | AI hallucination on rate quotes | Medium | High | Never state rates unless KB confidence > 0.85. Default to handoff. Monitor first 100 conversations manually. | Dev |
| 3 | Pilot UAT reveals critical UX issues | Medium | Medium | Reserve 2 days for fixes (Days 26–27). Reduce scope rather than delay launch. | Both |
| 4 | LLM rate limiting during peak hours | Low | Medium | Implement queue with retry. Consider Claude Haiku as overflow provider. | Dev |
| 5 | Hotel website blocks widget script (CSP) | Low | Medium | Provide iframe fallback. Offer to modify their CSP headers. | Dev |
| 6 | Guest data breach / PDPA violation | Low | Critical | Field-level encryption. RLS. Penetration test before go-live. | Dev |
| 7 | CAC > LTV (unit economics) | Medium | Critical | Track from first customer. Stop scaling acquisition if LTV:CAC < 3. | Product |
| 8 | "Build it and they will come" (no distribution) | High | Critical | 3–5 customer calls/week. Case study → demos. Distribution strategy from day one. | Product |
| 9 | ~~Dashboard lands on onboarding checklist, not revenue~~ | — | — | ✅ **RESOLVED v0.3.1** — Dashboard home shows revenue KPI cards as the first screen. | — |
| 10 | GM refuses Meta Cloud API number transfer | High | High | Shadow pilot data makes this a non-issue: "You had X after-hours messages last week on the shadow number. Your real number gets 4–5x that volume. We just need to route it to us." | Product/Sales |
| 11 | Shadow pilot volume too low to impress GM | Low | Medium | Pre-qualify using audit calculator estimate before provisioning shadow pilot. Properties projecting <5 after-hours msgs/day are below ICP threshold. | Sales |

---

## 7. Definition of Done

The product is **shipped** when ALL of these are true:

- [ ] A guest sends a WhatsApp message at 11pm and gets a correct AI response in < 30 seconds
- [ ] The web chat widget works on a client website on both mobile and desktop
- [ ] A guest email to reservations gets an AI response within 60 seconds
- [ ] When AI can't help, the guest is seamlessly handed to staff with full context
- [ ] Every conversation is captured as a lead (zero leakage)
- [x] ✅ The GM opens the dashboard and sees yesterday's inquiry count, after-hours recoveries, and estimated revenue (v0.3.1)
- [x] ✅ Staff can reply to guests directly from the dashboard (v0.3.1)
- [✓] Daily email infrastructure confirmed working — Cloud Scheduler jobs verified HTTP 200. Note: jobs deleted in 2026-03-23 GCP cleanup; recreate on next deploy.
- [x] ✅ Property B cannot see Property A's data (verified — RLS + property_id scoping)
- [ ] The system handles 500 concurrent conversations without degradation — load test pending
- [ ] First client's reservations team accepts the product (no critical bugs) — pilot scheduling in progress
- [x] ✅ GM sees revenue metrics (not an onboarding checklist) on first login (v0.3.1)
- [ ] BM/Manglish 50-question test suite run via WhatsApp — ≥80% pass rate confirmed (P0 blocker)
- [x] ✅ `FERNET_ENCRYPTION_KEY` confirmed in Secret Manager. PII encryption active.
- [x] ✅ Tenant owner can self-manage KB, team, channels via `/portal` without SheersSoft engineer (v0.4)
- [x] ✅ New client can complete onboarding via `/welcome` wizard without manual handholding (v0.4)

---

*Ship in 28 days. Prove ROI in 7. Close 10 customers in 60. The plan is tight, the scope is intentionally small, and every feature earns its place by answering one question: "Does this make the GM open the dashboard tomorrow morning?" Self-service onboarding (v0.4) means each new client can go live without a SheersSoft engineer in the loop. Aligned with [product_context.md](./product_context.md).*
