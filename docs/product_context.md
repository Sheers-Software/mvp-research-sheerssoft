# Product Context: Nocturn AI (SheersSoft)
**Source**: [sheerssoft.com](https://sheerssoft.com) — Research Date: 13 Feb 2026
**Steered by:** [building-successful-saas-guide.md](./building-successful-saas-guide.md) — Principal Engineer lessons (Google/Meta)

---

## 1. Executive Summary

**Nocturn AI** is an AI-powered hotel concierge built by **Sheers Software Sdn Bhd** (Malaysian company, SSM Registered, PDPA Compliant). The product captures every guest inquiry 24/7 across WhatsApp, web chat, and email — especially during after-hours when reservation desks are closed — and converts them into captured leads with proven revenue recovery metrics.

**Tagline:** *"Every Unanswered Inquiry Is a Booking Your Competitor Gets."*

**Value Proposition:** Live in 48 hours. Proving value in 7 days. 30-day free pilot. No credit card required.

**Survival imperative:** The company must avoid the graveyard patterns: solving problems nobody pays for, "build it and they will come," underpricing, ignoring unit economics, building horizontal platforms, premature scaling. This document enforces ruthless ICP focus, distribution strategy from day one, and metrics-driven execution.

---

## 2. The Problem (Website Claims)

| Statistic | Source | Implication |
|-----------|--------|-------------|
| **90%** of Malaysian hotel bookings come through manual channels | Website | WhatsApp, phone, email, walk-ins — not OTAs |
| **30%** of inquiries arrive after 6pm | Industry research, 2026 | When nobody answers |
| **85%** of unanswered callers never call back | Dialora Research, 2025 | They book with competitors |
| **15–25%** OTA commission per booking | Booking.com/Expedia | RM 170–285 lost per reservation at RM 230 ADR |
| **78%** of hotel chains have integrated AI in 2025 | Website | Independent hotels that act now gain the advantage |

**Core insight:** Reservation desks close at 6pm. Staff are overwhelmed. Leads go cold. Guests quietly book on Booking.com instead. *"This isn't a technology problem. It's revenue falling on the floor."*

---

## 3. Target Audience (Personas)

### Primary Decision Makers

| Persona | Role | Pain Point | Success Definition |
|---------|------|------------|--------------------|
| **The GM** | General Manager | Revenue leakage, OTA commissions, no night staff | *"I can see exactly how many leads we recovered last night"* |
| **Bernard** | Revenue Manager | Needs direct bookings at higher margins, hard data | *"I know exactly how much revenue was saved"* |
| **Zul** | Reservation Manager | Dreads checking phone at 9 PM | *"I get my nights back"* |
| **Shamsuridah** | Front Desk | Overwhelmed by "Hi, got room?" 50×/day | *"I focus on guests in the lobby"* |

### ICP (Ideal Customer Profile) — Ruthlessly Narrow

> *"Trying to serve everyone means serving no one well."* — Meta lesson. Pick the smallest viable segment that can sustain the business.

| Attribute | Value | Rationale |
|-----------|-------|-----------|
| **Property type** | 3–4 star independent / mid-tier branded only | Budget hotels lack margin; 5-star has complex procurement. Sweet spot has budget + pain. |
| **Size** | 50–300 rooms | Below 50 = too few inquiries. Above 300 = enterprise sales cycle. |
| **Location** | Malaysia only (v1) | Same timezone, PDPA, BM/EN, local relationships. No regional sprawl. |
| **Booking mix** | >50% manual channels (WhatsApp, phone, email) | OTAs don't need this product. Manual = after-hours gap. |
| **Pain signal** | No after-hours coverage; 2–5 person reservations team | Must be actively losing leads. Pre-qualify: >20 inquiries/day. |
| **Decision maker** | GM or Revenue Manager (NOT IT) | IT blocks deals. GMs care about revenue. |

**Explicitly NOT targeting:** Budget hostels, Airbnb-style, 5-star chains (yet), hotels with <15 inquiries/day.

### Problem Validation Status

| Validation Gate | Target | Status |
|-----------------|--------|--------|
| Customer interviews (pre-build) | 20–30 actual target market | Document Vivatel, Novotel, Ibis, Melia. Expand to 20+ before scaling. |
| Hair-on-fire test | Customers already paying for inadequate solutions or painful workarounds | Hotels hire night staff / lose leads. Confirmed pain. |
| Willingness to pay | RM 1,500–5,000/mo defensible | Pilot converts to paid. Validate at scale. |

**Question to answer:** *"Will people pay enough for this solution to build a sustainable business?"* — Not "Is this technically interesting?"

### Unit Economics (Survival Metrics)

| Metric | Target | Red Flag |
|--------|--------|----------|
| **LTV:CAC ratio** | ≥ 3:1 | If CAC > LTV/3, stop scaling acquisition |
| **CAC payback period** | < 6 months | > 6 months = cash flow risk at bootstrap stage |
| **Monthly churn** | < 5% (B2B SaaS benchmark) | > 10% = product problem, not sales |
| **Annual churn (contract)** | < 20% | Above = immediate attention |
| **Gross margin** | > 80% | RM 2,100–4,000 cost vs RM 22,500 MRR at 10 properties ✓ |

**Rule:** If CAC > LTV, you're buying revenue at a loss. Scale is the reward for PMF, not the path to it.

### Distribution Strategy (Avoid "Build It and They Will Come")

| Channel | v1 Investment | Notes |
|---------|---------------|-------|
| Design partner (Vivatel) | High — over-serve | First 10 customers are design partners. Do things that don't scale. |
| Referrals (Bob's SKS, Shamsuridah) | Medium | Warm intros beat cold outreach 10:1 |
| Case study + cold outreach | After pilot data | Armed with Vivatel numbers before scaling |
| Content / SEO | Low (post-PMF) | Not a priority until PMF |

**Non-negotiable:** If not good at marketing/sales, bring someone in or learn fast. Engineers building in isolation = death.

### Sales Motion Alignment (Match to Price)

| Price Band | Motion | Nocturn Fit |
|------------|--------|-------------|
| < RM 500/mo | Self-serve | N/A — below our floor |
| RM 1,500–2,000/mo (Starter/Pro) | Sales-assisted | Demo call, onboarding support, pilot handholding |
| RM 3,000–5,000+/mo (Pro/Enterprise) | Full sales process | ROI review, GM presentation, contract |

**Mismatch kill:** Don't build enterprise sales infrastructure for a RM 1,500 product. Don't expect self-serve conversion at RM 5,000.

### PMF Signals to Watch

| Signal | PMF Present | PMF Absent |
|--------|-------------|------------|
| Inbound | Increasing organically | Linear with marketing spend |
| Usage | Grows within accounts | Flat after onboarding |
| Sales cycle | Shortening | Every deal a push |
| Feature requests | "Enterprise" asks (contracts, SSO) | Constant core-feature complaints |
| Churn | < 5% monthly | > 10% or unclear reasons |

**Rule:** You'll know PMF when customers pull you forward. If you're pushing every deal, you don't have it yet.

---

## 4. Solution Overview

### Core Promise
> *"An AI Concierge That Never Sleeps, Never Forgets, and Proves Its Value Every Morning"*

### Key Capabilities

| Capability | Website Promise | Technical Requirement |
|------------|-----------------|------------------------|
| **WhatsApp AI** | Instant replies <30s, 24/7, bilingual (EN + BM) | Meta WhatsApp Business Cloud API, webhook + sender |
| **Web Chat Widget** | "One line of code" — single `<script>` tag | Embeddable JS, zero dependencies |
| **Email Auto-Handler** | "Turn your inbox into a revenue machine" | Forward reservation email → parse → AI response |
| **Lead Capture Dashboard** | Every inquiry: name, contact, intent, timestamp. Filter, export to Excel | CRM-lite, sortable table |
| **After-Hours Recovery Report** | GM email at **7am** property-local-time: inquiries, recovery %, est. revenue | Scheduled daily report (Cloud Scheduler `30 7 * * *` MYT) |
| **Human Handoff** | AI transfers with full context when complex/complaint/group | Detection + context packaging |

### What AI Handles vs. Transfers
- **AI:** Room availability, rates, FAQs, directions, facilities
- **Human:** Group bookings, complaints, special requests, negotiations

---

## 5. Onboarding & Timeline ("Live in 48 Hours")

| Day | Activity | Who | Effort |
|-----|----------|-----|--------|
| **Day 0** | Discovery Call — room types, rates, FAQs | Hotel | 15 min |
| **Day 1** | SheersSoft builds property KB | SheersSoft | 0 from hotel |
| **Day 1** | Connect channels: WhatsApp, script tag, forward email | Hotel | 30 min |
| **Day 2** | Live — AI handling real inquiries | — | 0 |
| **Day 7** | First Weekly Report to GM | — | Delivered |
| **Day 30** | Full ROI Review — decide to continue or walk away | Hotel | — |

**Critical constraint:** *"No complex integrations. No IT team required."*

---

## 6. Pricing (Website) — Value-Based

> *"B2B customers don't trust cheap software with their business processes."* — Charge 10–30% of value created. RM 9,315 recovered/mo → RM 2,000–3,000 defensible.

| Tier | Price | Target | Includes |
|------|-------|--------|----------|
| **Starter** | RM 1,500/mo | Budget & 3-star, <100 rooms | 1 WhatsApp line, web chat, 500 convos/mo, email support, basic dashboard |
| **Professional** | RM 3,000/mo | 4-star, 100–300 rooms | 2 WhatsApp lines, web chat, email auto-handler, 2,000 convos/mo, priority support, full dashboard + Reports |
| **Enterprise** | RM 5,000+/mo | 5-star, 300+ rooms | Unlimited convos, unlimited WA lines, custom integrations, dedicated account manager, full dashboard + API |

**Pricing model:** Tiered feature-based with clear upgrade path. Pilot is time-limited (30 days), not feature-limited — reduces friction. Free trial or freemium: never both time- and feature-limited.

**Commercial Terms:**
- Free 30-day pilot — no credit card
- Month-to-month after pilot — no contract
- Exceeding limit: notify first; upgrade or queue messages (no surprise charges)
- Annual: 2 months free (contact for details)

---

## 7. ROI & Proof Points

### Website ROI Calculator (Example)
- 30 daily inquiries, RM 230 ADR, 30% after hours → **RM 9,315 estimated monthly revenue recovered**
- OTA commission avoided: RM 1,863

### Case Study: Bukit Bintang City Hotel
> ⚠️ **Unverified benchmark — do not use in sales materials until confirmed.** Replace with Vivatel's real 30-day numbers once available (see `gtm_execution_plan.md` Task E2.4). Publish RM 920 honest estimate rather than RM 12,400 unverified figure.
- **Problem:** "Missing 40% of WhatsApp inquiries during peak hours; 100% after midnight"
- **Benchmark (unverified):** 463 inquiries handled, 92% captured, RM 12,400 est. revenue recovered — pending real Vivatel data to replace or confirm

### Trust Claim
> ⚠️ **"Trusted by hotels recovering RM 50,000+ monthly"** — remove from website until verified by real customer data. Replace with Vivatel's confirmed numbers.

---

## 8. Technology & Security Constraints

| Constraint | Website Commitment |
|------------|--------------------|
| **Response time** | <30 seconds |
| **Languages** | English + Bahasa Malaysia (bilingual) |
| **Setup** | Live in 48 hours |
| **Encryption** | End-to-end (rest + transit) |
| **Data isolation** | Tenant isolation — "Your data never mixes with other properties" |
| **Compliance** | PDPA compliant, built for Malaysian data protection |
| **Audit** | Complete logs of all AI interactions |
| **AI honesty** | "Never fabricates rates. Only quotes rates from verified KB. If unsure → hand off." |

---

## 9. Terminology

| Term | Usage |
|------|-------|
| **Product name** | Nocturn AI (public) |
| **Company** | Sheers Software Sdn Bhd |
| **Metric** | "Revenue Recovery" (not "Revenue Risk") |
| **Role** | "Concierge" (not "Chatbot") |
| **Report** | "After-Hours Recovery Report" / "GM Morning Report" |

---

## 10. FAQ Handling (Website)

| Question | Answer |
|----------|--------|
| Will it sound robotic? | No — trained on hospitality. Bilingual, concise, warm. Handoff when guest wants human. |
| PDPA? | Encrypted, tenant isolated, PDPA compliant, privacy policy published. |
| We already have a website chatbot | Most handle <10% of inquiries. Nocturn captures 90% (WhatsApp, phone, email). |
| Wrong rate information? | Never fabricates. Only quotes from verified KB. Default to handoff if unsure. |
| Setup time? | 48 hours. 30 min from hotel. One line of code for widget. |
| After free pilot? | Hard data. Numbers don't speak → walk away. No contracts. |

---

## 11. What Kills SaaS — Anti-Patterns to Avoid

| # | Killer | Mitigation |
|---|--------|------------|
| 1 | Solving problems nobody will pay for | Validate with 20–30 interviews. Vivatel pilot = first real test. |
| 2 | "Build it and they will come" | Distribution strategy from day one. Case study → demos. |
| 3 | Underpricing | RM 1,500–5,000. B2B doesn't trust cheap. Value-based: 10–30% of value created. |
| 4 | Technical perfectionism | Ship in 28 days. Monolith. Iterate based on feedback. |
| 5 | Ignoring unit economics | Track CAC, LTV, payback. LTV:CAC ≥ 3:1. |
| 6 | Horizontal platform ("Salesforce for hotels") | Vertical: "AI inquiry capture for Malaysian 3–4 star hotels." |
| 7 | Premature scaling | Hire after PMF. No enterprise features before enterprise customers. |
| 8 | Founder conflicts | Equity, roles, decision authority — written before scaling. |
| 9 | Technical debt explosion | Refactoring sprint every 4–5 feature sprints. Document TODOs with business thresholds. |
| 10 | Security until too late | PDPA, encryption, RLS from day one. SOC 2 when enterprise demands. |

---

## 12. Critical Success Patterns

| Pattern | Commitment |
|---------|------------|
| **Metrics-driven from day one** | Activation rate, retention cohorts, North Star Metric (inquiries captured → leads → revenue). |
| **Talk to customers constantly** | Technical founder: 3–5 customer calls/week. Non-negotiable. |
| **Ship fast, learn faster** | Weekly or bi-weekly deployments. Feature flags for safe production testing. |
| **Analytics infrastructure early** | Product analytics (Amplitude/Mixpanel) in month one. Every feature instrumented. |
| **Churn analysis immediately** | Track why every churned customer leaves. > 5% monthly churn = product problem. |
| **Documentation as product** | B2B: poor docs = churn. API docs auto-generated (OpenAPI/Swagger). |

---

## 13. Alignment Checklist for Foundational Docs

Use this section to validate PRD, Build Plan, and Architecture:

- [ ] **Onboarding:** Supports "Live in 48 hours" — KB build + channel connect in <2 days
- [ ] **Languages:** AI explicitly handles English + Bahasa Malaysia
- [ ] **Email:** Handles *forwarded* reservation emails (not just direct sends)
- [ ] **Widget:** Single `<script>` tag, no dependencies, works on WordPress
- [ ] **Pricing tiers:** Starter (RM 1,500), Pro (RM 3,000), Enterprise (RM 5,000+)
- [ ] **Pilot:** 30 days free, no credit card, month-to-month after
- [ ] **Report:** Daily at **7am** property-local-time (Cloud Scheduler `30 7 * * *` MYT); weekly summary Monday
- [ ] **Case study metrics:** Replace RM 12,400 unverified benchmark with Vivatel's real 30-day numbers once available
- [ ] **Product naming:** Nocturn AI (public)
- [ ] **Unit economics:** CAC, LTV, churn tracked from first paying customer
- [ ] **ICP ruthlessness:** No expansion beyond 3–4 star Malaysian hotels until PMF
