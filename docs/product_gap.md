# Product Gap Analysis
## Nocturn AI — What to Build, What to Drop, How to Get Paid
### Version 1.0 · 17 Mar 2026
### Cross-referenced with: prd.md v2.0, architecture.md v2.0, build_plan.md v2.0, revenue_methodology.md

---

## 1. The Situation

The codebase is at v0.3.0. The AI engine works. The backend is live on Cloud Run. The frontend dashboard exists. **But we cannot invoice a single hotel today** — not because the product doesn't work, but because the path from "demo" to "paying customer" is blocked by specific, fixable gaps.

This document maps exactly what stands between us and the first payment.

---

## 2. The Bridge — Path to First Payment

> *The "bridge" is the minimum sequence of steps required for Vivatel to hand over money.*

```
Step 1: GM opens dashboard → SEES revenue (not an onboarding checklist)
Step 2: GM sees leads from the previous night → UNDERSTANDS the value
Step 3: AI handled X inquiries. Y leads captured. RM Z recovered.
Step 4: Staff gets email at 7am confirming last night's numbers
Step 5: GM says "this is working" → signs agreement → pays invoice
```

**Every gap below is mapped to which step it blocks.**

---

## 3. The Obstacle — What Currently Blocks Getting Paid

### Obstacle A: The Dashboard Lies About What the Product Does

**What the GM sees on first login:** An onboarding setup checklist with progress rings and milestone cards.

**What the GM needs to see:** Yesterday's inquiry count, leads captured, revenue recovered.

**Why this is fatal:** The product's entire value proposition — "we capture revenue you were losing at night" — is invisible at the moment of highest intent. A GM who logs in to evaluate the product sees a task manager, not a revenue engine.

**Blocks:** Step 1 and Step 3 above. This is the #1 obstacle.

**Fix:** Replace `frontend/src/app/dashboard/page.tsx` with the KPI card view (currently at `/dashboard/analytics`). The analytics page already has everything — Revenue Recovered, Cost Savings, Total Inquiries, Leads Captured, AI Handled, Handoffs, After Hours, Avg Response. Move it to the landing page.

---

### Obstacle B: Staff Cannot Close the Loop After Handoff

**What happens now:** AI detects a complex inquiry → flags it for handoff → staff gets notified → staff must pick up their phone and reply via WhatsApp manually.

**What should happen:** Staff clicks on the conversation in the dashboard → types a reply → sends it. Full loop closed from one screen.

**Why this matters for payment:** The pitch is "AI handles it, staff oversees it." If staff can't reply from the dashboard, the product is half-finished. During UAT, Zul will notice immediately.

**Blocks:** Step 2. Vivatel UAT will flag this as a blocker.

**Fix:** Add a reply text input + send button to `frontend/src/app/dashboard/conversations/[id]/page.tsx`. Backend already supports `POST /api/v1/conversations/{id}/messages` with `role: "staff"`.

---

### Obstacle C: The Daily Email Report Is Broken in Production

**What happens now:** Daily email report works in development (APScheduler). In production, APScheduler is disabled. The Cloud Scheduler job has not been created. `SENDGRID_API_KEY` is missing from Secret Manager.

**Why this matters for payment:** The daily 7am email is the product's "daily active user" hook. It is how the GM stays engaged without logging in. Without it, the product is invisible between demos.

**Blocks:** Step 4. Cannot prove ongoing value delivery without this.

**Fix (2 steps):**
1. Add `SENDGRID_API_KEY` to GCP Secret Manager
2. Create Cloud Scheduler job: `POST /api/v1/internal/run-daily-report` @ `30 7 * * *` MYT with `X-Internal-Secret` header

---

### Obstacle D: PII Encryption Key Missing

**What happens now:** `FERNET_ENCRYPTION_KEY` is not in Secret Manager. `services/pii_encryption.py` bypasses encryption silently when key is absent.

**Why this matters for payment:** PDPA compliance is a contractual requirement for any hotel doing business in Malaysia. If a data breach occurs before this is fixed, liability is unambiguous.

**Blocks:** Step 5 — signing a contract without PDPA compliance is a legal risk.

**Fix:** Generate key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` → add to Secret Manager as `FERNET_ENCRYPTION_KEY`.

---

### Obstacle E: Bilingual Responses Untested End-to-End

**What happens now:** BM detection and response logic is implemented. It has NOT been tested with real WhatsApp conversations by a native BM speaker.

**Why this matters for payment:** ~40% of inquiries to Malaysian 3-4 star hotels come in Bahasa Malaysia. A degraded BM experience during the Vivatel pilot is visible immediately and will be cited as a reason not to pay.

**Blocks:** Step 3 and UAT confidence.

**Fix:** Run the 50-question BM/Manglish test suite via Twilio sandbox → Vivatel test number (see PRD F1 and `gtm_execution_plan.md` Task P0.6 for full question list). Must pass at ≥80%. Have a native speaker review failures. Document pass rate in writing before any bilingual claim on the website.

---

## 4. Feature Priority Matrix

### 4.1 Build Urgently (Blockers to First Payment)

| Feature | Gap Description | Blocks | Effort |
|---------|----------------|--------|--------|
| **Dashboard home → KPI cards** | Landing page is onboarding checklist, not revenue | Gets paid | 1–2 days |
| **Staff reply from dashboard** | No text input in conversations view | UAT pass | 1 day |
| **Daily email report (production)** | Missing API key + Cloud Scheduler job | Daily retention | 2 hours |
| **FERNET_ENCRYPTION_KEY** | PII unencrypted — PDPA non-compliant | Contract signing | 30 min |
| **BM end-to-end test** | Bilingual untested with real WhatsApp | UAT confidence | Half day |
| **"Lost" status in leads filter** | Cannot filter to show lost leads | Accurate reporting | 2 hours |
| **Vivatel KB population** | AI has nothing to answer with | Everything | 1 day (SheersSoft builds it) |

**Total estimated effort to clear all blockers: ~5–6 working days.**

---

### 4.2 Build Soon (Post-Pilot, Pre-Scale)

These features improve retention and conversion at the 2nd–5th customer stage, but do not block the first payment.

| Feature | Why It Matters | When to Build |
|---------|---------------|---------------|
| **Confirmed Revenue field** | Staff marks booked reservations → `actual_revenue` → real ROI proof | After Vivatel first payment |
| **Week-over-week comparison in daily email** | "This week vs last week" makes the email compelling | After first 14 days of data |
| **Lead status update from email** | Staff can update lead status by replying to the email | After pilot month |
| **Mobile-responsive dashboard** | GMs check on phones; current layout not mobile-optimized | Before 3rd property |
| **KB self-serve update** | Hotel can update their own knowledge base | Before 5th property |
| **Multi-property dashboard view** | GM with 2+ properties sees a combined view | After 3+ properties on same group |

---

### 4.3 Drop (Do Not Build in v1)

These features were built or partially scoped but are **not validated by market research** and distract from the core value proposition.

| Feature | Why to Drop |
|---------|-------------|
| **Gamified onboarding progress tracker** (current dashboard home) | No hotel GM asked for this. Replaced by revenue KPIs. |
| **Tenant/TenantMembership SaaS hierarchy** (active) | 0 paying tenants. Activate when ≥3 paying hotels confirmed. |
| **Stripe billing + webhook** | Manual invoicing works at pilot scale. Automate at ≥5 tenants. |
| **Supabase Auth (magic links, user admin)** | SheersSoft creates accounts manually for pilot hotels. |
| **SuperAdmin provisioning dashboard** | Scripted provisioning is sufficient for <10 properties. |
| **Support chatbot (nocturn-ai-support)** | Zero inbound support volume. Build when customer base justifies it. |
| **Application intake form (ai.sheerssoft.com/apply)** | No inbound demand pipeline yet. Build when advertising drives traffic. |
| **Guest insights / sentiment analysis** | Nice-to-have. No hotel asked for it. Build after ROI is proven. |
| **Email channel (SendGrid inbound)** | Malaysian hotels primarily use WhatsApp. Email intake can wait. |

---

## 5. What "Getting Paid" Looks Like

### The Direct Path (Vivatel Pilot)

```
Today → Fix 7 blockers (5–6 days) → Vivatel KB session (1 day)
→ Deploy to production → Vivatel UAT (2 days)
→ 7 days of real data → Case study one-pager
→ Invoice: RM 1,500 (Starter) or RM 3,000 (Professional) / month
```

**Target: First invoice within 3 weeks.**

### The Proof Loop (Replication to Properties 2–5)

```
Vivatel case study → 3 demo calls (Novotel, Ibis Styles, Melia)
→ Same 5-day onboarding per property
→ Same invoice
→ RM 4,500–9,000 MRR by Day 60 (3 paying); RM 15,000–30,000 MRR by Day 90 (10 paying)
```

### The Bridge Sentence

> *"We capture hotel inquiries at night and turn them into leads with names, phone numbers, and booking intent. Your GM gets a daily email at 7am showing exactly how much revenue we recovered. You pay us RM 1,500/month for something that recovers 10–20× that."*

This sentence only lands if the **dashboard shows the revenue** (Obstacle A) and the **daily email is live** (Obstacle C).

---

## 6. The Revenue Formula (Canonical)

Per `revenue_methodology.md`:

```
Estimated Revenue Recovered = Sum of (lead nights × property ADR) × 20%
  where: lead nights defaults to 1 if not captured
         ADR defaults to property setting (Vivatel ~RM 230)
         20% = conservative conversion assumption

Cost Savings = AI-handled inquiries × 0.25 hrs × RM 25/hr
```

**Example (Vivatel, 30 days):**
- 20 after-hours leads captured × RM 230 ADR × 20% = **RM 920 estimated revenue recovered**
- 400 AI-handled inquiries × 0.25 hrs × RM 25 = **RM 2,500 cost savings**
- Total value demonstrated: **RM 3,420/month** vs RM 1,500 subscription fee

Do not use RM 12,400 in any demo or case study until verified by real Vivatel data.

---

## 7. Decision Rule for New Feature Requests

Before building anything new, answer:

1. **Does it help get the first payment?** → Build it now.
2. **Does it help retain the first 5 paying properties?** → Build it after Vivatel is live.
3. **Does it help scale to 10+ properties?** → Build it when you have 5+ properties.
4. **None of the above?** → Do not build it.

The current codebase has features in category 3 and 4 that were built before category 1 was complete. Fix category 1 first.

---

*Every hour spent on dormant SaaS infrastructure is an hour not spent on getting Vivatel live and invoiced. The bridge is short — 5–6 days of focused work. The obstacle is clarity, not capability.*
