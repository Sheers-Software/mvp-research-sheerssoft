# 🧪 Nocturn AI Comprehensive Testing Guide

This guide outlines how to comprehensively test the Nocturn AI Inquiry Capture & Conversion Engine from three distinct perspectives: the **User (Guest)**, the **Operator (Hotel Staff/GM)**, and the **Administrator (IT/SheersSoft)**.

---

## 1. 👤 User (Guest) Perspective Testing

The goal here is to verify that the AI acts as a seamless digital concierge, handling queries accurately, capturing leads, and stepping back when human intervention is needed.

### 1.1 Web Chat Widget
* **Action:** Open the hotel's website where the widget is embedded (or run the frontend locally at `http://localhost:3000` and interact with the floating chat icon).
* **Test Cases:**
  * **Basic Inquiry:** Ask "What time is check-in?" -> *Verify AI answers immediately based on the property's Knowledge Base.*
  * **Multilingual Check:** Switch languages mid-conversation (e.g., reply with "Ada bilik kosong tak malam ni?"). -> *Verify AI switches to Bahasa Malaysia and maintains the context.*
  * **Booking Intent (Lead Capture):** Say "I want to book a Deluxe Room for tomorrow. My phone number is 0123456789." -> *Verify AI acknowledges the booking intent politely and registers the lead.*
  * **Complex Query / Complaint (Handoff):** Say "The air conditioning in my room is broken, and I need a manager right now!" -> *Verify AI apologizes, informs you that human staff will take over, and stops responding automatically.*

### 1.2 WhatsApp Channel
* **Action:** Send a message to the provisioned Twilio/Meta WhatsApp Business number.
* **Test Cases:**
  * Repeat the exact same flows as the Web Chat Widget to ensure parity across channels.
  * **Media Testing:** Send an emoji or a voice note (if supported) to see how the system gracefully handles non-text inputs.

### 1.3 Email Channel (Optional/Future)
* **Action:** Send an email to the property's designated ingestion address.
* **Test Cases:**
  * Send a booking inquiry formatted as an email. -> *Verify the AI responds via email with the correct template and tone.*

---

## 2. 👨‍💼 Operator (Hotel Staff/GM) Perspective Testing

Operators must verify that the dashboard correctly reflects real-time activity, accurately calculates KPIs, and provides intuitive tools for intervention.

### 2.1 The "Morning Coffee" Dashboard Check (GM)
* **Action:** Log into the Next.js frontend (`http://localhost:3000` or production URL) using manager credentials.
* **Test Cases:**
  * **KPI Validation:** Look at the Top Metrics cards (Est. Revenue Recovered, Leads Captured, Active Conversations). -> *Verify the numbers match the simulated/expected traffic.*
  * **Date Filtering:** Change the date filter (e.g., from "Today" to "Last 7 Days"). -> *Verify the metrics and charts update instantly and accurately.*
  * **Analytics Export:** Click the export buttons (CSV or PDF). -> *Verify a valid CSV is downloaded with the correct tabular data, or a visual PDF is generated containing the charts.*

### 2.2 Active Conversation Management (Reservations Staff)
* **Action:** Navigate to the **Conversations** tab.
* **Test Cases:**
  * **Real-time Sync:** While a "Guest" user is chatting on the widget/WhatsApp, watch the conversation update live in the dashboard.
  * **Handoff Alert:** Trigger a handoff from the guest side. -> *Verify the conversation status changes to "Handoff" and is highlighted/filtered correctly.*
  * **Staff Intervention:** Reply to the guest directly through the dashboard (or native WhatsApp Business app). -> *Verify the guest receives the message.*
  * **Resolution:** Click the "Resolve" button on a handed-off conversation. -> *Verify it is removed from the active queue and the guest can start a new AI thread later.*

### 2.3 Lead Processing
* **Action:** Navigate to the **Leads** tab.
* **Test Cases:**
  * Identify the lead captured during the User Testing phase. -> *Verify the Name, Phone Number, and Intent are populated correctly.*
  * Export the leads list to CSV. -> *Verify the export works and the staff member can open it in Excel/Google Sheets.*

---

## 3. ⚙️ Administrator Perspective Testing

Administrators focus on deployment, data isolation, integrations, and automated verifications to ensure system health and security.

### 3.1 Demo Orchestration & Simulation (Pre-Sales Testing)
* **Action:** Run the fully isolated demo environment.
* **Test Cases:**
  1. Execute `.\start_demo.ps1` from the project root. -> *Verify Docker Compose builds and starts the `-demo` containers without errors.*
  2. Run the Node.js simulation script: `node scripts/simulate_demo.mjs`. -> *Verify the script successfully authenticates, creates a demo property, and processes 100 seeded conversations (categorized by Room Inquiry, Complaints, Booking Requests, etc.). Check the terminal output for success rates.*
  3. Validate that the demo database now contains the populated leads, conversations, and analytics data without polluting the production database.

### 3.2 Automated UAT & Pipeline Scripts
* **Action:** Run the suite of Python verification scripts located in `scripts/`.
* **Test Cases:**
  * Run `python scripts/uat_scenario_pilot.py`. -> *Verify an end-to-end flow executes synchronously (auth -> fetch properties -> guest chat -> handoff trigger -> dashboard metric validation -> staff resolution) passing all assertions.*
  * Run `python scripts/verify_production_readiness.py`. -> *Verify health checks, telemetry headers, property schema (e.g., `deleted_at` field), and access controls are intact.*

### 3.3 Security & Integrations (GCP Secret Manager)
* **Action:** Check configuration loading.
* **Test Cases:**
  * Stop the backend container, remove the local `.env` file, and ensure GCP credentials are provided. Start the container. -> *Verify the application boots successfully by dynamically pulling secrets (Gemini, SendGrid, Twilio, Meta) from GCP Secret Manager, demonstrating the "Paste & Go" architecture.*
  * **Multi-Tenant RLS (Row-Level Security):** Run `python scripts/verify_rls_isolation.py`. -> *Verify that Property A's API token cannot read or mutate Property B's conversations or leads.*

---

**End of Testing Guide.**
*Regular execution of these manual and automated tests ensures Nocturn AI remains highly reliable and delivers on its revenue recovery promises.*
