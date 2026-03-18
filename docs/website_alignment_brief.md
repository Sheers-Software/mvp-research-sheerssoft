# Website Alignment Brief
## Nocturn AI · ai.sheerssoft.com & sheerssoft.com
### Version 1.0 · 18 Mar 2026
### Cross-referenced with: prd.md v2.1, gtm_execution_plan.md v1.1, website_design_brief.md, revenue_methodology.md, product_gap.md v1.3

---

## Purpose

This document audits the two public-facing websites against the product as it exists today — comparing live website copy against the canonical product documentation, identifying every factual error, unverified claim, and missing capability, and providing specific recommended copy for each fix.

**The standard:** No claim on either website should contradict a primary doc, overstate a capability, or attribute a metric that is not verified by a real customer or a cited source. Claims marked ⚠️ in the docs must not appear on the website.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [ai.sheerssoft.com — Issue Inventory](#2-aisheersoftcom--issue-inventory)
3. [sheerssoft.com — Issue Inventory](#3-sheersoftcom--issue-inventory)
4. [Changes Required by Priority](#4-changes-required-by-priority)
5. [Verified Claims — Safe to Use](#5-verified-claims--safe-to-use)
6. [Copy Replacements — Ready to Implement](#6-copy-replacements--ready-to-implement)
7. [Pending Until Vivatel Pilot Completes](#7-pending-until-vivatel-pilot-completes)

---

## 1. Executive Summary

Both websites contain content that needs updating. The misalignments fall into four categories:

| Category | ai.sheerssoft.com | sheerssoft.com |
|----------|-----------------|----------------|
| **Factually wrong** | 2 | 3 |
| **Unverified / overstated** | 3 | 2 |
| **Missing live capabilities** | 3 | — |
| **Inconsistent with docs** | 2 | 2 |
| **Total issues** | **10** | **7** |

**Most critical issue:** Pricing on `ai.sheerssoft.com` is RM 599–1,199/month. The business model documented across all strategy docs targets RM 1,500–5,000/month. The website is currently underpricing the product by 60–75%, which will attract the wrong segment, set wrong expectations at pilot conversion, and undermine positioning as a premium revenue tool.

**Second most critical:** `sheerssoft.com` describes Nocturn AI as answering in "over 50 languages" and "guiding guests directly to your booking engine." Both are incorrect. The product is bilingual (English + Bahasa Malaysia) and does not integrate with booking engines.

---

## 2. ai.sheerssoft.com — Issue Inventory

---

### ISSUE A1 — Pricing (CRITICAL — Factually Wrong)

**Current website:**
> Boutique (< 50 rooms): **RM 599/month**
> Independent (50–150 rooms): **RM 899/month**
> Resort / Mid-Scale (150+ rooms): **RM 1,199/month**
> "* Founding cohort members lock in 30% below these rates forever."

**What the docs say:**
From `website_design_brief.md` pricing page spec:
> Starter: RM 1,500/mo · Professional: RM 3,000/mo · Enterprise: RM 5,000+/mo

From `gtm_execution_plan.md`:
> "Budget authority: can approve RM 1,500-5,000/mo without board approval"

From `prd.md` v2.1:
> "RM 1,500–5,000/mo defensible"
> "Revenue Math: 10 customers × RM 2,250/mo average = RM 22,500 MRR"

**The problem:**
The current website prices contradict every financial model in the docs. At RM 899/mo for an Independent property (the most common tier), the product can only reach RM 8,990 MRR at 10 customers — not the RM 22,500 MRR modelled. Additionally, sub-RM 1,000/mo pricing signals "generic chatbot" to the GM persona, actively undermining the premium revenue-tool positioning.

**Fix:** Replace all pricing with the model from `website_design_brief.md`. See Section 6 for ready copy.

---

### ISSUE A2 — ROI Recovery Rate (Unverified / Overstated)

**Current website:**
> "Nocturn AI typically recovers 40–60% of this [revenue at risk]."

**What the docs say:**
From `revenue_methodology.md` and `prd.md`:
> Conversion rate used in formulas: **20%** (conservative industry standard)
> "The 20% figure is the conversion rate assumption — the likelihood that a captured lead becomes a booking."

**The problem:**
The "40–60% recovery" claim has no basis in any primary document or cited research. The conservative 20% conversion rate is the documented and defensible number. No real customer data exists yet to support 40–60%.

**Fix:** Remove the 40–60% claim. Replace with: *"Hotels like yours typically have RM 3,000–8,000/month in revenue at risk. Our conservative estimates use a 20% conversion rate on captured leads."*

---

### ISSUE A3 — Market Statistic Inconsistency

**Current website:**
> "70% of Malaysian hotel bookings come from manual channels"

**What the docs say:**
From `gtm_execution_plan.md`, `prd.md`, and `website_design_brief.md`:
> "**90%** of Malaysian hotel bookings come from manual channels — WhatsApp, phone, email, walk-ins"

**The problem:**
The website uses 70% while every strategy document uses 90% (validated by direct interview with Zul, Vivatel KL: *"90% of our bookings come from walk-ins, phone, WhatsApp, and email"*). The 90% figure is the more accurate and more compelling number.

**Fix:** Update to 90% throughout. Add attribution: *"Vivatel KL, Reservations Manager interview, 2026"* in the footnote or source tooltip.

---

### ISSUE A4 — Research Provenance ("18 months, 4 countries")

**Current website (Founder's Message):**
> "9 operators. 4 countries. 18 months of primary research."

**What the docs say:**
From `gtm_execution_plan.md` and interview records, research covered:
- Malaysia (Vivatel KL, Novotel KLCC, Ibis Styles KL, Melia KL, Tamu Hotel, Irama KL)
- Singapore (regional hotel context)
- Middle East (advisor with ME background)

That is **3 countries**, not 4. The "18 months" claim is not corroborated by any internal timeline document.

**Fix:** Update to "9 operators. 3 countries." Remove the "18 months" claim or replace with a verifiable statement: *"9 operators across Malaysia, Singapore, and the Middle East."*

---

### ISSUE A5 — Testimonials Attributed as Customer Quotes

**Current website:**
The testimonials section attributes quotes to people like *"Revenue Manager, International 4-Star Chain Hotel, Kuala Lumpur"* and *"Reservation Manager, City Hotel, Kuala Lumpur."* These are positioned as product endorsements.

**What the docs say:**
These are quotes from **pre-product research interviews**, not customers of Nocturn AI. The docs explicitly state:
> "Must be replaced with Vivatel's real 30-day numbers before scaling marketing"
> "Claim is ⚠️ UNVERIFIED — must be replaced with real customer data"

**The problem:**
Presenting research interview quotes as product testimonials is misleading. These people have not used the product. A prospect who investigates further will find the disconnect. More importantly, it sets a trust standard the product then has to maintain.

**Fix:** Reframe these as *"What hotel operators tell us"* or *"What we heard from the field"* — explicitly as research insights rather than product testimonials. See Section 6 for revised attribution. Replace with real customer quotes as soon as Vivatel pilot data is available.

---

### ISSUE A6 — Missing Live Feature: Monthly Guest Insights Report

**Current website:** Not mentioned.

**What the product does:**
The Monthly Guest Insights Report is a live, production feature. Every 30 days, the AI processes the full transcript history to extract:
- Guest sentiment
- Recurring objections and FAQs
- Feature requests and common complaints
- Delivered to the GM as part of the Day-30 pilot review

This is the most tangible, differentiated deliverable in the pilot and is not mentioned on the website at all.

**Fix:** Add to the "What You Get" section in the Founding Cohort offer: *"✅ Guest Insight Report (Day 30) — AI-compiled summary of what your guests are actually asking, their sentiment, and the objections that lost you bookings."*

It already appears in the founding cohort list on the site — verify it is rendered correctly and prominently enough.

---

### ISSUE A7 — Missing Live Feature: Staff Reply from Dashboard

**Current website:**
Only mentions *"Smart Human Handoff: AI transfers complex requests to staff with full context instantly."*

**What the product does:**
Staff can not only *see* handed-off conversations — they can **reply directly from the dashboard**, and the reply is forwarded to the guest via their original channel (WhatsApp or web chat). This is a full closed-loop handoff, not a one-way flag.

**Fix:** Update the Human Handoff feature description to:
> *"Smart Human Handoff — AI transfers complex requests to your team with full conversation context. Staff reply directly from the dashboard — and the guest receives your message instantly on WhatsApp or web chat."*

---

### ISSUE A8 — Missing Live Feature: Analytics Depth

**Current website:**
References *"Conversion Dashboard: See exactly how many inquiries came in and how many converted."* No detail beyond this.

**What the product does:**
The analytics dashboard includes:
- Revenue recovered (with formula tooltip)
- Cost savings (labour arbitrage)
- Actual confirmed revenue (staff-entered from converted leads)
- 7-day / 30-day / 90-day time range filtering
- Daily bar charts
- CSV export of all leads
- PDF report generation

**Fix:** Add a brief callout in the features list or a dedicated feature section. This level of analytics detail — especially the provable confirmed revenue column — is a key selling point for the GM persona who needs to justify the spend to ownership.

---

### ISSUE A9 — ROI Calculator Formula Transparency

**Current website calculator:**
Uses a formula that produces "RM 10,125 at risk" for 30 inquiries, RM 250 ADR, 30% after hours. No formula shown.

**What the docs say (`revenue_methodology.md`):**
The formula is:
```
Daily leads × after_hours_pct × ADR × nights_assumed × conversion_rate × 30
= 30 × 0.30 × 250 × 1 × 0.20 × 30 = RM 13,500/month
```

At 20% conversion: the "at risk" framing (100% of after-hours value) gives a higher shock number, but the "recovery estimate" should use 20% conversion, not 40-60%.

The website shows "RM 10,125 at risk" and "Nocturn AI typically recovers 40-60%" — resulting in a claimed RM 4,050–6,075/month recovery. The docs model RM 3,000–8,000 as the realistic range. The calculator numbers are in the right ballpark but the methodology is unexplained, and the 40-60% recovery claim is unverified.

**Fix:** Add a methodology footnote. Use the documented formula transparently. Replace "40–60% recovery" with the 20% conversion language.

---

### ISSUE A10 — "0% of inquiries captured after 6PM"

**Current website stat block:**
> "0% of inquiries captured after 6PM"

**Assessment:**
This is directionally accurate but technically unprovable as a universal claim. It's also a self-defeating stat for properties that already have some after-hours coverage. The more accurate framing from the docs is:

> "After 6pm, reservation desks close. Inquiries pile up. Nobody answers."

**Fix:** Replace the "0%" stat with a more credible agitation:
> *"6PM — Reservations closes. Inquiries keep coming."*
Or use the stat as a property-specific challenge: *"How many inquiries did your property miss last night?"*

---

## 3. sheerssoft.com — Issue Inventory

---

### ISSUE B1 — "Over 50 Languages" (Factually Wrong)

**Current website:**
> "Answers WhatsApp, Web Chat, and Email in seconds, **in over 50 languages**"

**What the product does:**
Nocturn AI is bilingual: **English and Bahasa Malaysia only**. The language capability is built around Malaysian hospitality specifically — it handles "Manglish" and code-switching, which is a differentiator. "Over 50 languages" is completely fabricated and will cause immediate loss of trust when a prospect asks the AI a question in Mandarin or Tamil.

**Fix:** Replace with:
> *"Answers WhatsApp, Web Chat, and Email in seconds — in English and Bahasa Malaysia, purpose-built for Malaysian hospitality."*

---

### ISSUE B2 — "Guides Guests Directly to Your Booking Engine" (Factually Wrong)

**Current website:**
> "Guides guests through the funnel directly to your booking engine, avoiding OTA fees"

**What the product does:**
Nocturn AI does **not** integrate with booking engines (Opera, Mews, Cloudbeds, etc.). The product captures the lead, responds with property-specific information, and hands off qualified leads to the reservations team. Booking confirmation happens through the hotel's existing workflow — not through any software integration.

This claim will immediately surface as false on first demo call when a prospect asks "which booking engine does it integrate with?"

**Fix:** Replace with:
> *"Captures every inquiry and qualifies the lead — so your team converts direct bookings before the guest goes to OTA."*

---

### ISSUE B3 — "Scale Globally" (Contradicts Positioning)

**Current website feature claim:**
> "Scale Globally"

**What the docs say:**
From `gtm_execution_plan.md` and `prd.md`:
> "Geographic Focus: Malaysia only (v1)"
> "Ruthlessly narrow ICP"
> "Explicitly NOT in v1: ... any market outside Malaysia"

The entire product differentiation — WhatsApp-native, Bahasa Malaysia, Malaysian hospitality context, PDPA 2010 compliance — is built around being the *only* product that is purpose-built for this specific market. "Scale Globally" is both inaccurate and actively undermines the positioning.

**Fix:** Remove "Scale Globally." Replace with:
> *"Built for Malaysia — the only AI concierge purpose-built for how Malaysian hotels actually operate."*

---

### ISSUE B4 — "Hotel Genius: Coming Q3 2026" (Not in Product Docs)

**Current website:**
> "Hotel Genius — Coming Q3 2026 — Autonomously handles guest enquiries"

**What the docs say:**
"Hotel Genius" does not appear in any product documentation — not in `prd.md`, `architecture.md`, `build_plan.md`, `gtm_execution_plan.md`, or any roadmap doc. The product roadmap in the docs identifies v2.0 as "F&B Revenue Intelligence" and v2.5 as "Guest Recognition & KYC" — neither is called "Hotel Genius."

The description ("autonomously handles guest enquiries") also overlaps with what Nocturn AI already does, creating confusion about what differentiates the two products.

**Fix:** Remove "Hotel Genius" until the product has a defined spec in the docs. If a second product is being planned, it needs to be documented first. Alternatively, if this is an alias for the v2.x roadmap, update the roadmap docs to confirm and align the name.

---

### ISSUE B5 — "Nocturn AI Autonomously Handles Bookings" (Overstated)

**Current website:**
> "Nocturn AI — Autonomously handles bookings, even while you sleep"

**What the product does:**
Nocturn AI captures leads, responds to inquiries, and qualifies guests. It does not complete bookings autonomously — booking confirmation requires staff involvement. The docs are explicit:
> "AI acknowledges → publishes to Redis → dashboard shows → staff clicks Take Over → staff sees full context + lead data"
> "Our team will follow up first thing tomorrow morning."

"Handles bookings" implies the full transaction is automated, which will trigger the FAQ objection in every demo.

**Fix:** Replace with:
> *"Nocturn AI — Captures every inquiry and qualifies every lead, even while you sleep"*

---

### ISSUE B6 — "100% Satisfaction Guarantee — Refund Every Penny"

**Current website:**
> "100% Satisfaction Guarantee: We're so confident in our solutions that if you're not completely satisfied within the first 30 days, we'll refund every penny. No questions asked."

**What the docs say:**
The pilot is free. There is no payment to refund. The guarantee in the docs is:
> "Run Nocturn AI for 30 days. If your team doesn't agree that it has measurably improved your inquiry response time and follow-up consistency, you pay nothing."

The "refund every penny" language creates a false implication that customers have paid money upfront. This could cause confusion and undermine trust when prospects see it alongside "No credit card required."

**Fix:** Align with the actual pilot offer. See Section 6 for copy.

---

### ISSUE B7 — "10x Faster Operations" (Ungrounded)

**Current website:**
> "10x Faster Operations"

**Assessment:**
This claim has no basis in any product document, research interview, or measured metric. It is generic SaaS marketing copy that the GM persona will ignore or distrust. Response time is measurable and documented — <30 seconds vs. the typical "next morning" reply — which is a far more powerful, specific claim.

**Fix:** Replace with a specific, grounded claim:
> *"From overnight backlog to instant response — replies in under 30 seconds, 24/7"*

---

## 4. Changes Required by Priority

| Priority | Site | Issue | Impact if Not Fixed |
|----------|------|-------|---------------------|
| 🔴 P1 | ai.sheerssoft.com | A1 — Pricing wrong (RM 599 vs RM 1,500) | Wrong customer segment; conversion at wrong price; financial model broken |
| 🔴 P1 | sheerssoft.com | B1 — "50 languages" (product is EN + BM only) | Immediate credibility loss on first demo call |
| 🔴 P1 | sheerssoft.com | B2 — "Booking engine integration" (doesn't exist) | Immediate trust destruction on first demo |
| 🟠 P2 | ai.sheerssoft.com | A5 — Research quotes presented as customer testimonials | Legal/ethical risk; trust erosion if discovered |
| 🟠 P2 | ai.sheerssoft.com | A2 — "40–60% recovery" claim (unverified) | Expectation mismatch at Day 30 ROI review |
| 🟠 P2 | sheerssoft.com | B4 — "Hotel Genius" product (not in docs) | Prospect confusion; internal alignment issue |
| 🟠 P2 | sheerssoft.com | B5 — "Autonomously handles bookings" (overstated) | Misleads on capability; FAQ objection in every demo |
| 🟡 P3 | ai.sheerssoft.com | A3 — Stat says 70% (docs say 90%) | Minor but inconsistent with research |
| 🟡 P3 | ai.sheerssoft.com | A4 — "4 countries, 18 months" (unverified) | Credibility risk if probed |
| 🟡 P3 | sheerssoft.com | B3 — "Scale Globally" (contradicts ICP) | Attracts wrong segment |
| 🟡 P3 | sheerssoft.com | B6 — "Refund every penny" (product is free pilot) | Copy confusion |
| 🟡 P3 | sheerssoft.com | B7 — "10x Faster Operations" (ungrounded) | Generic, ignored by GM persona |
| 🟢 P4 | ai.sheerssoft.com | A6 — Monthly Insights Report missing | Lost differentiation in pitch |
| 🟢 P4 | ai.sheerssoft.com | A7 — Staff reply capability understated | Lost differentiation in pitch |
| 🟢 P4 | ai.sheerssoft.com | A8 — Analytics depth not described | Lost differentiation in pitch |

---

## 5. Verified Claims — Safe to Use

These are grounded in cited research, direct interview quotes, or confirmed product behaviour. Use freely.

| Claim | Source | Notes |
|-------|--------|-------|
| "90% of Malaysian hotel bookings come from manual channels" | Vivatel KL interview, 2026 | Use with attribution |
| "15–25% OTA commission on every booking" | Booking.com/Expedia rate analysis | Cite "industry standard" |
| "85% of unanswered callers never call back" | Dialora Research, 2025 | Cite source |
| "Responds in under 30 seconds, 24/7" | Product spec — confirmed in testing | No qualification needed |
| "Live in 48 hours" | Onboarding timeline — confirmed in docs | Accurate |
| "No PMS integration required" | Product architecture — confirmed | Core differentiator |
| "Free 30-day pilot — no credit card required" | GTM plan — confirmed offer | Accurate |
| "PDPA 2010 compliant" | Fernet encryption + RLS + right-to-delete | Confirmed in architecture |
| "Each property's data is fully isolated" | RLS + tenant scoping — confirmed | Confirmed in architecture |
| "English and Bahasa Malaysia" | Language capability — confirmed | Do not expand scope |
| "78% of hotel chains have integrated AI in 2025" | Global Hospitality AI Study, 2025 | Must include citation |
| "30–200 daily inquiry touchpoints per property on busy days" | Novotel KLCC interview | Attribute as research |
| "RM 3,000–8,000/month revenue at risk" | Revenue model — conservative estimate | Frame as "at risk", not "recovered" |
| "Estimated revenue recovered uses a 20% conversion rate" | Revenue methodology — documented | Provide formula tooltip |

---

## 6. Copy Replacements — Ready to Implement

### 6a. ai.sheerssoft.com — Pricing Section

**Remove entirely:**
> Boutique (< 50 rooms) — RM 599/month
> Independent (50–150 rooms) — RM 899/month
> Resort / Mid-Scale (150+ rooms) — RM 1,199/month

**Replace with:**

```
After Your 30-Day Pilot

If the numbers work, continuing is simple. Month-to-month. No lock-in.

┌─────────────────────────────────────────────────────────────────────────┐
│  STARTER              PROFESSIONAL           ENTERPRISE                 │
│  RM 1,500/mo          RM 3,000/mo            RM 5,000+/mo               │
│  < 100 rooms          100–300 rooms          300+ rooms                 │
│                                                                         │
│  ✓ 1 WhatsApp line    ✓ 2 WhatsApp lines     ✓ Unlimited lines          │
│  ✓ Web chat widget    ✓ Web chat widget       ✓ Web chat widget          │
│  ✓ 500 conversations  ✓ Email auto-handler    ✓ Email auto-handler       │
│  ✓ Basic dashboard    ✓ 2,000 conversations   ✓ Unlimited conversations  │
│  ✓ Email support      ✓ Full dashboard        ✓ Full dashboard + API     │
│                       ✓ Priority support      ✓ Dedicated manager        │
│  [Start Free Pilot]   [Start Free Pilot]      [Contact Us]               │
└─────────────────────────────────────────────────────────────────────────┘

Every plan starts with a free 30-day pilot. No contracts. Cancel anytime.
```

---

### 6b. ai.sheerssoft.com — Testimonials / Research Quotes Section

**Remove:** Current attribution labels (e.g., "Revenue Manager, International 4-Star Chain Hotel, KL")

**Replace section header and attribution framing:**

```
What Hotel Operators Told Us

Before we built Nocturn AI, we spent months sitting across from
Revenue Managers, Reservation Managers, and GMs across Malaysia.
Every conversation told the same story.

"Our primary operational weakness is systematic follow-up on inquiries."
— Revenue Manager, International 4-Star Chain, Kuala Lumpur*

"90% of our bookings come from walk-ins, phone, WhatsApp, and email.
 Once office hours end, inquiries are effectively dropped."
— Reservation Manager, City Hotel, Kuala Lumpur*

"If you could switch acquisition from OTA to direct — even 1% —
 that's thousands in savings per month."
— Pre-Sales Specialist, Global Hospitality Technology Company*

* Research interview conducted 2025–2026. These individuals have not
  yet used Nocturn AI. Pilot results from live properties will replace
  these quotes when available.
```

---

### 6c. ai.sheerssoft.com — ROI Calculator Claim

**Remove:**
> "Nocturn AI typically recovers 40–60% of this."

**Replace with:**
```
Hotels like yours typically have RM 3,000–8,000/month in revenue at risk
from inquiries that go unanswered or unfollowed.

Our estimates use a conservative 20% conversion rate on captured leads —
the same rate used by revenue managers when forecasting direct bookings.
```

---

### 6d. ai.sheerssoft.com — Market Stat Fix

**Remove:**
> "70% of Malaysian hotel bookings come from manual channels"

**Replace with:**
> "90% of Malaysian hotel bookings come from manual channels — WhatsApp, phone, email, and walk-ins¹"
> `¹ Reservation Manager interview, Vivatel KL, 2026`

---

### 6e. ai.sheerssoft.com — Founder's Message Research Claim

**Remove:**
> "9 operators. 4 countries. 18 months of primary research."

**Replace with:**
> "9 operators. Malaysia, Singapore, and the Middle East."

---

### 6f. ai.sheerssoft.com — Human Handoff Feature

**Remove:**
> "🤝 Smart Human Handoff: AI transfers complex requests to staff with full context instantly."

**Replace with:**
> "🤝 Smart Human Handoff — When the AI can't help, it transfers to your team with the full conversation context. Your staff reply directly from the dashboard — the guest gets your message instantly on WhatsApp or web chat. No information lost. No starting over."

---

### 6g. ai.sheerssoft.com — What You Get (Founding Cohort)

**Existing list is largely correct. Add one bullet:**

After the ✅ for "Guest Insight Report (Day 30)", expand it:
```
✅ Guest Insight Report (Day 30) — AI-compiled analysis of 30 days
   of real guest conversations: what they're asking, recurring objections,
   sentiment, and the topics that lost you bookings. Written for your GM.
```

---

### 6h. sheerssoft.com — Nocturn AI Description

**Remove:**
> "Answers WhatsApp, Web Chat, and Email in seconds, in over 50 languages"
> "Guides guests through the funnel directly to your booking engine, avoiding OTA fees"
> "Nocturn AI — Autonomously handles bookings, even while you sleep"

**Replace with:**
```
Nocturn AI — Captures every inquiry while you sleep

Your hotel receives 30+ inquiries a day via WhatsApp, email, and
your website. After 6pm, nobody answers. Nocturn AI responds in
under 30 seconds — 24/7 — in English and Bahasa Malaysia, captures
the lead, and hands your team a qualified inquiry with full context
every morning.

• WhatsApp, Web Chat, and Email — all channels covered
• Purpose-built for Malaysian hospitality — not a generic chatbot
• Replies in English and Bahasa Malaysia
• Every inquiry → captured lead with name, contact, intent, timestamp
• PDPA 2010 compliant · Encrypted · Hosted on Google Cloud Singapore
```

---

### 6i. sheerssoft.com — Guarantee Language

**Remove:**
> "100% Satisfaction Guarantee: We're so confident in our solutions that if you're not completely satisfied within the first 30 days, we'll refund every penny. No questions asked."

**Replace with:**
```
30-Day Prove-It Guarantee

Run Nocturn AI for 30 days — free. If your team doesn't agree it
has measurably improved your inquiry response time and follow-up,
you pay nothing. No contracts. No credit card required to start.
```

---

### 6j. sheerssoft.com — Remove "Scale Globally" and "10x Faster Operations"

**Remove both claims.**

**Replace "Scale Globally" with:**
> *"Built for Malaysia — the only AI concierge purpose-built for how Malaysian hotels actually operate."*

**Replace "10x Faster Operations" with:**
> *"From overnight backlog to instant response — replies in under 30 seconds, 24/7."*

---

### 6k. sheerssoft.com — Hotel Genius

**Remove** until a product spec exists in the docs. If the intent is to signal a roadmap, replace with:

```
More products coming in 2026

We're building the AI layer for the full hotel revenue stack.
[Join the waitlist →]
```

Do not name or describe a product that does not have a defined spec.

---

## 7. Pending Until Vivatel Pilot Completes

The following website improvements **should not be made yet** because they require real customer data. Action them at Day 30 of the Vivatel pilot.

| Action | Trigger | What to Add |
|--------|---------|-------------|
| Replace research quotes with customer testimonial | Vivatel pilot live, Zul approves quote | Full name, title, property, photo if available |
| Add case study / results section | 30-day pilot data collected | Inquiries captured, after-hours recovery rate, estimated revenue, confirmed revenue |
| Update hero "eyebrow badge" | First paying customer | *"Trusted by [Property Name], [City] — RM [X] recovered"* |
| Update ROI calculator defaults | Real Vivatel numbers available | Use actual ADR and inquiry volume |
| Add real dashboard screenshot | Pilot live with data | Replace any mock data with real (blurred if needed) numbers |
| Activate case studies page (`/case-studies`) | 2+ pilot completions | Per template in `website_design_brief.md` Section 4.5 |

**Standing rule (from `prd.md`):**
> No feature claim goes live on the website without written product confirmation that the capability is in production. No metric is stated on the website without being either a cited external source or a verified customer outcome.

---

*Document owner: Ahmad Basyir Azahari · Next review: upon Vivatel Day 30 data*
