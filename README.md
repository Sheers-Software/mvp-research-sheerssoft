# SheersSoft AI Inquiry Capture & Conversion Engine

An AI-powered hotel inquiry capture system that recovers revenue lost after hours.

## Architecture

- **Backend:** Python 3.12 + FastAPI (single container)
- **Frontend:** Next.js 14 + TypeScript + TailwindCSS
- **Database:** PostgreSQL 16 + pgvector (semantic search)
- **LLM:** Google Gemini (Primary), OpenAI GPT-4o-mini & Anthropic (Fallbacks)
- **Channels:** WhatsApp (Meta Cloud API), Web Chat Widget, Email (SendGrid)

## Key Features (New)
- **Lead Flagging & Prioritization:**
  - Auto-flags "High Value" leads (Weddings, Groups, Long stays).
  - Identifies "Action Required" conversations (e.g., unhappy guests).
- **Daily Intelligence:**
  - Automated daily email report to GM/Reservations.
  - Highlights revenue opportunities and urgent handoffs.
- **Sales Demo Construction Kit:**
  - `scripts/seed_demo_data.py`: Resets DB to a "Golden State" for demos.
  - `start_demo.ps1`: One-click launcher for the entire stack.
- **Enhanced Dashboard:**
  - Unified inbox for managing WhatsApp conversations.
  - Real-time lead tracking and status updates.
  - Full TypeScript migration for improved reliability.

## Sales Demo Mode

To run a full local demo for a client:

1. **Launch the Stack:**
   ```powershell
   .\start_demo.ps1
   ```
   This will:
   - Start Backend & Frontend.
   - Wipe the DB and seed "Grand Horizon Resort" data.
   - Populate 30 days of analytics history.

2. **Access the Dashboard:**
   - URL: http://localhost:3000
   - Login: `admin` / `password123`

3. **Follow the Script:**
   - See `docs/sales_demo_script.md` for the step-by-step presentation flow.

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── database.py          # Async SQLAlchemy engine
│   │   ├── models.py            # Database models (6 entities)
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── routes.py            # All API endpoints
│   │   └── services/
│   │       ├── __init__.py      # KB ingestion + RAG search
│   │       ├── conversation.py  # AI conversation engine
│   │       └── analytics.py     # Daily analytics aggregation
│   ├── scripts/
│   │   ├── seed_demo_data.py    # Sales Demo "Golden State" seeder
│   │   ├── simulate_demo_flow.py# Automated backend verification
│   │   └── seed_vivatel.py      # Pilot property seed data
│   ├── alembic/                 # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── docs/                        # Research & playbooks
├── docker-compose.yml
└── .gitignore
```

## Sprint Status

- [x] **Sprint 1:** AI Conversation Core (The Brain Works)
- [x] **Sprint 2:** WhatsApp + Web Widget + Email (Guests Can Reach Us)
- [x] **Sprint 3:** Dashboard + Analytics + Reports (The GM Sees the Money)
- [x] **Sprint 4:** Sales Demo Mode + Pilot Hardening (Ready for Show & Tell)



