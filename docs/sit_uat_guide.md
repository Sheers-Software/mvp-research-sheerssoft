# Nocturn AI: System Integration Testing (SIT) & User Acceptance Testing (UAT) Master Plan

---

## Document Control
| Version | Date | Author | Status |
| :--- | :--- | :--- | :--- |
| 1.0 | 2026-02-23 | AI QA Architecture Team | DRAFT |

## 1. Executive Summary
This document outlines the comprehensive testing strategy for the Nocturn AI Inquiry Capture & Conversion Engine. It follows enterprise-grade software delivery lifecycles, separating testing into two distinct phases:
1.  **System Integration Testing (SIT):** Conducted by engineering and QA to ensure all sub-components (Database, Backend API, LLM Engines, Third-Party Channels) communicate seamlessly and securely.
2.  **User Acceptance Testing (UAT):** Conducted by business stakeholders (General Managers, Operations Staff) using production-like data (via the Demo Orchestrator) to validate that business requirements and ROI objectives are met.

---

## 2. System Integration Testing (SIT)

SIT focuses on the technical boundaries, data flow, and error handling between internal modules and external APIs (OpenAI, Gemini, Twilio, Meta, SendGrid).

### 2.1 Environmental Readiness Prerequisites
- [ ] Staging environment deployed matching production architecture (Docker Compose).
- [ ] Test databases seeded with baseline property configurations.
- [ ] Dummy phone numbers (Twilio Sandbox/Meta Test Numbers) configured.
- [ ] Integration credentials secured in GCP Secret Manager (Test Project).

### 2.2 Core Component Integrations

| Test ID | Component | Scenario Description | Expected Outcome | Pass/Fail |
| :--- | :--- | :--- | :--- | :--- |
| **SIT-INT-001** | LLM Engine | Route inquiry to Primary LLM (Gemini) and validate RAG context injection. | Context from property KB is successfully injected; response time < 3 seconds. | |
| **SIT-INT-002** | LLM Engine | Simulate Primary LLM timeout to trigger Fallback LLM (OpenAI/Anthropic). | System automatically retries with secondary model without dropping the user session. | |
| **SIT-INT-003** | Database | High-concurrency lead write simulation (100 simultaneous requests). | Zero database deadlocks; asynchronous SQLAlchemy sessions process queue cleanly. | |
| **SIT-INT-004** | Auth/Security | Execute API actions using cross-tenant tokens (Tenant A trying to read Tenant B's data). | Robust Row-Level Security (RLS) enforcement; API returns 403/404 for unauthorized access. | |
| **SIT-INT-005** | Auth/Security | Verify `x-request-id` headers and structured JSON logging. | Every microservice hop traces the same correlation ID; logs are parsable in GCP Logging. | |

### 2.3 Channel Mux/Demux (Omnichannel)

| Test ID | Component | Scenario Description | Expected Outcome | Pass/Fail |
| :--- | :--- | :--- | :--- | :--- |
| **SIT-CH-001** | WhatsApp (Meta) | Ingest incoming webhook simulating a text message. | Webhook parsed, session identified, message queued for AI processing. | |
| **SIT-CH-002** | WhatsApp (Meta) | Ingest non-supported media type (e.g., location pin or voice note). | Graceful degradation; AI replies asking for text input or triggers handoff flag. | |
| **SIT-CH-003** | Email | Ingest SendGrid parse webhook containing HTML and attachments. | Content is sanitized to plain text; attachments are ignored/stripped securely. | |

---

## 3. User Acceptance Testing (UAT)

UAT is executed by business users to ensure the application solves the correct problems in a usable way. Testing is persona-driven.

### 3.1 Persona A: The Guest (End-User)

*Objective: Seamless, human-like interaction resulting in an answered query or a captured lead.*

**Scenario UAT-G-001: The After-Hours Booking**
1.  **Action:** User messages the WhatsApp number at 2:00 AM (simulated) asking, *"Hi, do you have any suites available for tomorrow night?"*
2.  **Action:** User provides details when prompted (e.g., *"John Doe, john@example.com"*).
3.  **Acceptance Criteria:**
    *   AI responds within 5 seconds.
    *   AI confirms suite availability based on KB context.
    *   AI politely requests contact details to "reserve" or pass to reservations.
    *   Session state persists correctly through multiple turns.

**Scenario UAT-G-002: The Complex Escapade (Handoff)**
1.  **Action:** User asks heavily nuanced question: *"I need to book a block of 15 rooms for a wedding, and 3 need to be wheelchair accessible."*
2.  **Acceptance Criteria:**
    *   AI recognizes the query exceeds standard automated booking limits.
    *   AI politely informs the user that a senior reservations manager will contact them.
    *   Conversation status in Dashboard changes to `needs_attention` (Handoff).

### 3.2 Persona B: Reservations Staff (Operator)

*Objective: Efficient queue management and lead conversion.*

**Scenario UAT-O-001: Managing Handoffs**
1.  **Action:** Staff logs into Dashboard (`app.nocturn.ai`).
2.  **Action:** Filters Conversations by `Status: Handoff`.
3.  **Action:** Reviews the chat history of `UAT-G-002`.
4.  **Action:** Staff clicks "Resolve" after handling the request manually via native channels.
5.  **Acceptance Criteria:**
    *   Chat history is fully visible and accurate.
    *   Resolving the chat removes it from the Active/Handoff queue.

**Scenario UAT-O-002: Lead Extraction**
1.  **Action:** Staff navigates to the Leads module.
2.  **Action:** Exports the lead list generated from `UAT-G-001` to CSV.
3.  **Acceptance Criteria:**
    *   CSV contains accurate parsed data (Name: John Doe, Email: john@example.com, Intent: Suite Booking).

### 3.3 Persona C: General Manager (Business Sponsor)

*Objective: Visibility into ROI and Operations.*

**Scenario UAT-M-001: Morning Coffee Dashboard Review**
1.  **Action:** GM logs in. Evaluates the "Performance (Today)" cards.
2.  **Action:** Changes date filter to "Last 30 Days".
3.  **Acceptance Criteria:**
    *   **Estimated Revenue Recovered** metric accurately reflects the sum of potential bookings captured.
    *   **Operations Hours Saved** calculation (Chats * Avg Handle Time * Wage) is mathematically sound.
    *   UI states do not flicker or crash during heavy date-range aggregations.

**Scenario UAT-M-002: Persona Tuning (Future Proofing)**
1.  **Action:** GM accesses Property Settings.
2.  **Action:** Alters AI strictly to "Concise Professional" instead of "Warm and Friendly".
3.  **Acceptance Criteria:**
    *   Subsequent test chats demonstrate a noticeable shift in NLP generation tone.

---

## 4. Non-Functional Testing (NFT)

| Category | Requirement | Validation Method |
| :--- | :--- | :--- |
| **Performance (Latency)** | 95th percentile response time < 5s. | Load test (e.g., Locust) with simulated Meta API webhooks under 50 TPS. |
| **Scalability** | Support 10,000 active sessions per pod. | Stress testing Kubernetes/Cloud Run autoscaling triggers. |
| **Security (PDPA/GDPR)** | No PII in application logs; DB encryption at rest. | Log sanitization review; GCP Cloud SQL encryption audit. |
| **Resilience (Chaos)** | Database failover. | Terminate primary DB instance; verify read-replicas handle read queries while writing queues back up gracefully without data loss. |

---
## 5. Sign-Off

*Upon execution of this document in the staging/UAT environment, stakeholders must sign off before transitioning the release candidate to Production.*

| Role | Name | Signature | Date |
| :--- | :--- | :--- | :--- |
| Lead Engineer | | | |
| QA Manager | | | |
| General Manager (Client) | | | |
