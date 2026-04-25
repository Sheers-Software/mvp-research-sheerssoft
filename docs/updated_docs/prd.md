# Product Requirements Document (PRD)
## Nocturn AI — AI Inquiry Capture & Conversion Engine
### Version 2.5 · 24 Apr 2026
### Aligned with [product_context.md](./product_context.md)
### Cross-referenced with: [architecture.md](./architecture.md) v2.5, [build_plan.md](./build_plan.md) v2.5, [shadow_pilot_spec.md](./shadow_pilot_spec.md) v1.0, [product_gap.md](./product_gap.md) v1.4

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
| 3 | **Zero burden on hotel staff** | One QR scan links the WhatsApp. No training manual. No IT department required. |
| 4 | **Honest AI** | Never fabricate rates or availability. When unsure, hand off to a human with full context. Trust is the product. |
| 5 | **Show, don't tell** | The dashboard is the sales pitch. If the GM opens it every morning, we win. If they don't, we've failed. |
| 6 | **Live in 48 Hours** | Onboarding must be frictionless. No complex IT integrations. Scan one QR code and go live. |
| 7 | **Proof Before Commitment** | Never ask for a hotel's commitment before showing the GM real data from their own actual WhatsApp conversations. The shadow pilot connects to their existing number, observes real traffic, and builds the evidence file over 7 days. |

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

#### F1: AI Conversation Engine
| Attribute | Detail |
|---|---|
| **User Story** | *As a guest, I ask a question about the hotel on any channel and receive an accurate, helpful response within 30 seconds — even at 2am.* |
| **Capabilities** | Answer FAQs: rates, room types, availability, facilities, directions, check-in/out times, F&B hours, parking |
| **AI Modes** | **Concierge** (default, informative) → **Lead Capture** (booking intent detected, collect name/dates/contact) → **Handoff** (complex request or guest demands human) |
| **Language** | English and Bahasa Malaysia. Auto-detect from guest input. Respond in the language the guest uses. |
| **Guardrails** | Never fabricate rates. Never confirm "availability" unless KB has real-time data. Default to human handoff when confidence < 70%. |
| **Knowledge Source** | Property-specific knowledge base: rates, room descriptions, facilities, FAQs, policies. |
| **Acceptance Criteria** | >80% accuracy on 50 sample questions per property. Response latency < 30 seconds. Correctly identifies and responds in Bahasa Malaysia including basic Manglish code-switching — **50-question BM/Manglish test suite must pass at ≥80% before 1st pilot go-live** (P0 blocker). |

#### F2: WhatsApp AI Responder
| Attribute | Detail |
|---|---|
| **User Story** | *As a guest, I send a WhatsApp message to the hotel and get an instant AI response — no waiting for office hours.* |
| **Integration** | Primary (hybrid): Baileys/whatsapp-web.js linked device on hotel's existing WhatsApp Business number. Stage 3: Meta WhatsApp Business Cloud API. `Property.whatsapp_provider` controls which is active: `"baileys" | "meta" | "twilio"`. |
| **Behavior** | Incoming message → conversation engine → AI response → reply via WhatsApp. Multi-turn context preserved. Non-text media (image/audio/video) returns a bilingual canned reply without calling the AI. `Property.shadow_pilot_mode = True` activates the **Shadow Pilot** — incoming and outgoing messages are observed and logged but Nocturn does NOT send any response. |
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
| **Staff Reply** | Staff can reply to guest directly from the `/dashboard/conversations` view. ✅ Done in v0.3.1. |
| **Acceptance Criteria** | Staff sees full conversation context and captured lead data. Staff can send reply from dashboard. Staff can mark conversation resolved from dashboard. |

#### F7: After-Hours Recovery Dashboard
| Attribute | Detail |
|---|---|
| **User Story** | *As a GM, I open the dashboard and immediately see how many inquiries came in overnight, how many the AI handled, and the estimated revenue recovered.* |
| **Entry Point** | The authenticated dashboard home (`/dashboard`) **must display revenue KPI cards as the first visible content**. |
| **Key Metrics** | Total inquiries · After-hours inquiries · Leads captured · AI handled vs. handoffs · Avg response time · **Estimated revenue recovered** · **Cost savings** · **Actual confirmed revenue** (from converted leads) |
| **Revenue Formula** | `Sum of (lead nights × property ADR, defaulting to 1 night if unknown) × 20% conversion rate`. See [revenue_methodology.md](./revenue_methodology.md) for canonical definition. |
| **Cost Savings** | `AI-handled inquiries × 0.25 hrs × property hourly rate (default RM 25/hr)`. Shows labour arbitrage alongside revenue recovery. |
| **Confirmed Revenue** | Sum of `Lead.actual_revenue` for staff-confirmed conversions. Verifiable, not estimated. |
| **Time Ranges** | 7-day, 30-day, 90-day. Daily bar charts for inquiries, leads, revenue, cost savings. |
| **Acceptance Criteria** | Dashboard home shows revenue KPI cards first. Loads in < 3 seconds. KPI data accurate within 24 hours (daily aggregation job). All metrics visible without navigating to a sub-page. |

#### F8: Automated Daily Email Report
| Attribute | Detail |
|---|---|
| **User Story** | *As a GM, I receive a daily email every morning — no login required — showing yesterday's inquiry performance and recovered revenue.* |
| **Content** | Leads captured · Est. revenue recovered · Conversations handled · Pending handoffs (count + urgency) · One-click CTA to full dashboard |
| **Schedule** | Daily at **7:00am** property-local time. Triggered by Cloud Scheduler → `POST /api/v1/internal/run-daily-report`. |
| **Format** | Mobile-optimised HTML. Concise. Read in bed before the GM gets up. |
| **Acceptance Criteria** | Reports send at 7:00am. Data matches dashboard. Mobile-optimised. One-click link to authenticated session. |

#### F9: After-Hours Revenue Audit Calculator
| Attribute | Detail |
|---|---|
| **User Story** | *As a hotel GM, I enter my property details into a free calculator and immediately see how much revenue I am losing overnight — with zero commitment required.* |
| **Route** | Public page at `/audit` (no authentication). |
| **Inputs** | Room count (slider), Average room rate RM (slider), Daily WhatsApp messages (dropdown), Front desk closure time, OTA commission rate |
| **Output** | Monthly revenue leaking (RM), Monthly OTA commission displaced, Annual total leakage, Conservative estimate (40% discount), ROI multiple if subscribing to Nocturn AI, Net Year-1 recovery |
| **Lead Gate** | To receive the full report: GM enters name, hotel name, email, WhatsApp number. POST to `/api/v1/audit/submit` → saves AuditRecord → triggers email within 60 seconds → SheersSoft receives notification for follow-up within 10 minutes. |
| **Acceptance Criteria** | Live calculation updates in <300ms. Submit saves AuditRecord. Email triggered. Rate limited: 60/min on calculate, 5/min on submit per IP. |

---

#### F10: Shadow Pilot Mode — Linked Device Observation (v2.5 — Fully Rewritten)

> **This is the core proof mechanism.** The shadow pilot connects to the hotel's existing WhatsApp Business number as a linked device, observes all real guest conversations for 7 days without touching a single one, calculates exactly how much revenue leaked due to unanswered and slow-responded inquiries, and delivers a personalised evidence report to the GM. The goal is not to demonstrate a hypothetical — it is to surface facts from the hotel's own live traffic.

##### F10.1 — What the Shadow Pilot Is

| Attribute | Detail |
|---|---|
| **Core mechanic** | Nocturn connects to the hotel's existing WhatsApp Business number using Baileys (Node.js multi-device protocol library) as an additional linked device. This is architecturally identical to how a second phone connects to the same WhatsApp account — the hotel's staff continue using WhatsApp exactly as before. Nocturn observes silently. |
| **What it observes** | Every incoming guest message (with timestamp) AND every outgoing staff reply (with timestamp). From these two streams, Nocturn computes exact response times, identifies unanswered conversations, and flags after-hours abandonment. |
| **What it does NOT do** | It does NOT send any reply to guests. It does NOT modify any conversation. It does NOT disrupt the hotel's normal WhatsApp operations. It does NOT require the hotel to promote a new number. |
| **Setup** | SheersSoft AM opens the shadow pilot provisioning page in `/admin/shadow-pilots`. Enters hotel details, ADR, operating hours, GM email. System generates a QR code. Hotel owner/GM scans QR with their WhatsApp Business phone (same flow as adding a new linked device). Session established in under 30 seconds. |
| **Duration** | 7 days of observation. Minimum 5 days required for the weekly report to be statistically meaningful. |
| **Why linked device vs separate number** | A separate Twilio number requires the hotel to actively promote it and divert traffic — creating friction and producing artificial (not representative) data. Linked device observes the hotel's real traffic with zero guest-facing change, making the evidence irrefutable: "This is what actually happened on your real WhatsApp last week." |

##### F10.2 — Metrics Tracked During Shadow Pilot

All metrics are computed per property per day and rolled up weekly for the GM report.

**Group A: Inquiry Volume**

| Metric | Definition | Why It Matters |
|---|---|---|
| `total_inquiries` | Total unique guest WhatsApp conversations initiated during the period | Baseline volume |
| `after_hours_inquiries` | Conversations where the first guest message arrived outside operating hours | The core revenue leak window |
| `business_hours_inquiries` | Conversations where the first guest message arrived during operating hours | Baseline for comparison |
| `booking_intent_inquiries` | Conversations where AI intent classifier flagged `booking`, `rate_query`, or `availability_check` | The high-value subset |
| `group_booking_inquiries` | Conversations where AI classified intent as `group_booking` (≥5 rooms or "event") | Highest-value individual leads |
| `repeat_guest_contacts` | Conversations from a number that has contacted the hotel before (same property) | Loyalty signal |

**Group B: Response Behaviour**

| Metric | Definition | Why It Matters |
|---|---|---|
| `responded_count` | Conversations where staff sent at least one reply | Coverage rate |
| `unanswered_count` | Conversations where no staff reply was ever sent | The hard leakage number |
| `after_hours_unanswered` | After-hours conversations with zero staff reply | The core overnight leak |
| `after_hours_responded_next_day` | After-hours conversations where staff replied the following business day | Too late — guest has already booked on OTA |
| `avg_response_time_minutes` | Mean time from first guest message to first staff reply, across all responded conversations | Speed of service |
| `avg_response_time_business_hours` | Response time during staffed hours only | Baseline service quality |
| `avg_response_time_after_hours` | Response time for after-hours conversations that DID get a reply | How much the team is actually checking at night |
| `response_time_over_1hr` | Count of conversations where response took >1 hour | Slow response = lost guest |
| `response_time_over_4hr` | Count where response took >4 hours | High churn risk |
| `response_time_over_8hr` | Count where response took >8 hours (typically overnight) | Almost certainly lost |
| `response_time_over_24hr` | Count where response took >24 hours | Definitively lost |

**Group C: Revenue Leakage**

| Metric | Definition | Formula |
|---|---|---|
| `revenue_at_risk_total` | Estimated revenue lost from unanswered after-hours booking-intent inquiries | `booking_intent_after_hours_unanswered × ADR × avg_stay_nights × 20% conversion` |
| `revenue_at_risk_conservative` | 40% discount applied for credibility | `revenue_at_risk_total × 0.60` |
| `ota_commission_equivalent` | What an OTA would have earned on the same bookings | `revenue_at_risk_conservative × 18%` |
| `slow_response_revenue_at_risk` | Revenue at risk from booking-intent inquiries with response time >4hr (guest likely abandoned) | `slow_response_booking_intent_count × ADR × avg_stay_nights × 15% conversion` |
| `weekly_revenue_leakage` | Total estimated leakage for the 7-day period | `revenue_at_risk_conservative + slow_response_revenue_at_risk` |
| `annualised_revenue_leakage` | Projected annual leakage if pattern continues | `weekly_revenue_leakage × 52` |
| `nocturn_year_1_net_recovery` | Net gain if Nocturn AI were active: annualised leakage − annual Nocturn cost | `annualised_revenue_leakage × 0.60 − (999 + 199×12)` |

**Group D: Time-of-Day & Pattern Insights**

| Metric | Definition |
|---|---|
| `peak_inquiry_hour` | The hour of day (0–23, property local time) with the highest inquiry volume |
| `after_hours_peak_hour` | The after-hours hour with the highest unanswered inquiry count |
| `inquiries_by_hour` | JSON array: inquiry count for each of 24 hours (for the hour-by-hour chart) |
| `inquiries_by_day_of_week` | JSON array: inquiry count for each day of week |
| `staff_first_reply_hour` | Distribution of when staff first replies to overnight messages (shows "next morning catch-up" pattern) |

**Group E: Intent & Content Signals**

| Metric | Definition |
|---|---|
| `top_inquiry_topics` | Top 5 most common inquiry themes from AI topic extraction (e.g., "room rates", "pool access", "weekend availability") |
| `top_unanswered_topics` | Top 5 topics in UNANSWERED conversations — what's falling through the cracks |
| `booking_intent_rate` | `booking_intent_inquiries / total_inquiries` — what % are revenue-ready |
| `language_breakdown` | `{bm: %, en: %, mixed: %}` — what language guests are using |

##### F10.3 — Shadow Pilot Dashboard (Token-Gated GM View)

A dedicated read-only dashboard accessible to the GM via a unique signed URL (no login required, expires in 30 days):

`/shadow/[property-slug]?token=[signed_jwt]`

**Dashboard layout — three sections:**

**Section 1: The Evidence (headline KPIs)**
```
┌─────────────────────────────────────────────────────────────────┐
│  YOUR HOTEL · LAST 7 DAYS                                       │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │     127      │  │      43      │  │     RM 12,400        │  │
│  │  Inquiries   │  │  After-Hours │  │  Revenue Leaked      │  │
│  │  Received    │  │  Unanswered  │  │  (Conservative Est.) │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   6.2 hrs    │  │    RM 645k   │  │        73%           │  │
│  │  Avg After-  │  │  Annualised  │  │  Booking Intent in   │  │
│  │  Hrs Resp.   │  │  Leakage     │  │  Unanswered Msgs     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Section 2: The Pattern (visual charts)**
- Hour-by-hour inquiry volume chart (24-hour bar chart) — highlighting the after-hours window
- Response time distribution (stacked bar: <30min / 1-4hr / 4-8hr / 8-24hr / unanswered)
- Day-by-day inquiry trend over 7 days
- "What guests were asking" — top inquiry topics (horizontal bar chart)
- "What they didn't get answers for" — top unanswered topics (highlighted in red)

**Section 3: The Opportunity (CTA)**
- Side-by-side comparison: "Current state" vs "With Nocturn AI"
- Revenue recovery projection (conservative)
- Nocturn AI cost vs projected recovery (ROI multiple)
- "Start 48-Hour Implementation — RM 999" CTA linking to `/apply`

##### F10.4 — Weekly Report Email

Sent automatically on Day 7 of the shadow pilot and on each subsequent 7-day anniversary while `shadow_pilot_mode = True`.

**Subject line formula**: `[Hotel Name]: You left RM [X] on the table this week. Here's the proof.`

**Email sections:**

1. **Headline** — The single most important number: `RM [weekly_revenue_leakage]` in large type. Subheader: "Estimated revenue lost from [after_hours_unanswered_count] unanswered after-hours inquiries this week."

2. **The Numbers** — Three-column layout:
   - Column 1: Volume (total inquiries, after-hours count, business hours count)
   - Column 2: Response (unanswered count, avg response time, worst response time)
   - Column 3: Revenue (weekly leakage, booking intent rate, annualised projection)

3. **Hour-by-Hour Chart** — 24-hour bar chart rendered as HTML/CSS (no image dependency). Bars coloured green (business hours, handled) and red (after-hours, unanswered). Visually shows exactly when the leakage happens.

4. **The Unanswered Conversations** — A sample of 3–5 actual unanswered conversations (guest phone number replaced with "Guest +60XXXXX12"): time received, rough topic, revenue estimate for that specific inquiry. Real examples from their own hotel.

5. **What If** section — "If Nocturn AI had handled these 43 inquiries: 
   - 43 instant responses in under 30 seconds
   - Est. RM [recovery] in captured direct bookings
   - RM 0 in OTA commissions paid
   - Your morning team wakes up to 43 warm leads, not silence."

6. **CTA** — One button: "See Full Dashboard + Start 48-Hour Implementation" → links to the token-gated dashboard URL with scroll-to-CTA.

##### F10.5 — Acceptance Criteria

**Shadow Pilot Provisioning:**
- [ ] SheersSoft AM creates shadow pilot in `/admin/shadow-pilots` in under 2 minutes
- [ ] QR code generated and displayed in the admin panel
- [ ] Hotel GM scans QR → Baileys session established → confirmation shown in admin panel within 60 seconds
- [ ] `shadow_pilot_mode = True` on Property record, `shadow_pilot_start_date` set, `shadow_pilot_phone` populated with hotel's real WA number

**Message Observation:**
- [ ] Incoming guest message → `ShadowPilotConversation` record created with `first_guest_message_at` timestamp
- [ ] Outgoing staff message → `first_staff_reply_at` populated on that conversation, `response_time_minutes` computed
- [ ] Conversations still open after 24 hours with no staff reply → `status = "abandoned"`, `is_unanswered = true`
- [ ] After-hours flag set correctly based on `Property.operating_hours` timezone-aware
- [ ] AI intent classification runs on every incoming message (BM + EN) — result stored in `intent` field
- [ ] **NO message is sent to guests at any point during shadow pilot mode**

**Analytics Aggregation:**
- [ ] Daily aggregation job (`run_shadow_pilot_aggregation`) runs at midnight property-local-time
- [ ] All 30+ metrics computed and stored in `ShadowPilotAnalyticsDaily`
- [ ] Revenue leakage formula applied correctly using `Property.adr` and `Property.avg_stay_nights` (default: 1.0)
- [ ] `annualised_revenue_leakage` computed as `weekly × 52`

**Dashboard:**
- [ ] Token-gated GM dashboard accessible at `/shadow/[slug]?token=[jwt]`
- [ ] Dashboard renders without authentication — token verification only
- [ ] All 6 headline KPIs visible above the fold
- [ ] Hour-by-hour chart renders in HTML/CSS (no external image dependency)
- [ ] Dashboard loads in < 3 seconds
- [ ] Token expires after 30 days; refreshable by SheersSoft AM via admin panel

**Weekly Report:**
- [ ] Email fires automatically 7 days after `shadow_pilot_start_date`
- [ ] All revenue figures in RM, correctly formatted (RM X,XXX)
- [ ] Sample unanswered conversations included (minimum 3, maximum 5)
- [ ] Phone numbers partially masked in email
- [ ] CTA button links to token-gated dashboard
- [ ] SheersSoft AM receives internal notification (Slack webhook or email) within 1 minute of GM report being sent — with a "call this GM today" prompt
- [ ] Email renders correctly on mobile (max-width: 600px layout)

---

#### F11: Audit-to-Full Conversion Automation

| Attribute | Detail |
|---|---|
| **User Story** | *As a SheersSoft account manager, I receive an automatic notification when a GM submits the audit calculator and when a shadow pilot reaches Day 7 — so I can respond within 10 minutes and close the deal at the highest-probability moment.* |
| **Audit submission trigger** | POST `/audit/submit` → AuditRecord saved → email to GM with full report within 60 seconds → Slack/internal notification to SheersSoft AM within 10 minutes |
| **Shadow pilot Day 7 trigger** | `run_shadow_pilot_weekly_report` scheduler job → sends GM email with real inquiry data → SheersSoft AM notified to initiate Day 7 call |
| **AM follow-up sequence** | T+0: Audit submitted → AM WhatsApps GM within 10 minutes. T+7 days: Weekly report sent → AM calls same day: "You had [X] after-hours messages. Want me to activate the AI on your real number today?" |
| **Acceptance Criteria** | Internal notifications send within 60 seconds of trigger events. Weekly report email sends on day 7. Email content includes actual inquiry count and computed RM leakage from ShadowPilotAnalyticsDaily. |

---

### 4.1.1 Known Gaps — Status as of v2.5

| # | Gap | Status | Fix |
|---|-----|--------|-----|
| 1 | **Shadow pilot uses separate Twilio number** | ❌ **ARCHITECTURE CHANGE** — Shadow pilot must use Baileys linked device on hotel's REAL number. Separate number produces artificial data and requires the hotel to promote a new number. | Replace Twilio-number approach with Baileys linked device. See architecture.md v2.5 Section 2.6. |
| 2 | **Shadow pilot metrics are too sparse** | ❌ **REDESIGN** — Current `AnalyticsDaily` captures total_inquiries and after_hours_inquiries but not response times, unanswered counts, intent classification, or revenue leakage per conversation. | New `ShadowPilotConversation` + `ShadowPilotAnalyticsDaily` models. See F10.2. |
| 3 | **No token-gated GM dashboard for shadow pilot** | ❌ **NOT BUILT** — GMs cannot see their shadow pilot data without a full Nocturn login. | Build `/shadow/[slug]` token-gated page. |
| 4 | **Weekly report email lacks substance** | ❌ **REDESIGN** — Current weekly audit email is a stub. Must include sample conversations, hour-by-hour chart, full metric breakdown. | Full email redesign per F10.4. |
| 5 | **Bilingual AI not formally tested** | ❌ **OUTSTANDING** — BM/Manglish support is live but 50-question test suite not run. | Run 50-question suite (≥80%). Half-day field work. P0 blocker. |

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
| Stripe billing | Pilot invoicing is manual. Activate when ≥3 paying tenants confirmed. |
| Automated PDF report generation | HTML email is sufficient. Post-PMF investment. |

---

## 5. Success Metrics

### Shadow Pilot Specific KPIs

| Metric | Target | Action if Missed |
|---|---|---|
| **Shadow pilot QR scan → session established** | < 60 seconds | Debug Baileys session init |
| **Message observation latency** | < 5 seconds from WhatsApp to `ShadowPilotConversation` record | Check Baileys event listener pipeline |
| **Weekly report Day 7 delivery** | 100% of shadow pilots receive email on Day 7 | Cloud Scheduler alert on failure |
| **Shadow pilot → co-pilot conversion rate** | > 50% of GMs who receive the Day 7 report initiate onboarding | If below 30%: revenue figures not compelling enough — audit formula or data quality issue |
| **Dashboard token click-through** | > 60% of GMs who receive the email open the dashboard | Email CTA or subject line issue |

### Product KPIs (Per Property — Full Co-Pilot)

| Metric | Definition | v1 Target |
|---|---|---|
| **Inquiries Captured** | Total conversations initiated with AI | 30+/day |
| **After-Hours Recovery Rate** | % of after-hours inquiries responded to | >95% |
| **Response Latency** | Guest message → AI first response | <30 seconds |
| **Human Handoff Rate** | % escalated to staff | <20% |
| **Lead Capture Rate** | % of conversations with contact info collected | >60% |
| **Estimated Revenue Recovered** | `(lead nights × ADR, default 1 night) × 20%` | RM 3,000–5,000+/month per property |
| **Shadow Pilot → Full Product Conversion** | % of shadow pilots that convert to paid subscription | >50% |
| **Days Shadow Pilot → Paid** | Calendar days from shadow pilot start to first subscription payment | <14 days |

---

## 6. Pricing — Performance-Based

| Component | Amount | Notes |
|-----------|--------|-------|
| **Platform Fee** | RM 199/month | Full omni-channel access + dashboard + daily GM report |
| **Setup + AI Training** | RM 999 one-time | 48-hour implementation by SheersSoft team |
| **Performance Fee** | 3% only on confirmed direct bookings closed by Nocturn AI | Outcome-aligned — zero bookings = zero performance fee |

**Guarantee:** 30-day revenue recovery guarantee — if we don't demonstrate recovery, next month's platform fee is waived.

**Shadow Pilot:** Free. No commitment. Connects to their real number. Disconnectable at any time. The proof is the close.

---

## 7. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Baileys session drops during shadow pilot | Missed observations → incomplete data | Implement auto-reconnect with exponential backoff. Alert SheersSoft AM if session offline > 30 minutes. |
| Hotel has multi-device already at limit (max 4) | Cannot add Baileys as linked device | Check during provisioning call. Most hotels use 1 device. |
| WhatsApp ToS regarding unofficial API usage | Risk of number being banned | Shadow pilot = read-only. No message sending. Low risk. For production co-pilot, migrate to official BSP (Wati/360dialog) after pilot proves ROI. |
| AI hallucinations / wrong rate quotes | Destroys trust | Never state rates unless in KB. Default to handoff if unsure. |
| PDPA compliance gaps | Legal risk | Encrypt PII at rest. Data isolation per property. Mask phone numbers in all reports. |
| Shadow pilot volume too low | Can't prove ROI | Pre-qualify: estimate volume using audit calculator before provisioning. Properties projecting <5 after-hours msgs/day are below ICP threshold. |
| GM dismisses revenue figures as estimates | Shadow pilot doesn't close | Show sample real conversations from their own WhatsApp. Hard to dismiss something they recognise. |

---

## 8. Go-To-Market

### Launch Sequence (Current)

1. **Application outreach** — Direct prospects to sheerssoft.com/apply
2. **Application → Shadow pilot offer** — "Let me connect a listener to your WhatsApp for 7 days. You'll see your real numbers. No commitment."
3. **Shadow pilot → Day 7 report** — GM receives evidence email + dashboard link
4. **Day 7 call → Co-pilot activation** — "You had [X] inquiries you never answered. Want to activate Nocturn AI on your number today?"
5. **Co-pilot → 30-day ROI** — Daily GM report shows RM recovered every morning
6. **Day 30 review → Referral** — Review confirmed revenue vs 3% fee. Request warm intro to peer GM.

### The Shadow Pilot Pitch (1 sentence)

> *"Let me connect a silent listener to your WhatsApp for 7 days — no new number, no change to how your team works — and I'll show you exactly how much revenue left your hotel last week."*

---

## 9. Roadmap

### 9.1 Sprint 2.5 — Shadow Pilot Deep Implementation (This Sprint)

> Full implementation spec in [shadow_pilot_spec.md](./shadow_pilot_spec.md).

**Critical pivot from previous architecture**: Shadow pilot now uses Baileys linked device on hotel's real WhatsApp number, not a separate Twilio number. This produces real, irrefutable data.

Status as of v2.5:

| Item | Status |
|---|---|
| `audit_only_mode` flag on Property | ✅ Built (v0.5) — will be replaced by `shadow_pilot_mode` flag in v2.5 migration |
| Weekly audit email — stub | ✅ Built (v0.5) — will be replaced by full F10.4 email template |
| `/admin/shadow-pilots` provisioning page | ✅ Built (v0.5) — must be updated to support Baileys QR flow |
| Baileys/whatsapp-web.js linked device service | ❌ Not built — Sprint 2.5 P0 |
| `ShadowPilotConversation` model | ❌ Not built — Sprint 2.5 P0 |
| `ShadowPilotAnalyticsDaily` model | ❌ Not built — Sprint 2.5 P0 |
| Response time tracking + unanswered detection | ❌ Not built — Sprint 2.5 P0 |
| Intent classification on shadow messages | ❌ Not built — Sprint 2.5 P1 |
| Token-gated GM shadow dashboard | ❌ Not built — Sprint 2.5 P0 |
| Full weekly report email (F10.4) | ❌ Not built — Sprint 2.5 P0 |
| Internal AM notification on Day 7 | ❌ Not built — Sprint 2.5 P1 |

### 9.2 Sprint 2.6 — Hybrid AI Co-Pilot (Following Sprint)

| Item | Status |
|---|---|
| Hybrid reply drafting UI (dashboard → "Copy to WhatsApp") | ❌ Not built |
| Google Sheet real-time inventory reader (2-minute polling) | ❌ Not built |
| FPX/DuitNow payment link generator in AI reply drafts | ❌ Not built |
| Daily GM report: "RM X recovered today" | ❌ Not built |

### 9.3 Post-Pilot Roadmap

| Phase | Feature | Trigger |
|---|---|---|
| **v1.1** | Week-over-week comparison in daily email | 14+ days of data |
| **v1.2** | "Mark as Booked" confirmed revenue in dashboard | Paying customers want verified ROI for renewal |
| **v1.3** | Inquiry Volume by Hour chart (staffing insights) | Pilot data available |
| **v1.4** | Lost lead reason analytics | After Lost status UI is live and data accumulates |
| **v2.0** | Meta Cloud API full automation (Stage 3) | After 5 paying pilots + virtual office address verified |
| **v2.5** | Official BSP migration (Wati or 360dialog) | After pilot proves ROI and Meta registration completes |

---

*This PRD describes the product that solves the validated problem. If a feature isn't in Section 4.1, it doesn't exist in v1. The market research is the acceptance test.*

*v2.5 changes: F10 completely rewritten. Shadow pilot architecture changed from Twilio secondary number to Baileys linked device on hotel's real WhatsApp number. New metrics model (30+ metrics vs previous 4). Token-gated GM dashboard added. Weekly report email fully specified. New shadow_pilot_spec.md document created as canonical implementation reference.*
