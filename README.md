# SheersSoft AI Inquiry Capture & Conversion Engine — v1.2.0

An AI-powered hotel inquiry capture system that recovers revenue lost after hours and tracks granular ROI.

## v1.2.0: The "High-Fidelity KB" Release
This version introduces a significant upgrade to the knowledge base and retrieval architecture:
- **3000+ entries**: Expanded from 400 to **2,991** professional hospitality Q&A pairs.
- **Gemini Embeddings (3072 Dimensions)**: Switched to `gemini-embedding-001` for 4x higher vector granularity than standard 768-dim models.
- **Direct REST RAG**: Implemented direct REST API integration for state-of-the-art embedding generation, bypassing SDK versioning bottlenecks.

## Architecture

- **Backend:** Python 3.12 + FastAPI
- **Frontend:** Next.js 14 + TypeScript + TailwindCSS
- **Database:** PostgreSQL 16 + pgvector (Semantic AI Search)
- **LLMs:** Google Gemini (Primary), OpenAI GPT-4o-mini & Anthropic (Fallbacks)
- **Channels:** WhatsApp (Meta Cloud API & Twilio), Web Chat Widget, Email (SendGrid)

## Key Features

1. **AI Conversation Engine (RAG):** Answers guest inquiries using a 3,000-entry knowledge-base, captures leads, and hands off complex issues seamlessly.
2. **"Paste & Go" Integrations Setup:** Zero code changes required for integrating Meta, Twilio, SendGrid, and AI credentials. Configured entirely via GCP Secret Manager.
3. **Demo Mode Orchestrator:** Fully isolated environment running on simulated channel data with 100+ native conversation scenarios for flawless sales pitches without touching production. 
4. **Operations Tuning:** Revenue managers can tune AI personas, set required screening questions, and input front desk hourly wages directly via the Dashboard Settings interface.
5. **Advanced Analytics & Export:** 
   - Real-time pipeline calculation estimating Gross Revenue Recovered and Ops Cost Savings.
   - Broad time-scaling filters (Daily, Weekly, Monthly, Quarterly, Yearly, Custom).
   - Generates CSV tabular spreadsheets and exports Canvas-rendered visual PDF reports in-browser.

## Getting Started

1. **Setup Integrations (Phase 0):** Push API keys for Gemini, OpenAI, WhatsApp, Twilio, and SendGrid to GCP Secret Manager (project `nocturn-ai-487207`). See `.env.example` for the list of required secret keys.
2. **Launch the Real Application:**
   ```powershell
   docker-compose up -d --build
   ```
3. **Seed the High-Fidelity Knowledge Base (3000+ entries):**
   ```powershell
   docker exec mvp-research-sheerssoft-demo-backend-1 python scripts/seed_kb_full.py
   ```
4. **Launch the Local Simulated Demo Stack:**
   ```powershell
   .\start_demo.ps1
   ```

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── kb.py            # RAG Retrieval Service (3072-dim)
│   ├── scripts/
│   │   ├── seed_kb_full.py      # Entry point for 3000-doc ingestion
│   │   ├── kb_*.py              # 35 Segmented data files (Hotel, Festive, Homestay)
```

## Sprint Completion Status

Everything from the blueprint and the KB expansion plan has been fully implemented:

- [x] Phase 1-12: Core Application & Live Channels
- [x] Phase 13: 3000-Entry Knowledge Base Expansion ✅
- [x] Phase 14: Gemini 3072-Dimensional Embedding Pipeline ✅
- [x] Phase 15: Vector Storage Strategic Analysis ✅
- [x] Phase 16: Separate Release Branch (v1.2.0) ✅
