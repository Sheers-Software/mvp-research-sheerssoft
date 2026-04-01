# Go-to-Market Execution Plan
## Nocturn AI — From Build to First Paying Customer
### Version 1.1 · 18 Mar 2026
### Cross-referenced with: product_gap.md, prd.md v2.0, opportunity_2_playbook.md, gap_analysis.md, alignment.md, building-successful-saas-guide.md, portal_architecture.md, auth_rbac_plan.md

---

## Why Most Startups at This Stage Fail

Before the plan, the diagnosis. The graveyard is full of products that:

1. **Built features no one asked for** — then called it "vision." The result is a codebase with a full multi-tenant SaaS hierarchy, Stripe billing, gamified onboarding, and a support chatbot, while the GM still lands on a setup checklist instead of revenue numbers. This is the current state.
2. **"Build it and they will come"** — treated shipping as the hard part. Distribution is 10× harder than engineering. The warm pipeline of 10 properties from the 8 interviews is a gift. It evaporates within 3 months if not actioned.
3. **Ran out of runway before getting to proof** — delayed the first real customer by chasing perfect infrastructure. Every day without Vivatel live is a day without data, case studies, or evidence.
4. **Demoed a product that didn't match the pitch** — the website says "see revenue you recovered while you slept." The dashboard opens to an onboarding checklist. That gap destroys trust in the first 10 seconds.
5. **Skipped the conversation and lost the deal in silence** — Amsyar is transitioning to Accor. The opportunity to lock in an advisor/design partner who validated Opportunity #1 (F&B Intelligence) had a 48-hour window. These windows close.

This plan is designed to avoid every one of these. It is sequenced by what removes the biggest obstacle to payment, not by what is most technically interesting.

---

## The One Number That Matters Right Now

**Days to first invoice: ≤ 21**

Every task in this plan is evaluated against this constraint. If a task does not move you closer to that invoice, it does not happen before the invoice.

---

## Plan Structure

| Phase | Name | Duration | Outcome |
|-------|------|----------|---------|
| **0** | Fix the Gaps | Days 1–5 | Product matches the pitch; demo-ready |
| **1** | Activate Vivatel | Days 6–12 | Pilot live with real guests |
| **1.5** | Internal Controls | Days 10–20 | SheersSoft can operate multi-tenant safely |
| **2** | Capture the Evidence | Days 13–30 | Numbers in hand |
| **3** | Convert to Paid | Days 28–35 | First invoice issued |
| **4** | Replicate the Pilot | Days 35–60 | 3 more properties; tenant self-service live |
| **5** | Close to 10 | Days 55–90 | RM 15,000–30,000 MRR; portal fully operational |

These phases overlap intentionally. Sales conversations happen during Phase 1. Marketing updates happen before Phase 3. Nothing waits for "the right time."

---

## Portal Architecture — GTM Alignment

The platform has three distinct portals (see `docs/portal_architecture.md`). Each unlocks a different GTM capability:

| Portal | Path | Who Uses It | GTM Gate |
|--------|------|-------------|----------|
| **Property Operations** | `/dashboard` | Hotel staff (daily use) | Phase 0 — must be right before any demo |
| **Internal Ops** | `/admin` | SheersSoft team | Phase 1.5 — needed before multi-tenant scale |
| **Tenant Management** | `/portal` | Hotel owners/admins | Phase 4 — enables self-service onboarding |
| **Onboarding Wizard** | `/welcome` | New hotel owners | Phase 4 — replaces manual SheersSoft-led setup |

**Implication for sequencing:**
- Phase 0–3 live entirely on `/dashboard`. Get that right first.
- Phase 1.5 adds maintenance mode and health monitoring to `/admin`. Operational necessity before having 2+ live tenants.
- Phase 4 is when `/portal` and `/welcome` become revenue-multipliers: each new tenant self-serves in 48 hours instead of requiring a SheersSoft engineer session.

---

## Phase 0: Fix the Gaps
### Days 1–5 · Owner: Ahmad Basyir (Dev) · Goal: Product matches the pitch

> **Failure pattern addressed:** Demoing a product that contradicts the value proposition. A GM who opens the dashboard and sees a setup checklist will not pay for a revenue engine.

The seven blockers from `product_gap.md`. Do them in this order — the first three unlock the Vivatel conversation.

---

### Task P0.1 — Rebuild Dashboard Home as the "Money Slide"
**Priority:** #1 · **Effort:** 1–2 days · **Blocks:** Every sales conversation

**What to do:**
Replace `frontend/src/app/dashboard/page.tsx`. The current page renders `OnboardingProgress` milestone cards and a `ProgressRing`. Delete it.

The new landing page must show:
```
┌──────────────────────────────────────────────────────┐
│  Yesterday  ·  [Date]                                │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │
│  │    47    │ │    21    │ │    14    │ │RM 3,220│  │
│  │Inquiries │ │After-Hrs │ │  Leads  │ │Recovered│  │
│  │ Handled  │ │Recovered │ │Captured │ │ Revenue │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘  │
│                                                      │
│  Avg Response: 18s     AI Handled: 88%               │
│  [View Full Analytics →]   [View Leads →]            │
└──────────────────────────────────────────────────────┘
```

**Source data:** Call `GET /api/v1/analytics/dashboard` (already exists). Display yesterday's snapshot. If no data yet (new property), show "Waiting for first inquiry — your AI concierge is live and listening."

**Do not remove:** The onboarding checklist route. It can live at `/dashboard/setup` for SheersSoft-internal use during KB population. The GM never needs to see it.

**Definition of done:** A logged-in user lands on the dashboard and the first thing they read is a revenue number, not a task list.

**Failure lesson:** *From building-successful-saas-guide.md — "The dashboard is the product's handshake. Make it say what you promised, not what you built."*

---

### Task P0.2 — Add Staff Reply Box to Conversations View
**Priority:** #2 · **Effort:** 1 day · **Blocks:** Vivatel UAT

**What to do:**
In `frontend/src/app/dashboard/conversations/[id]/page.tsx` (or equivalent), add below the conversation thread:

```
[ Type your reply here...                    ] [Send →]
```

On submit, call `POST /api/v1/conversations/{id}/messages` with `{ role: "staff", content: "..." }`.

The backend already supports this endpoint. The channel routing logic in `conversation.py` must then forward the staff message back to the guest via the original channel (WhatsApp or web widget). Verify this works end-to-end — a staff reply typed in the dashboard must arrive in the guest's WhatsApp.

**Definition of done:** Staff types a message in the dashboard. Guest receives it on WhatsApp within 10 seconds.

**Failure lesson:** *During Vivatel UAT, Zul will use the handoff queue. The moment he discovers there is no reply box, he will call this "unfinished." That word, spoken once, echoes in every subsequent procurement conversation.*

---

### Task P0.3 — Unblock the Daily Email Report in Production
**Priority:** #3 · **Effort:** 2 hours · **Blocks:** Ongoing value delivery

This is two separate actions, both required:

**Action A — Add `SENDGRID_API_KEY` to Secret Manager:**
```bash
# Get the key from SendGrid dashboard → Settings → API Keys
echo -n "SG.xxxxxxxxxxxxxxxxxxxx" | gcloud secrets versions add SENDGRID_API_KEY \
  --data-file=- --project=nocturn-aai
```

**Action B — Create Cloud Scheduler job for daily report:**
```bash
gcloud scheduler jobs create http nocturn-daily-report \
  --location=asia-southeast1 \
  --schedule="30 7 * * *" \
  --time-zone="Asia/Kuala_Lumpur" \
  --uri="https://nocturn-backend-owtn645vea-as.a.run.app/api/v1/internal/run-daily-report" \
  --http-method=POST \
  --headers="X-Internal-Secret=<value from Secret Manager INTERNAL_SCHEDULER_SECRET>" \
  --attempt-deadline=30s
```

While here, also create the remaining 3 scheduled jobs:
```bash
# Follow-up reminders — hourly
gcloud scheduler jobs create http nocturn-followups \
  --schedule="0 * * * *" --time-zone="Asia/Kuala_Lumpur" \
  --uri="...run-followups" --http-method=POST \
  --headers="X-Internal-Secret=<value>"

# Monthly insights — 1st of month 8am
gcloud scheduler jobs create http nocturn-insights \
  --schedule="0 8 1 * *" --time-zone="Asia/Kuala_Lumpur" \
  --uri="...run-insights" --http-method=POST \
  --headers="X-Internal-Secret=<value>"

# DB keep-alive — every 6 days at noon
gcloud scheduler jobs create http nocturn-keepalive \
  --schedule="0 12 */6 * *" --time-zone="Asia/Kuala_Lumpur" \
  --uri="...health" --http-method=GET
```

**Definition of done:** Cloud Scheduler console shows 4 jobs created. Trigger the daily-report job manually once and verify the email arrives in the test inbox.

---

### Task P0.4 — Add FERNET_ENCRYPTION_KEY to Secret Manager
**Priority:** #4 · **Effort:** 30 minutes · **Blocks:** PDPA compliance, contract signing

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy output, then:
echo -n "the-key-output" | gcloud secrets versions add FERNET_ENCRYPTION_KEY \
  --data-file=- --project=nocturn-aai
```

Redeploy backend after adding. Verify `pii_encryption.py` encrypts new lead phone/email fields by checking a test lead in the database directly.

**Definition of done:** New lead captured via WhatsApp test → guest phone appears encrypted in `leads` table when queried directly via SQL.

---

### Task P0.5 — Fix "Lost" Status in Leads Filter
**Priority:** #5 · **Effort:** 2 hours

In `frontend/src/app/dashboard/leads/page.tsx`, add "Lost" to the status filter chips (alongside New, Contacted, Qualified, Converted). This is a 3-line frontend change.

---

### Task P0.6 — BM/Manglish Test Suite (50 Questions)
**Priority:** #6 · **Effort:** Half day · **Standard:** PRD F1 Acceptance Criteria — ≥80% pass rate required

Run the 50-question BM/Manglish test suite against the live Vivatel KB via WhatsApp (Twilio sandbox). The suite must cover:
- Standard room inquiries in BM ("ada bilik available untuk 2 malam?")
- Rate questions ("berapa harga bilik standard?", "ada package tak?")
- After-hours messages at unusual hours
- Complaints ("aircond bilik saya rosak")
- Group bookings in Manglish ("nak book 30 bilik untuk majlis, boleh bagi harga special?")
- Code-switching mid-sentence ("Can I check in early? Saya sampai pukul 10 pagi")
- Directions in BM ("macam mana nak pergi dari KLCC?")
- Facilities in BM ("kolam renang buka pukul berapa?")
- Polite refusal test ("kalau tak ada bilik, boleh suggest lain?")
- Ambiguous / informal input ("ok ke tempat ni?", "best tak?")
- 40 additional variations on the above categories

Document each question, the AI response, and a pass/fail assessment. **If pass rate < 80%, do not proceed to Phase 1.** Log failures as bugs, patch the prompt/KB, re-run before pilot.

Share the documented pass rate with marketing before any bilingual claim appears on the website.

**Definition of done:** 50 questions answered, pass rate ≥80% documented, failures logged as bugs, marketing briefed in writing.

---

### Task P0.7 — Populate Vivatel KB
**Priority:** #7 · **Effort:** 1 day · **Requires:** Zul (Vivatel)

Schedule a 90-minute working session with Zul. Collect:
- Room types and descriptions (Superior, Deluxe, Suite)
- Published room rates (rack rate, weekend rate, packages)
- Facilities list (pool, gym, restaurant, meeting rooms, parking)
- F&B options (restaurant hours, menu highlights, room service)
- Check-in/check-out times, early/late check-in policy
- Cancellation policy
- Frequently asked questions (from Zul's memory — what do guests ask most?)
- Operating hours
- Location and directions (nearest MRT, from KLCC)
- Contact information

Ingest via admin script: `python backend/scripts/ingest_kb.py --property-slug vivatel --file vivatel_kb.md`

**Definition of done:** `KBDocument` table has ≥ 30 entries for Vivatel property. Test 5 representative questions via WhatsApp — all answered correctly without hallucination.

---

### Phase 0 Exit Criteria

All 7 tasks complete. Run the following verification sequence before moving to Phase 1:

1. Log in to dashboard → KPI cards visible immediately ✓
2. Send a WhatsApp message to Vivatel test number → AI responds correctly in < 30s ✓
3. Trigger a handoff → staff sees notification in dashboard → types reply → guest receives it ✓
4. Trigger Cloud Scheduler daily-report job manually → email arrives in inbox ✓
5. Send 3 BM messages → all answered in BM ✓
6. New lead created → phone encrypted in DB ✓

---

## Phase 1: Activate Vivatel
### Days 6–12 · Owner: Ahmad Basyir (Product) + Zul (Vivatel) · Goal: First real guest served

> **Failure pattern addressed:** Building indefinitely without a real customer. Vivatel's Zul is the design partner. Design partners are not beta testers — they co-create the product. Every conversation with Zul is as important as any code commit.

---

### Task V1.1 — Production Configuration for Vivatel
**Effort:** Half day

Configure the Vivatel property record in production:
```
Property:
  name: "Vivatel Kuala Lumpur"
  slug: "vivatel-kl"
  timezone: "Asia/Kuala_Lumpur"
  operating_hours: { mon-fri: 07:00-23:00, sat-sun: 07:00-23:00 }
  notification_email: [Zul's email + GM's email]
  plan_tier: "starter"
  whatsapp_provider: "meta"  (or "twilio" based on Zul's setup)
  adr: 230  (confirm with Zul)
```

---

### Task V1.2 — WhatsApp Business Number Linked
**Effort:** 1–3 days (Meta approval timeline) · **Start immediately**

Two parallel tracks:
- **Track A (Meta Cloud API):** Submit Vivatel's WhatsApp Business number for verification via Meta Business Manager. Approval: 1–7 days. Apply on Day 1 of this phase.
- **Track B (Twilio sandbox, live immediately):** Configure Twilio WhatsApp sandbox for Vivatel's test number. Usable from Day 1 for UAT while Meta approval processes.

Vivatel goes live on Track B first. Cut over to Track A (Meta) once approved.

---

### Task V1.3 — Widget Installation on Vivatel Website
**Effort:** 1 hour (from Vivatel's IT) · **Dependency:** Zul arranges with their web team

Generate widget snippet for Vivatel property. Provide to Zul:
```html
<script src="https://nocturn-frontend-owtn645vea-as.a.run.app/widget.js"
  data-property="vivatel-kl"
  data-theme="dark">
</script>
```

If Vivatel's IT team is slow, offer to send the one-liner to their web developer directly. This takes 5 minutes for any developer.

---

### Task V1.4 — Staff Onboarding (Zul + Front Desk Team)
**Effort:** 1-hour session

Walk Zul and 1–2 front desk staff through the dashboard:
1. Show the KPI landing page — "this is what you see every morning"
2. Show the Conversations view — "these are all active chats right now"
3. Show the Leads view — "these are the guests the AI has qualified"
4. Demonstrate a handoff — "when the AI can't handle it, you see this notification, you click, you reply from here"
5. Show the daily email format — "tomorrow morning at 7am you'll get this in your inbox"

Do not train on anything else. The product has 5 screens. Show 5 screens. Leave.

**Common failure:** Over-training. Staff become overwhelmed and avoid the product. The simpler the onboarding, the higher the adoption.

---

### Task V1.5 — 48-Hour Supervised Launch
**Effort:** Ongoing monitoring · **Owner:** Ahmad Basyir

For the first 48 hours after Vivatel goes live:
- Monitor every conversation in real-time
- Log any AI response that is wrong, unhelpful, or inappropriate
- Respond to Zul's messages within 15 minutes during business hours
- Patch KB immediately if AI gives wrong information

**This is not optional.** The first 48 hours of a pilot determine whether the customer becomes a champion or a detractor. Be obsessively present.

---

### Task V1.6 — First-Week Check-in Call with Zul
**Day 7 of pilot · Duration:** 30 minutes

Questions to ask:
1. "What was the most useful thing the AI did this week?"
2. "What did it get wrong or miss?"
3. "Did the daily email feel accurate?"
4. "Did any guest complain about the AI?"
5. "Would you feel comfortable if we quoted your name in our case study?"

Document answers verbatim. This is primary research for the case study.

**Do not:** Pitch the paid plan in this call. This call is about listening. The pitch comes in Week 4.

---

### Phase 1 Exit Criteria

- Vivatel WhatsApp is live (at minimum via Twilio sandbox)
- Widget is installed on Vivatel website
- Zul is logging in to the dashboard daily (verify via session logs)
- AI is answering real guest inquiries correctly
- At least 1 real lead captured

---

## Phase 1.5: Internal Controls
### Days 10–20 · Owner: Ahmad Basyir (Dev) · Goal: SheersSoft can operate multi-tenant safely

> **Why this exists:** Running a live pilot with real hotel guests is different from running a demo. Things break. APIs go down. Bad AI responses happen. Without operational controls, your only option is to call Zul personally and explain why the AI told a guest the wrong rate. That is not a scalable business.

---

### Task I1.1 — Maintenance Mode Toggle
**Effort:** 1 day (backend + admin UI)

Add a maintenance mode toggle to `/admin/system`. When enabled:
- Channel webhooks respond with a canned message to guests (not an error)
- Tenant dashboards show a maintenance banner with ETA
- `/admin` stays accessible to SheersSoft team

**Backend:** `PUT /api/v1/superadmin/maintenance` writing to `system_config` table. Middleware check on all non-admin routes. See `docs/portal_architecture.md` Section 4.3.

**Use case:** Supabase free tier goes into maintenance, or a bad deployment needs a 10-minute rollback window. Instead of Vivatel guests getting 500 errors, they get: "Our reservation system is undergoing scheduled maintenance. We'll be back shortly."

---

### Task I1.2 — Service Health Dashboard
**Effort:** 2 days

Build `/admin/health`. Show live status of: PostgreSQL, Redis, Supabase Auth, Gemini, OpenAI, Anthropic, SendGrid, WhatsApp API, Stripe. Color-coded (green/amber/red), latency readout, last-checked time.

**Backend:** `GET /api/v1/superadmin/service-health` — parallel asyncio checks, 3s timeout per service, 20s cache.

**Use case:** Gemini degrades at 2pm on a Tuesday. You know before Vivatel's front desk notices the AI is slow. You have a 5-minute head start to investigate or activate maintenance mode.

---

### Task I1.3 — Announcements System
**Effort:** 3 days (backend + admin composer + tenant banner)

Build the ability to notify all tenants (or specific ones) of planned maintenance, incidents, or new features — via in-app banner.

1. `POST /api/v1/superadmin/announcements` — create
2. `GET /api/v1/announcements/active` — tenant-scoped fetch
3. `/admin/announcements` — composer UI (title, body, type, target, schedule)
4. `/dashboard/layout.tsx` — banner strip (dismissable, re-appears for maintenance type)

**Data model:** `announcements` table (see `docs/portal_architecture.md` Section 4.4).

**Use case:** Before taking the system down for a 30-minute maintenance window, SheersSoft creates an announcement. All logged-in hotel staff see a yellow banner: "Scheduled maintenance tonight 11pm–11:30pm MYT. All conversations will resume automatically." Professional. No personal WhatsApp calls needed.

---

### Phase 1.5 Exit Criteria

- Maintenance mode toggle works: flip to ON in `/admin/system`, send a WhatsApp test message, verify canned response arrives
- Health dashboard shows green for all live services
- Create a test announcement, verify it appears as a banner in `/dashboard`

---

## Phase 2: Capture the Evidence
### Days 13–30 · Owner: Ahmad Basyir (Product + Sales) · Goal: Data that sells the next customer

> **Failure pattern addressed:** Demos built on hypotheticals. The ROI calculator on the website shows RM 9,315 monthly recovered. That number means nothing to a skeptical GM until Vivatel's real data confirms it. Real numbers, even smaller ones, beat made-up big numbers.

---

### Task E2.1 — Daily Monitoring and KB Refinement
**Cadence:** Every day · **Duration:** 15 minutes

Review the previous day's conversations. Identify:
- Questions the AI could not answer (add to KB)
- Responses that were technically correct but tone-deaf (refine prompt)
- Handoffs that could have been avoided (AI gave up too early — raise threshold)
- Handoffs that should have happened sooner (AI held on too long — lower threshold)

Log every change made to the KB in a simple change log. This becomes part of the onboarding documentation for the next property.

---

### Task E2.2 — Track the Real Numbers (Week-by-Week)
**Cadence:** Every Monday

Pull from the dashboard:
- Total inquiries handled by AI
- After-hours inquiries captured
- Leads captured (with names and contact details)
- Revenue recovered (formula: leads × ADR × 20%)
- Cost savings (AI-handled × 0.25hr × RM 25)
- Daily email open rate (if SendGrid tracking enabled)

Build a simple weekly tracker spreadsheet. You will need this for the case study.

---

### Task E2.3 — Collect Unprompted Feedback
**Days 14–28 · Passive**

Watch for:
- WhatsApp messages from Vivatel staff (not guest) about the system
- Zul forwarding a conversation saying "look at this one"
- Any guest complaint that came from the AI
- Any booking that was explicitly confirmed after an AI-initiated conversation

Every piece of unsolicited feedback — positive or negative — is more valuable than any survey.

---

### Task E2.4 — Build the Vivatel Case Study One-Pager
**Day 25–28 · Effort:** Half day · **Requires:** Zul's approval to be named

Format:
```
VIVATEL KUALA LUMPUR — 30-DAY RESULTS
-------------------------------------
Before: Inquiries after 6pm went unanswered until morning.
After:  AI handled 100% of after-hours inquiries in < 30 seconds.

Numbers:
  [X] inquiries handled by AI in 30 days
  [Y] after-hours leads captured
  [Z] estimated revenue recovered (RM ___)
  [A]% response rate improvement
  [B] seconds average response time

"[Zul's quote about the product]"
— Zul [Last name], Reservation Manager, Vivatel KL

Setup: 48 hours · RM 999 one-time setup · RM 199/month + 3% on facilitated bookings · No long-term contract
```

If the numbers are modest (e.g., RM 920 recovered instead of RM 9,315), publish them anyway. An honest RM 920 in 30 days beats a fabricated RM 12,400. The next property wants to know what is real.

**Do not:** Publish without Zul's written approval (WhatsApp confirmation is sufficient). Do not exaggerate or round up numbers.

---

### Task E2.5 — Update Website with Vivatel Case Study
**Day 28 · Effort:** 1 hour

Replace the "Bukit Bintang City Hotel" placeholder on the website with Vivatel's real numbers (if Zul approves). Until then, mark the existing case study as "Pilot benchmark" not "Customer result."

**Failure lesson:** *From product_context.md — "30% direct booking increase" claim exists without verification. Marketing must not publish numbers the product cannot prove. One journalist or skeptical GM asking for the source destroys credibility with the entire pipeline.*

---

### Task E2.6 — Begin 3 Outreach Conversations (Parallel with Phase 2)
**Days 13–20 · Owner:** Ahmad Basyir · **Use warm pipeline from gap_analysis.md**

Do not wait for Vivatel's case study before starting conversations. Start them now, but honestly:

> *"We just launched a pilot with Vivatel. I'll have 30-day numbers by [date]. In the meantime, I want to understand your after-hours inquiry problem before I show you anything. Can I have 20 minutes?"*

**Priority order from pipeline** (aligned with PRD Section 8 launch sequence):
1. **SKS Hospitality** — Bob's referral. **Highest priority.** Referrals convert 10× better than cold. Use Bob's name in the first message. Start this conversation in Phase 1 — do not wait for Vivatel data.
2. **Novotel KLCC** — Shamsuridah. Already interviewed. Said "200–300 emails, 30% manual." Warm. Reference the Feb interview.
3. **Ibis Styles KL** — Simon. Interviewed. Has the problem. Medium chain — needs GM sign-off.

**Do not pitch.** Ask questions. *"Since we spoke in February, have you found a solution to the after-hours inquiry problem?"* The silence after that question is your opening.

The goal of this outreach is to have 3 active conversations that you can bring real Vivatel data into on Day 30.

---

### Task E2.7 — Maintain a 3×/Week Customer Call Cadence
**Permanent ritual · Starts Day 1 · Non-negotiable**

From `building-successful-saas-guide.md`: *"3–5 customer calls/week. Non-negotiable. Cannot build great products from a conference room."*

These calls are not pitches. They are discovery conversations. Questions to rotate through:
- "What did you do last night when an inquiry came in after your team left?"
- "How do you currently know which leads are worth calling back?"
- "What would need to be true for you to feel that RM 199/month plus 3% on bookings we close is a good deal?"
- "If this product disappeared tomorrow, what would you miss?"
- "What do you use today instead of this?"

Document every call. Share patterns with the product team weekly.

---

## Phase 3: Convert to Paid
### Days 28–35 · Owner: Ahmad Basyir (Sales) · Goal: First invoice issued

> **Failure pattern addressed:** Infinite free pilots. The Malaysian hospitality market is relationship-driven. GMs will accept endless freebies if you let them. The conversion conversation must be planned and executed deliberately.

---

### Task C3.1 — The Pilot Review Call (Day 28–30)
**Duration:** 45 minutes · **Attendees:** Ahmad Basyir + Zul + ideally the GM

**Structure:**
- Minutes 1–5: Show the 30-day numbers side by side with the pilot agreement goals
- Minutes 5–15: Walk through 2–3 specific conversations that saved a booking or captured a lead
- Minutes 15–25: Ask Zul to narrate what changed operationally ("before vs now")
- Minutes 25–35: Present the paid plan options
- Minutes 35–45: Handle objections, agree on next step

**The pitch (from opportunity_2_playbook.md 60-second version — updated pricing 31 Mar 2026):**
> *"Vivatel received [X] inquiries after hours last month. Your AI handled all of them in under 30 seconds and captured [Y] leads. Based on your RM 230 ADR, we estimate RM [Z] in recovered revenue. Our fee is RM 199/month plus 3% only on confirmed bookings we facilitated. Compare that to what Agoda charges you — 15–18% on every booking. Want to continue?"*

Do not over-complicate the pitch. Ask for the business.

---

### Task C3.2 — Pricing Presentation
**During the pilot review call**

> **Updated 31 Mar 2026:** Flat-tier pricing (Starter/Professional) retired. Present the single Revenue Partner Plan.

| Component | Amount |
|-----------|--------|
| **Platform fee** | RM 199/month |
| **Setup** | RM 999 one-time (already paid / credited from pilot) |
| **Performance fee** | 3% on confirmed direct bookings facilitated by Nocturn AI |

**Anchor on value:** "You're paying 15–18% to OTAs. We charge 3% only on what we actually close for you. The RM 199/month covers the platform, dashboard, and daily GM report."

**Simple close:** "Continuing is RM 199 a month. The 3% is self-funding — it only triggers when we win a booking for you."

**Invoicing:** Manual invoice for first 3 customers. Stripe is not required. Use a simple PDF invoice from Wave or similar. Collect by bank transfer (Maybank or RHB). Add payment details to the proposal.

---

### Task C3.3 — Objection Handling (Preparation)
**Prepare before the call. These will come:**

| Objection | Response |
|-----------|----------|
| "Can we continue free for another month?" | "I'd love to, but we need to invest in your property specifically — KB updates, integration improvements. That requires us to be on a paid relationship. I can offer 50% off the first month." |
| "It's expensive for a chatbot" | "It's not a chatbot, and it's not expensive — RM 199/month plus 3% only on bookings we close. You pay Agoda 15–18% on every booking. We charge 3% only on the ones we win for you. The comparison is with your OTA bill, not with chatbot software." |
| "I need to check with my GM / owner" | "Of course. Can we have a 20-minute call with them this week? I'll bring the numbers." |
| "The system made some mistakes" | "Yes, and we fixed them in real time. Here are the 3 KB updates we made. That's normal in the first month. Month 2 will be sharper because we know your property now." |
| "We're evaluating other solutions" | "Which ones? I'd like to know what you're comparing us against. Most of the alternatives either don't support BM or require 3-month onboarding. What specifically are they offering?" |

**The silence rule:** After asking for the business, stop talking. The next person to speak loses leverage.

---

### Task C3.4 — Issue the Invoice
**Day 30–32 · Once verbal agreement is received**

Issue within 24 hours of verbal agreement. Delay kills deals.

Invoice contents:
- Sheers Software Sdn Bhd (company name, SSM registration, bank details)
- Vivatel Kuala Lumpur
- Service: Nocturn AI — Revenue Partner Plan
- Period: [Month] 2026
- Platform fee: RM 199
- Performance fee: 3% × RM [confirmed bookings value] = RM [amount]
- Total: RM [199 + performance fee]
- Payment due: 14 days
- Bank: [Bank name, account number]

Follow up 3 days before due date. Follow up on due date. Follow up 2 days after. Do not wait silently for payment.

---

### Task C3.5 — If Vivatel Does Not Convert
**Contingency plan — do not skip this**

If Zul's GM declines after the pilot:
1. Ask why, verbatim. Write it down.
2. Ask if they would refer one property that might be interested.
3. Do not burn the relationship. Leave the door open: "Completely understood. If anything changes, or if your occupancy data shifts, I'd love to revisit."
4. Use the pilot data (with Vivatel's permission, anonymized) for the next pitch.
5. Immediately escalate the 3 parallel conversations from Task E2.6 to pilot stage.

**Failure lesson:** *First customer is the hardest. But if the first 3 pilots do not convert, it is a product problem, not a sales problem. Review churn reasons, not pipeline.*

---

## Phase 4: Replicate the Pilot
### Days 35–60 · Goal: 3 more properties live → 3 more paying

> **Failure pattern addressed:** One customer is not a business. It is a data point. Three customers with different profiles confirm the pattern. Five customers confirm PMF signals.

---

### Task R4.1 — Systematize the Onboarding
**Day 30–35 · Effort:** 1 day · **Do this before the second pilot**

Document everything that was learned from Vivatel:
- KB intake form template (room types, rates, FAQs, operating hours)
- Standard property configuration script
- WhatsApp setup walkthrough (Meta Cloud API + Twilio backup)
- Widget installation guide (1-page PDF for IT teams)
- First-48-hour monitoring checklist
- Staff training script (30-minute walkthrough)

**Target:** Second property should go live in 48 hours from KB handoff. Vivatel took longer because you were learning. The process is now documented.

**Create:** `docs/onboarding_playbook_internal.md` — SheersSoft internal use only. This is the operations manual.

**Portal readiness check:** By Phase 4, the following must be live or the second onboarding still requires a SheersSoft engineer for every step:
- `/portal/kb/[propertyId]` — tenant can upload/edit their own KB (eliminates 90-minute KB session dependency)
- `/welcome` onboarding wizard — guides new property owner through KB → channel → team → go-live without a call
- `/admin` maintenance mode — SheersSoft can gracefully pause the platform if something breaks during a new onboarding without alarming existing tenants

**If these are not live by Phase 4**, fall back to admin scripts for KB ingestion. Do not delay the second pilot for portal completeness.

---

### Task R4.2 — Activate the 3 Warm Conversations
**Days 35–40 · Based on Vivatel results**

Now you have a real case study. Use it. Email each of the 3 active conversations (from Task E2.6):

> **Subject:** Vivatel results — 30 days in
>
> *[Name], we just completed 30 days with Vivatel KL. [X] inquiries handled, [Y] leads captured, RM [Z] recovered. I promised to share real numbers before asking for anything.*
>
> *Can I show you the same for your property? RM 999 setup, live in 48 hours, RM 199/month after that plus 3% only on confirmed bookings we close. We have a 30-day recovery guarantee — if we don't prove value, we waive the next month.*

**Do not send this email and wait.** Follow up by WhatsApp or call within 48 hours if no reply.

---

### Task R4.3 — Prioritize by "Time to Evidence"
**Days 40–55**

Not all properties produce good case study data at the same speed. Prioritize properties with:
- High volume of after-hours inquiries (more data faster)
- Willingness to be named in case study
- GM who is active on WhatsApp (easier feedback loop)
- No complex IT approval process (faster setup)

**Deprioritize for now:**
- Large chains with IT procurement requirements (Novotel, Dorsett, Hyatt) — these take 2–3 months of sales cycles
- Properties with custom PMS integrations
- Any property where the GM is not the decision maker

**Focus:** 3–5 star independent hotels. The ICP from `prd.md` is correct.

---

### Task R4.4 — Conduct Parallel Sales Conversations
**Ongoing · 3 active conversations minimum at all times**

Pipeline math: if 3 in 10 pilots convert, and each pilot takes 30 days, you need 3 pilots running simultaneously to reliably get 1 new paying customer per month.

Track in a simple spreadsheet (no CRM needed yet):

| Property | Contact | Status | Last Touch | Next Action | Due |
|---|---|---|---|---|---|
| Vivatel KL | Zul | Paying | 15 Mar | Monthly check-in | 15 Apr |
| Novotel KLCC | Shamsuridah | Contacted | 20 Mar | Follow-up call | 25 Mar |
| SKS Hospitality | Bob's referral | Intro | 22 Mar | Demo call | 27 Mar |
| Ibis Styles KL | Simon | Pilot | 18 Mar | Week-2 check-in | 1 Apr |

**Rule:** No deal goes more than 5 days without a touchpoint. Silent deals are dead deals.

---

### Task R4.5 — Bob's Referral (SKS Hospitality)
**Priority:** Highest of all pipeline · **Do not delay**

From `gap_analysis.md`: *"Leverage Bob's SKS Hospitality referral — Fresh properties = faster decisions."*

A warm referral from someone who has been in the room with the customer is worth 10 cold outreach attempts. Use it immediately. Message Bob:

> *"Bob — we're now live with a pilot at Vivatel. Getting strong early results. Is SKS Hospitality still the right contact for this, and can I use your name when I reach out?"*

Do not do anything with SKS until Bob confirms. Once he does, move SKS to the top of the priority list.

---

### Task R4.6 — Collect Micro-Testimonials
**Ongoing · Every satisfied interaction**

Ask every happy contact for one sentence by WhatsApp:
> *"We're putting together early results from pilots. Can I quote you? Just one sentence about what changed for your team."*

WhatsApp quote → pull quote in pitch deck, website, next case study. These compound.

---

### Phase 4 Exit Criteria

- 3 additional properties onboarded on free pilots
- Onboarding process documented and repeatable in 48 hours
- At least 1 additional property converting to paid (= 2 total paying customers)

---

## Phase 5: Scale to 10
### Days 55–90 · Goal: RM 15,000–30,000 MRR

> **Failure pattern addressed:** Premature scaling before proof. Do not hire, do not expand into new verticals, do not build new features, until you have 5+ paying customers with <5% monthly churn. At 10 customers, you have a business, not an experiment.

---

### Task S5.1 — Activate Cold Outreach Using the Case Study
**Day 55+ · Requires:** ≥2 confirmed case studies

LinkedIn outreach to GMs of 3–4 star independent hotels in:
- Kuala Lumpur (Bukit Bintang, KLCC, Mont Kiara)
- Penang (Georgetown)
- Kota Kinabalu

Message formula:
> *"[Name], I help [type of property] hotels in Malaysia recover bookings they're currently losing after hours. We're working with Vivatel KL — [X] leads captured last month, RM [Y] recovered. I'd love to show you the same for [Property Name] with a free 30-day pilot. 15 minutes?"*

Personalize the opening line using one specific fact about their property (recent review, renovation, upcoming event). Generic outreach gets ignored.

Volume target: 20 outreach messages per week. Expect 10–15% response rate from warm/targeted. 2–3 demo calls per week.

---

### Task S5.2 — Define the "Pilot to Paid" Conversion Funnel
**Day 55 · Formalize what has been learned**

Based on Vivatel and the first 3 replications, document:
- Average days from pilot start to paid conversion
- Most common objection and what resolved it
- What data point in the case study was most persuasive
- What caused pilots to churn without converting

Use this to improve the pilot review call script (Task C3.1) before scaling.

---

### Task S5.3 — Implement Confirmed Revenue in the Dashboard
**Day 55–65 · Product task**

This is the next most important product improvement after Phase 0:

In the leads table, add a "Mark as Booked" button. When staff clicks it:
- Prompt: "Enter booking value (RM):" with property ADR as default
- Updates `Lead.status` to `"converted"`, sets `Lead.actual_revenue = amount`
- Updates `AnalyticsDaily.actual_revenue_recovered`

**Impact:** The daily email shifts from "estimated RM 920 recovered" to "confirmed RM 2,100 in bookings this month." Confirmed numbers are 5× more persuasive than estimates in the conversion conversation.

This is what allows the case study to grow from "we think we recovered RM 920" to "we confirmed RM 2,100 in bookings that came from AI-captured leads."

---

### Task S5.4 — Prepare the Upsell Path (F&B Intelligence)
**Day 60+ · Plant seeds only — do not build yet**

From `gap_analysis.md`: *"Recommended play: #2 (AI Inquiry) → #1 (F&B Intelligence) as warm pitch."*

Once a hotel is paying and has 60+ days of data:
> *"We're starting to explore F&B revenue intelligence as our next product. You mentioned in [month] that F&B data is opaque. Would you be willing to spend 30 minutes helping us define what that should look like?"*

This is research, not a pitch. But it plants the seed for the next product, and turns paying customers into co-designers of what comes next.

**Do not build F&B Intelligence until you have ≥5 paying hotel customers on Nocturn AI and at least one design partner actively engaged on F&B.**

---

### Task S5.5 — Unit Economics Review (Monthly, Starting Month 2)
**Permanent ritual · Non-negotiable**

Track monthly:

| Metric | Formula | Target |
|--------|---------|--------|
| MRR | Sum of monthly subscriptions | RM 15,000 by Day 90 |
| COGS/property | Cloud + LLM + WhatsApp per property | < RM 400 |
| Gross Margin | (MRR - COGS) / MRR | > 75% |
| CAC | Total sales+marketing spend / new customers | < RM 3,000 |
| LTV | ARPU / monthly churn rate | > RM 15,000 (10 months at RM 1,500) |
| LTV:CAC | LTV / CAC | ≥ 3:1 |
| Monthly Churn | Cancelled / total at start of month | < 5% |
| Payback Period | CAC / (ARPU × gross margin) | < 6 months |

**If LTV:CAC falls below 3:1, stop scaling acquisition.** Fix either CAC (sales efficiency) or LTV (retention). Do not pour fuel on a leaking engine.

---

### Task S5.6 — Churn Analysis Protocol
**After every churned customer**

Within 48 hours of a churn:
1. Call the contact. Do not email. Ask: "Help me understand — what didn't work?"
2. Document the reason in the churn log (product gap / price / budget / competitor / hotel closed / relationship)
3. If it is a product reason, log it as a bug with priority = critical
4. If 3 customers cite the same reason, stop everything else and fix it

**Failure lesson:** *From building-successful-saas-guide.md — ">5% monthly churn = product problem, not sales problem. >20% annual = red flag." At 5 customers, one churn is 20% monthly churn. Treat every loss as a signal.*

---

## Marketing Alignment Track
### Runs in parallel with all phases above

> These tasks are owned by the marketing function (or Ahmad Basyir acting as both). They must be synchronized with product milestones per the handoff sequence in `alignment.md`.

---

### M1 — Bilingual Claim Audit (Day 3 — after Task P0.6)
After the BM end-to-end test:
- If pass rate ≥ 90%: update website to "Fully bilingual — English and Bahasa Malaysia" with specifics
- If pass rate 70–89%: update to "English and Bahasa Malaysia supported" (no superlative)
- If pass rate < 70%: remove bilingual claim from homepage hero until fixed. Replace with "English and Bahasa Malaysia — in development."

**Never claim a capability the product cannot demonstrate on demand.**

---

### M2 — ROI Calculator Alignment (Day 5 — after confirming revenue formula)
Verify the website ROI calculator uses the exact formula from `revenue_methodology.md`:
```
Estimated Revenue = (leads × property ADR × 1 night) × 20%
```

If the calculator shows different math, fix it. Add a transparency footnote: *"Based on RM [ADR] ADR, 1 night average stay, 20% conversion rate. Actual results vary. See [Vivatel case study] for real data."*

---

### M3 — Replace Unverified Case Study (Day 28 — after Vivatel data)
- Replace "Bukit Bintang City Hotel: RM 12,400 recovered" with Vivatel's real numbers
- If Vivatel does not consent to be named, use "Kuala Lumpur 3-star hotel" anonymized version
- Add the exact formula and dashboard screenshot to prove the numbers

---

### M4 — Add Staff Workflow to Features Page (Day 10)
The website describes the AI concierge experience but not what staff actually do. Add a section to the Features page:

**"From AI-captured lead to confirmed booking"**
1. Guest messages after hours → AI captures name, intent, contact
2. 7am: GM receives daily email with all leads
3. Staff opens lead in dashboard → sees conversation context
4. Staff calls the guest → has everything they need
5. Booking confirmed → marks lead as converted in dashboard

This is the workflow that Shamsuridah and Zul actually care about. The AI is the night-shift worker. The staff are the closers.

---

### M5 — "Live in 48 Hours" Proof Point (Day 48)
Once the second property is onboarded in 48 hours (not 7 days), publish the onboarding timeline as a specific claim: *"Connected in 48 hours — we've done it. Here's how."*

---

### M6 — LinkedIn Authority Content (Weeks 2–8, 2×/week)
Ahmad Basyir's LinkedIn is the distribution channel until paid marketing begins. Post:

**Week 1–2:** "What I learned from talking to 8 hotel GMs about after-hours bookings" (interview insights, no product pitch)
**Week 3:** "What the data from our first 30 days with a Vivatel pilot showed us" (real numbers, with permission)
**Week 4:** "Why we deleted our own dashboard and rebuilt it from scratch" (the product iteration story)
**Week 5:** "The moment a GM said 'this is working'" (Zul's quote, if permitted)
**Week 6+:** Weekly "Numbers from the dashboard" format — share one surprising metric from the week

**Rule:** Every post must have a specific number or specific quote. Opinions without evidence are noise.

---

### M7 — Website "Pilot" CTA Optimization (Day 20)
Replace the generic "Start Free Pilot" CTA with social proof-loaded language:
- Before: "Start Free Pilot — No Credit Card Required"
- After: "Start Free Pilot — Like Vivatel KL. See Your Numbers in 7 Days."

A/B test if traffic warrants it. If not, just update the copy.

---

## The North Star Metric and Weekly Review

Track one number above all others. Not MRR. Not leads captured. Not NPS.

**North Star Metric: Number of properties where the GM opened the dashboard this week.**

This measures active value delivery, not just payment. A GM who opens the dashboard 5× a week is renewing. A GM who has not logged in for 10 days is churning.

### Weekly Review Ritual (Every Monday, 30 minutes)

1. How many properties had ≥3 dashboard logins this week?
2. How many leads were captured across all properties?
3. How many daily emails were opened?
4. What is the pipeline status? (conversations, pilots, converting, paying, churned)
5. What did we learn from customer conversations this week?
6. What is the one thing that most threatens the first/next payment?

**This meeting is more important than any standup.** The answers tell you where to spend the next week.

---

## The 90-Day Scorecard

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| 7 Phase 0 blockers resolved | Day 5 | — |
| Vivatel KB populated and tested | Day 7 | — |
| Vivatel live (Twilio sandbox) | Day 8 | — |
| Vivatel live (Meta WhatsApp) | Day 12 | — |
| First real guest AI conversation | Day 8–9 | — |
| First real lead captured | Day 8–14 | — |
| Daily email live in production | Day 3 | — |
| 3 active pipeline conversations | Day 14 | — |
| Vivatel pilot review call | Day 30 | — |
| Vivatel case study published | Day 30 | — |
| First invoice issued | Day 35 | — |
| First payment received | Day 49 | — |
| Second property pilot live | Day 45 | — |
| Third property pilot live | Day 55 | — |
| Second paying customer | Day 60 | — |
| Third paying customer | Day 70 | — |
| MRR: RM 4,500 (3 properties) | Day 70 | — |
| MRR: RM 10,500 (7 properties) | Day 80 | — |
| MRR: RM 15,000 (10 properties) | Day 90 | — |

---

## What to Stop Doing (Immediately)

These activities consume time without moving toward the first invoice. Stop them until the scorecard above reaches RM 10,000 MRR:

| Activity | Why to Stop |
|----------|-------------|
| Working on Stripe billing integration | Manual invoicing works for 10 properties. Stripe is for 50+. |
| Building the Supabase Auth flow (self-serve signup) | You are provisioning accounts manually. Self-serve signup is not needed yet. |
| Building staff RBAC / `staff_tier` permission system | Zero tenants to enforce permissions for. Build when a tenant asks for it. |
| Building the `/portal` tenant management layer | Use admin scripts until Phase 4. Do not build self-service for 1 tenant. |
| Building the `/welcome` onboarding wizard | Manual onboarding is fine for 3 pilots. Build when it bottlenecks Phase 4. |
| Building the support chatbot | Zero support tickets. Build when you have customers who need support. |
| Optimizing the application intake form | Zero inbound traffic to justify it. Build when marketing drives leads. |
| Adding new AI capabilities (voice, image, etc.) | Customers haven't asked. Fix what's broken before adding what's new. |
| Refactoring existing code | Ship, then refactor. Not the reverse. |
| Exploring Opportunity #1 (F&B Intelligence) | Right direction, wrong timing. Get 5 paying customers on Opp #2 first. |

**What IS worth building now (internal portal — Phase 1.5):**

| Activity | Why It Belongs Now |
|----------|-------------------|
| Maintenance mode toggle (`/admin/system`) | You need a graceful way to pause the platform without alarming Vivatel's guests mid-conversation |
| Service health dashboard (`/admin/health`) | You need to know before Vivatel does when Supabase/Gemini/WhatsApp is degraded |
| Announcements system | When scheduled maintenance is needed, you need a way to tell tenants via in-app banner — not a personal WhatsApp message |

These are SheersSoft **operational tools**, not customer-facing features. They protect the quality of the pilot and every subsequent relationship. Build them between Vivatel going live and onboarding the second property.

---

## The Single Most Important Insight from the Research

From `building-successful-saas-guide.md`, the principal engineer's warning:

> *"The company graveyard is full of technically excellent products that solved problems no one would pay for. The difference between a successful company and a corpse is not the quality of the code — it is the answer to one question: 'Did you talk to customers before you built it, and did you keep talking to them while you built it?'"*

Eight interviews validated this product. Zul, Shamsuridah, Bob, and the others named a real problem. The product is built. The AI works. The infrastructure is live.

The only remaining obstacle between this and a paying customer is execution.

**Talk to 3 customers this week. Fix the 7 blockers. Get Vivatel live.**

---

*Cross-referenced with docs/product_gap.md, docs/prd.md v2.0, docs/opportunity_2_playbook.md, docs/gap_analysis.md, docs/alignment.md, docs/building-successful-saas-guide.md, docs/revenue_methodology.md, docs/sales_demo_script.md. All dollar amounts in MYR. All dates relative to 17 Mar 2026.*
