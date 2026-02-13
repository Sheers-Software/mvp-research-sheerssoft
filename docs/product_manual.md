# Nocturn AI – Product Manual & User Stories

## 1. Product Overview
**Nocturn AI** is an automated inquiry capture and revenue recovery engine designed specifically for hotels. It acts as a 24/7 digital concierge that sits on top of a hotel's existing communication channels (WhatsApp, Email, Website), instantly answering guest queries and capturing high-intent leads that would otherwise be lost—especially after hours.

### 1.1 Language Support
The system is fully bilingual and automatically detects the language of the guest's message.
-   **Supported Languages**: English, Bahasa Malaysia.
-   **Dialect Support**: Handles "Manglish" (Malaysian English) and mixed-code switching (e.g., "ada room available tak?").
-   **Behavior**: The AI matches the guest's language. If a guest switches language mid-conversation, the AI adapts instantly.
-   **Limitations**: Extremely slang-heavy local dialects (e.g., Kelantanese dialect) may trigger a fallback to standard Bahasa Malaysia or English.

### Core Value Proposition
- **Recover Revenue:** Captures booking inquiries when staff are unavailable.
- **Instant Response:** Responds to guests in <30 seconds, preventing them from booking competitors.
- **Zero Leakage:** Logs every single interaction as a traceable lead.

---

## 2. Distribution Model
The product is distributed as a **Managed SaaS (Software as a Service)** solution.

### How Users Get Access
1.  **Onboarding (Done-For-You):**
    -   The SheersSoft team provisions the tenant (Property) in the system.
    -   **Knowledge Base Setup:** Hotel provides PDFs/Docs (Policy, Rates, Facilities); SheersSoft ingests them into the AI brain.
    -   **Channel Connection:**
        -   **WhatsApp:** Hotel verifies their Business API number (or allows SheersSoft to host it).
        -   **Email:** Hotel sets up auto-forwarding to the Nocturn AI ingestion address.
        -   **Web Widget:** Hotel's IT/Web team adds a simple `<script>` tag to their existing website.
2.  **Access Credentials:**
    -   The General Manager (GM) and key staff receive a login URL (e.g., `app.nocturn.ai`) and credentials.

---

## 3. Consumption Model
Users "consume" the product in two ways: **Passive Reliance** (the AI doing the work) and **Active Management** (Dashboard & Intervention).

### A. The "Passive" Consumption (AI Engine)
*Most of the value is delivered without the user logging in.*
-   **Guest Interaction:** The AI autonomously handles guest questions about room rates, pool hours, check-in times, etc.
-   **Lead Capture:** When a guest shows booking intent, the AI extracts their Name, Phone, and Intent and saves it to the database.
-   **Handoff Notification:** If the AI is stumped, it triggers a notification (email/dashboard alert) for human staff to intervene.

### B. The "Active" Consumption (Dashboard Workflows)

#### 1. The Morning Coffee Ritual (General Manager)
*Goal: See ROI immediately.*
-   **Login:** GM logs into the dashboard at the start of the day.
-   **The "Money Slide":** Views the **Performance (Today)** cards:
    -   **Est. Revenue Recovered:** Dollar value of leads captured overnight.
    -   **Leads Captured:** Count of potential bookings saved.
    -   **Total Inquiries:** Volume of traffic handled automatically.
-   **Outcome:** GM feels reassured that the system is paying for itself.

#### 2. The Daily Operation (Reservations Staff)
*Goal: Handle complex queries and close leads.*
-   **Live Monitor:** Keeps the **Live Operations** view open.
    -   Watches "Active Conversations" count.
    -   Responds to "Pending Handoffs" where the AI needs help.
-   **Lead Processing:**
    -   Navigates to the **Leads** tab.
    -   Exports the CSV of new leads.
    -   Calls/Emails high-value leads to finalize bookings.
    -   Updates status to "Converted" or "Lost" later.

---

## 4. User Stories

### A. The Guest (End User)
> *"I want immediate answers so I can make a booking decision now, even at 11 PM."*

1.  **As a Guest**, I want to ask about room availability on WhatsApp at midnight and get an instant answer, so I don't book a different hotel that answers faster.
2.  **As a Guest**, I want to know if the pool is open for kids, so I can plan my family trip.
3.  **As a Guest**, I want to be transferred to a human if the AI doesn't understand my specific request (e.g., "wedding block booking").

### B. The General Manager (Buyer/Decision Maker)
> *"I want to prove to the owners that we aren't losing money on missed calls."*

1.  **As a GM**, I want to see a dashboard showing exactly how much potential revenue the AI saved yesterday, so I can justify the software cost.
2.  **As a GM**, I want to know the volume of "After-Hours" inquiries, so I can optimize my staffing schedules.
3.  **As a GM**, I want to see a list of captured leads, so I can ensure my sales team is following up.

### C. The Reservations Staff (Operator)
> *"I want the AI to handle the repetitive FAQs so I can focus on VIPs and complex bookings."*

1.  **As a Staff Member**, I want to see a real-time list of active conversations, so I know if the system is working.
2.  **As a Staff Member**, I want to be notified when a conversation needs my attention (Handoff), so I can jump in and save the guest experience.
3.  **As a Staff Member**, I want to download a CSV of high-intent leads, so I can call them during office hours to close the sale.
4.  **As a Staff Member**, I want to mark a conversation as "Resolved" after I've helped the guest, to keep my queue clean.

### D. The System Administrator (SheersSoft)
> *"I need to safely onboard new properties and ensure data isolation."*

1.  **As an Admin**, I want to create a new Tenant (Property) with their specific Knowledge Base, so they can start using the system customized to their hotel.
2.  **As an Admin**, I want to ensure Property A cannot see Property B's conversations, to maintain data privacy and trust.
