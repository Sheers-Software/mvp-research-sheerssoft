PRODUCT TEAM DIRECTIVES
Your mandate is straightforward: close the gap between what the website promises and what the system actually delivers, then surface hidden value that marketing doesn't know it can sell.

P0 — IMMEDIATE (This Week)
1. Audit and Document Bilingual AI Capability
The website is selling "Bilingual Analysis" and "Manglish" comprehension as a named feature. Your product manual says nothing about language support. This silence is unacceptable regardless of the actual state of the capability.
If the AI does handle Malay/Manglish today:

Write a dedicated section in the product manual titled "Language Support" that specifies exactly which languages and dialects the model handles, what the confidence threshold is before fallback behavior triggers, and what that fallback behavior looks like (does it switch to English, does it handoff, does it apologize).
Build a Malay/Manglish test suite of at minimum 50 real-world guest query patterns. Include code-switching ("Bilik for 2 malam, ada tak?"), local abbreviations, and informal spelling. Run the suite against the current model. Document pass/fail rates.
Identify the top 10 failure patterns and file them as bugs with priority labels.
Share the results — pass rates, failure patterns, and known limitations — with marketing within 5 business days so they can adjust copy to match reality.

If the AI does not reliably handle Malay/Manglish today:

Communicate this to marketing immediately with a clear written summary: "The model can handle basic Malay greetings and simple queries but cannot reliably parse complex Manglish code-switching. Estimated timeline to production-ready bilingual support is [X weeks]."
Do not let marketing continue selling a capability that does not exist. This is a brand integrity issue that will become a revenue integrity issue the moment a pilot hotel tests it in Malay.

Deliverable: Language Capability Assessment document shared with marketing. Due in 5 business days.

2. Co-Define the Revenue Estimation Methodology
The dashboard shows "Est. Revenue Recovered." The website has an ROI calculator. Neither is backed by a documented, defensible formula. You need to own the math.

Define the formula explicitly. Recommended starting point:

Est. Revenue Recovered = (High-Intent Leads Captured in Period) × (Property's Average Booking Value from Knowledge Base) × (Assumed Conversion Rate)
The assumed conversion rate should either be a conservative default (e.g., 20%) or, once you have enough pilot data, a property-specific historical rate.


Expose the formula transparently on the dashboard. Below the "Est. Revenue Recovered" card, add a subtitle or tooltip: "Based on [X] leads × RM [Y] avg. booking × [Z]% est. conversion."
Write up the methodology as a one-page internal document and share it with marketing so the ROI calculator on the website can be calibrated to use the identical logic.
Ensure the numbers a prospect sees on the website calculator and the numbers a pilot customer sees on their dashboard are produced by the same math. Any discrepancy here will be interpreted as dishonesty.

Deliverable: Revenue Estimation Methodology document shared with marketing. Due in 7 business days.

P1 — HIGH PRIORITY (Next 2 Sprints)
3. Build the Daily Summary Email
The website tells GMs they will "wake up and see we saved RM 3,000 in bookings while I slept." The product currently requires a dashboard login to see any performance data. Most independent hotel GMs will not form a daily login habit. You will lose them silently.
Specification:

Scheduled email sent daily at 7:00 AM property-local time.
Contents:

Leads Captured (count, last 24 hours)
Est. Revenue Recovered (RM value, using the formula from Directive 2)
Total Conversations Handled (count)
Pending Handoffs (count, if any, with urgency framing: "X conversations need your team's attention")
One-click CTA button: "View Full Dashboard" linking directly to the authenticated session.


Design the email template in collaboration with marketing. They will provide brand guidelines, tone of voice, and visual style. You own the data pipeline and delivery infrastructure.
The email must be mobile-optimized. Assume it will be read on a phone screen in bed before the GM gets up.

Deliverable: Daily summary email live in production. Target: end of Sprint 2.

4. Build Intelligent Lead Flagging / Prioritization
The website promises the reservation manager will only see conversations flagged as "High Value" or "Complex." The product currently has a binary system: AI handles it, or AI triggers a generic handoff. There is no prioritization, no scoring, no intelligent triage.
Specification:

Implement a lead scoring layer that classifies captured leads by estimated value. At minimum, two tiers:

High Value: Multi-room inquiries, event/wedding mentions, extended-stay requests, or any inquiry where the estimated booking value exceeds a configurable threshold (e.g., 3× the property's average nightly rate).
Standard: All other captured leads.


Surface the classification in the dashboard:

Add a visual indicator (color tag, badge, or icon) next to each conversation/lead in the Live Operations and Leads views.
Add a filter or toggle: "Show High Value Only."
Consider a separate "High Priority" queue in the Pending Handoffs section.


Classification logic should initially be rule-based (keyword detection for "wedding," "group," "corporate," "event," room count > 5, stay duration > 5 nights). You can layer ML-based scoring later once you have enough labeled conversion data.
Document the classification rules in the product manual so that hotel staff understand why something was flagged.

Deliverable: Lead flagging system live in production. Target: end of Sprint 2.

P2 — IMPORTANT (Sprint 3-4)
5. Add a "Booking Confirmed" Status to the Lead Lifecycle
The product currently supports "Converted" and "Lost" statuses. The website's case study claims "30% increase in direct bookings" — a metric your product cannot currently verify or generate.

Add a "Booking Confirmed" status to the lead lifecycle with an optional field for booking value (RM amount) and booking date.
When a staff member marks a lead as "Booking Confirmed" and enters the value, aggregate these into a new dashboard metric: Confirmed Revenue Attributed — the sum of booking values from leads that originated through Nocturn AI.
This gives you a verifiable, product-generated proof point that marketing can use in case studies, sales decks, and the website. It replaces anecdotal claims with system-of-record data.
Over time, this data also feeds back into refining your assumed conversion rate in the revenue estimation formula, making the ROI number more accurate with each passing month.

Deliverable: Booking Confirmed status and Confirmed Revenue metric live. Target: end of Sprint 4.

6. Expose Inquiry Timing Data for Staffing Insights
The product manual states the GM wants to "optimize staffing schedules" based on after-hours inquiry volume. This data already exists in your system — every conversation has a timestamp. You just need to surface it.

Add a simple visualization to the dashboard: Inquiry Volume by Hour — a 24-hour bar chart showing when conversations occur, segmented by "Business Hours" and "After Hours" (configurable per property).
Add a summary stat: After-Hours Inquiry % — e.g., "68% of inquiries arrived outside business hours last month."
This is low engineering effort, high perceived value. It gives the GM an operational insight they cannot get from any other system and creates a data-backed justification for the product that goes beyond lead capture.

Deliverable: Timing analytics live on dashboard. Target: end of Sprint 4.

P3 — BACKLOG (Sprint 5+)
7. Document and Expose Multi-Tenant Security Architecture
The product manual confirms tenant-level data isolation. This is not surfaced anywhere that a prospect or their procurement team can see.

Write a Security & Data Isolation page in the product documentation. Cover:

Tenant-level data segregation model (how it works architecturally at a high level).
Access control (who can see what, role-based permissions).
PDPA (Malaysian Personal Data Protection Act) alignment — what data is collected, how it's stored, retention policy.


Share this document with marketing for use on the website and in enterprise sales materials.

Deliverable: Security documentation complete and shared with marketing. Target: Sprint 5.