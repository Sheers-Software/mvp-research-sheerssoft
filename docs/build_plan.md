# Build Plan
## Nocturn AI — AI Inquiry Capture & Conversion Engine
### Version 2.0 · 17 Mar 2026 · Original Ship Date: 11 Mar 2026
### Aligned with [product_context.md](./product_context.md) · Steered by [building-successful-saas-guide.md](./building-successful-saas-guide.md)
### Implementation Status: v0.3.0 (Phase 16 — Auth & Integration Hardening) · Live on Cloud Run

---

## ⚠️ Current Blockers to Pilot Go-Live (as of 17 Mar 2026)

These 7 items must be resolved before Vivatel can go live. Everything else is ready.

| # | Blocker | Impact | Action Required |
|---|---------|--------|-----------------|
| 1 | **Dashboard home shows onboarding checklist, not revenue** | GM sees setup tasks instead of the money slide on first login | Rebuild `dashboard/page.tsx` to show KPI cards (yesterday's metrics) as the landing screen |
| 2 | **Staff cannot reply from dashboard** | After handoff, staff must reply via phone — no in-dashboard reply box | Add text input + send button to conversations view |
| 3 | **Daily email report blocked in production** | `SENDGRID_API_KEY` missing from GCP Secret Manager; Cloud Scheduler job not created | Add key to Secret Manager; create Cloud Scheduler job (`30 7 * * *` MYT) |
| 4 | **`FERNET_ENCRYPTION_KEY` missing** | PII encryption bypassed — PDPA non-compliant | Generate key, add to Secret Manager |
| 5 | **Bilingual (BM) responses untested end-to-end** | May degrade guest experience for Malay-speaking guests | Run 50-question BM/Manglish test suite via WhatsApp — must pass at ≥80% before pilot go-live (PRD F1 acceptance criteria) |
| 6 | **Vivatel KB not populated** | AI has no property knowledge to answer with | KB build session: collect rate card, FAQs, facilities from Zul |
| 7 | **"Lost" status missing from leads filter UI** | Staff cannot filter to see lost leads; revenue reporting incomplete | Add "Lost" chip to leads filter dropdown |

---

## 1. Plan Overview

**Objective:** Ship a production-ready AI inquiry capture engine in **28 calendar days** (4 sprints × 7 days) and deploy the first live pilot at Vivatel KL.

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
- [x] Vivatel pilot KB seeded
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
| **16–17** | Handoff Queue UI | Dev | Staff sees pending handoffs with context summary. "Take Over" button. ⚠️ *Reply interface NOT implemented — staff must reply via original channel (phone/email). Reply text input is the #2 remaining gap.* | Handoff flow (Sprint 2) |
| **17–18** | GM Analytics Dashboard + **Dashboard Home Fix** | Dev | Key metrics: total inquiries, after-hours %, response time, leads captured, estimated revenue recovered. Time-series charts. ⚠️ **CRITICAL**: Dashboard home (`/dashboard`) currently shows onboarding checklist — must be replaced with KPI cards showing yesterday's metrics. Analytics exist at `/dashboard/analytics` but are not the landing page. | Analytics aggregation service |
| **18** | Analytics aggregation CRON job | Dev | Daily job: aggregate conversations → `analytics_daily` table. Compute estimated revenue. | Data models (exist) |
| **18** | Product analytics instrumentation | Dev | Amplitude/Mixpanel: activation events, feature usage. North Star Metric: inquiries → leads → revenue. | — |
| **18–19** | Lead Management view | Dev | Sortable/filterable table: leads with name, phone, email, intent, status, value, channel, timestamp. Click-to-view conversation. Status update (new→contacted→converted→lost). CSV export. | Lead data (exists) |
| **19–20** | Automated daily email report | Dev | Scheduled job (7:00am property-local-time). Email to GM: yesterday's metrics, week-over-week comparison. HTML template. ⚠️ *BLOCKED in production: requires `SENDGRID_API_KEY` in Secret Manager + Cloud Scheduler job created.* | SendGrid outbound + analytics data |
| **20** | Dashboard UI polish | Product | Color palette, typography, responsive design. The GM should WANT to open this every morning. Big numbers. Clean layout. | All views built |
| **21** | **Sprint 3 Integration Test** | Both | Generate 100 simulated conversations across all channels. Verify: dashboard shows correct totals, charts render, leads are accurate, daily report sends. | All above |

**Quality Gates:**
- [x] Dashboard loads in < 3 seconds
- [x] Analytics numbers match raw conversation data (seed_dashboard_demo.py generates 100+ scenarios)
- [ ] Daily email report sends on schedule — ⚠️ **BLOCKED in production** (`SENDGRID_API_KEY` missing, Cloud Scheduler job not created)
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

> **Goal:** Vivatel is live. AI is answering real guest inquiries. Dashboard shows real data. GM gets daily reports.

| Day | Task | Owner | Deliverable | Dependencies |
|-----|------|-------|-------------|--------------|
| **22** | Error handling & retry logic | Dev | Graceful LLM failures (fallback to template responses). Webhook retry handling. Circuit breaker for external APIs. | All services |
| **22–23** | Property onboarding flow | Dev | Create property → ingest KB (markdown/JSON) → link WhatsApp → get widget snippet → go live. **Target: supports "Live in 48 hours"** (Day 1: KB build + channel connect; Day 2: live). SheersSoft team handles KB build; hotel spends ~30 min on channel setup. | Backend onboard endpoint |
| **23** | Multi-tenant security audit | Dev | Verify: Property A cannot see Property B's data. RLS enforced. Vector search scoped. Test with 2+ properties. | Data isolation code |
| **24** | PDPA compliance implementation | Dev | PII encryption at field level. Data retention auto-purge. Privacy policy page. Consent flow on widget. Right-to-delete endpoint. | Security requirements |
| **24** | Churn tracking: exit reason capture | Dev | When customer churns: capture reason (product, price, budget, competitor). >5% monthly = product problem. | — |
| **24–25** | Load testing | Dev | Simulate 500 concurrent conversations. Verify Cloud Run auto-scales. Identify and fix bottlenecks. Measure P50/P95/P99 latency. | Production-like environment |
| **25–26** | Vivatel UAT (User Acceptance Testing) | Product | Deploy to production. Zul and team test for 2 days with real scenarios. Collect feedback. | All features complete |
| **26–27** | Bug fixes from UAT | Dev | Address blockers found during Vivatel testing. | UAT feedback |
| **27** | Property onboarding guide + FAQ | Product | One-pager: how to get started, what the AI can/can't do, how to update KB, how to read reports. | Onboarding flow finalized |
| **28** | **🎉 GO LIVE AT VIVATEL** | Both | Vivatel's WhatsApp + website widget are live with real guests. Dashboard is online. GM receivesirst daily report the next morning. | All above |

**Quality Gates:**
- [x] Graceful fallback for LLM failures (template response sent to guest)
- [x] Zero data leakage in multi-tenant audit (RLS + property_id scoping verified)
- [x] PII encrypted at rest (Fernet field-level encryption on phone/email)
- [ ] 500 concurrent conversations load test — pending
- [ ] P95 response latency < 5 seconds — pending formal measurement
- [ ] Vivatel team accepts the product (no critical bugs) — pilot scheduling in progress
- [ ] First daily report email received by GM — pending Vivatel go-live

**Go-Live Checklist:**

| # | Item | Status |
|---|------|--------|
| 1 | Vivatel KB fully populated (rooms, rates, facilities, FAQs, policies) | ○ Pending |
| 2 | WhatsApp Business number verified and linked | ○ Pending |
| 3 | Widget script installed on Vivatel website | ○ Pending |
| 4 | SendGrid inbound parse configured for Vivatel email | ○ Pending |
| 5 | Operating hours configured (affects after-hours tagging) | ○ Pending |
| 6 | GM notification email set (daily reports) | ○ Pending |
| 7 | Cloud Run deployed and accessible | ✅ Live: nocturn-backend-owtn645vea-as.a.run.app |
| 8 | GCP Secret Manager secrets loaded | ✅ All critical secrets loaded (missing: FERNET_ENCRYPTION_KEY, ANTHROPIC_API_KEY, SENDGRID_API_KEY) |
| 9 | Cloud Scheduler jobs created | ○ Pending (4 jobs: daily-report, followups, insights, db-keepalive) |
| 10 | ~~Stripe webhook configured~~ | ⊘ Not required for pilot — invoicing is manual. Activate Stripe when ≥3 paying tenants confirmed. |
| 11 | Rollback plan documented (disable AI, revert to manual) | ○ Pending |

---

## 2.5 Dormant Infrastructure: Built Ahead of Validation

> ⚠️ **These features are implemented but NOT in the v1 customer scope.** They were built speculatively, beyond what 8 market interviews validated. Do not activate until release conditions below are met. Reference: PRD Section 9.2.

> This infrastructure was not in the original 28-day plan but was shipped in v0.2–v0.3 as forward investment.

| Feature | Status | Release Condition |
|---------|--------|------------------|
| Tenant + TenantMembership + OnboardingProgress models | ✅ Built | ≥3 paying tenants onboarded |
| Supabase Auth integration (magic links, admin API) | ✅ Built | Self-serve signup flow needed |
| SuperAdmin provisioning API (`/api/v1/onboarding/provision-tenant`) | ✅ Built | ≥3 paying tenants onboarded |
| SuperAdmin dashboard routes (`/api/v1/superadmin/`) | ✅ Built | ≥3 paying tenants onboarded |
| Stripe billing — checkout session + webhook stub | ✅ Built | ≥3 paying tenants confirmed; live Stripe webhook configured |
| Support chatbot + ticket CRUD | ✅ Built | Customer volume requires self-serve support |
| Application intake (`ai.sheerssoft.com/apply` → Application model) | ✅ Built | Inbound demand requires intake funnel |
| Internal scheduler endpoints (Cloud Scheduler integration) | ✅ Built | ✅ **Use now** — required for daily reports in production |
| Circuit breaker for external calls | ✅ Built | ✅ **Active now** — used in production |
| PII field-level encryption (Fernet) | ✅ Built | ⚠️ **Add `FERNET_ENCRYPTION_KEY` to Secret Manager first** |
| Graceful Redis fallback (in-memory dict) | ✅ Built | ✅ **Active now** — enables Cloud Run without Memorystore |
| Monthly Gemini-powered guest insights | ✅ Built | Activate via Cloud Scheduler when pilot data ≥30 days |

**Pending infra to complete before scaling:**
1. Add remaining secrets to GCP Secret Manager: `FERNET_ENCRYPTION_KEY`, `ANTHROPIC_API_KEY`, `SENDGRID_API_KEY`, `WHATSAPP_API_TOKEN`, `WHATSAPP_APP_SECRET`
2. Create 4 Cloud Scheduler jobs
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

### Week 5–6: Prove It

| Action | Goal |
|---|---|
| Capture Vivatel's first 7 days of data | Real numbers: inquiries, after-hours recovery, leads |
| Build the "Vivatel Case Study" one-pager | Target formula: 20 leads × RM 230 ADR × 20% conversion = RM 920 recovered in first week. Scale to 30-day case study. Do NOT use RM 12,400 until verified by real Vivatel data. |
| Activate SKS Hospitality (Bob's referral) — **highest priority** | Referrals convert 10× better than cold. Use Bob's name. Start in parallel with Vivatel, not after. |
| Share results with Novotel (Shamsuridah), Ibis Styles (Simon) | Book demo calls using Vivatel case study |
| Deploy pilots at 3 more properties | Onboarding flow must work in < 2 hours |

### Week 7–8: Convert

| Action | Goal |
|---|---|
| ROI report for each pilot property — real numbers from their dashboard | Proof, not promises |
| Conversion calls: pilot → paid (Starter or Professional tier) | Target: 60%+ conversion |
| Cold outreach to 10 new properties using Vivatel case study | Expand pipeline |
| Leverage Bob's SKS Hospitality referral | Fresh properties = faster decisions |

### Week 9–10: Scale

| Action | Goal |
|---|---|
| 10 paying customers | RM 20,000+ MRR |
| Formalize onboarding documentation | Repeatable process |
| Hire Customer Success / Support | First non-engineering hire |

---

## 5. Cost Budget (Monthly at 10 Properties)

| Item | Cost / Month | Notes |
|------|-------------|-------|
| Cloud Run (backend + dashboard) | RM 200–400 | Auto-scaling, min 1 instance |
| Cloud SQL (PostgreSQL) | RM 300–500 | db-custom-2-8192, HA |
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
| 3 | Vivatel UAT reveals critical UX issues | Medium | Medium | Reserve 2 days for fixes (Days 26–27). Reduce scope rather than delay launch. | Both |
| 4 | LLM rate limiting during peak hours | Low | Medium | Implement queue with retry. Consider Claude Haiku as overflow provider. | Dev |
| 5 | Hotel website blocks widget script (CSP) | Low | Medium | Provide iframe fallback. Offer to modify their CSP headers. | Dev |
| 6 | Guest data breach / PDPA violation | Low | Critical | Field-level encryption. RLS. Penetration test before go-live. | Dev |
| 7 | CAC > LTV (unit economics) | Medium | Critical | Track from first customer. Stop scaling acquisition if LTV:CAC < 3. | Product |
| 8 | "Build it and they will come" (no distribution) | High | Critical | 3–5 customer calls/week. Case study → demos. Distribution strategy from day one. | Product |
| 9 | Dashboard lands on onboarding checklist, not revenue | High | Critical | GM's first impression is a setup form, not the money slide. Rebuilding dashboard home is the #1 pre-pilot task. | Dev |

---

## 7. Definition of Done

The product is **shipped** when ALL of these are true:

- [ ] A guest sends a WhatsApp message to Vivatel at 11pm and gets a correct AI response in < 30 seconds
- [ ] The web chat widget works on Vivatel's website on both mobile and desktop
- [ ] A guest email to reservations gets an AI response within 60 seconds
- [ ] When AI can't help, the guest is seamlessly handed to staff with full context
- [ ] Every conversation is captured as a lead (zero leakage)
- [ ] The GM opens the dashboard and sees yesterday's inquiry count, after-hours recoveries, and estimated revenue
- [ ] The GM receives a daily email report at **7am** with accurate metrics
- [ ] Property B cannot see Property A's data (verified by test)
- [ ] The system handles 500 concurrent conversations without degradation
- [ ] Zul (Vivatel Reservation Manager) says: *"Yes, this is live. We're using it."*
- [ ] GM sees revenue metrics (not an onboarding checklist) on first login
- [ ] BM/Manglish 50-question test suite run via WhatsApp — ≥80% pass rate confirmed and documented

---

*Ship in 28 days. Prove ROI in 7. Close 10 customers in 60. The plan is tight, the scope is intentionally small, and every feature earns its place by answering one question: "Does this make the GM open the dashboard tomorrow morning?" Aligned with [product_context.md](./product_context.md).*
