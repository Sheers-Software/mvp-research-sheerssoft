# Zero to First Payment: Complete Workflow
## Nocturn AI — SheersSoft · Updated 18 Mar 2026

---

## Why This Document Exists

Getting paid is not a product problem. The product is built, deployed, and working on GCP Cloud Run. The AI engine answers WhatsApp messages in multiple languages. The dashboard shows revenue numbers. The daily email fires at 7am. The infrastructure is solid. None of that is what stands between SheersSoft and a paying customer right now.

What stands between now and the first invoice is a set of execution gaps that live entirely outside the codebase. There is no pilot agreement template. There is no KB intake form. There is no discovery call script. There is no CRM, not even a spreadsheet with the warm pipeline tracked. There is no pitch deck. There is no invoice template. There is no demo environment with seeded data. There is no LinkedIn presence posting to the people who make hotel buying decisions. The website has a fabricated case study with unverified numbers. None of these are engineering problems. All of them are execution problems.

This document exists because a brilliant product with no sales process does not get paid. Every stage of the customer journey — from the moment a GM first hears the name "Nocturn AI" to the moment a bank transfer arrives — requires specific artifacts, scripts, templates, and rituals that do not yet exist. This document names every one of them, tells you what to do, and tells you in what order. It is written for someone who has never seen the project. Pick it up and execute. The one number that matters is days to first invoice, and the target is 21.

---

## The Customer Journey Map

```
STRANGER ──► AWARE ──► INTERESTED ──► CONSIDERING ──► PILOT AGREED ──► PILOT LIVE ──► PROOF ──► PAYING CUSTOMER
   │            │           │               │                │               │           │            │
   │         Sees a       Visits         Has demo         Signs           AI handles    Numbers      Invoice
   │         LinkedIn     website,       call, gets       pilot           real guests   in hand      paid
   │         post or      asks for       proposal,        agreement,      every day,   confirm      within
   │         gets         more info      thinks about     goes live       GM opens     ROI          14 days
   │         WhatsApp     or books       it              on WhatsApp      dashboard                of verbal
   │         outreach     demo                                            + widget                  yes
   │
   Stage 1   Stage 2      Stage 3        Stage 3b         Stage 4         Stage 5      Stage 6     Stage 7-8
```

The journey is not linear. A GM can move from Aware to Considering in a single demo call. A pilot can stall at Stage 5 for 90 days if there is no conversion push. The stages below address every transition point and every place deals die.

---

## Stage 1: Awareness
### Goal: A hotel GM discovers Nocturn AI exists.

---

### What Must Happen

1. Ahmad Basyir publishes content on LinkedIn that hotel GMs and Revenue Managers in Malaysia actually read.
2. Direct WhatsApp outreach to the 8 interview contacts who already validated the problem.
3. Bob is asked explicitly for the SKS Hospitality referral. Use his name.
4. Website hero messaging matches the 60-second pitch, not a generic "AI chatbot" tagline.
5. A demo video (2–3 minute screen recording) exists for sharing after initial interest.
6. The "Bukit Bintang City Hotel" case study is marked as a benchmark, not a verified result, before any outreach begins.

---

### Required Artifacts

| Artifact | Status | Needed By |
|----------|--------|-----------|
| LinkedIn content calendar (4 weeks) | Missing | Day 3 |
| 3 draft LinkedIn posts (weeks 1–2) | Missing | Day 4 |
| WhatsApp outreach message templates | Missing | Day 1 |
| Demo video (screen recording, 2–3 min) | Missing | Day 5 |
| Website hero copy aligned to pitch | Exists but misaligned — fix unverified case study | Day 2 |
| Bob referral ask message | Missing | Day 1 |

---

### Channels

- LinkedIn (Ahmad Basyir personal account — not a company page yet)
- Direct WhatsApp to warm contacts
- Email to interview contacts who provided email
- Referral through Bob → SKS Hospitality

---

### Current Status

- LinkedIn: account exists, zero content published
- Website: sheerssoft.com exists, unverified "Bukit Bintang City Hotel" case study with RM 12,400 number must be corrected before any outreach
- Warm pipeline of 8 interview contacts is untouched
- Bob has not been asked to facilitate the SKS introduction
- No demo video exists

---

### Owner

Ahmad Basyir

---

### LinkedIn Content — Weeks 1–4 Specific Posts

**Week 1, Post 1 (Day 3–4):**
Title: "What 8 hotel GMs in KL told me about after-hours bookings"
Content: Share the single most surprising insight from the interview research without naming products or companies. Example: "Seven of the eight GMs I interviewed said the same thing unprompted: 'I check my phone at 11pm because I know inquiries are coming in and nobody is answering.' One of them hasn't taken a full weekend off in 18 months because of this." End with a question: "If you're a GM in Malaysia, is this your reality too?"

**Week 1, Post 2 (Day 6–7):**
Title: "The cost of an unanswered WhatsApp at 9pm"
Content: Walk through the revenue math. 30 inquiries/day, 30% after hours = 9 missed per night. At RM 230 ADR, 20% convert. That is RM 414 per night falling on the floor. RM 12,420 per month. Not dramatic. Just arithmetic.

**Week 2, Post 3 (Day 10–11):**
Title: "We just launched a pilot at a KL hotel — here's what we're watching"
Content: Post the first real data point from the Vivatel pilot. Even if it is one conversation, one lead, one correct BM response — make it specific and honest. "Day 3 of our pilot. 14 WhatsApp inquiries after 6pm. 14 captured. 2 leads with names and booking intent. One was in Bahasa Malaysia asking about a weekend package. The AI answered correctly in 30 seconds." Do not exaggerate.

**Week 2, Post 4 (Day 13–14):**
Title: "Why I stopped calling it a chatbot"
Content: Explain the distinction between a scripted chatbot and an AI that reads context, speaks BM, and knows when to hand off to a human. The word "chatbot" carries a specific connotation — scripted, frustrating, dead-end. Reframe it. "It's a concierge, not a chatbot. The difference is that it knows what it doesn't know."

---

## Stage 2: Interest
### Goal: GM wants to learn more and agrees to a conversation.

---

### Website: What the Landing Page Must Communicate

The homepage must answer five questions in the first 10 seconds:
1. What does it do? — "AI concierge that captures hotel inquiries 24/7, especially after hours"
2. For whom? — "3–4 star hotels in Malaysia using WhatsApp and direct bookings"
3. What does it cost? — "30-day free pilot, then RM 1,500/month. No contract."
4. Does it work? — Real numbers from real pilots (replace unverified benchmark by Day 28)
5. How do I try it? — "Start your free pilot" CTA — one button, no form friction

The current hero says "Every Unanswered Inquiry Is a Booking Your Competitor Gets." This is correct and should stay. What must change is the case study section and the CTA flow.

---

### Outreach Message Templates

**WhatsApp — Interview follow-up (to the 8 known contacts):**

> Hi [Name], Ahmad Basyir here from SheersSoft. We spoke in [month] about after-hours inquiry handling at [property]. We've just launched a pilot at Vivatel KL — the AI is live, handling WhatsApp inquiries 24/7 in English and BM. I'm reaching out to a small number of hotels I respect before I expand further. Would you be open to a 20-minute call to see if it makes sense for [property]? No pitch, just a quick walkthrough of the pilot results.

**WhatsApp — Bob referral ask:**

> Bob, we've launched our hotel AI pilot at Vivatel. Getting strong early signals. I remember you mentioned SKS Hospitality might be facing similar after-hours booking problems. Is that still the case? If so, can I use your name when I reach out to them? Happy to loop you in on the intro if you prefer.

**Email — Shamsuridah (Novotel KLCC):**

> Subject: Nocturn AI pilot — 30 days in at Vivatel KL
>
> Hi Shamsuridah,
>
> Ahmad Basyir from SheersSoft. We spoke in February about the volume of after-hours WhatsApp inquiries your team was managing manually — 200–300 messages, about 30% handled by hand.
>
> We launched a pilot at Vivatel KL [X] weeks ago. The AI is handling all after-hours inquiries in under 30 seconds, in both English and Bahasa Malaysia, and capturing leads with full context before your team starts the day.
>
> I promised to come back with real numbers before asking for anything. I have them now. Would 20 minutes this week work for a quick walkthrough?
>
> Ahmad Basyir
> SheersSoft | Nocturn AI
> +60 [number]

---

### Inbound Inquiry Handling Process

Response time standard: reply within 2 hours during business hours (9am–6pm MYT), within 4 hours outside. This is not a suggestion. A GM who fills a form on a website and gets a reply 3 days later does not become a customer.

If someone books a demo through Calendly or the website contact form:
1. Confirm receipt immediately by WhatsApp (more personal than email)
2. Send a confirmation email with the call link and one preparatory question: "What's your biggest challenge with after-hours bookings right now?"
3. Review their property website before the call — know their room types and approximate ADR

---

### Demo Booking

Use Calendly. Set up a 30-minute block. Do not use a custom form for now — one question only: "Property name and location." Do not ask for budget or company size at this stage. That friction costs you more than it helps.

---

## Stage 3: Consideration (Discovery + Demo)
### Goal: GM understands product value and agrees to a pilot.

---

### Discovery Call Script (Before Demoing Anything)

Duration: 15 minutes before showing the product. Do not skip this. The demo lands 10× better when you understand their specific pain first.

**Questions to ask in order:**

1. "How many WhatsApp inquiries do you typically get in a day?"
2. "What time does your reservations desk close?"
3. "What happens to messages that come in after that?"
4. "Have you lost bookings because of this — or do you just suspect you have?"
5. "When a guest sends 'got room?' at 11pm, what's the current process?"
6. "Who on your team would use a tool like this day-to-day?"
7. "What's your average room rate?" (This is for the ROI calculation — ask directly)
8. "If you could solve one thing about your current inquiry process, what would it be?"

Listen for: volume of inquiries, after-hours percentage, their current workaround (personal phone, WhatsApp groups, nothing), who owns the decision (GM vs ownership group), and any urgency signals ("we've been looking for something like this").

---

### Demo Environment Setup Requirements

Before any external demo, the demo environment must have:
- At least 30 days of seeded conversation data showing realistic volume
- 3–5 lead examples with names, phone numbers, booking intent populated
- Analytics showing: 80+ inquiries handled, 15+ after-hours, 10+ leads captured, RM 1,200+ estimated revenue recovered
- At least 2 conversations in Bahasa Malaysia
- One handoff example showing the staff reply flow working end-to-end
- Daily email format visible (screenshot or live if possible)

If the demo data shows zero leads and zero revenue on a blank screen, the product looks like it does not work. Seed it before every demo.

---

### Demo Script — 5-Minute Walkthrough Narrative

**Minute 0–1: The problem, their words**
> "Before I show you anything — you told me your desk closes at [time] and you get about [X] messages a night after that. Let me show you what happened at Vivatel last night."

Open the dashboard. Point to the KPI cards.

> "47 inquiries handled by AI. 21 after 6pm. 14 leads with names and phone numbers. RM 3,220 in estimated recovered revenue. All while your team was offline."

Pause. Let them read the numbers.

**Minute 1–2: The AI in action**
> "Here is one of last night's conversations."

Open a conversation thread. Show a guest asking about room availability in BM or English, the AI responding in under 30 seconds with correct rate information, capturing the guest name and phone number, and offering to confirm a booking.

> "Notice it answered in Bahasa Malaysia. It knew the correct rate from the KB we built with the hotel's own information. It asked for the guest's contact. All before 7am."

**Minute 2–3: What your team sees every morning**
> "At 7am, your reservations manager gets this email."

Show the daily email format: summary stats, list of leads with names and phone numbers.

> "They arrive at work with a call list. They know which leads are warm. They call. They close."

**Minute 3–4: Staff reply and handoff**
> "When the AI cannot handle something — a group booking, a complaint, a negotiation — it flags it for your team."

Open the conversations view, show a handoff. Show the reply box.

> "Your team types here. The guest receives it on WhatsApp in seconds. The AI never pretends to be human — it introduces itself and then hands off cleanly."

**Minute 4–5: The math**
> "You said you get about [X] inquiries per day with roughly [Y%] after hours. At your ADR of RM [Z], our estimate is [calculated number] in recovered revenue per month. The Starter plan is RM 1,500/month. That is [multiplier]× covered by one confirmed booking from a lead the AI captured. The pilot is free for 30 days. You pay nothing to find out if the math is right."

Then stop talking.

---

### ROI Calculation Live During Demo

Formula to run in front of them:
```
Monthly estimated recovery = (daily inquiries × after-hours %) × 30 days × ADR × 20%
Example: 30 inquiries × 30% = 9/night × 30 days = 270 leads/month × RM 230 × 20% = RM 12,420
```

Use their actual ADR. Do not use Vivatel's numbers for a different property — run it live with their inputs. If they say "I don't know my ADR" use RM 200 as a conservative floor. If they say "we have 50 rooms and 40% occupancy," you can back-calculate.

---

### Follow-Up Email Template (Same Day, Within 2 Hours of Demo)

> Subject: Nocturn AI — next step for [Property Name]
>
> Hi [Name],
>
> Thank you for the time today. Quick recap:
>
> Based on your [X] daily inquiries at [Y%] after-hours rate and RM [Z] ADR, we estimate RM [calculated] in monthly recovered revenue against the RM 1,500 Starter subscription — that's [multiplier]× ROI.
>
> The pilot is 30 days, free, no credit card. Here is what the first week looks like:
> - Day 1: I send you a KB intake form (15 minutes of your time)
> - Day 2: We build the property knowledge base
> - Day 3: WhatsApp connected via Twilio sandbox, live immediately
> - Day 7: First data in your inbox
>
> Do you want to start this week?
>
> If you'd like to see the numbers from our Vivatel pilot before deciding, I can send those across.
>
> Ahmad Basyir
> SheersSoft | Nocturn AI
> +60 [number]

---

### Pilot Proposal Template Structure

**Page 1 — Cover**
- "Nocturn AI — 30-Day Free Pilot Proposal"
- Property Name, prepared for [GM name]
- Date
- Prepared by: Ahmad Basyir, SheersSoft

**Section 1 — Your Current Situation (1 paragraph)**
Summarize what you heard in the discovery call. Name their specific problem. This shows you listened.
> "[Property] currently receives approximately [X] WhatsApp inquiries per day, with [Y%] arriving after [time] when the reservations desk is closed. Current process: [their answer — e.g., 'front desk checks personal phone at night']. Estimated lost bookings per month: [your estimate, conservatively]."

**Section 2 — What the Pilot Delivers**
- 30 days of AI handling all WhatsApp inquiries 24/7
- Bilingual responses (English + Bahasa Malaysia)
- Daily 7am email report to the GM with leads, revenue estimate
- Staff dashboard access — all conversations and leads visible
- Human handoff for complex inquiries — staff replies from dashboard
- No credit card, no contract, walk away at Day 30 if the numbers don't justify it

**Section 3 — Your ROI Estimate**
Show the calculation with their actual inputs. Be conservative. Put the RM 1,500/month subscription next to the estimate. Show the multiplier.

**Section 4 — What We Need From You**
- 90 minutes with [Zul equivalent] for the KB session (room types, rates, FAQ, hours)
- Your WhatsApp Business number (or we set up a test number)
- Web team contact to add the widget script (5 minutes of their time)

**Section 5 — Timeline**
```
Day 0 (today): Pilot agreement signed
Day 1: KB session (90 minutes with your team)
Day 2: SheersSoft builds property knowledge base
Day 3: WhatsApp connected, widget installed, AI live
Day 7: First weekly report, your team reviews
Day 30: Pilot review call — decide to continue or walk away
```

**Section 6 — After the Pilot**
Starter RM 1,500/month or Professional RM 3,000/month. Month-to-month. No lock-in.

**Section 7 — Signatures**
- SheersSoft signatory and details
- Hotel property name, GM name, date

---

### Handling Objections at Consideration Stage

**"I need to think about it":**
> "Completely understood. What's the one thing you'd need to be more confident before starting a free pilot? It costs you nothing to try."

If they still hesitate: "Can I send you our Vivatel pilot results? It's one page. If the numbers don't convince you, I won't follow up."

**"I need to show my GM / owner":**
> "Of course. Can we get 20 minutes with them this week? I can bring the numbers and answer their questions directly. Alternatively, I can send a one-page summary you can share — it takes 3 minutes to read."

Do not let a deal die in a forwarded email chain. Get in the room.

---

## Stage 4: Decision (Pilot Agreement)
### Goal: Pilot starts. Property is live. First guest is served.

---

### Pilot Agreement — 1-Page Template Structure

**PILOT AGREEMENT**
Between Sheers Software Sdn Bhd (Company No: [SSM]) and [Hotel Property Name]
Date: [DD/MM/YYYY]

**1. Pilot Period**
30 calendar days commencing [start date]. Free of charge. No payment obligation during the pilot period.

**2. Services Provided**
- Nocturn AI concierge — 24/7 WhatsApp + web chat inquiry handling
- Property-specific knowledge base built by SheersSoft
- Daily GM report (email, 7am MYT)
- Staff dashboard access
- Human handoff capability

**3. Data Ownership**
All conversation data, lead data, and inquiry data belongs to [Hotel Property Name]. SheersSoft processes this data solely for the purpose of providing the service. Data is stored on GCP infrastructure in the asia-southeast1 region. SheersSoft will not share, sell, or use this data for any other purpose.

**4. PDPA Compliance**
SheersSoft is PDPA compliant. Guest data collected during the pilot (name, phone, email, booking intent) is encrypted at rest and in transit. A Data Processing Agreement is available on request.

**5. Hotel Obligations**
- Provide property information for knowledge base construction (one 90-minute session)
- Connect WhatsApp Business number as directed by SheersSoft
- Install widget script tag on property website (optional, 5 minutes)
- Designate one point of contact (reservation manager or equivalent)

**6. Limitations**
SheersSoft is not responsible for lost bookings resulting from incorrect information provided during the KB session. The AI does not fabricate rates — it quotes only from the approved KB. If the KB is incomplete, the AI defers to human handoff.

**7. After the Pilot**
Either party may terminate at the end of the pilot with no obligation. If the hotel chooses to continue, a monthly service agreement will be issued at the agreed subscription rate.

**8. Confidentiality**
Both parties agree to keep the terms of this agreement confidential. SheersSoft may reference the hotel by name in case studies only with written permission (WhatsApp message is sufficient).

**Signed:**
[SheersSoft] _________________ Date: _______
[Hotel] ______________________ Date: _______

---

### KB Intake Form — Exact Questions

Send this form 24 hours before the KB session, or work through it live in the 90-minute call. Every question must be answered before the KB is considered complete.

**Section A: Property Basics**
1. Property full name (as guests know it)
2. Address (full, including postcode)
3. How to get there from KLCC / Bukit Bintang / KL Sentral (directions)
4. Nearest MRT/LRT station and walking time
5. Check-in time, check-out time
6. Early check-in policy (cost, availability by request, or guaranteed?)
7. Late check-out policy (cost, availability, cut-off time)

**Section B: Room Types**
For each room type: Name, description (size, bed type, view, features), rack rate, weekend rate, any current packages or promotions. Confirm which rates the AI is allowed to quote.

**Section C: Facilities**
8. Swimming pool (hours, heated, indoor/outdoor, children allowed?)
9. Gym (hours, equipment, membership or included?)
10. Restaurant name, hours, cuisines offered, room service hours
11. Meeting rooms (capacity, AV, pricing per half-day/full-day)
12. Parking (valet, self-park, daily rate, EV charging?)
13. WiFi (free? speed? login method?)
14. Airport transfer (offered? cost? how to book?)

**Section D: Policies**
15. Cancellation policy (standard, non-refundable rates)
16. Pet policy
17. Smoking policy
18. Extra bed / cot availability and cost
19. Group booking minimum (rooms) and process
20. Corporate rate availability — how do guests inquire?

**Section E: FAQ (From Zul's Memory)**
21. What are the 5 most common questions you get on WhatsApp?
22. What are the 3 most common complaints?
23. Is there anything the AI should NEVER say or promise?
24. What should the AI say when a guest asks for a discount?
25. What is your standard response to "got room?"

**Section F: Escalation Rules**
26. When should the AI always hand off to a human? (e.g., complaints, groups over 10, VIP guests)
27. Who is the on-call contact for urgent handoffs? (name, WhatsApp number)
28. What hours is a human available to respond to handoffs?

---

### Property Configuration Checklist (SheersSoft Internal)

Before calling a property "live":

**Phase 0–3: Admin-led (manual, SheersSoft does it all)**
- [ ] Property record created via `/admin/onboarding` form (or admin script)
- [ ] ADR set correctly (verify with GM)
- [ ] Operating hours configured (affects "after-hours" classification)
- [ ] Notification email(s) set (GM + reservations manager)
- [ ] Timezone confirmed: Asia/Kuala_Lumpur
- [ ] WhatsApp provider set: "twilio" (sandbox first) or "meta" (after approval)
- [ ] KB ingested: minimum 30 KBDocument entries (via admin script until `/portal/kb` is live)
- [ ] KB tested: 10 representative questions answered correctly, no hallucinations
- [ ] Widget snippet generated and provided to IT contact
- [ ] Staff accounts created: GM + reservations manager minimum (via `/admin/tenants/[id]` invite)
- [ ] Dashboard login tested: GM logs in via magic link, lands on `/dashboard`, sees KPI cards
- [ ] Test WhatsApp conversation: send 5 messages, verify responses
- [ ] Test handoff: trigger handoff, verify staff notification, test staff reply from dashboard
- [ ] Daily email: trigger manually, verify arrives in GM's inbox
- [ ] FERNET key active: verify lead phone number encrypted in DB after capture
- [ ] Pilot agreement signed and filed

**Phase 4+: Tenant self-service (once `/portal` and `/welcome` are live)**
- [ ] Owner invited via `/admin/onboarding` → receives magic link → lands on `/welcome`
- [ ] Owner completes onboarding wizard: confirms property → uploads KB → tests channel → invites staff → goes live
- [ ] SheersSoft reviews KB quality before activating (or provides async feedback via announcements)
- [ ] `/dashboard` login verified by owner (KPI cards visible from Day 1)

---

### WhatsApp Setup Steps

**Track A — Twilio Sandbox (Live Immediately, Use for Pilot Start)**
1. Log in to Twilio console
2. Create a new Twilio number or use existing sandbox number
3. Set Property.whatsapp_provider = "twilio" and Property.twilio_phone_number in database
4. Configure webhook: Twilio → HTTPS POST → `https://nocturn-backend-owtn645vea-as.a.run.app/api/v1/channels/whatsapp/twilio`
5. Provide the sandbox number to the hotel team with join instructions
6. Test: send "Hi, got room?" — verify AI responds in < 30 seconds

**Track B — Meta Cloud API (Apply Immediately, Approve in 1–7 Days)**
1. Request Meta Business Manager access from hotel's Facebook Page admin
2. Submit WhatsApp Business number for verification via Meta Business Manager
3. Once approved: set Property.whatsapp_provider = "meta" and configure WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_TOKEN
4. Set webhook: Meta → HTTPS POST → `https://nocturn-backend-owtn645vea-as.a.run.app/api/v1/channels/whatsapp/meta`
5. Verify webhook token with Meta
6. Cut over from Twilio to Meta once approved and tested

---

### Widget Installation One-Pager (For Hotel IT Team)

**Title: Installing the Nocturn AI chat widget — 5 minutes**

Add this single line of code before the closing `</body>` tag on your website:

```html
<script src="https://nocturn-frontend-owtn645vea-as.a.run.app/widget.js"
  data-property="[your-property-slug]"
  data-theme="dark">
</script>
```

Replace `[your-property-slug]` with the slug provided by SheersSoft (e.g., `vivatel-kl`).

That is all. No account required. No configuration. No dependencies. Works on WordPress, Wix, Squarespace, and any HTML site.

To verify installation: visit your website and look for the chat bubble in the bottom-right corner. Send a test message. You should receive a reply within 30 seconds.

Contact Ahmad Basyir on WhatsApp at +60 [number] if there are any issues.

---

### Staff Training Session Outline (60 Minutes)

**Minutes 0–10: Why we're here**
Explain the product in one sentence: "The AI handles all WhatsApp and web inquiries automatically. Your job is to review leads in the morning and close the ones worth calling." Show the KPI cards on the dashboard home. Let them read the numbers.

**Minutes 10–20: The morning routine**
Walk through the daily workflow:
1. Open dashboard (bookmark the URL)
2. Check KPI cards — how many inquiries, how many leads
3. Open Leads view — filter by "New"
4. For each new lead: read the conversation summary, decide call priority
5. Call the lead, update status to "Contacted"

**Minutes 20–30: Managing live conversations**
Show the Conversations view. Walk through:
- How to see the full conversation thread
- How to identify a handoff request (AI flags it)
- How to type a reply and send it from the dashboard
- What the guest sees on their WhatsApp when you reply

**Minutes 30–40: The daily email**
Show the email format. Confirm the email is arriving in the right inbox. Walk through how to read it. Emphasize: the email is the product's morning briefing. If it is not being opened, leads are being missed.

**Minutes 40–50: When to call us**
Give Ahmad Basyir's WhatsApp number. Scenarios when to call immediately:
- The AI gives a wrong rate
- A guest is complaining and escalating
- The system is not responding
- A lead looks like a large group booking

**Minutes 50–60: Questions and test run**
Send a live test message to the hotel WhatsApp. Walk through the full flow in real time. Answer questions. Leave with their WhatsApp contact confirmed.

---

### Go-Live Checklist

Run this on the day the pilot officially starts:

- [ ] Property configuration complete (from checklist above)
- [ ] Pilot agreement signed
- [ ] KB session complete, knowledge base ingested and tested
- [ ] WhatsApp live (Twilio sandbox at minimum)
- [ ] Widget installed on hotel website
- [ ] GM dashboard login confirmed working
- [ ] Staff training session completed
- [ ] Ahmad Basyir's WhatsApp number given to GM and reservations manager
- [ ] First test message sent and verified end-to-end
- [ ] Daily email triggered and confirmed arriving in GM's inbox
- [ ] Calendar reminder: 48-hour check-in call booked
- [ ] Calendar reminder: 7-day check-in call booked
- [ ] Calendar reminder: 30-day pilot review call booked

---

## Stage 5: Pilot Running (30 Days)
### Goal: AI handles real guests. GM sees value every day.

---

### Daily Monitoring Checklist (15 Minutes Every Morning)

Pull up the dashboard before 9am:

- [ ] How many conversations happened overnight?
- [ ] Were any conversations flagged for handoff? If yes, are they resolved?
- [ ] Were there any AI responses that look wrong, tone-deaf, or incomplete? (Spot-check 3–5 conversations)
- [ ] Did the daily email fire? (Check Cloud Scheduler logs if not received by GM)
- [ ] Were any new leads captured? Check for data quality (name, phone captured correctly)
- [ ] Any WhatsApp messages from Zul or hotel staff about the system?
- [ ] Check for any error logs in GCP (Cloud Run logs — filter for ERROR level)

Log anything unusual. Fix KB errors same day.

---

### KB Update Protocol

When the AI gives a wrong or incomplete answer:

1. Identify the question type (rate query, facility question, direction question, policy question)
2. Determine root cause: missing KB entry vs wrong KB entry vs AI misinterpreted correct KB
3. If missing: add the correct information to the KB via admin script
4. If wrong: correct the existing KBDocument entry
5. If AI misinterpreted: refine the prompt or add a more explicit KB entry
6. Test the fix: send the same question via test WhatsApp, verify corrected response
7. Log the change in the KB change log (date, what was wrong, what was fixed)

Turnaround: same-day fix for any factual error. Same-day fix for any response that could mislead a guest about rates or availability.

---

### Weekly Check-in Call Script (Day 7, Day 14, Day 21)

Duration: 30 minutes. Do not shorten.

**Opening (2 minutes):**
> "Before I show you any numbers, I want to hear from you first. How has the first week felt from your team's perspective?"

Listen. Do not interrupt.

**Review the numbers together (10 minutes):**
Pull up the dashboard together (screen share or in person). Walk through:
- Total inquiries handled
- After-hours breakdown
- Leads captured — read through 2–3 specific ones
- Revenue estimate

**Ask the five questions (10 minutes):**
1. "What was the most useful thing the AI did this week?"
2. "What did it get wrong or miss — be specific if you can"
3. "Did the daily email arrive every morning?"
4. "Did any guest complain about the AI?"
5. "If we closed the pilot today, what would you miss?"

Document answers verbatim. These are primary research for the case study and for the conversion call.

**Close (5 minutes):**
Confirm any KB fixes needed. Confirm next week's touchpoint. Do not pitch the paid plan until Day 28.

---

### Weekly Data Tracking Template (Columns)

Maintain this spreadsheet from Day 1:

| Week | Total Inquiries | After-Hours | Leads Captured | Leads Called | Leads Converted | Est. Revenue (RM) | Daily Email Opens | KB Updates Made | Issues Logged |
|------|----------------|-------------|----------------|--------------|-----------------|-------------------|-------------------|-----------------|---------------|
| W1   |                |             |                |              |                 |                   |                   |                 |               |
| W2   |                |             |                |              |                 |                   |                   |                 |               |
| W3   |                |             |                |              |                 |                   |                   |                 |               |
| W4   |                |             |                |              |                 |                   |                   |                 |               |
| Total|                |             |                |              |                 |                   |                   |                 |               |

Data sources:
- Inquiries/After-Hours/Leads: `GET /api/v1/analytics/dashboard` or `GET /api/v1/analytics/daily`
- Email opens: SendGrid dashboard (if tracking enabled)
- Conversions: updated manually as hotel staff reports booking confirmations

---

### First-48-Hour Crisis Protocol

If something breaks in the first 48 hours:

**Scenario A: AI gives a factually wrong rate**
1. Fix the KB entry within 1 hour
2. WhatsApp Zul directly: "We just found an error in the rate information. Fixed now. Here is what was wrong and what we corrected."
3. Check if the wrong rate was sent to any guest — if yes, a human follow-up may be needed
4. Do not wait to be asked. Proactive disclosure builds trust.

**Scenario B: WhatsApp stops responding**
1. Check Cloud Run logs immediately
2. Check Twilio or Meta webhook delivery logs
3. If backend is down: restart Cloud Run service from GCP console
4. WhatsApp Zul within 15 minutes: "We're aware of a technical issue. Estimated resolution: [time]. In the meantime, your team should monitor WhatsApp directly."
5. Never leave a hotel without a response plan for downtime.

**Scenario C: Zul reports a guest complaint about the AI**
1. Ask for the conversation ID or approximate time
2. Review the conversation in full
3. Determine if the AI was at fault or if the guest had unrealistic expectations
4. If AI at fault: fix immediately, apologize to Zul, offer a remediation
5. Document what triggered the complaint — it is likely a KB gap or edge case worth addressing before the next property

---

### Proactively Sharing Wins with GM

Do not wait for them to notice good results. Send them via WhatsApp when you see something notable:

> "Zul — just spotted this in last night's conversations. Guest asked in BM about a weekend package at 11:30pm. AI answered correctly, captured name and phone. Lead in your dashboard now. [screenshot]"

> "Week 2 update: 43 inquiries handled, 18 after hours, 12 leads captured. Your team has been very active on the call-backs — 8 leads updated to 'Contacted' already. Solid week."

Frequency: at least 2 proactive messages per week during the pilot. These moments build the case for renewal without ever asking for money.

---

### Re-Engagement Protocol (If GM Goes Silent)

If no dashboard logins for 5+ days and no replies to check-in messages:

**Day 5 of silence — WhatsApp:**
> "Zul — just checking in on the pilot. Noticed we haven't had a chance to review this week. The AI handled [X] inquiries overnight. Worth 10 minutes to look at the leads together?"

**Day 8 of silence — Call:**
Call directly. "I wanted to make sure everything is working well on your end. Is there anything about the system that is not meeting expectations?"

**Day 12 of silence — Decision point:**
> "Zul — I want to be direct. If the pilot is not adding value, I'd rather know now so we can either fix it or close it honestly. What would it take for this to be useful to your team?"

A silent GM is usually a busy GM or a GM who has doubts they have not voiced. Surface the doubt. A stated objection can be addressed. Silence cannot.

---

## Stage 6: Evidence Capture
### Goal: Numbers in hand that prove ROI.

---

### 30-Day Pilot Report Template

```
NOCTURN AI — 30-DAY PILOT REPORT
[PROPERTY NAME] | [START DATE] – [END DATE]
Prepared by SheersSoft | Nocturn AI

─────────────────────────────────────────────────────────
SUMMARY
─────────────────────────────────────────────────────────
Total WhatsApp + web inquiries handled by AI:    [X]
After-hours inquiries captured (post-6pm):       [Y] ([Y/X × 100]%)
Leads captured (name + contact + intent):        [Z]
Estimated revenue recovered:                     RM [A]
  (Formula: Z leads × RM [ADR] ADR × 20% conversion)
Staff cost savings (AI handling):                RM [B]
  (Formula: X inquiries × 0.25 hrs × RM 25/hr)
Total value demonstrated:                        RM [A+B]

Monthly subscription cost:                       RM 1,500
ROI multiplier:                                  [A+B / 1,500]×

─────────────────────────────────────────────────────────
WEEK-BY-WEEK BREAKDOWN
─────────────────────────────────────────────────────────
          W1      W2      W3      W4      Total
Inquiries  [  ]    [  ]    [  ]    [  ]    [  ]
After-Hrs  [  ]    [  ]    [  ]    [  ]    [  ]
Leads      [  ]    [  ]    [  ]    [  ]    [  ]
Revenue    [RM ]   [RM ]   [RM ]   [RM ]   [RM ]

─────────────────────────────────────────────────────────
3 CONVERSATIONS THAT MATTERED
─────────────────────────────────────────────────────────
[Date, time] — Guest inquired about [room type] at [time] in [language].
AI responded in [X] seconds with correct rate. Guest provided name and
phone. Lead status: [Contacted / Converted / Lost].

[Repeat for 2 more notable conversations]

─────────────────────────────────────────────────────────
ISSUES RESOLVED DURING PILOT
─────────────────────────────────────────────────────────
[Date]: [What was wrong] → [How it was fixed]
[Date]: [What was wrong] → [How it was fixed]

─────────────────────────────────────────────────────────
RECOMMENDATION
─────────────────────────────────────────────────────────
Based on 30 days of data, continuing on the Starter plan (RM 1,500/month)
delivers approximately [A+B / 1,500]× return on investment.

For [Property Name]'s volume profile, we recommend:
  ☐ Starter Plan — RM 1,500/month (current pilot configuration)
  ☐ Professional Plan — RM 3,000/month (add email handler, weekly summary)

─────────────────────────────────────────────────────────
```

---

### Case Study One-Pager Template

```
┌──────────────────────────────────────────────────────────────┐
│  NOCTURN AI — CUSTOMER RESULT                                │
│  [Property Name], [City]                                     │
│  [Month] [Year] — 30-Day Pilot                               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  THE CHALLENGE                                               │
│  [Property Name] was receiving [X] WhatsApp inquiries per    │
│  day, with [Y%] arriving after [time] when the reservations  │
│  desk was closed. Leads went unanswered until morning.       │
│                                                              │
│  THE RESULT (30 days)                                        │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  [X]     │  │  [Y]     │  │  [Z]     │  │  RM [A]    │  │
│  │Inquiries │  │After-Hrs │  │  Leads   │  │ Recovered  │  │
│  │Handled   │  │Captured  │  │Captured  │  │ (est.)     │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
│                                                              │
│  "[Zul's direct quote — one sentence about what changed      │
│   for their team or their mornings]"                         │
│  — [Name], [Title], [Property Name]                          │
│                                                              │
│  HOW IT WORKS                                                │
│  Setup: 48 hours · KB session: 90 minutes                    │
│  Monthly cost: RM 1,500 · No long-term contract              │
│                                                              │
│  Ready to see your numbers?                                  │
│  sheerssoft.com | +60 [number]                               │
└──────────────────────────────────────────────────────────────┘
```

---

### How to Get Zul's Quote

Send this by WhatsApp at Day 25 of the pilot:

> "Zul — we're putting together a one-page summary of the pilot results to share with other hotels. Would you be okay with being quoted? Just one sentence — something like what changed for your team in the last month. I'll share the draft with you before anything goes out. No pressure at all."

If he agrees, follow up with: "What would you say in your own words about what the AI has done for your mornings / your team / your bookings?"

Use his exact words. Do not clean them up too much. Authentic quotes outperform polished marketing copy.

---

### Data Sources: API Endpoints to Numbers

| Number Needed | API Endpoint | Notes |
|--------------|-------------|-------|
| Total inquiries handled | `GET /api/v1/analytics/dashboard` | `total_conversations` field |
| After-hours inquiries | `GET /api/v1/analytics/dashboard` | `after_hours_recovered` field |
| Leads captured | `GET /api/v1/analytics/dashboard` | `leads_captured` field |
| Revenue recovered (est.) | `GET /api/v1/analytics/dashboard` | `revenue_recovered` field |
| AI handled % | `GET /api/v1/analytics/dashboard` | `ai_handled_rate` field |
| Week-by-week data | `GET /api/v1/analytics/daily?from=&to=` | Filter by date range |
| Individual leads | `GET /api/v1/leads` | Status, name, created_at |
| Conversation details | `GET /api/v1/conversations/{id}` | Full thread for case study |

---

## Stage 7: Conversion (Pilot Review to Close)
### Goal: Verbal agreement to pay.

---

### Pilot Review Call Structure (45-Minute Agenda)

Attendees: Ahmad Basyir + Zul + ideally the GM or hotel owner. Book this at Day 28. Do not let it drift to Day 35.

**Minutes 0–5: Show the numbers first, words second**
Open the 30-day pilot report. Put the numbers on screen. Say nothing until they have read them. Then: "Before I say anything, what stands out to you?"

**Minutes 5–15: Walk through 2–3 specific conversations**
Not statistics — stories. "This one was at 11:47pm on a Tuesday. Guest asked in BM about a family package. The AI answered, asked for their name and phone. The lead was in your dashboard at 7am. Did your team call this one?"

**Minutes 15–25: Ask Zul to narrate**
"Zul, what was different this month compared to the month before we started?" Let him speak. Document exactly what he says. This is your case study material and your conversion argument.

**Minutes 25–35: Present the two options**
Use the pricing table below. Anchor on Professional first.

**Minutes 35–45: Handle objections, close**
Ask for the business. Stop talking.

---

### The Full Pitch Script

> "[Property Name] received [X] WhatsApp inquiries last month. [Y] of those came in after [time] — when your team was offline. The AI handled all of them. [Z] became leads with names and phone numbers. Based on your RM [ADR] ADR, we estimate RM [calculated] in recovered revenue.
>
> Your subscription would be RM 1,500 per month. The first confirmed booking from an AI-captured lead pays for roughly [divide RM 1,500 by (ADR × 20%)] months of the subscription.
>
> The Starter plan is RM 1,500/month. No contract. Month-to-month. We invoice you on the 1st. You can cancel anytime.
>
> Do you want to continue?"

Then stop. Do not add qualifiers. Do not pre-empt objections. Ask the question and wait.

---

### Pricing Comparison Table

| | **Starter** | **Professional** |
|---|---|---|
| **Monthly price** | RM 1,500 | RM 3,000 |
| **WhatsApp lines** | 1 | 2 |
| **Web chat widget** | Included | Included |
| **Email auto-handler** | Not included | Included |
| **Conversations/month** | Up to 500 | Up to 2,000 |
| **Daily GM report (7am)** | Included | Included |
| **Weekly summary** | Not included | Included |
| **Staff dashboard** | Full access | Full access |
| **Human handoff** | Included | Included |
| **Bilingual (EN + BM)** | Included | Included |
| **Support** | Email (48h response) | Priority WhatsApp (4h response) |
| **Properties** | 1 | Up to 3 |
| **Best for** | Single-property pilot converting to paid | Revenue-focused GM, or 2–3 properties |
| **Contract** | Month-to-month | Month-to-month |

Recommend Starter for Vivatel if it is a single property with < 1,000 inquiries/month. Recommend Professional if the GM is actively tracking revenue or has a second property in mind.

---

### Objection Handling — 5 Most Common

**1. "Can we continue free for another month?"**
> "I understand — you want more data. Here is my honest position: we have been investing heavily in your property — KB updates, daily monitoring, being available on WhatsApp. That investment makes sense in a paid relationship, not an indefinite free one. What I can offer is 50% off the first paid month — RM 750 — so you have one more month of data at minimal cost while we formalize the relationship."

**2. "It's expensive for a chatbot"**
> "I hear that. It is not a chatbot — chatbots follow scripts and dead-end conversations. Nocturn captured [Z] leads last month and estimated RM [A] in recovered revenue. If even one of those leads converts to a booking, the subscription pays for itself [RM 1,500 / (ADR × 20%)] times over. You are not paying RM 1,500 for software. You are paying for the equivalent of a night-shift reservation agent who never sleeps and never misses a message."

**3. "I need to check with my GM / owner"**
> "Absolutely — this is the right decision for them to be part of. Can I be on that call? I can walk through the numbers directly and answer any questions they have. Would this week or next week work for a 20-minute call with them?"

**4. "The system made some mistakes"**
> "Yes — and we fixed every one of them, same day, without being asked. Here are the [X] KB updates we made over the 30 days. That is normal in month one. The KB is now [X] entries richer because of real conversations with your guests. Month two will be sharper. Month three will be almost invisible in terms of errors. What specific mistakes are you still concerned about?"

**5. "We're evaluating other solutions"**
> "I'd like to understand what you're comparing. Most alternatives either don't support Bahasa Malaysia natively, require 3-month onboarding, or require your IT team to do a full integration. What specifically are they offering that you're not seeing here? I'd rather address it directly than let it be an invisible objection."

**The silence rule:** After "Do you want to continue?" — stop talking. The next person to speak loses leverage. This is not a metaphor. It is the single most important moment in the conversion call. Silence.

---

### When They Say Yes

1. Confirm the plan verbally: "So we're going with Starter at RM 1,500/month, starting [date]?"
2. Say: "I'll send the invoice today. Payment by bank transfer within 14 days."
3. Note: nothing changes technically — pilot configuration becomes the paid configuration
4. Send invoice within 24 hours (see Stage 8)
5. Send a WhatsApp confirmation: "Great speaking today. Invoice on the way. We're continuing — same setup, nothing changes. I'll keep the daily monitoring going."

---

### When They Say No

1. Ask: "Help me understand — what was the deciding factor?"
2. Write down the exact words. Do not paraphrase.
3. Ask: "Is this a permanent no, or is it a timing issue?"
4. If timing: "When would be a good time to revisit? Can I follow up in [month]?"
5. Ask: "Would you be comfortable referring one hotel who might benefit from this? Even anonymously — I just want to talk to the right people."
6. Do not burn the relationship. End with: "Completely understood. The pilot data is yours to keep. If circumstances change, I'd love to revisit."
7. Use the pilot data (anonymized, with permission) for the next pitch immediately.

---

## Stage 8: Payment
### Goal: Invoice paid. Customer confirmed.

---

### Invoice Template Structure

```
INVOICE

Sheers Software Sdn Bhd
Company No: [SSM Registration Number]
[Registered Address]
Email: [billing@sheerssoft.com]
SST Registered: [Yes/No — check current SST registration status]

Invoice No: NSS-2026-001
Invoice Date: [DD/MM/YYYY]
Due Date: [DD/MM/YYYY + 14 days]

Bill To:
[Hotel Property Name]
[Full Address]
Attn: [GM Name or Finance Contact]

─────────────────────────────────────────────────────
Description                     Qty    Rate      Amount
─────────────────────────────────────────────────────
Nocturn AI — Starter Plan        1    RM 1,500   RM 1,500.00
(April 2026)
AI inquiry handling, leads
dashboard, daily GM report,
WhatsApp + web chat, 1 property
─────────────────────────────────────────────────────
                                         Subtotal: RM 1,500.00
                                         SST (0%): RM 0.00
                                            TOTAL: RM 1,500.00

Payment Method: Bank Transfer
Bank: [Maybank / RHB / CIMB]
Account Name: Sheers Software Sdn Bhd
Account Number: [account number]
Reference: INV-NSS-2026-001 + [Property Name]

Please use the invoice number as the payment reference.
For questions: [billing@sheerssoft.com] or +60 [number]
─────────────────────────────────────────────────────
```

---

### Invoice Timing and Follow-Up Cadence

| Day | Action |
|-----|--------|
| Day 0 (verbal yes) | Issue invoice. Send by email + WhatsApp. |
| Day 3 | WhatsApp: "Just checking the invoice arrived safely. Any questions on the payment details?" |
| Day 11 | Email: "Invoice INV-NSS-2026-001 due in 3 days. Bank details are in the invoice. Let me know if any issues." |
| Day 14 (due date) | WhatsApp: "Invoice due today. Happy to confirm receipt once the transfer goes through." |
| Day 17 (3 days overdue) | Call directly. "Wanted to follow up on the invoice. Has there been a hold-up on the finance side?" |
| Day 21 | Email from billing address + call. Escalate if needed. |

Do not wait silently for payment. Payment follow-up is not rude. It is normal business.

---

### What Triggers Paid Plan vs Pilot Plan

Nothing changes technically. The pilot database configuration becomes the paid configuration. The only change is billing status. Technically: update `Property.plan_tier` from pilot to "starter" or "professional" in the database once invoice is paid. This is a single SQL update. No re-provisioning required.

---

### Bookkeeping Setup Recommendation

Use Wave App (wavefinancial.com) — free for invoicing and basic bookkeeping. It handles:
- Invoice creation and PDF export
- Payment tracking (mark as paid when transfer confirmed)
- Basic P&L reporting
- Invoice templates with bank details

Do not set up QuickBooks or Xero until you have more than 10 customers or a finance person. Wave is sufficient for the first year.

---

### What to Send on First Payment Received

WhatsApp to GM (same day payment is confirmed):

> "Payment received — thank you. You're our first paid customer and I want you to know we're taking that seriously. Your dashboard is fully active. Daily report continues at 7am. I'll be in touch on [first of month] with a quick monthly summary. Any questions anytime — just WhatsApp me directly."

This message sets the tone for the paid relationship. It acknowledges the milestone, confirms continuity, and establishes the communication cadence.

---

## Stage 9: Retention and Expansion
### Goal: Customer renews. Refers others.

---

### Monthly Check-in Cadence

| Month | Activity | Duration |
|-------|----------|----------|
| Month 1 (30 days after paid) | Monthly review call: show trends, ask about staff adoption | 30 min |
| Month 2 | WhatsApp summary + ask about upsell interest | 15 min |
| Month 3 | Quarterly review: full numbers, upsell conversation if appropriate | 45 min |
| Ongoing | Monthly WhatsApp update with one key metric highlight | 5 min |

Rule: no paying customer goes more than 30 days without a direct touchpoint from Ahmad Basyir.

---

### When to Upsell to Professional Tier

Triggers that indicate readiness for Professional (RM 3,000/month):
- Property is hitting the 500 conversation/month limit consistently
- GM asks about email inquiry handling (Professional includes email auto-handler)
- Hotel acquires or manages a second property
- GM mentions they are sharing the dashboard with ownership group (Weekly Summary helps here)
- Hotel ADR is above RM 350 (Professional ROI multiplier is stronger at higher ADR)

Upsell script:
> "Over the last [X] months, you've been averaging [Y] conversations/month. You're close to the Starter limit. Before you hit it, I wanted to flag that the Professional plan at RM 3,000 includes email handling, up to 3 properties, and a weekly summary that you could share with ownership. Based on your ADR, the additional RM 1,500/month is covered by roughly [calculate] leads per month. Want to see the comparison?"

---

### How to Ask for Referrals

At Month 2, after two successful monthly reports:

> "Zul — you've been with us for two months now. The numbers are solid and your team has been great to work with. I have a favour to ask: is there a GM or reservations manager you respect at another property who might be facing the same after-hours problem? I'm not asking you to sell anything — just an introduction. I'll do the rest. One name."

Then stop talking.

If they hesitate: "You can also just forward them my number with a one-line message. That's all I need."

Referral from a satisfied customer converts at 10× the rate of cold outreach. One introduction from Zul is worth 20 LinkedIn messages.

---

### F&B Intelligence Introduction (Day 60+)

For paying customers at 60+ days with good data:

> "We're exploring a new product called F&B Intelligence — essentially helping hotels understand which F&B services are driving revenue and which aren't. You mentioned [month] that the restaurant data is opaque. Would you be willing to spend 30 minutes helping us define what that should look like for a property like yours?"

This is research framing, not a sales pitch. It plants the seed, engages the customer as a co-designer, and gives you validated demand before writing a line of code. Do not build F&B Intelligence until at least 5 paying customers on Nocturn AI and one hotel actively co-designing the feature.

---

### Churn Early Warning Signals

Monitor these weekly:

| Signal | Threshold | Response |
|--------|-----------|----------|
| Dashboard login frequency | No logins for 10 days | WhatsApp check-in immediately |
| Daily email open rate | Below 50% for 2 consecutive weeks | Call to discuss — is the email landing in spam? |
| Lead follow-up rate | Staff not updating lead statuses for 7+ days | Training refresher — are they using the dashboard? |
| Unprompted complaints | Any | Address same day |
| No response to monthly check-in | 48 hours | Escalate to phone call |
| Invoice payment delay | > 5 days past due | Call immediately |

---

### Save Protocol (Customer at Risk)

1. Call, do not email. "I want to understand what's happening before making any assumptions."
2. Ask directly: "Is the value not there, or is something else going on?"
3. Diagnose: is it product (AI quality), relationship (communication), budget (can't justify), or operational (team not using it)?
4. For product issues: offer a 2-week intensive KB improvement sprint at no extra cost
5. For budget issues: offer a one-month pause instead of cancellation
6. For operational issues: schedule a re-training session
7. If they are determined to cancel: "Understood. Can I ask one final question — what would have made you stay?" Write down the answer. It is more valuable than the subscription.

---

## Gap Analysis: What Doesn't Exist Yet

### Product Engineering Gaps (Re-prioritized — 18 Mar 2026)

The product portal architecture (`docs/portal_architecture.md`) defines three portals: `/dashboard` (property ops), `/admin` (SheersSoft internal), `/portal` (tenant management). Priorities below reflect GTM sequencing — only build what unlocks the next payment.

| Gap | Portal | Blocks | Priority | GTM Phase |
|-----|--------|--------|----------|-----------|
| Dashboard home → KPI cards (rebuild) | `/dashboard` | Every demo and every daily GM session | **P0 — build now** | 0 |
| Staff reply box in conversations | `/dashboard` | Vivatel UAT sign-off | **P0 — build now** | 0 |
| Daily email in production (Cloud Scheduler) | Backend | Ongoing daily value delivery | **P0 — build now** | 0 |
| FERNET encryption key in Secret Manager | Backend | PDPA compliance for contract signing | **P0 — build now** | 0 |
| "Lost" status filter in leads | `/dashboard` | Complete lead lifecycle | P0 — quick fix | 0 |
| Maintenance mode toggle | `/admin` | Safe multi-tenant ops during Vivatel pilot | **P1 — before second tenant** | 1.5 |
| Service health dashboard | `/admin` | Proactive ops — know before tenants know | P1 | 1.5 |
| Announcements system | `/admin` + `/dashboard` | Notify tenants of maintenance without WhatsApp | P1 | 1.5 |
| KB management UI | `/portal` | Tenant self-service (reduces SheersSoft KB sessions) | P2 — before Phase 4 | 4 |
| `/portal` tenant home | `/portal` | Owner self-service (multi-property view) | P2 | 4 |
| `/welcome` onboarding wizard | `/welcome` | Automated onboarding — removes per-tenant engineering time | P2 | 4 |
| Team management UI | `/portal` | Staff invites without SheersSoft involvement | P2 | 4 |
| AI insights page | `/dashboard` | Delight — helps GM improve AI performance | P3 | 5 |
| Channel reconfiguration UI | `/portal` | Self-service channel updates | P3 | 5 |
| Billing portal (Stripe customer portal) | `/portal` | Automated subscription management | P3 | 5 |

**Do not build P2/P3 items before having 2 paying customers.** Manual admin scripts and SheersSoft-led sessions work fine until then.

### Sales, Ops, and Legal Gaps

| Gap | Type | Blocks | Priority | Effort | Owner |
|-----|------|--------|----------|--------|-------|
| Pitch deck (5 slides) | Sales | Every demo | P0 | 1 day | Ahmad Basyir |
| Pilot agreement template | Legal/Ops | Contract signing | P0 | Half day | Ahmad Basyir |
| KB intake form | Ops | Vivatel KB session | P0 | 2 hours | Ahmad Basyir |
| Property configuration checklist | Ops | Go-live | P0 | 2 hours | Ahmad Basyir |
| Widget installation guide (1-pager) | Ops | Hotel IT setup | P0 | 1 hour | Ahmad Basyir |
| Staff training guide / script | Ops | Staff adoption | P0 | 2 hours | Ahmad Basyir |
| Go-live checklist | Ops | Go-live | P0 | 1 hour | Ahmad Basyir |
| Demo environment with seeded data | Product | Every demo | P0 | Half day | Ahmad Basyir (Dev) |
| Discovery call script | Sales | Demo prep | P0 | 1 hour | Ahmad Basyir |
| Demo script (5-min narrative) | Sales | Every demo | P0 | Half day | Ahmad Basyir |
| Follow-up email template (post-demo) | Sales | Deal velocity | P0 | 1 hour | Ahmad Basyir |
| Follow-up email template (post-pilot-W1) | Sales | Retention | P1 | 1 hour | Ahmad Basyir |
| Follow-up email template (post-pilot-W2) | Sales | Retention | P1 | 1 hour | Ahmad Basyir |
| Pre-conversion call prep template | Sales | Conversion | P1 | 1 hour | Ahmad Basyir |
| Pilot proposal template | Sales | Post-demo | P0 | 2 hours | Ahmad Basyir |
| 30-day pilot report template | Sales | Conversion | P0 | 2 hours | Ahmad Basyir |
| Case study one-pager template | Sales/Marketing | Pipeline | P1 | 2 hours | Ahmad Basyir |
| Pricing sheet (standalone PDF) | Sales | Leave-behind | P1 | 1 hour | Ahmad Basyir |
| Invoice template | Finance | Getting paid | P0 | 1 hour | Ahmad Basyir |
| Wave App / bookkeeping setup | Finance | Payment receipt | P0 | 2 hours | Ahmad Basyir |
| CRM / pipeline tracker (spreadsheet) | Ops | Pipeline visibility | P0 | 1 hour | Ahmad Basyir |
| LinkedIn content calendar (4 weeks) | Marketing | Awareness | P1 | Half day | Ahmad Basyir |
| Outreach message templates (WhatsApp + email) | Sales | Awareness | P0 | 2 hours | Ahmad Basyir |
| Demo video (2–3 min screen recording) | Marketing | Async demos | P1 | Half day | Ahmad Basyir |
| ROI calculator (standalone, shareable) | Sales | Demo reinforcement | P1 | Half day | Ahmad Basyir (Dev) |
| Data processing agreement (PDPA) | Legal | Contract signing | P1 | 1 day (lawyer) | Ahmad Basyir |
| Service agreement template (post-pilot) | Legal | Month 2+ billing | P1 | Half day | Ahmad Basyir |
| Referral ask template | Sales | Pipeline expansion | P2 | 30 min | Ahmad Basyir |
| P0.6 BM test execution (50 questions) | Product | UAT confidence | P0 | Half day | Ahmad Basyir |
| P0.7 Vivatel KB population | Product | Everything | P0 | 1 day | Ahmad Basyir + Zul |
| Website case study updated to verified data | Marketing | Credibility | P0 | 1 hour | Ahmad Basyir |
| Vivatel pilot agreement signed | Legal/Sales | Pilot start | P0 | Day 1 | Ahmad Basyir + Zul |

P0 = blocks first payment. P1 = needed before second payment. P2 = needed before 5th payment.

---

## Next Phase Plan: Days 1–21

### The 21-Day Sprint: From Demo-Ready to Pilot-Live to Proof-In-Hand

---

### Week 1 (Days 1–7): Get Demo-Ready + Vivatel Live

**Updated priority order — 18 Mar 2026:** The portal architecture (`docs/portal_architecture.md`) has been finalized. Product tasks below reflect the re-prioritized build sequence: `/dashboard` (P0) → internal ops controls (P1.5) → `/portal` self-service (P2). Nothing in P2+ happens before 2 paying customers.

**Day 1 (Monday 17 Mar) — COMPLETE:**
- [SALES] Set up CRM pipeline spreadsheet with all warm contacts.
- [SALES] WhatsApp Bob — confirm SKS Hospitality referral.
- [LEGAL/OPS] Draft pilot agreement template.
- [OPS] Create KB intake form.
- [SALES] Write outreach WhatsApp message templates.

**Day 2 (Tuesday 18 Mar) — IN PROGRESS:**
- [PRODUCT] **P0.1 — Rebuild `/dashboard` home as revenue KPI page.** Delete the onboarding checklist. Show: Inquiries Handled, After-Hours Recovered, Leads Captured, Revenue Recovered (RM), AI Rate, Avg Response Time. This is the #1 priority — every demo starts here.
- [PRODUCT] Fix website: add "pilot benchmark — not verified" disclaimer to Bukit Bintang case study.
- [PRODUCT] Seed demo environment: 30-day realistic data (conversations, leads, revenue estimates).
- [SALES] Draft pilot proposal template.

**Day 3 (Wednesday 19 Mar):**
- [PRODUCT] **P0.2 — Staff reply box.** Add text input + send button below conversation thread. `POST /api/v1/conversations/{id}/messages` with `role: "staff"`. Verify staff reply arrives on guest WhatsApp.
- [PRODUCT] P0.6: Begin BM test — run first 25 questions via Twilio sandbox. Document pass/fail.
- [SALES/MARKETING] Write 3 LinkedIn posts for weeks 1–2. Schedule them.
- [SALES] Book KB session with Zul — target Day 3–5.

**Day 4 (Thursday 20 Mar):**
- [PRODUCT] **P0.3 — Daily email in production.** Add SENDGRID_API_KEY to Secret Manager. Create 4 Cloud Scheduler jobs (daily-report, followups, insights, keepalive).
- [PRODUCT] P0.6: Complete remaining 25 BM test questions. Document pass rate. Log failures.
- [SALES] Draft 5-slide pitch deck.
- [OPS] Test full demo flow end-to-end with rebuilt dashboard home.

**Day 5 (Friday 21 Mar):**
- [PRODUCT] **P0.4 — FERNET key.** Generate + add to Secret Manager. Redeploy. Verify encryption active on new leads.
- [PRODUCT] **P0.5 — Lost status filter** (10-min fix in leads page).
- [PRODUCT] P0.7: KB session with Zul. Ingest all 28 questions → KB entries.
- [FINANCE] Set up Wave App. Create invoice template.

**Day 6 (Saturday 22 Mar):**
- [PRODUCT] KB testing: send 10 test messages to Vivatel number. Fix any hallucinations same day.
- [OPS] Complete property configuration checklist for Vivatel.

**Day 7 (Sunday 23 Mar) — or Monday if weekend:**
- [PRODUCT] Vivatel go-live on Twilio sandbox. All checklist items verified.
- [OPS] Staff training session with Zul + front desk team (60-minute walkthrough).
- [LEGAL/OPS] Pilot agreement signed.
- [PRODUCT] 48-hour supervised monitoring begins.

---

### Week 2 (Days 8–14): Pilot Live + Outreach Active

**Days 8–9:**
- [PRODUCT] 48-hour supervised launch. Monitor every conversation in real time. Log any AI error. Fix KB same day. Respond to Zul within 15 minutes during business hours.
- [SALES] Send first proactive win message to Zul if anything notable happens in first 48 hours.

**Day 10:**
- [SALES/MARKETING] Publish first LinkedIn post (scheduled from Day 3). Check engagement. Reply to all comments within 2 hours.
- [OPS] Daily monitoring checklist begins (15 minutes every morning from this day forward).

**Day 11:**
- [SALES] Send outreach message to Shamsuridah (Novotel KLCC) — use email template in Stage 2 above.
- [SALES] Send outreach to Simon (Ibis Styles KL) — WhatsApp or email.

**Day 12:**
- [SALES] Follow up Bob for SKS referral confirmation. If he has confirmed, send the intro message to SKS contact using Bob's name.
- [PRODUCT] Meta Cloud API: submit Vivatel WhatsApp Business number for Meta verification (if not done on Day 1). Approval timeline: 1–7 days.

**Day 13:**
- [SALES/MARKETING] Publish second LinkedIn post.
- [SALES] Follow-up WhatsApp to Shamsuridah and Simon (if no reply to Day 11 outreach). No email goes unanswered for more than 48 hours.

**Day 14:**
- [SALES] First week check-in call with Zul (30 minutes — use script in Stage 5 above). Document answers verbatim.
- [SALES] Update pipeline CRM spreadsheet with current status for all 4+ contacts.
- [OPS] Complete weekly data tracking template (Week 1 row). Pull numbers from dashboard API.

---

### Week 2.5 (Days 10–14): Internal Controls Sprint — Run Parallel with Pilot Monitoring

> **Why now:** Vivatel is live. You are monitoring 48 hours. Sales outreach is active. The pilot is working. Now build the tools that let SheersSoft operate safely when a second and third tenant is added — without babysitting every interaction. These are not customer features. They are operator tools.

**Day 10–11:**
- [PRODUCT] **I1.1 — Maintenance mode.** Backend: `PUT /api/v1/superadmin/maintenance` writing `maintenance_mode` key to `system_config`. Middleware: skip on `/admin/*`, `/api/v1/internal/*`, `/api/v1/system/info`. Frontend: toggle on `/admin/system` page. Maintenance banner in `/dashboard/layout.tsx`. *Effort: ~1 day.*

**Day 12–13:**
- [PRODUCT] **I1.2 — Service health dashboard.** `GET /api/v1/superadmin/service-health` — asyncio parallel checks for all 9 services (DB, Redis, Supabase, Gemini, OpenAI, Anthropic, SendGrid, WhatsApp, Stripe). 3s timeout per check, 20s cache. Frontend: `/admin/health` status grid, 30s auto-refresh. *Effort: ~2 days.*

**Day 14–16:**
- [PRODUCT] **I1.3 — Announcements.** `announcements` table migration (add to `main.py` lifespan). CRUD endpoints. `GET /api/v1/announcements/active` (tenant-scoped). Admin composer at `/admin/announcements`. Banner strip in `/dashboard/layout.tsx`. *Effort: ~3 days.*

---

### Week 3 (Days 15–21): Evidence Building + Pipeline Moving

**Day 15:**
- [PRODUCT] Weekly data pull — Week 2 numbers. Update tracker.
- [SALES] Proactive WhatsApp update to Zul: "Week 2 update: [numbers]. Strong week."

**Day 16–17:**
- [SALES] Schedule demo calls with any warm pipeline contacts who have responded (SKS, Novotel, or Ibis). Do not demo without a discovery call first — book 45 minutes: 15 discovery + 30 demo.
- [SALES/MARKETING] Draft pilot report template (use format in Stage 6 above). This is not for Vivatel yet — it is the template ready for Day 28.

**Day 18:**
- [SALES] Conduct first warm pipeline demo if scheduled. Use the seeded demo environment. Run the 5-minute demo script.
- [SALES] Send post-demo follow-up email within 2 hours.
- [MARKETING] Publish third LinkedIn post (Vivatel pilot numbers if data is compelling — even Week 2 data is worth sharing honestly).

**Day 19–20:**
- [SALES] Second week check-in call with Zul. Continue monitoring.
- [OPS] Begin 30-day pilot report data collection — all Week 3 numbers locked in tracker.
- [SALES] Follow up SKS contact if outreach sent Day 12 has not had response.

**Day 21:**
- [SALES] Pipeline review: every contact has a status, a last touch date, and a next action with a due date. No deal is silent.
- [PRODUCT] KB update log: how many entries have been added or corrected in 3 weeks?
- [LEGAL/OPS] Data processing agreement — draft or consult lawyer this week. Needed before any customer asks.

---

## The Non-Negotiable Sequence

If you do nothing else, do these 10 things in this exact order:

1. **Create the CRM spreadsheet today (Day 1, 30 minutes).** Open Google Sheets. Five columns: Property, Contact, Status, Last Touch, Next Action. Add Vivatel, SKS, Novotel KLCC, Ibis Styles KL, and the other 4 interview contacts. This is your business, tracked in one place.

2. **WhatsApp Bob today (Day 1, 5 minutes).** "Bob — can I use your name when I reach out to SKS Hospitality? We're live with a pilot at Vivatel and getting good early results." Do not wait for the right moment. The right moment is now.

3. **Create the pilot agreement template (Day 1–2, half day).** Use the structure in Stage 4. It does not need to be reviewed by a lawyer before the first pilot. It needs to exist and be signed. Get it done.

4. **Book the Vivatel KB session with Zul (Day 1, 5 minutes).** WhatsApp him now. Book for Day 3–5. The KB session is the single most important prerequisite for going live. Nothing else matters until this is scheduled.

5. **Complete the BM test suite — all 50 questions (Day 2–3, half day).** Run every question. Document every result. If pass rate is < 80%, fix the failures before go-live. This is not optional.

6. **Populate the Vivatel KB (Day 3–5, 90 minutes + SheersSoft build day).** The session with Zul, the ingest, the testing. Do not go live without at least 30 KB entries and 10 test questions passing.

7. **Go live on Twilio sandbox with the full go-live checklist verified (Day 5–7).** Not "mostly ready." Not "close enough." Run the checklist. Every item checked. Then call it live.

8. **Run the 48-hour supervised launch (Days 7–9).** Be obsessively present. Every conversation reviewed. Every error fixed same day. This is how you retain pilots and get quotes.

9. **Set up Wave App and create the invoice template (Day 5, 1 hour).** Invoice number INV-NSS-2026-001 should be ready to send within 24 hours of Vivatel saying yes. Being unprepared to invoice loses deals at the last step.

10. **Book the Day 28 pilot review call with Zul today (Day 1, 5 minutes).** Put it on both calendars before the pilot starts. A pilot without a scheduled end date and review call is a free product with no conversion pressure. The date on the calendar is the commitment.

---

## What to Stop Doing

These activities consume time without moving toward the first invoice. Stop them until you have 10 paying customers:

| Activity | Why to Stop | When to Restart |
|----------|-------------|-----------------|
| Working on Stripe billing integration | Manual invoicing works for the first 10 customers. Bank transfer + Wave App is sufficient. | When you have 10+ paying customers and are spending > 2 hours/month on invoicing |
| Building the Supabase Auth self-serve flow | You are manually provisioning pilot accounts. There is no inbound signup traffic to justify it. | When you have a marketing channel driving inbound leads at volume |
| Improving the SuperAdmin dashboard | You are the only superadmin. Scripted provisioning takes 5 minutes. The UI takes days to build. | When you hire a second person who needs the UI |
| Building the support chatbot | Zero support tickets. The product has no customers yet. | When support ticket volume exceeds 10/week |
| Optimising the application intake form | No inbound traffic to the intake form. There is no funnel to optimise. | When paid or organic traffic drives 50+ applications/month |
| Adding new AI capabilities (voice, image, document parsing) | Your customers have not asked for these. The core WhatsApp flow is what they care about. | When a paying customer explicitly requests it and is willing to co-fund the build |
| Refactoring existing working code | The code works. Ship, learn, refactor after PMF. | After the 5th paying customer is stable and churn is < 5% |
| Exploring F&B Intelligence product development | Right direction, wrong timing. Get 5 paying customers on Nocturn AI inquiry capture first. | When 5+ paying customers are live and one actively wants to co-design it |
| Building the tenant hierarchy and multi-tenant SaaS features | Zero tenants. The data model exists — do not add to it until customers need it. | When you have 3+ properties under one hotel group that need unified billing |
| Obsessing over the website beyond fixing the unverified case study | The website is not your bottleneck. Warm outreach and demos are. Fix the case study and move on. | After you have 3 verified case studies to publish |

The test for every activity: "Does this get me closer to an invoice in the next 21 days?" If the answer is no, it does not happen before the invoice.

---

*Cross-referenced with docs/gtm_execution_plan.md, docs/product_gap.md, docs/product_context.md. All amounts in MYR. All dates relative to 17 Mar 2026 (Day 0). This document is an operational manual — read it, then close it and execute.*
