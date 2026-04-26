# Nocturn AI — Product Component Breakdown

This document provides a comprehensive breakdown of the Nocturn AI architecture, identifying the core services and dependencies required to deliver consistent results.

## 1. Nocturn Frontend (Next.js)
The primary user interface for hotels, staff, and internal administrators.

*   **SaaS Portal (`/portal`)**: Multi-tenant management area where hotel owners manage their Knowledge Base (KB), team members, and billing subscriptions.
*   **Staff Dashboard (`/dashboard`)**: Operational inbox for managing live guest conversations, capturing leads, and using the AI-powered hybrid co-pilot sidebar for drafting replies.
*   **Admin Dashboard (`/admin`)**: Internal SheersSoft controls for provisioning new tenants, monitoring the onboarding pipeline, and managing global system configurations.
*   **Public Tools**: 
    *   `/audit`: AI-powered leakage calculator for prospective clients.
    *   `/apply`: Intake form for the Founding Cohort program.
*   **Onboarding Wizard (`/welcome`)**: A guided, step-by-step setup process for new hotels to configure their identity and communication channels.

## 2. Nocturn Backend (FastAPI)
The core logic engine and API service.

*   **Core AI Engine**: Handles multi-turn context management, RAG (Retrieval-Augmented Generation) for property knowledge, bilingual support (English/Bahasa Melayu), and intent detection.
*   **Channel Webhooks**: Managed listeners for incoming messages from Meta WhatsApp, Twilio WhatsApp, Email, and Web Chat.
*   **Multi-tenant RBAC**: Secure access control using JWT-based authentication, integrated with Supabase.
*   **Shadow Pilot Engine**: Automated background processing that classifies guest inquiries, aggregates performance metrics, and generates property-relative Day-7 proof reports.
*   **Billing Service**: Integration with Stripe for handling both one-time setup fees and recurring RM 199/month subscriptions.
*   **Internal Scheduler**: Managed periodic tasks for sending daily morning reports, automated follow-ups, and monthly performance insights.

## 3. Middle Services (Specialized Bridges)
Standalone services that handle specific transport or integration logic.

*   **Baileys Bridge (Node.js)**: A specialized transport service that allows Nocturn to link with existing hotel WhatsApp numbers via QR code pairing (using the Baileys library). It manages the session lifecycle and proxies messages to the main backend.

## 4. Data Layer & Storage
*   **Supabase PostgreSQL + pgvector**: Primary relational database with vector search capabilities for the RAG system.
*   **Redis**: High-performance key-value store used for real-time messaging pub/sub, session caching, and rate limiting.
*   **GCP Secret Manager**: Secure storage for sensitive configuration, including API keys for LLM providers and database credentials.

## 5. External Dependencies
Critical third-party services that the product relies on:

*   **Identity**: Supabase Auth (OIDC / Passwordless).
*   **Payments**: Stripe (RM 999 setup fee + RM 199/mo subscription).
*   **Communication**: Meta WhatsApp Cloud API, Twilio, SendGrid (Email).
*   **LLM Providers**: Google Gemini (Primary), OpenAI (Fallback), Anthropic (Fallback).
*   **Inventory (Future)**: Google Sheets (planned for live room availability sync).
