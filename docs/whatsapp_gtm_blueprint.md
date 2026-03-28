# WhatsApp GTM Automation Blueprint — Nocturn AI

**Objective**: Convert 330 cold WhatsApp leads (independent hotels in Malaysia) into 30-day free pilots.
**Target**: 15% reply rate → 5% pilot conversion → 16–17 pilots from first 330-lead batch.

---

## 0. Newbie Guide — Read This First (GM/RM Edition)

> **Who this section is for:** You've been asked to help run this WhatsApp outreach campaign. You've never set up a CRM or automation tool before. Start here. The rest of the document is the technical reference — come back to it when needed.

### What Are We Actually Doing?

We have a list of **330 hotel phone numbers**. These are real hotels in Malaysia that are losing money every month by over-relying on Agoda and Booking.com (paying 15–18% commission per booking). We want to send each of them a WhatsApp message explaining this, and invite them to try Nocturn AI free for 30 days.

That's it. Your job is to make sure the right message goes to the right hotel at the right time — and to respond quickly when a hotel replies.

### The Three Tools You'll Use (Plain English)

**HubSpot** — think of it as your contact book. Every hotel is stored here with their name, phone number, and status (e.g., "waiting to be messaged", "replied", "pilot started"). You'll check HubSpot to see who replied and what to do next.

**Make.com** — the robot that sends the messages automatically on a schedule. You won't need to touch Make.com day-to-day unless something breaks. The technical team sets this up once.

**Wati** — this is the WhatsApp Business inbox. Every message you send and receive shows up here. Think of it like WhatsApp Web but for a business account, with a proper inbox shared by the team.

### Your Daily Routine (15–30 min/day)

**Morning (10 min):**
1. Open Wati. Check for any overnight replies (hotels sometimes reply late).
2. For each reply, go to HubSpot and mark them as "replied" (there's a checkbox field).
3. If the reply looks interested — forward to Anas immediately via WhatsApp.

**Afternoon (10–15 min):**
1. Check that today's batch of messages went out (Make.com sends automatically — you'll see them appear in Wati's Sent tab).
2. If you see any "message failed" warnings in Wati, note the hotel name and phone number. Report to Anas.
3. Respond to any replies that came in since morning.

**Friday (20 min extra):**
Fill in the weekly tracking sheet (see Section 5 — Weekly Review Metrics). Takes 5 minutes once you know the numbers to look for.

### How to Reply When a Hotel Responds

**Scenario A — They seem interested ("boleh cerita lagi?" / "what's the cost?" / "tell me more")**

Reply within 1 hour. Use this template (adapt as needed):

> Hi [Name], thanks for responding! Nocturn AI is a WhatsApp assistant that handles your guest enquiries 24/7 — so you capture bookings even after office hours without paying OTA commission.
>
> We're offering a free 30-day pilot for selected hotels this month. I can set up a quick 15-minute call to walk you through how it works. When works for you?

Then create a HubSpot task: "Follow-up call — [Hotel Name]" and assign it to Anas.

**Scenario B — They ask about price**

> The pilot is completely free — no setup fee, no monthly charge for 30 days. If you don't see a real improvement in bookings, you don't pay anything. We only charge after the pilot if you want to continue.

**Scenario C — They say "not interested" or "STOP"**

Reply: "No problem at all. Thank you for your time!" — then mark them as "opted out" in HubSpot. Do not message them again.

**Scenario D — No reply at all**

Do nothing. Make.com will automatically send a follow-up on Day 3 and Day 7. You don't need to manually chase anyone unless they show up in the "HOT" list.

### The "HOT" List — Who to Prioritize

A lead becomes HOT when:
- They reply within 10 minutes of receiving the first message (very high intent)
- They mention "owner" or "GM" in their reply (decision-maker is looped in)
- They send a phone number and ask you to call them

When a lead goes HOT: Stop everything else. Forward the full conversation to Anas. Book a call within 2 hours.

### What You Should NEVER Do

- **Never send a second message manually if Make.com already has one scheduled.** Check Make.com or ask first — doubling up looks spammy and can get the account flagged.
- **Never promise a specific price** unless Anas has confirmed it with you.
- **Never ignore a reply for more than 2 hours** during business hours. Speed of response is a key conversion signal.
- **Never message someone who has replied "STOP" or "not interested".** Mark them opted out and move on.

### What Success Looks Like

By the end of Week 4, you should have:
- 330 hotels messaged
- ~50 hotels replied (15% target)
- ~5–8 demo calls booked
- 3–5 pilots started

If reply rates are below 10% after the first 50 sends, flag it immediately — the message copy may need adjusting before we continue.

### Who to Contact for Help

| Problem | Contact |
|---|---|
| A hotel is angry or threatening | Anas immediately |
| Make.com stopped sending messages | Technical team |
| Wati inbox is showing errors | Technical team |
| A hotel wants a demo NOW | Anas immediately |
| Unsure how to reply to a specific message | Anas — forward the screenshot |

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GTM AUTOMATION STACK                          │
│                                                                       │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────────────┐  │
│  │   HubSpot   │───▶│  Make.com    │───▶│  Wati / Zoko           │  │
│  │   (CRM)     │    │  (Automation)│    │  (WhatsApp Business API)│  │
│  └─────────────┘    └──────────────┘    └────────────────────────┘  │
│         │                  │                       │                  │
│         ▼                  ▼                       ▼                  │
│   Lead scoring       Batch triggers         Approved templates        │
│   Pipeline stages    Delay logic            Reply detection           │
│   Deal creation      Human handoff          Opt-out handling          │
│   Follow-up tasks    Sequence pause         Message logs              │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Layer | Tool | Purpose |
|---|---|---|
| CRM | HubSpot | Lead storage, lifecycle stage, deal pipeline |
| Automation | Make.com | Sequence scheduling, webhook processing, pause logic |
| Messaging | Wati or Zoko | WhatsApp Business API, template management, inbox |
| Enrichment | Pre-generated CSV | `agoda_waste`, `roi_potential`, `rooms` per hotel |

### Data Flow

```
nocturn_leads_whatsapp_ready.csv (330 leads)
  → Import to HubSpot (Company + Contact)
  → Set custom property: nocturn_sequence_status = "queued"
  → Make.com: watch for status change → trigger 3-step sequence
  → Wati: send approved template (personalized per lead)
  → Reply detected → Make.com pauses sequence → HubSpot task: "Human: qualify"
  → No reply by Day 7 → sequence completes → status = "no_reply"
```

---

## 2. Batch Processing Engine

### Batch Size & Cadence

**Week 1 (Warm-up):** 10 leads/day × 5 days = 50 leads
**Week 2–4 (Steady state):** 20 leads/day × 5 days = 100 leads/week

Rationale: A new WhatsApp Business number must be warmed over the first 2 weeks. Starting at 10/day and escalating prevents the number being flagged. At steady state, 330 leads clears in ~3 weeks.

**Daily cap (hard limit):** 50 outbound template messages per day.
**Time window:** Send between 10:00 AM – 12:00 PM and 2:00 PM – 5:00 PM (Malaysia local time). Never send on Saturday after 6 PM or Sunday.

### Priority Segmentation

Pull leads in this order for each daily batch:

| Priority | Criteria | Count | Why first |
|---|---|---|---|
| 1 — Klang Valley HOT | State = Selangor/KL + agoda_waste ≥ RM10k | ~35 | Fastest to close; founder can visit in person |
| 2 — Penang HOT | State = Penang + agoda_waste ≥ RM8k | ~20 | High-density, owner-run boutiques |
| 3 — Johor HOT | State = Johor + agoda_waste ≥ RM8k | ~30 | Growing market, JB expansion |
| 4 — All remaining | Sorted by agoda_waste descending | 245 | Volume plays |

### Make.com Sequence Trigger Logic

```
Trigger: HubSpot Contact property "nocturn_sequence_status" changes to "queued"
  → Wait: randomized delay (3–7 min from trigger, not top of hour)
  → Action: Send Template 1A via Wati API
  → Set: "nocturn_last_touch_date" = today
  → Set: "nocturn_sequence_step" = 1
  → Schedule: Day 3 follow-up (Step 2)
  → Schedule: Day 7 follow-up (Step 3)

Pause Condition (check before EVERY send):
  → If HubSpot contact property "nocturn_replied" = true → STOP sequence, create HubSpot task
  → If HubSpot contact "hs_lead_status" = UNQUALIFIED → STOP
  → If "nocturn_opted_out" = true → STOP permanently
```

### Human Handoff

When Wati detects an inbound reply:
1. Wati webhook fires → Make.com scenario "Reply Handler"
2. Make.com: sets `nocturn_replied = true` in HubSpot
3. Make.com: cancels all scheduled sequence steps for this contact
4. Make.com: creates HubSpot Task → "🔥 REPLY: [Hotel Name] — qualify now" (due: same day)
5. Make.com: posts notification to Slack/WhatsApp ops group

**Rule**: A human must take over within 2 hours of a reply. Automated follow-up must never fire after a reply is detected.

---

## 3. The 3-Step "Agoda Waste" Sequence

### Template Naming Convention (Wati/Meta)

Templates must be submitted to Meta for approval before use. Name them:
- `nocturn_hook_v1` (Day 1)
- `nocturn_proof_v1` (Day 3)
- `nocturn_close_v1` (Day 7)

Use **utility** category (not marketing) where possible — lower rejection rate, higher deliverability.

---

### Step 1 — The Hook (Day 1)

**Goal**: Make the number feel real. Open a pattern interrupt around a specific RM figure.
**Tone**: Observational, not salesy. Peer-to-peer. Written like a text from a knowledgeable friend.
**Character limit**: Keep under 160 chars for the opening line.

---

**Template: `nocturn_hook_v1`**

> Hi {{1}}, saya Anas dari Nocturn AI.
>
> Hotel anda ada {{2}} bilik — jangka kami, lebih kurang *RM{{3}} sebulan* pergi ke Agoda/Booking.com dalam komisen.
>
> Ada cara nak recover balik tu tanpa tambah kos. Boleh share 2 minit?

**Variable mapping:**
- `{{1}}` = Hotel name (e.g., "The Point Boutique Hotel")
- `{{2}}` = Room count (e.g., "48")
- `{{3}}` = `agoda_waste` in RM (e.g., "9,071")

**English variant** (for hotels in Klang Valley/international flags):

> Hi {{1}}, I'm Anas from Nocturn AI.
>
> Based on your {{2}} rooms, we estimate ~*RM{{3}}/month* is going to Agoda/Booking.com in commissions.
>
> There's a way to recover a chunk of that — no extra cost to you. Worth 2 minutes?

**Why this works:**
- Opens with a specific, verifiable number (not a generic claim)
- "2 minit" is a micro-commitment, not a meeting request
- No product name-drop until they reply

---

### Step 2 — The Proof (Day 3, only if no reply)

**Goal**: Show the "10 PM problem" in action. Move from abstract to visceral.
**Condition**: Only fires if `nocturn_replied = false` AND `nocturn_opted_out = false`.

---

**Template: `nocturn_proof_v1`**

> {{1}}, nak tanya satu benda —
>
> Bila tetamu WhatsApp hotel pukul 11 malam nak tanya bilik, siapa yang reply?
>
> Kalau tiada sesiapa, tu lah "after-hours gap" — guest booking terus kat Agoda sebab takde response.
>
> Nocturn AI cover slot tu. AI jawab, capture details, secure booking — terus ke nombor WhatsApp hotel.
>
> Boleh tengok demo 60-saat? [demo.nocturnal.ai/demo]

**English variant:**

> {{1}}, quick question —
>
> When a guest WhatsApps at 11 PM asking about room availability — who replies?
>
> If no one does, they book on Agoda. That's the commission you're losing.
>
> Nocturn AI covers that window. The AI replies instantly, captures their details, and secures the booking — right on your hotel's WhatsApp number.
>
> Worth seeing a 60-second demo? [demo.nocturnal.ai/demo]

**Variable mapping:**
- `{{1}}` = Hotel name

**Note**: The demo link must be a short, fast-loading page — ideally a 90-second Loom or a CapCut clip showing the AI responding to a mock guest inquiry at 11:42 PM.

---

### Step 3 — The Permission Close (Day 7, only if no reply)

**Goal**: Make the pilot offer feel scarce and low-risk.
**Tone**: Honest, direct. Founder energy. Not corporate.

---

**Template: `nocturn_close_v1`**

> {{1}}, mesej terakhir dari saya.
>
> Kami bagi *30-hari pilot percuma* untuk 5 hotel bulan ini. Zero setup cost. Kalau ROI tak nampak dalam sebulan, kami tak charge langsung.
>
> Hotel anda ada potential RM{{2}} boleh di-recover. Kami nak buktikan dulu sebelum minta satu sen.
>
> Berminat? Reply "YA" atau call terus: +60XXXXXXXX

**English variant:**

> {{1}}, last message from me.
>
> We're onboarding *5 hotels this month* for a free 30-day pilot. Zero setup cost. If you don't see ROI in 30 days, you pay nothing.
>
> Your property has ~RM{{2}} in recoverable revenue. We want to prove it before charging a single cent.
>
> Interested? Reply "YES" or call me directly: +60XXXXXXXX

**Variable mapping:**
- `{{1}}` = Hotel name
- `{{2}}` = `roi_potential` in RM (e.g., "12,960")

**Why "5 hotels this month"**: Creates real scarcity (founder-led onboarding genuinely limits capacity). Do not increase this number until you have a repeatable onboarding process.

---

## 4. Anti-Ban & Compliance Protocols

### WhatsApp Business Policy Requirements

| Rule | Requirement | Implementation |
|---|---|---|
| Template approval | All first-touch messages must use Meta-approved templates | Submit all 3 templates via Wati console before launch |
| Opt-out | Every template sequence must include opt-out | Step 3 footer: "Reply STOP to opt out" |
| Session window | Reply-based follow-ups can use free-form text (within 24h) | After a reply, human uses session window — no template needed |
| Category | Use "Utility" not "Marketing" for lower ban risk | Frame as "account update" or "service information" |

### Frequency & Delay Rules

```
Day 1: Template 1 sent
Day 3: Template 2 sent (if no reply) — minimum 48h gap
Day 7: Template 3 sent (if no reply) — minimum 96h gap after Step 2

Intra-day randomization: ±15 minutes from scheduled time
Daily send window: 10:00 AM – 5:00 PM MYT only
Max daily sends: 50 (hard limit in Make.com)
Inter-message delay within same number: ≥ 3 minutes
```

### Account Warming (First 2 Weeks)

| Day | Max sends | Notes |
|---|---|---|
| 1–2 | 10/day | Send to known contacts first (team, partners) |
| 3–5 | 20/day | Highest-ICP leads only |
| 6–10 | 30/day | Expand to full Priority 1 batch |
| 11–14 | 40/day | Priority 1 + 2 |
| 15+ | 50/day | Full steady-state |

**Quality signal targets** (monitor weekly in Wati dashboard):
- Delivered rate: > 95%
- Read rate: > 40% (healthy for B2B cold outreach)
- Reply rate: > 15% (target)
- Block/spam report rate: < 2% (if above this, pause and review messaging)

### Opt-Out Handling

- Every Step 3 template includes: *"Reply STOP to unsubscribe."*
- Make.com reply handler checks for keyword "STOP" or "BERHENTI" → sets `nocturn_opted_out = true` → HubSpot lifecycle = UNSUBSCRIBED
- Never message an opted-out contact again (enforced at Make.com router level)

---

## 5. Operations Manual

### Week-by-Week Execution Plan

**Week 1 — Warm-up (50 leads)**
- Import batch 1: 10 Priority-1 leads/day
- Monitor: open rates, block reports, reply quality
- Set up Make.com reply handler + Slack notification
- Submit all 3 templates to Meta; expect 24–48h approval

**Week 2 — Scale (100 leads)**
- Increase to 20/day
- First replies coming in → qualify manually, book demo calls
- Review Step 1 open rate; A/B the BM vs. English variant by state
- First pilot signed → document onboarding time to validate capacity

**Week 3 — Optimize (180 leads)**
- Analyze: which state has best reply rate?
- Optimize send times (test 10 AM vs. 2 PM slots)
- Prune leads with wrong numbers (update HubSpot, reduce wasted sends)

### Manual Trigger Protocol

Situations where a human manually restarts a sequence step:

| Scenario | Action |
|---|---|
| Lead replied but then went quiet (3+ days) | Send Step 3 manually as free-form text (within original session window if < 24h, else new template) |
| Lead said "call me" but call not answered | WhatsApp follow-up: "Hi {{name}}, tried calling earlier — still happy to help. When's a good time?" |
| Lead forwarded message to "owner" | Mark as HOT, assign to founder, personalize next touch |

### HubSpot Pipeline Stages

```
Lead Stage          → HubSpot Lifecycle / Deal Stage
─────────────────────────────────────────────────────
Queued              → Lead (nocturn_sequence_status = "queued")
Step 1 Sent         → Lead (nocturn_sequence_step = 1)
Replied             → MQL (human qualifying)
Demo Booked         → SQL / Deal Stage: "Demo Booked"
Pilot Agreed        → Deal Stage: "Pilot Active"
Pilot Complete      → Deal Stage: "Closed Won" / "Churn Risk"
```

### Escalation Rules

- Any reply mentioning "owner" or "GM" → flag as HIGH priority, founder follows up personally
- Any reply in first 10 minutes of send → respond within 1 hour (highest intent signal)
- Any reply with a phone number → call within 2 hours

### Weekly Review Metrics (30-min Friday review)

| Metric | Target | Action if below target |
|---|---|---|
| Sends this week | Plan ± 10% | Check Make.com errors |
| Delivered rate | > 95% | Investigate failed numbers |
| Reply rate | > 15% | A/B test template copy |
| Demo rate (reply → demo) | > 30% | Review qualification script |
| Block/spam report | < 2% | Pause; revise templates |

---

## 6. Copywriting Personalization Matrix

Use these variants based on lead attributes in the CSV:

| State | Language | Variant |
|---|---|---|
| Johor (115 leads) | BM + EN mix | Start with BM Step 1, switch to EN if reply is in English |
| Selangor (102 leads) | EN or BM | Default EN for urban hotels, BM for suburban |
| KL (63 leads) | EN | Higher English literacy, international flags |
| Penang (49 leads) | EN | Predominantly English-speaking hotel market |

### High-ROI Personalization (for Priority-1 leads)

For any lead with `agoda_waste` > RM15,000:

Manually personalize Step 1 before sending — add one specific detail:
- Check if they're listed on Agoda with recent reviews (search hotel name)
- Reference their actual Agoda listing: *"I checked — you have 142 reviews on Agoda. That's a lot of traffic… going through OTA."*

This alone can double reply rate on top-tier leads.

---

## 7. Quick-Start Checklist

- [ ] Import `nocturn_leads_whatsapp_ready.csv` into HubSpot
- [ ] Create custom contact properties in HubSpot: `nocturn_agoda_waste`, `nocturn_roi_potential`, `nocturn_sequence_status`, `nocturn_sequence_step`, `nocturn_replied`, `nocturn_opted_out`
- [ ] Submit `nocturn_hook_v1`, `nocturn_proof_v1`, `nocturn_close_v1` to Meta via Wati for approval
- [ ] Build Make.com Scenario 1: "Sequence Starter" (trigger on status = queued)
- [ ] Build Make.com Scenario 2: "Reply Handler" (Wati reply webhook → pause + notify)
- [ ] Test end-to-end with 3 internal numbers before live launch
- [ ] Add Slack/WhatsApp ops group notification for all replies
- [ ] Set Make.com hard limit: 50 messages/day
- [ ] Set send window filter: MYT 10 AM–5 PM, Mon–Fri only
- [ ] Begin with 10 Priority-1 leads on Day 1
