# Walkthrough: Live WhatsApp Demo Support via Twilio

This document details the successful implementation of the live sales demo stack, allowing the Nocturn AI sales team to demo the product live to prospects using real WhatsApp interactions via Twilio.

## 1. Architecture Changes

To support live interaction without affecting the production stack, we developed an isolated demonstration stack with Twilio routing:

-   **Demo `.env` Configuration**: We scrubbed actual secrets from the tracked `.env.demo` file. During runtime, the application uses Pydantic Settings to automatically fallback and securely fetch the real `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `OPENAI_API_KEY`, and `GEMINI_API_KEY` directly from Google Cloud Secret Manager (`nocturn-ai-487207` project).
-   **Twilio Bypass**: In `demo` mode, the backend now bypasses the rigorous Twilio Webhook X-Signature checks. This is necessary because routing webhook traffic through reverse proxy tunnels alters the host headers and causes the Twilio SDK's signature validator to fail securely. Since the demo stack is not production, bypassing this check is pragmatic and safe.
-   **Database Seeding**: The `seed_demo_data.py` script was updated to dynamically set the `whatsapp_provider` to `"twilio"` and populate the `twilio_phone_number` if configured in the environment variables, ensuring the `Grand Horizon Resort` demo property routes properly via Twilio instead of the default mock simulator.

## 2. Orchestration & Tunneling

We created a new orchestration script: `start_live_demo.ps1`.
This script:
1.  Validates that AI keys and Twilio credentials exist in the environment or Secret Manager.
2.  Boots the `docker-compose.demo.yml` stack (Postgres, Redis, Backend, Frontend).
3.  Instructs the user to run a tunneling proxy to expose port `8001` securely.

> [!CAUTION]
> **Important Note on Proxy Tools**: We discovered that tools like `localtunnel` inject a mandatory "Splash Screen" or click-through warning page for the first visitor. Twilio's HTTP Webhook client cannot bypass this, leading to failed webhooks. Always use **Cloudflare Tunnels (`cloudflared`)** or **Ngrok** for the demo stack to ensure Twilio can successfully reach the API.

## 3. End-to-End Testing & Bug Fixes

During validation, two major bugs were discovered and fixed:

1.  **GCP Secret Manager Local ADC Crash**: When spinning up the demo stack locally, the fallback mechanism crashed if Google Cloud Application Default Credentials (ADC) weren't found locally. We added error handling in `backend/app/config.py` to gracefully skip GCP secret fetching if the client fails to initialize.
2.  **Twilio Pydantic Property Dropout**: Pydantic's `BaseSettings` was implicitly dropping the `TWILIO_PHONE_NUMBER` environment variable because it wasn't explicitly declared in the class. As a result, the backend was passing an empty `From` number back to Twilio, causing Twilio to reply with `400 Bad Request`. `twilio_phone_number` was added to `Settings` to fix the outbound payload.

## 4. How to Conduct a Live Demo

1.  Run `.\start_live_demo.ps1` in a powershell terminal.
2.  In a separate terminal, launch a cloudflare tunnel: `cloudflared tunnel --url http://localhost:8001`
3.  Copy the generated `.trycloudflare.com` URL.
4.  Navigate to the Twilio Console -> Messaging -> Try it out -> Send a WhatsApp Message -> **Sandbox settings**.
5.  Paste the URL into the **"WHEN A MESSAGE COMES IN"** field, appending `/api/v1/webhook/twilio/whatsapp`. Hit **Save**.
6.  The prospect can now message the Twilio sandbox number from their own phone and receive real, live AI concierge responses!
