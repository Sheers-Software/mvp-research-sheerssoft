# Product Requirements Document (PRD)
## Nocturn AI — AI Inquiry Capture & Conversion Engine
### Version 2.4 · 20 Apr 2026
### Aligned with [product_context.md](./product_context.md) · Ground truth: [opportunity_2_playbook.md](./opportunity_2_playbook.md)
### Cross-referenced with: [portal_architecture.md](./portal_architecture.md), [product_gap.md](./product_gap.md), [gtm_execution_plan.md](./gtm_execution_plan.md)

---

## 1. Problem Statement (2026 Reality)

Independent Malaysian 3–4 star hotels (40–150 rooms) still lose 57.35% of bookings to OTAs while their own WhatsApp/email inquiries (30–50+/day) go unanswered after 6 PM. Guests default to Agoda/Booking.com → hotel waits 30–60 days for net payout while wages (RM1,700+), utilities (+20–30%), and staff turnover crush cash flow.

**No product today turns those direct inquiries into same-day FPX/DuitNow bookings while proving the exact RM recovered.**

---

## 2. Product Vision

An AI-powered Direct-Booking Closer that sits on top of the hotel's existing WhatsApp Business App + Google Sheet and delivers **15%+ recovered direct revenue (same-day cash + 15–30% OTA commission savings) in as little as 7 days**.

### Design Principles

| # | Principle | What It Means in Practice |
|---|---|---|
| 1 | **Results before features** | Every screen, every notification, every report answers: *"How much money did this make me?"* |
| 2 | **Guest experience is sacred** | AI responses must feel like a knowledgeable concierge, not a chatbot. Under 30 seconds. Warm, not robotic. |
| 3 | **Zero burden on hotel staff** | One `<script>` tag for the widget. One WhatsApp number linked. No training manual. No IT department required. |
| 4 | **Honest AI** | Never fabricate rates or availability. When unsure, hand off to a human with full context. Trust is the product. |
| 5 | **Show, don't tell** | The dashboard is the sales pitch. If the GM opens it every morning, we win. If they don't, we've failed. |
| 6 | **Live in 48 Hours** | Onboarding must be frictionless. No complex IT integrations. Forward an email, drop a script tag, and go live. |
| 7 | **Proof Before Commitment** | Never ask for a hotel's WhatsApp Business API credentials before showing the GM real data from their own number. The shadow pilot gives them 7 days of actual inquiry volume before they transfer their real number. |

---

## 3. Target Customer

### Primary ICP (Ideal Customer Profile) — Ruthlessly Narrow

- Independent 3–4 star Malaysian hotels (40–150 rooms)
- WhatsApp is primary booking channel (>60% of inquiries)
- No PMS (or legacy Excel/Google Sheet only)
- GM/Revenue Manager is the buyer
- Heavy OTA dependency + cash-flow pain from delayed payouts
- Locations: Klang Valley, Penang, Johor Bahru first

**Explicitly NOT**: Chains, budget hostels, 5-star, properties <20 inquiries/day.

### User Personas

**Persona 1: The GM — "Show me the money"**
- Cares about: occupancy, revenue, OTA cost reduction, guest satisfaction scores
- Uses the product: daily email report, morning dashboard check
- Success = *"I can see exactly how many leads we recovered last night."*

**Persona 2: The Reservations Manager — "Stop the drowning"**
- Cares about: inbox volume, response speed, shift handover gaps
- Uses the product: handoff queue, live conversation view, lead list
- Success = *"I come in at 8am and the AI already handled the overnight inquiries. I just follow up on the warm leads."*

**Persona 3: The Guest — "Just answer my question"**
- Cares about: fast, accurate answers about rates, availability, facilities
- Interacts via: WhatsApp, hotel website chat bubble, email
- Success = *"I got a helpful reply in 20 seconds at 11pm. I'm booking direct."*

---

## 4. Feature Requirements

### 4.1 v1 Scope — Ship This

#### F0: Hybrid AI Co-Pilot (P0 — Ship First)
| Attribute | Detail |
|---|---|
| **User Story** | *As a hotel GM, I receive AI-drafted WhatsApp/email replies in my dashboard — complete with availability from our Google Sheet and an FPX payment link — and send them with one click via my existing WhatsApp Business App. No Meta API required.* |
| **Flow** | Guest messages hotel's WhatsApp Business App → Hotel opens dashboard → AI drafts reply in <5 seconds including availability + FPX/DuitNow link → Hotel sends with one click or copies to WhatsApp Business App |
| **Data Source** | Google Sheet inventory (2-minute polling) as availability source until full Meta API integration |
| **Response Target** | <60 seconds end-to-end (beats manual 8–24 hr delays) |
| **Success Metric** | 15%+ shift to direct bookings with same-day cash in first 7 days (proven in daily GM report) |
| **Acceptance Criteria** | AI-drafted replies appear in dashboard within 5 seconds. FPX/DuitNow payment link included. Hotel can send via one-click forward or copy-paste. Daily GM report shows RM recovered (same-day vs OTA 30-day delay). |

**F1–F9**: All features below now support hybrid as default, full automation (Meta Cloud API) as Stage 3.

#### F1: AI Conversation Engine
| Attribute | Detail |
|---|---|
| **User Story** | *As a guest, I ask a question about the hotel on any channel and receive an accurate, helpful response within 30 seconds — even at 2am.* |
| **Capabilities** | Answer FAQs: rates, room types, availability, facilities, directions, check-in/out times, F&B hours, parking |
| **AI Modes** | **Concierge** (default, informative) → **Lead Capture** (booking intent detected, collect name/dates/contact) → **Handoff** (complex request or guest demands human) |
| **Language** | English and Bahasa Malaysia. Auto-detect from guest input. Respond in the language the guest uses. |
| **Guardrails** | Never fabricate rates. Never confirm "availability" unless KB has real-time data. Default to human handoff when confidence < 70%. |
| **Knowledge Source** | Property-specific knowledge base: rates, room descriptions, facilities, FAQs, policies. |
| **Acceptance Criteria** | >80% accuracy on 50 sample questions per property. Response latency < 30 seconds. Correctly identifies and responds in Bahasa Malaysia including basic Manglish code-switching — **50-question BM/Manglish test suite must pass at ≥80% before 1st pilot go-live** (Phase 0 blocker). Full test suite documented and re-run before each new property onboarded. |

#### F2: WhatsApp AI Responder
| Attribute | Detail |
|---|---|
| **User Story** | *As a guest, I send a WhatsApp message to the hotel and get an instant AI response — no waiting for office hours.* |
| **Integration** | Primary: Meta WhatsApp Business Cloud API (official). Fallback/sandbox: Twilio WhatsApp. `Property.whatsapp_provider` controls which is active. |
| **Behavior** | Incoming message → conversation engine → AI response → reply via WhatsApp. Multi-turn context preserved. Non-text media (image/audio/video) returns a bilingual canned reply without calling the AI. `Property.audit_only_mode = True` activates the **Shadow Pilot** — incoming messages are logged and counted but the AI does not respond. Used during the 7-day proof period before a GM transfers their real number. |
| **Acceptance Criteria** | Full round-trip conversation over WhatsApp. Message delivery confirmed. Unsupported media handled gracefully. |

#### F3: Web Chat Widget
| Attribute | Detail |
|---|---|
| **User Story** | *As a website visitor, I see a chat bubble that lets me ask questions and get instant answers without leaving the page.* |
| **Delivery** | Embeddable `<script>` tag. Zero dependencies. Works on any website including WordPress. |
| **UX** | Floating chat bubble (bottom-right). Expandable to chat window. Property-branded greeting. |
| **Acceptance Criteria** | One line of HTML to install. Works on mobile and desktop. Loads in < 2 seconds. |

#### F4: Email Intake & Response
| Attribute | Detail |
|---|---|
| **User Story** | *As a guest who emails the hotel, I get an immediate AI acknowledgement and helpful response while the reservations team follows up.* |
| **Integration** | SendGrid Inbound Parse webhook. Incoming email → parsed → AI response → reply email. |
| **Behavior** | Auto-categorize intent. Generate response. CC reservations team for visibility. |
| **Acceptance Criteria** | Inbound email → AI response within 60 seconds. Original email thread preserved. |

#### F5: Lead Capture & CRM-lite
| Attribute | Detail |
|---|---|
| **User Story** | *As a reservations manager, every inquiry — regardless of channel or time — is captured as a lead with contact info, intent, and conversation history.* |
| **Data Captured** | Guest name, phone, email, channel, intent (booking / inquiry / complaint / group_booking / event), estimated value, actual revenue (entered by staff on conversion), priority, captured timestamp |
| **Lead Lifecycle** | `new` → `contacted` → `qualified` → `converted` / `lost` |
| **Lead Priority** | Leads scored as high/medium/low. High = group bookings, events, extended stay. Visible as a badge in the lead table. |
| **Revenue Verification** | When staff marks a lead converted, they enter the actual booking value (RM). This `actual_revenue` field feeds a verified metric separate from the AI estimate. |
| **UX** | Filterable by status (including Lost). Export to CSV. Summary KPI bar: total leads, est. pipeline, converted count, actual revenue. |
| **Acceptance Criteria** | Zero inquiry leakage. Every conversation generates a lead record. Staff can record actual revenue on conversion. Staff can mark a lead as Lost with a reason. Lost leads appear in a dedicated filter tab. Lead list exports to CSV with all fields. |

#### F6: Human Handoff
| Attribute | Detail |
|---|---|
| **User Story** | *As a guest with a complex request, I seamlessly transition from AI to a real person who already knows what I've been asking about.* |
| **Triggers** | Guest requests human. AI confidence below threshold. Complaint detected. Complex booking (group, event). |
| **Behavior** | AI acknowledges → publishes to Redis → dashboard shows conversation in `handed_off` status → staff clicks "Take Over" → staff sees full message history and lead data. |
| **After-Hours** | *"Our team will follow up first thing tomorrow morning."* Lead is flagged as priority follow-up. |
| **Staff Reply** | Staff can reply to guest directly from the `/dashboard/conversations` view. Reply is forwarded to the guest via the original channel (WhatsApp or web widget). Implemented via `POST /api/v1/conversations/{id}/reply`. ✅ Done in v0.3.1. |
| **Acceptance Criteria** | Staff sees full conversation context and captured lead data. Staff can send reply from dashboard. Staff can mark conversation resolved from dashboard. |

#### F7: After-Hours Recovery Dashboard
| Attribute | Detail |
|---|---|
| **User Story** | *As a GM, I open the dashboard and immediately see how many inquiries came in overnight, how many the AI handled, and the estimated revenue recovered.* |
| **Entry Point** | The authenticated dashboard home (`/dashboard`) **must display revenue KPI cards as the first visible content**. No setup checklist. No milestone tracker. The money slide is what the GM sees on login. |
| **Key Metrics** | Total inquiries · After-hours inquiries · Leads captured · AI handled vs. handoffs · Avg response time · **Estimated revenue recovered** · **Cost savings** · **Actual confirmed revenue** (from converted leads) |
| **Revenue Formula** | `Sum of (lead nights × property ADR, defaulting to 1 night if unknown) × 20% conversion rate`. See [revenue_methodology.md](./revenue_methodology.md) for canonical definition. Shown with tooltip: *"Based on X leads × RM Y avg. booking × 20% est. conversion."* |
| **Cost Savings** | `AI-handled inquiries × 0.25 hrs × property hourly rate (default RM 25/hr)`. Shows labour arbitrage alongside revenue recovery. |
| **Confirmed Revenue** | Sum of `Lead.actual_revenue` for staff-confirmed conversions. Verifiable, not estimated. Builds toward case study data. |
| **Time Ranges** | 7-day, 30-day, 90-day. Daily bar charts for inquiries, leads, revenue, cost savings. |
| **Acceptance Criteria** | Dashboard home shows revenue KPI cards first. Loads in < 3 seconds. KPI data accurate within 24 hours (daily aggregation job). All metrics visible without navigating to a sub-page. |

#### F8: Automated Daily Email Report
| Attribute | Detail |
|---|---|
| **User Story** | *As a GM, I receive a daily email every morning — no login required — showing yesterday's inquiry performance and recovered revenue.* |
| **Content** | Leads captured · Est. revenue recovered · Conversations handled · Pending handoffs (count + urgency) · One-click CTA to full dashboard |
| **Schedule** | Daily at **7:00am** property-local time. Triggered by Cloud Scheduler → `POST /api/v1/internal/run-daily-report`. |
| **Format** | Mobile-optimised HTML. Concise. Read in bed before the GM gets up. |
| **Production Blockers** | ✅ **Resolved (v0.3.2)** — `SENDGRID_API_KEY` and `SENDGRID_FROM_EMAIL` in Secret Manager. Cloud Scheduler jobs were created, verified (HTTP 200), and **deleted in 2026-03-23 GCP cleanup**. Must be recreated on next production deploy before daily reports resume. Internal endpoints (`/api/v1/internal/run-daily-report`) are live and tested. |
| **Acceptance Criteria** | Reports send at 7:00am after blockers resolved. Data matches dashboard. Mobile-optimised. One-click link to authenticated session. |

#### F9: After-Hours Revenue Audit Calculator
| Attribute | Detail |
|---|---|
| **User Story** | *As a hotel GM, I enter my property details into a free calculator and immediately see how much revenue I am losing overnight — with zero commitment required.* |
| **Route** | Public page at `/audit` (no authentication). Accessible from ai.sheerssoft.com/audit. |
| **Inputs** | Room count (slider 20–200), Average room rate RM (slider 80–800), Daily WhatsApp messages (dropdown with "I don't know" auto-derive), Front desk closure time (8pm/9pm/10pm/11pm/midnight/24h), OTA commission rate (15%/18%/20%/22%/25%) |
| **Output (instant, no gate)** | Monthly revenue leaking (RM), Monthly OTA commission displaced (RM), Annual total leakage (RM, highlighted), Conservative estimate (40% discount applied for credibility), ROI multiple if subscribing to Nocturn AI (RM 499/mo boutique tier), Net Year-1 recovery |
| **Lead Gate** | To receive the full PDF report: GM enters name, hotel name, email, WhatsApp number. POST to `/api/v1/audit/submit` → saves AuditRecord → triggers email within 60 seconds → SheersSoft receives notification for follow-up within 10 minutes. |
| **Calculation Method** | 60% of messages arrive after hours (industry benchmark). 20% conservative conversion rate. 2.0 avg stay nights. 65% of unanswered guests book via OTA. Final figure discounted 40% for credibility. |
| **Acceptance Criteria** | Live calculation updates in <300ms as inputs change. Submit saves AuditRecord. Email triggered. Rate limited: 60/min on calculate, 5/min on submit per IP. |

#### F10: Shadow Pilot Mode
| Attribute | Detail |
|---|---|
| **User Story** | *As a hotel GM considering Nocturn AI, I have a Twilio shadow number listening on my hotel's incoming WhatsApp inquiries for 7 days — with no disruption to my existing setup — and receive a report showing exactly how many after-hours inquiries my hotel received and the RM value I left on the table.* |
| **What it is** | A Twilio-hosted WhatsApp number provisioned per prospect. The GM promotes it as a "booking enquiries" channel in their WhatsApp bio, email footer, or printed signage for 7 days. The hotel's EXISTING number is not touched. |
| **`audit_only_mode`** | `Property.audit_only_mode = True` — incoming messages are logged to conversations and AnalyticsDaily but the AI does NOT send any response. The shadow pilot is an observation window, not an AI deployment. |
| **Why not the real number** | WhatsApp routes a number to ONE destination only: either the phone app (hotel staff) or the Meta/Twilio webhook. There is no passive tap mode. The shadow number sidesteps this constraint by being a new number entirely. |
| **7-Day Audit Email** | On Day 7, an automated email is sent to the GM: *"Your hotel received [X] inquiries after 10pm this week. Based on your ADR of RM [Y], you left approximately RM [Z] on the table."* This email is the close. |
| **Transition to Full Product** | On the Day 7 call, SheersSoft initiates the Meta Cloud API registration for the GM's REAL WhatsApp Business number. Once approved (2–4 days), `audit_only_mode` is set to False on the production property and the AI goes live. |
| **Property Fields Added** | `audit_only_mode: bool`, `shadow_pilot_start_date: datetime`, `shadow_pilot_phone: str` |
| **Acceptance Criteria** | Shadow pilot property created via `/admin`. Incoming messages logged. No AI response sent. Weekly audit email triggered by scheduler. Day 7 transition flow documented in admin. |

#### F11: Audit-to-Full Conversion Automation
| Attribute | Detail |
|---|---|
| **User Story** | *As a SheersSoft account manager, I receive an automatic notification when a GM submits the audit calculator and when a shadow pilot reaches Day 7 — so I can respond within 10 minutes and close the deal at the highest-probability moment.* |
| **Audit submission trigger** | POST `/audit/submit` → AuditRecord saved → email to GM with full report within 60 seconds → Slack/internal notification to SheersSoft AM within 10 minutes |
| **Shadow pilot Day 7 trigger** | `run_weekly_audit_report` scheduler job → sends GM email with real inquiry data → SheersSoft AM notified to initiate Day 7 call |
| **AM follow-up sequence** | T+0: Audit submitted → AM WhatsApps GM within 10 minutes: "I see you ran the audit for [Hotel Name]. Want to install a shadow listener this week?" T+7 days: Audit email sent → AM calls same day: "You had [X] after-hours messages. Want me to set up the full AI on your real number?" |
| **Acceptance Criteria** | Internal notifications send within 60 seconds of trigger events. Weekly audit email sends on day 7 of shadow pilot. Email content includes actual inquiry count and computed RM leakage from AnalyticsDaily. |

---

### 4.1.1 Known Gaps — Status as of v2.1

| # | Gap | Status | Fix |
|---|-----|--------|-----|
| 1 | **Dashboard home shows onboarding checklist, not revenue KPIs** | ✅ **RESOLVED** — `/dashboard` home shows revenue KPI cards (inquiries, after-hours, leads, estimated revenue recovered). Rebuilt in v0.3.1. | — |
| 2 | **Staff cannot reply to guest from dashboard** | ✅ **RESOLVED** — Staff reply input live in `/dashboard/conversations`. Replies forwarded to guest via original channel (WhatsApp/web). v0.3.1. | — |
| 3 | **Daily email non-functional in production** | ✅ **RESOLVED (code + infra confirmed)** — `SENDGRID_API_KEY` and `SENDGRID_FROM_EMAIL` in Secret Manager. Cloud Scheduler jobs were created, verified (HTTP 200), and later deleted as part of GCP cleanup on 2026-03-23. **Must be recreated** on next production deploy before daily reports resume. Internal endpoints (`/api/v1/internal/*`) are live and tested. | Recreate 4 Cloud Scheduler jobs on next deploy. |
| 4 | **"Lost" status missing from leads UI** | ✅ **RESOLVED** — Lost filter tab live in `/dashboard/leads`. Staff can mark leads lost. v0.3.1. | — |
| 5 | **Bilingual AI not formally tested** | ❌ **OUTSTANDING** — BM/Manglish support is live but the 50-question test suite has not been run. Must pass ≥80% before pilot go-live. | Run 50-question suite (see `docs/bm_test_suite.md`) via Twilio sandbox. Half-day field work. |

**Summary: 4 of 5 gaps resolved. Remaining:** BM test (P0.6) — half-day field work. No product code or infra outstanding for P0.

---

### 4.2 Explicitly NOT in v1

| Feature | Reason |
|---|---|
| Booking engine / payment processing | Hotel's existing booking engine handles conversion. We capture and warm the lead. |
| PMS / Opera integration | Walled garden. $25k API cost. Not needed for v1. |
| Multi-language beyond EN/BM | v1 targets Malaysia. Expand post-validation. |
| F&B ordering / room service | That's Opportunity #1. Separate product. |
| Voice call handling | Requires telephony integration. Phase 2. |
| Guest profile / loyalty | That's Opportunity #3. Future upsell layer. |
| Mobile app for staff | Web dashboard is sufficient for v1. Mobile-responsive design. |
| Stripe billing and subscription management | Payment infrastructure follows proven value, not precedes it. Pilot pricing is manual invoicing. UI in `/portal/billing` is live but Stripe activation is gated on ≥3 paying tenants. |
| Public application intake form | Self-serve signup. Not needed until sales motion is established. |
| Automated PDF report generation | The audit calculator shows results on-screen; the "full report" email is a text-based summary. A designed PDF is a post-PMF investment. |

---

## 5. Success Metrics

### Product KPIs (Per Property — What the Dashboard Shows)

| Metric | Definition | v1 Target |
|---|---|---|
| **Inquiries Captured** | Total conversations initiated with AI | 30+/day |
| **After-Hours Recovery Rate** | % of after-hours inquiries responded to | >95% |
| **Response Latency** | Guest message → AI first response | <30 seconds |
| **Human Handoff Rate** | % escalated to staff | <20% |
| **Lead Capture Rate** | % of conversations with contact info collected | >60% |
| **Estimated Revenue Recovered** | `(lead nights × ADR, default 1 night) × 20%` | RM 3,000–5,000+/month per property (based on RM 230 ADR × 20 after-hours leads/day × 20% conversion). First pilot property will establish the first verified benchmark. |
| **Audit → Shadow Pilot Conversion** | % of audit submissions that accept the shadow pilot offer | >30% |
| **Shadow Pilot → Full Product Conversion** | % of shadow pilots that convert to paid subscription | >50% |
| **Days Audit → Paid** | Calendar days from audit submission to first subscription payment | <21 days |

### Business KPIs (Internal — What We Track)

Targets aligned with `gtm_execution_plan.md` 90-day scorecard:

| Metric | Day-35 Target | Day-60 Target | Day-90 Target | Red Flag |
|---|---|---|---|---|
| Active Pilots | 1 full product client OR 3 shadow pilots running | 3–4 | 5+ | — |
| Paying Customers | 1 | 3 paying clients (from shadow pilot conversions) | 10 | <5 by Day 90 = value prop issue |
| MRR | RM 1,500 | RM 4,500–9,000 | RM 15,000–30,000 | — |
| Pilot → Paid Conversion | — | First data point | >60% | Below 50% = value prop weak |
| Monthly Churn | — | <5% | <5% | >10% = product problem, not sales |
| NPS (hotel staff) | — | >40 (first pilot) | >40 | — |

### Unit Economics (Survival Metrics)

| Metric | Target | Action if Missed |
|--------|--------|------------------|
| LTV:CAC ratio | ≥ 3:1 | Stop scaling acquisition until fixed |
| CAC payback period | < 6 months | > 6 months = cash flow risk at bootstrap stage |
| Gross margin | > 80% | Already met at 10 properties |

### PMF Signals

| Signal | PMF Present | PMF Absent |
|--------|-------------|------------|
| Inbound | Increasing organically | Linear with marketing spend |
| Sales cycle | Shortening | Every deal a push |
| Churn reasons | Voluntary (budget, strategy) | Product complaints, "not useful" |
| Feature requests | Enterprise asks (SSO, contracts) | Constant core-feature complaints |

**Rule:** Customers pulling you forward = PMF. Pushing every deal = not yet.

---

## 6. Pricing — Performance-Based (Updated 20 Apr 2026)

| Component | Amount | Notes |
|-----------|--------|-------|
| **Platform Fee** | RM 199/month | Full omni-channel access + dashboard + daily GM report |
| **Setup + AI Training** | RM 999 one-time | 48-hour implementation by SheersSoft team |
| **Performance Fee** | 3% only on confirmed direct bookings closed by Nocturn AI | Outcome-aligned — zero bookings = zero performance fee |

**Guarantee:** 30-day revenue recovery guarantee — if we don't demonstrate recovery, next month's platform fee is waived.

**Positioning:** Nocturn AI charges 3% vs OTA's 15–25%, saving hotels ~12–15% per direct booking. The pitch is OTA displacement, not AI chatbot.

**Entry into the service:** Application form at sheerssoft.com/apply (Founding Cohort — limited enrollment). Fields: hotel name, city, room count (<30 / 30–50 / 50–150 / 150+), after-hours process, WhatsApp number.

**Invoicing for v1:** Manual invoicing (direct bank transfer). Stripe billing infrastructure exists in the codebase but is not customer-facing until conversion is proven.

**Sales motion:** Application → SheersSoft review → onboarding call → RM 999 setup → live in 48 hours → RM 199/mo + 3% performance.

---

## 7. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| WhatsApp API approval delayed | Blocks primary channel | Apply Day 1. Web widget + email as fallback for pilot. |
| AI hallucinations / wrong rate quotes | Destroys trust with hotel and guest | Never state rates unless in KB. Default to handoff if unsure. |
| PDPA compliance gaps | Legal risk | Encrypt PII at rest. Data isolation per property. Privacy policy. Data retention controls. |
| Hotel IT blocks widget | Can't deploy on property website | Single `<script>` tag. Offer to install directly. Most hotel sites are WordPress. |
| Low inquiry volume at pilot property | Can't prove ROI | Pre-qualify: >20 inquiries/day confirmed before onboarding any new client. |
| AI chatbot market is crowded | Prospects have already evaluated generic chatbots and dismissed them | Differentiation must be explicit in every demo: this is **after-hours revenue recovery tied to a GM dashboard** — not a chatbot. Lead with the RM number, not the AI feature. |
| **"Build it and they will come"** | No customers despite product | Distribution strategy from day one. Case study → demos. 3–5 customer calls/week. |
| **CAC > LTV** | Buying revenue at a loss | Track unit economics from first customer. Stop scaling if LTV:CAC < 3. |
| GM refuses Meta Cloud API registration (number transfer) | High sales friction, delays Stage 3 | Shadow pilot data eliminates this objection — GM has seen their own numbers. "You had 14 after-hours messages last week. Your real number is getting 4-5x that. We just need to point your WhatsApp number to us." |
| Shadow pilot volume too low to impress GM | Can't prove ROI on weak-volume properties | Pre-qualify: estimate shadow volume using room count before provisioning. Properties with <5 msgs/day are too small for the current ICP. |

---

## 8. Go-To-Market — Distribution Strategy from Day One

> *"You need distribution strategy from day one. 'Build it and they will come' kills companies."* — First 10 customers are design partners; over-serve them.

> **Updated 31 Mar 2026:** GTM funnel simplified. Shadow pilot stage is now secondary to the direct application → onboarding flow. Primary entry point is the public application form.

### Launch Sequence (Current)

1. **Application outreach (cold/warm)** — Direct prospects to sheerssoft.com/apply. Framing: "Stop paying 18% to OTAs. We charge 3%. Apply for the Founding Cohort." No shadow pilot required upfront.
2. **Application → Onboarding call** — SheersSoft reviews application, schedules onboarding call within 48 hours.
3. **Onboarding call → Setup** — RM 999 setup fee collected. SheersSoft builds property KB, links WhatsApp + web widget. Live in 48 hours.
4. **Live → Day 7 Report** — First weekly performance report delivered: inquiries handled, leads captured, estimated RM recovered.
5. **Day 30 ROI call → Referral** — Review confirmed revenue vs 3% fee. Request warm intro to peer GM.
6. **Case study → Cold expansion** — Only armed with real, confirmed numbers from pilot property.

### Shadow Pilot (Secondary Path — Prospects Who Want Proof First)

Still available for risk-averse GMs who won't commit without data. Deploy Twilio shadow number, `audit_only_mode = True`, 7-day observation, Day 7 email with real inquiry count + RM leakage. Then convert to full onboarding.

### The 60-Second Pitch (Updated)

> *"Your hotel is paying 15–18% commission every time a guest books through Agoda or Booking.com. We capture those same guests directly — on WhatsApp, email, and your website — 24 hours a day, 7 days a week. We charge RM 199 a month plus 3% only on bookings we actually convert. That's it. No long contracts. Apply at sheerssoft.com/apply."*

---

## 9.3 Client Dashboard Hierarchy

Nocturn AI presents a different experience depending on the user's role and onboarding state:

```
New client login
       │
       ▼
/welcome  ─── 5-step Onboarding Wizard (first-time owner)
       │       Step 1: Property details
       │       Step 2: Add KB content
       │       Step 3: Test a channel
       │       Step 4: Invite team members
       │       Step 5: Go live
       │
       ▼ (onboarding_completed = true)
/portal   ─── Tenant Owner / Admin self-service
       │       /portal/home         — multi-property summary, health
       │       /portal/kb           — add/edit/delete KB documents
       │       /portal/team         — manage staff, send invites
       │       /portal/channels     — channel status, widget embed code
       │       /portal/properties   — property list, add property
       │       /portal/billing      — subscription tier, Stripe checkout
       │       /portal/support      — submit / view support tickets
       │
       ▼ (role = staff)
/dashboard ── Property Staff daily operations
               /dashboard           — revenue KPI cards (the money slide)
               /dashboard/conversations — live conversations + handoff queue
               /dashboard/leads     — lead list, status updates, CSV export
               /dashboard/analytics — charts, trends, AI vs human rate
               /dashboard/insights  — monthly Gemini-powered sentiment summary
```

**ICP Workflow — what hotel GMs care about:**

| Cadence | What They Check |
|---------|-----------------|
| **Daily** | Overnight leads, revenue recovered, active conversations, pending handoffs |
| **Weekly** | Inquiry trends, lead conversion rate, AI vs human handling rate |
| **Monthly** | Revenue by channel, KB gaps, cost savings, sentiment summary |
| **Quarterly** | ROI, guest satisfaction trends, plan utilization |

**SheersSoft operator tools:**
- `/admin` — platform ops, tenant management, maintenance mode, service health (superadmin only)
- `/admin/kb-ingestion` — KB setup tool for doing client onboarding on their behalf

---

## 9. Roadmap

### 9.1 Validated v1.x Roadmap

**Pre-pilot deliverables** — status as of v2.4 (actual):
- ✅ After-Hours Revenue Audit calculator at `/audit` (v0.5)
- ✅ AuditRecord model + audit endpoints (v0.5)
- ✅ Internal admin revenue audit tool at `/admin/tools/revenue-audit` (v0.5)
- ✅ `ENVIRONMENT=production` in cloudbuild.yaml (v0.5)
- ✅ `audit_only_mode` flag on Property — Shadow Pilot Mode (v0.5)
- ✅ Weekly audit email + scheduler job (v0.5)
- ✅ Shadow pilot provisioning in admin panel (v0.5)
- ✅ Dashboard home shows revenue KPI cards (rebuilt v0.3.1)
- ✅ Staff reply input in conversations view (v0.3.1)
- ✅ "Lost" status filter in leads UI (v0.3.1)
- ✅ Maintenance mode — backend + admin toggle + tenant banner (v0.3.2)
- ✅ Service health dashboard `/admin/health` (v0.3.2)
- ✅ Daily email live in production — `SENDGRID_API_KEY` + 4 Cloud Scheduler jobs confirmed (v0.3.2)
- ✅ `FERNET_ENCRYPTION_KEY` in Secret Manager — PII encryption active (v0.3.2)
- ✅ Infra migration: Supabase-only DB, GCP Secret Manager–only secrets, Cloud SQL removed (v0.3.3)
- ✅ `/portal` self-service — KB, team, channels, billing, support (v0.4)
- ✅ `/welcome` 5-step onboarding wizard (v0.4)
- ✅ Role-based auth callback routing (v0.4)
- ✅ `/admin/kb-ingestion` tool for SheersSoft operators (v0.4)
- ❌ 50-question BM/Manglish test suite run at ≥80% pass rate (half-day field work — **P0 blocker**)

**Sprint 2.6 — Hybrid Co-Pilot (Next Sprint, NOT yet built):**
- ❌ Hybrid AI Co-Pilot reply drafting UI (dashboard → "Copy to WhatsApp")
- ❌ Google Sheet real-time inventory reader
- ❌ FPX/DuitNow payment link generator in AI replies
- ❌ Daily GM report: "RM X recovered today (same-day cash vs OTA 30-day delay)"

**Post-pilot roadmap** (after first real-world data):

| Phase | Feature | Trigger |
|---|---|---|
| **v1.1** | Week-over-week comparison in daily email | 14+ days of data accumulated |
| **v1.2** | Lead status update by replying to daily email | Pilot feedback: staff wants to triage from inbox |
| **v1.3** | Inquiry Volume by Hour chart (staffing insights) | Pilot data available; GM asks "when should I staff more?" |
| **v1.4** | Lost lead reason analytics (why leads fail to convert) | After Lost status UI is live and data accumulates |
| **v1.5** | "Confirmed Revenue" mark-as-booked in dashboard | Paying customers want verified ROI for case study / renewal |
| **v2.0** | F&B Revenue Intelligence (Opportunity #1) | 5+ paying properties; Amsyar or equivalent advisor locked |
| **v2.5** | Guest Recognition & KYC (Opportunity #3) | Cross-stay data accumulated from inquiry + F&B layers |

### 9.2 SaaS Infrastructure — Activation Status

The codebase contains infrastructure built ahead of validation. This table tracks what is active vs dormant.

| Feature | Status | Notes |
|---------|--------|-------|
| Multi-tenant hierarchy (Tenant, TenantMembership, OnboardingProgress) | ✅ **Active** | Used by admin provisioning, `/portal`, and `/welcome`. |
| Supabase Auth (magic links, admin provisioning) | ✅ **Active** | Magic link login live. Role-based auth callback routing implemented. |
| SuperAdmin dashboard (`/admin`) | ✅ **Active (internal ops)** | SheersSoft ops tool — tenant management, scheduler config, maintenance mode, service health. Never shown to hotel clients. |
| Stripe billing (checkout, subscriptions) | ❌ **Dormant** | Activate when pilot-to-paid conversion is proven; manual invoicing until ≥3 paying tenants. |
| Support chatbot + ticket system | ✅ **Active** | `/portal/support` allows tenant users to submit and view tickets. Backend ticket CRUD live. |
| Application intake form | ✅ **Active (primary entry point, v0.4)** | Founding Cohort application at /apply is now the primary GTM entry point per new website (31 Mar 2026). Fields: hotel name, city, room count, after-hours process, WhatsApp number. Backend `Application` model + `/api/v1/applications` endpoint are live. |
| Tenant self-service portal (`/portal`, `/welcome`) | ✅ **Active** | Full portal built in v0.4: KB self-management, team management, channel status, billing, support. `/welcome` 5-step onboarding wizard live. |
| After-Hours Revenue Audit (`/audit`, AuditRecord, audit endpoints) | ✅ **Active** | Built in v0.5. Public calculator + superadmin submissions pipeline. |
| Shadow Pilot Mode (`audit_only_mode`, shadow provisioning, weekly email) | ✅ **Active (v0.5.1)** | Shadow pilot + hybrid onboarding path complete. Core to the three-stage sales funnel. |

**Rule for activating dormant features:** Follow the decision tree in `product_gap.md` Section 7. A feature unlocks only when its release condition is met — not when it is technically ready.

---

*This PRD describes the product that solves the validated problem. If a feature isn't in Section 4.1, it doesn't exist in v1. The market research is the acceptance test. Context validated against [opportunity_2_playbook.md](./opportunity_2_playbook.md) and [gap_analysis.md](./gap_analysis.md).*
