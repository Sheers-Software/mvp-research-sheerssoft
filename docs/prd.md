# Product Requirements Document (PRD)
## Nocturn AI — AI Inquiry Capture & Conversion Engine
### Version 2.0 · 17 Mar 2026
### Aligned with [product_context.md](./product_context.md) · Ground truth: [opportunity_2_playbook.md](./opportunity_2_playbook.md)

---

## 1. Problem Statement

Malaysian hotels receive **90% of bookings through manual channels** — WhatsApp, phone, email, and walk-ins. After 6pm, reservations desks close and inquiries are dropped. At properties like Novotel KLCC, a team handles 200–300 touchpoints on busy days with 30% needing manual follow-up — a pattern confirmed across the target segment. **Revenue literally falls on the floor every night.**

Meanwhile, hotels pay **15–25% commission** on every OTA booking. Every direct inquiry they fail to answer pushes the guest toward Booking.com or Agoda — where the hotel pays for what should have been free.

**No product today captures, responds to, and converts inquiries across WhatsApp, web, and email — 24/7 — and proves the revenue impact to the GM.**

---

## 2. Product Vision

> An AI-powered, always-on concierge that captures every hotel inquiry — WhatsApp, web, email — converts them into bookings, and proves to the GM exactly how much revenue was recovered from leads that would have been lost.

### Design Principles

| # | Principle | What It Means in Practice |
|---|---|---|
| 1 | **Results before features** | Every screen, every notification, every report answers: *"How much money did this make me?"* |
| 2 | **Guest experience is sacred** | AI responses must feel like a knowledgeable concierge, not a chatbot. Under 30 seconds. Warm, not robotic. |
| 3 | **Zero burden on hotel staff** | One `<script>` tag for the widget. One WhatsApp number linked. No training manual. No IT department required. |
| 4 | **Honest AI** | Never fabricate rates or availability. When unsure, hand off to a human with full context. Trust is the product. |
| 5 | **Show, don't tell** | The dashboard is the sales pitch. If the GM opens it every morning, we win. If they don't, we've failed. |
| 6 | **Live in 48 Hours** | Onboarding must be frictionless. No complex IT integrations. Forward an email, drop a script tag, and go live. |

---

## 3. Target Customer

### Primary ICP (Ideal Customer Profile) — Ruthlessly Narrow

> *"Pick the smallest viable market segment that can sustain your business. You can expand later."*

| Attribute | Value | Rationale |
|---|---|---|
| **Property Type** | Independent and mid-tier brand hotels (3–4 star) only | Budget lacks margin; 5-star has enterprise procurement |
| **Size** | 50–300 rooms | Sweet spot for inquiry volume and sales cycle |
| **Location** | Malaysia (initial market) | PDPA, BM/EN, local relationships. No regional sprawl until PMF |
| **Booking Mix** | >50% manual channels (WhatsApp, phone, email, walk-in) | OTAs don't need this. Must have after-hours gap |
| **Pain Signal** | No after-hours inquiry coverage; 2–5 person reservations team; >20 inquiries/day | Pre-qualify. Low volume = can't prove ROI |
| **Decision Maker** | GM or Revenue Manager (NOT IT) | IT blocks deals. GMs care about revenue |
| **Budget** | RM 1,500–5,000/month | Value-based: 10–30% of RM 3,000–5,000 recovered/month |

**Explicitly NOT in v1:** Budget hostels, Airbnb-style, 5-star chains, properties with <15 inquiries/day.

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

#### F1: AI Conversation Engine
| Attribute | Detail |
|---|---|
| **User Story** | *As a guest, I ask a question about the hotel on any channel and receive an accurate, helpful response within 30 seconds — even at 2am.* |
| **Capabilities** | Answer FAQs: rates, room types, availability, facilities, directions, check-in/out times, F&B hours, parking |
| **AI Modes** | **Concierge** (default, informative) → **Lead Capture** (booking intent detected, collect name/dates/contact) → **Handoff** (complex request or guest demands human) |
| **Language** | English and Bahasa Malaysia. Auto-detect from guest input. Respond in the language the guest uses. |
| **Guardrails** | Never fabricate rates. Never confirm "availability" unless KB has real-time data. Default to human handoff when confidence < 70%. |
| **Knowledge Source** | Property-specific knowledge base: rates, room descriptions, facilities, FAQs, policies. |
| **Acceptance Criteria** | >80% accuracy on 50 sample questions per property. Response latency < 30 seconds. Correctly identifies and responds in Bahasa Malaysia including basic Manglish code-switching — **50-question BM/Manglish test suite must pass at ≥80% before 1st pilot go-live** (Phase 0 blocker). Full test suite documented and re-run before each new pilot property onboarded. |

#### F2: WhatsApp AI Responder
| Attribute | Detail |
|---|---|
| **User Story** | *As a guest, I send a WhatsApp message to the hotel and get an instant AI response — no waiting for office hours.* |
| **Integration** | Primary: Meta WhatsApp Business Cloud API (official). Fallback/sandbox: Twilio WhatsApp. `Property.whatsapp_provider` controls which is active. |
| **Behavior** | Incoming message → conversation engine → AI response → reply via WhatsApp. Multi-turn context preserved. Non-text media (image/audio/video) returns a bilingual canned reply without calling the AI. |
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
| **Current Gap** | Staff view full context from the dashboard but **reply to the guest on the original channel** (WhatsApp, email). There is no in-dashboard reply input yet. This is a v1 gap — see Section 4.1.1. |
| **Acceptance Criteria** | Staff sees full conversation context and captured lead data. Staff can mark conversation resolved from dashboard. *(In-dashboard reply is a pending v1 deliverable — not yet met.)* |

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
| **Production Blockers** | ⚠️ Not yet functional in production: (1) `SENDGRID_API_KEY` missing from GCP Secret Manager; (2) Cloud Scheduler `run-daily-report` job not created. Both required before pilot go-live. |
| **Acceptance Criteria** | Reports send at 7:00am after blockers resolved. Data matches dashboard. Mobile-optimised. One-click link to authenticated session. |

---

### 4.1.1 Known Gaps — Must Fix Before Pilot Go-Live

| # | Gap | Impact | Fix Required |
|---|-----|--------|--------------|
| 1 | **Dashboard home shows onboarding checklist, not revenue KPIs** | GM logs in and sees a milestone tracker instead of recovered revenue. Violates Design Principle #5 and F7. The product's retention hook doesn't fire. | `/dashboard` home must show revenue KPI cards first. Redirect to `/dashboard/analytics` post-setup, or embed KPIs inline. This is the single most important fix before the pilot. |
| 2 | **Staff cannot reply to guest from dashboard** | Handoff transfers context but reply happens outside the product (WhatsApp app, email client). The "same thread" experience is broken. | Add staff reply text input to the conversations page that sends via the correct channel adapter. |
| 3 | **Daily email non-functional in production** | The GM morning report — the product's primary retention mechanism — is silent. GMs who don't log in daily will silently disengage. | Add `SENDGRID_API_KEY` to GCP Secret Manager. Create Cloud Scheduler `run-daily-report` job. |
| 4 | **"Lost" status missing from leads UI** | Churned leads are invisible. The team cannot track why leads fail to convert, making churn analysis impossible. | Add Lost filter tab. Allow staff to mark a lead Lost with a required reason field. |
| 5 | **Bilingual AI not formally tested** | BM/Manglish support is claimed but untested. A pilot hotel testing in Bahasa Malaysia could encounter failures that immediately destroy trust. | Build 50-question BM/Manglish test suite. Run against current model before 1st pilot go-live. Document pass rate. If below 80%, implement language fallback before pilot. Re-run before each subsequent property onboarded. |

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
| Multi-tenant SaaS hierarchy (Tenant model, TenantMembership, OnboardingProgress) | Billing infrastructure for a future SaaS. Not validated by interviews. Single-property pilot first. |
| Stripe billing and subscription management | Payment infrastructure follows proven value, not precedes it. Pilot pricing is manual invoicing. |
| Supabase Auth, magic links, admin provisioning API | Over-engineered for pilot. JWT auth per property is sufficient. |
| SuperAdmin dashboard (platform metrics, tenant CRUD) | SheersSoft internal tooling. Not a hotel-facing feature. |
| Gamified onboarding milestone tracker | Not a hotel need validated by interviews. SheersSoft onboards properties manually for v1. |
| Support chatbot and ticket system | At pilot scale, support is handled directly by the SheersSoft team. |
| Public application intake form | Self-serve signup. Not needed until sales motion is established. |

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
| **Estimated Revenue Recovered** | `(lead nights × ADR, default 1 night) × 20%` | RM 3,000–5,000+/month per property (based on RM 230 ADR × 20 after-hours leads/day × 20% conversion). Vivatel pilot will establish the first verified benchmark. |

### Business KPIs (Internal — What We Track)

Targets aligned with `gtm_execution_plan.md` 90-day scorecard:

| Metric | Day-35 Target | Day-60 Target | Day-90 Target | Red Flag |
|---|---|---|---|---|
| Active Pilots | 1 (Vivatel live) | 3–4 | 5+ | — |
| Paying Customers | 1 | 2–3 | 10 | <5 by Day 90 = value prop issue |
| MRR | RM 1,500 | RM 4,500–9,000 | RM 15,000–30,000 | — |
| Pilot → Paid Conversion | — | First data point | >60% | Below 50% = value prop weak |
| Monthly Churn | — | <5% | <5% | >10% = product problem, not sales |
| NPS (hotel staff) | — | >40 (Vivatel) | >40 | — |

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

## 6. Pricing — Value-Based, Not Cost-Plus

> *"B2B customers don't trust cheap software. Charge 10–30% of value created."*

| Tier | Price | Target Segment | Includes |
|---|---|---|---|
| **Starter** | RM 1,500/mo | Budget/3-star, <100 rooms | 1 WhatsApp line, web widget, 500 conversations/mo, basic dashboard |
| **Professional** | RM 3,000/mo | 4-star, 100–300 rooms | 2 WhatsApp lines, web widget, email handling, 2,000 conversations/mo, full dashboard + reports |
| **Enterprise** | RM 5,000+/mo | 5-star, 300+ rooms | Unlimited lines, custom AI training, priority support, API access |

**Pilot Offer:** 30 days FREE, time-limited only. No credit card. Prove value before asking for money.

**Invoicing for v1:** Pilot billing is manual (direct bank transfer or invoice). Stripe billing infrastructure exists in the codebase but is not customer-facing until pilot-to-paid conversion is proven.

**Sales motion:** Starter/Pro = sales-assisted. Enterprise = full sales process.

---

## 7. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| WhatsApp API approval delayed | Blocks primary channel | Apply Day 1. Web widget + email as fallback for pilot. |
| AI hallucinations / wrong rate quotes | Destroys trust with hotel and guest | Never state rates unless in KB. Default to handoff if unsure. |
| PDPA compliance gaps | Legal risk | Encrypt PII at rest. Data isolation per property. Privacy policy. Data retention controls. |
| Hotel IT blocks widget | Can't deploy on property website | Single `<script>` tag. Offer to install directly. Most hotel sites are WordPress. |
| Low inquiry volume at pilot property | Can't prove ROI | Pre-qualify: >20 inquiries/day. Vivatel (30+/day confirmed). |
| AI chatbot market is crowded | Prospects have already evaluated generic chatbots and dismissed them | Differentiation must be explicit in every demo: this is **after-hours revenue recovery tied to a GM dashboard** — not a chatbot. Lead with the RM number, not the AI feature. |
| **"Build it and they will come"** | No customers despite product | Distribution strategy from day one. Case study → demos. 3–5 customer calls/week. |
| **CAC > LTV** | Buying revenue at a loss | Track unit economics from first customer. Stop scaling if LTV:CAC < 3. |

---

## 8. Go-To-Market — Distribution Strategy from Day One

> *"You need distribution strategy from day one. 'Build it and they will come' kills companies."* — First 10 customers are design partners; over-serve them.

### Launch Sequence

1. **Vivatel KL (Zul)** — Design partner #1. 90% manual, 30+ daily touchpoints, zero after-hours coverage. Deploy first. Do things that don't scale.
2. **SKS Hospitality (Bob's referral)** — **Highest priority after Vivatel.** Referrals convert 10× better than cold outreach. Use Bob's name. Activate in parallel with Vivatel pilot, not after.
3. **Novotel KLCC (Shamsuridah)** — 100 emails/day. Relationship established. Longer sales cycle (chain hotel).
4. **Ibis Styles KL, Melia KL, Tamu Hotel** — Warm pipeline. Book demos once Vivatel data is in hand.
5. **Cold expansion** — Only after Vivatel case study with real numbers. Proof, not promises.

### The 60-Second Pitch

> *"Your hotel gets 30+ inquiries a day via WhatsApp and email. After 6pm, nobody answers. Our AI captures every single inquiry, responds in under 30 seconds — 24/7 — and hands you a daily report showing exactly how many leads would have been lost. Hotels like yours recover RM 3,000–5,000+/month by capturing direct inquiries that would otherwise go cold or convert via OTA."*

---

## 9. Roadmap

### 9.1 Validated v1.x Roadmap

**Pre-pilot deliverables** (must complete before Vivatel goes live — see Section 4.1.1 and `gtm_execution_plan.md` Phase 0):
- Dashboard home shows revenue KPI cards (not onboarding checklist)
- Staff reply input in conversations view
- Daily email live in production (SENDGRID_API_KEY + Cloud Scheduler)
- `FERNET_ENCRYPTION_KEY` in Secret Manager
- 50-question BM/Manglish test suite run at ≥80% pass rate
- "Lost" status filter in leads UI
- Vivatel KB populated

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

### 9.2 Dormant SaaS Infrastructure (Codebase — Not Customer-Facing v1)

The following systems exist in the codebase and must not be broken by new development. They are **not part of the v1 customer-facing product** and must not be referenced in demos, sales materials, or hotel-facing documentation until explicitly released.

| Feature | Release Condition |
|---------|-------------------|
| Multi-tenant hierarchy (Tenant, TenantMembership, OnboardingProgress) | 10+ paying customers; need for multi-property group billing |
| Supabase Auth (magic links, admin provisioning) | Self-serve signup motion validated with real inbound |
| SuperAdmin dashboard (platform metrics, tenant CRUD) | Onboarding volume exceeds manual process (>2 new properties/week) |
| Stripe billing (checkout, subscriptions) | Pilot-to-paid conversion proven; manual invoicing no longer viable |
| Support chatbot + ticket system | Support ticket volume exceeds direct handling |
| Application intake form | Self-serve GTM motion validated |

---

*This PRD describes the product that solves the validated problem. If a feature isn't in Section 4.1, it doesn't exist in v1. The market research is the acceptance test. Context validated against [opportunity_2_playbook.md](./opportunity_2_playbook.md) and [gap_analysis.md](./gap_analysis.md).*
