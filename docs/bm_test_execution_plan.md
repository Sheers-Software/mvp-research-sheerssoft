# BM Test Execution Plan
## P0.6 — Twilio WhatsApp Setup & 50-Question Test Run
### Nocturn AI · Vivatel Kuala Lumpur · 17 Mar 2026

---

## Overview

This document covers everything from Twilio console configuration to running all 50 BM/Manglish test questions. It assumes you have purchased a Twilio number and it is not yet WhatsApp-enabled.

**Webhook URL (backend, already live):**
```
https://nocturn-backend-343745766874.asia-southeast1.run.app/api/v1/webhook/twilio/whatsapp
```

**Important:** The backend is in `ENVIRONMENT=demo`. Twilio signature verification is **skipped in demo mode** — you do not need to configure the auth token in the console for the webhook to accept messages. This makes setup significantly faster.

---

## Part 1 — Two Tracks, Pick One

Twilio has two ways to use WhatsApp. Choose based on how fast you need to test.

### Track A — Twilio WhatsApp Sandbox (Today, ~15 minutes)

Uses Twilio's shared sandbox number. Not your purchased number. Testers must "join" by sending a code first. **Good enough for the BM test.**

| Pros | Cons |
|------|------|
| Live in 15 minutes | Sandbox number (not your number) |
| No Meta approval needed | Each tester must join with a code |
| Free | Shared number across all Twilio sandbox users |
| Works immediately for testing | Cannot be used for real Vivatel guests |

### Track B — Your Purchased Number (1–7 days, depending on Meta)

Register your purchased Twilio number for WhatsApp Business API via Meta.

| Pros | Cons |
|------|------|
| Your own number — permanent | Meta approval takes 1–7 days |
| Works for real guests | Requires Facebook Business Manager |
| Production-ready | May require additional docs |

**Recommendation:** Use Track A now to run the BM test. Start Track B in parallel so the real number is ready for Vivatel go-live.

---

## Part 2 — Setup (Track A: Sandbox)

### Step 1: Enable Twilio Sandbox (5 min)

1. Log in to [console.twilio.com](https://console.twilio.com)
2. Left sidebar → **Messaging** → **Try it out** → **Send a WhatsApp message**
3. You will see a sandbox number (e.g., `+1 415 523 8886`) and a join code like `join silver-dog`
4. From your personal WhatsApp, send the join code to the sandbox number
5. Each tester/phone that will send test messages must join the sandbox

### Step 2: Configure the Webhook URL (3 min)

In Twilio Console:
1. **Messaging** → **Settings** → **WhatsApp Sandbox Settings**
2. Under **"When a message comes in"**, set:
   - URL: `https://nocturn-backend-343745766874.asia-southeast1.run.app/api/v1/webhook/twilio/whatsapp`
   - Method: `HTTP POST`
3. Leave **"Status callback URL"** blank for now
4. Click **Save**

The sandbox number for the webhook is typically `+14155238886`. Note it — this is what goes into the DB as `twilio_phone_number`.

### Step 3: Update the Vivatel Property in the DB (5 min)

Run this against the production Supabase DB via the admin API (or directly if you have DB access):

**Via the Settings API (using your dashboard login):**
```
PUT /api/v1/properties/09b0fd6a-dd3e-4138-b1df-56c2ba7ce9fc/settings
{
  "notification_email": "a.basyir@sheerssoft.com"
}
```

**The fields that need direct DB update** (no admin API endpoint yet for these — run via Supabase SQL editor):
```sql
UPDATE properties
SET
  whatsapp_provider = 'twilio',
  twilio_phone_number = '+14155238886',  -- replace with actual sandbox number
  slug = 'vivatel-kl'
WHERE id = '09b0fd6a-dd3e-4138-b1df-56c2ba7ce9fc';
```

> **Note:** The Twilio sandbox number must exactly match what Twilio sends as the `To` field in the webhook payload (after stripping the `whatsapp:` prefix).

### Step 4: Verify End-to-End Before the Test (2 min)

From your WhatsApp (already joined the sandbox), send:
```
Hello, ada bilik kosong tak?
```

Expected: AI responds in BM within 10–15 seconds.

If it responds: proceed to test.
If it doesn't respond: check Cloud Run logs at:
```
https://console.cloud.google.com/run/detail/asia-southeast1/nocturn-backend/logs?project=nocturn-aai
```

Look for: `"twilio_whatsapp_webhook"` or `"Property not found"` errors.

---

## Part 2B — Setup (Track B: Your Own Number)

### Step 1: Register Number for WhatsApp Business API via Twilio

1. Twilio Console → **Messaging** → **Senders** → **WhatsApp Senders**
2. Click **"Request Access"**
3. Select **"Use your own number"**
4. Enter your purchased Twilio number
5. You will be redirected to Facebook Business Manager to complete the WhatsApp Business API registration
6. Requirements:
   - A Facebook Business Manager account (verify at business.facebook.com)
   - Business display name (e.g., "Vivatel Kuala Lumpur" or "SheersSoft")
   - Business category
7. Approval: 1–7 business days

### Step 2: Configure Webhook (after approval)

Same as Track A Step 2, but under **Messaging** → **Senders** → select your approved number → **Configure Webhook**.

URL: same as above.

### Step 3: Update DB

```sql
UPDATE properties
SET
  whatsapp_provider = 'twilio',
  twilio_phone_number = '+601XXXXXXXXX',  -- your actual purchased number
  slug = 'vivatel-kl'
WHERE id = '09b0fd6a-dd3e-4138-b1df-56c2ba7ce9fc';
```

---

## Part 3 — Minimal KB Before Testing

The BM test will partly test language handling (should pass even without KB) and partly test factual responses (will fail without KB). Add at minimum these 6 KB entries before running — this takes 10 minutes and prevents false failures on basic factual questions.

**Add via Supabase SQL or the admin KB endpoint:**

```sql
-- Minimum viable KB for Vivatel (replace values with real ones after Zul session)
-- These are placeholders that allow the test to run without full KB population

INSERT INTO kb_documents (id, property_id, title, content, doc_type, created_at)
VALUES
(gen_random_uuid(), '09b0fd6a-dd3e-4138-b1df-56c2ba7ce9fc',
 'Check-in and Check-out Times',
 'Check-in time is 3:00 PM (15:00). Check-out time is 12:00 noon (12:00). Early check-in is subject to availability and may incur an additional charge. Late check-out can be requested at the front desk.',
 'policy', NOW()),

(gen_random_uuid(), '09b0fd6a-dd3e-4138-b1df-56c2ba7ce9fc',
 'Room Types',
 'Vivatel Kuala Lumpur offers the following room types: Superior Room (1 queen bed, city view), Deluxe Room (1 king bed, upgraded amenities), Junior Suite (separate living area, premium floor), Executive Suite (full suite, butler service available). All rooms include complimentary Wi-Fi, air conditioning, flat-screen TV, and daily housekeeping.',
 'rooms', NOW()),

(gen_random_uuid(), '09b0fd6a-dd3e-4138-b1df-56c2ba7ce9fc',
 'Room Rates',
 'Room rates start from RM 230 per night for a Superior Room. Deluxe Rooms from RM 290 per night. Junior Suite from RM 420 per night. Executive Suite from RM 650 per night. Rates include complimentary Wi-Fi. Breakfast can be added for RM 45 per person per day. Rates are subject to 10% service charge and 6% SST.',
 'rates', NOW()),

(gen_random_uuid(), '09b0fd6a-dd3e-4138-b1df-56c2ba7ce9fc',
 'Facilities and Operating Hours',
 'Swimming Pool: Open daily 7:00 AM to 10:00 PM. Fitness Centre: Open 24 hours. Restaurant (The Vivatel Brasserie): Open daily 6:30 AM to 10:30 PM. Room service available 24 hours. Business Centre: Open 8:00 AM to 9:00 PM. Meeting rooms available, capacity from 10 to 80 persons. Parking: Available on-site, RM 8 per hour or RM 30 per day.',
 'facilities', NOW()),

(gen_random_uuid(), '09b0fd6a-dd3e-4138-b1df-56c2ba7ce9fc',
 'Location and Directions',
 'Vivatel Kuala Lumpur is located in the heart of Kuala Lumpur city centre. Distance to key landmarks: KLCC Twin Towers — 1.2 km (5 minutes by Grab/taxi). Bukit Bintang shopping area — 800 metres (10 minutes walk). KL Sentral — 4 km (10 minutes by taxi/Grab). From KL Sentral: Take the KL Monorail (Maharajalela station), 2 stops to Imbi station, then 5-minute walk. Airport transfer available on request (KLIA and KLIA2). Parking entrance from Jalan Imbi.',
 'location', NOW()),

(gen_random_uuid(), '09b0fd6a-dd3e-4138-b1df-56c2ba7ce9fc',
 'Policies — Pets, Cancellation, Payment',
 'Pet policy: Pets are not allowed on the premises. Cancellation policy: Free cancellation up to 24 hours before check-in. Late cancellation or no-show will be charged one night rate. Payment: We accept Visa, Mastercard, American Express, cash (MYR), and bank transfer. For group bookings of 10 rooms or more, please contact reservations for corporate rates. For wedding and events inquiries, please contact our events team.',
 'policy', NOW());
```

> **Why minimal KB first:** Q7 (check-out time), Q34 (pool hours), Q37 (KLCC distance), Q46 (pet policy) will all FAIL without this. Adding 6 rows now saves roughly 8 false failures from KB-absence, not AI-quality issues.

---

## Part 4 — Test Execution Strategy

### The Context Problem

All messages from the same WhatsApp number go into **one conversation thread** in our system. If you send 50 questions from one phone, by Q20 the AI has the context of the previous 19 messages and may give different answers.

**Solution: Use 3 testers (phone numbers) and divide by category:**

| Tester | WhatsApp | Categories | Questions |
|--------|----------|------------|-----------|
| Tester 1 | Your personal number | A, B, C, D | Q1–Q25 |
| Tester 2 | Second phone / colleague | E, F, G, H | Q26–Q44 |
| Tester 3 | Third phone / colleague | I, J + retest fails | Q45–Q50 |

If you only have one phone: send questions in batches of 8–10, then send `"Terima kasih"` and wait 30 minutes before the next batch. The AI will naturally wind down the conversation.

### Timing for Category C (After-Hours)

Questions Q15–Q20 test after-hours behaviour. Some should be sent at specific times:

| Q | Send at | Why |
|---|---------|-----|
| Q15 | 11:30 PM | Tests genuine after-hours response |
| Q16 | Any night after 11 PM | Guest arrival scenario |
| Q17 | Any time | Just contextual; test as written |
| Q18 | 6:00 AM | Early morning tone test |

If you cannot send at exact times, send with a **note in the Q itself** (e.g., prepend "Masa ni pukul 11:30 malam, ") — the AI won't know real time but will pick up on cues in the message. This is acceptable for the test.

### Pace

- Do not send all 50 back-to-back from one phone
- Wait for the AI reply before sending the next question (avoids queue backup)
- Typical response time: 5–15 seconds
- Full test from one phone: approximately 90 minutes
- With 3 testers in parallel: approximately 35 minutes

### Recording Results

Open the dashboard → Conversations while testing:
```
https://nocturn-frontend-343745766874.asia-southeast1.run.app/dashboard/conversations
```

You will see conversations appear in real-time. You can read the AI responses here rather than switching between the dashboard and your phone.

Also have the Results Log from `bm_test_suite.md` open in a spreadsheet — paste each question number, the AI response summary, and your PASS/FAIL/PARTIAL score.

---

## Part 5 — Monitoring During the Test

### Cloud Run Logs (errors only)
```
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=nocturn-backend AND severity>=ERROR" \
  --project=nocturn-ai-487207 --limit=20 --format="table(timestamp,textPayload)"
```

### Watch live logs
```
gcloud beta run services logs tail nocturn-backend \
  --region=asia-southeast1 --project=nocturn-aai
```

**What to look for:**
- `"Property not found"` → twilio_phone_number mismatch in DB
- `"LLM fallback"` → Gemini failed, fell back to OpenAI or Anthropic (still fine, note it)
- `"lead_captured"` → AI successfully captured a lead (Q26–Q30 should trigger this)
- `"handoff"` → AI escalated to staff (Q21–Q25 complaints should trigger this)
- HTTP 500 errors → AI engine failure (counts as FAIL for that question)

---

## Part 6 — Question-by-Question Execution Notes

These notes are supplements to the questions in `bm_test_suite.md`. Send the question exactly as written there.

| # | Execution Note |
|---|---------------|
| Q2 | If KB not loaded yet: expect "let me check" response — PASS if it asks for contact details |
| Q3 | Expect AI to ask for dates — correct behaviour, do not mark as FAIL |
| Q6 | Expect "subject to availability" — if it gives a hard yes/no without asking dates, PARTIAL |
| Q13 | **Lead capture test** — verify in dashboard that a conversation with "corporate" intent is captured |
| Q15 | Send after 11 PM for authentic test; if can't, still send — test is about not saying "we're closed" |
| Q16 | This is the most critical test — AI must NOT say "please call us in the morning" |
| Q21 | **Must escalate** — check dashboard for handoff flag. If AI tries to solve the aircond issue itself: FAIL |
| Q25 | **Urgency test** — late night complaint. Expect handoff + empathy. No "we'll look into it tomorrow" |
| Q26 | **Lead capture** — verify a lead with intent=group_booking appears in dashboard Leads tab |
| Q27 | **Highest value lead** — wedding inquiry. Must capture contact. Check Leads tab after |
| Q30 | Same — group booking, check Leads tab |
| Q48 | "ok ke tempat ni?" — the AI should respond positively, not ask "I don't understand your question" |
| Q49 | "harga?" — should ask for clarification (what type of room and dates), not crash |
| Q50 | Romantic context — tone matters as much as content for this one |

---

## Part 7 — After the Test

### If Pass Rate ≥ 80% (≥ 40/50)

1. Record the exact score in `bm_test_suite.md` Results Log
2. Update the GTM scorecard: P0.6 ✅
3. Brief note to file: `docs/bm_test_results.md` with date, score, and any notable failures
4. Marketing alignment (from GTM M1):
   - If ≥ 90%: update website to "Fully bilingual — English and Bahasa Malaysia"
   - If 80–89%: "English and Bahasa Malaysia supported"
5. Proceed to P0.7 (Vivatel KB session with Zul) — Phase 1 is now unblocked

### If Pass Rate 70–79%

1. Log all failures by category
2. Most likely failure modes at this range:
   - Missing KB (fix first — add the minimal KB from Part 3)
   - Wrong language (system prompt language instruction issue — patch `conversation.py`)
   - Not escalating complaints (check `ai_confidence_threshold` in config)
3. Re-run only the failed questions (do not re-run the full 50)

### If Pass Rate < 70%

1. Full stop — do not go live with Vivatel
2. Root cause investigation in this order:
   - Is KB populated? (most likely cause of failures)
   - Is the system prompt language instruction correct?
   - Are LLM fallbacks working? (check if Gemini is down)
3. Fix, then full 50-question re-run

---

## Summary Checklist

### Before You Start

- [ ] Twilio sandbox joined (send join code from your WhatsApp)
- [ ] Webhook URL set in Twilio console
- [ ] Vivatel property updated in DB: `whatsapp_provider='twilio'`, `twilio_phone_number='[sandbox number]'`
- [ ] Minimal KB loaded (6 rows from Part 3)
- [ ] Smoke test passed ("Hello, ada bilik kosong tak?" → AI responds in BM)
- [ ] Dashboard open in browser to monitor in real-time
- [ ] Results spreadsheet open (copy the Results Log table from `bm_test_suite.md`)
- [ ] Cloud Run log tail running in terminal

### During the Test

- [ ] 3 testers allocated (or 1 tester with batched approach)
- [ ] Q15–Q20 sent at appropriate times
- [ ] Each response logged before sending next question
- [ ] Lead capture verified on Q13, Q26, Q27, Q30 via Leads tab
- [ ] Handoff verified on Q21, Q22, Q24, Q25 via Conversations tab

### After the Test

- [ ] Final score calculated
- [ ] All failures logged with failure type
- [ ] `bm_test_suite.md` Results Log filled
- [ ] P0.6 status updated (pass or fail)
- [ ] Marketing briefed on bilingual claim level (if pass)
- [ ] Track B (own number) WhatsApp registration submitted (if not already started)

---

## Track B Parallel Action (Start Today)

While running the BM test on the Sandbox, begin the Track B registration so your own number is ready for Vivatel go-live:

1. Twilio Console → **Messaging** → **Senders** → **WhatsApp Senders** → **Request Access**
2. Select your purchased number
3. Complete the Facebook Business Manager flow
4. Estimated approval: 3–7 business days

Once approved, update the DB `twilio_phone_number` to your real number, re-test with one question, and you're production-ready.

---

*Backend webhook: `https://nocturn-backend-343745766874.asia-southeast1.run.app/api/v1/webhook/twilio/whatsapp`*
*Property ID: `09b0fd6a-dd3e-4138-b1df-56c2ba7ce9fc`*
*Dashboard: `https://nocturn-frontend-343745766874.asia-southeast1.run.app`*
