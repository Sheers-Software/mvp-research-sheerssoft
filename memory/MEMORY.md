# Project Memory — Nocturn AI / SheersSoft

## GCP / Infrastructure

- **GCP Project**: `nocturn-ai-487207` (numeric: `343745766874`)
- **GCP ADC**: Authenticated locally — `gcloud auth application-default login` was run
- **Supabase project ref**: `ramenghkpvipxijhfptp` → URL: `https://ramenghkpvipxijhfptp.supabase.co`
- **Supabase status**: Free tier project — may be PAUSED after inactivity. DB hostname `db.ramenghkpvipxijhfptp.supabase.co` does not resolve when paused. Unpause from Supabase dashboard.

## GCP Secret Manager — Current State

Secrets that **exist** in Secret Manager (`nocturn-ai-487207`):
- DATABASE_URL, GEMINI_API_KEY, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_HOURS
- OPENAI_API_KEY, STRIPE_API_KEY, SUPABASE_ACCESS_TOKEN, SUPABASE_URL (added)
- TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, TWILIO_API_KEY_SID, TWILIO_API_KEY_SECRET
- WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_VERIFY_TOKEN

Secrets **missing** from Secret Manager (need to be added from dashboards):
- `SUPABASE_ANON_KEY` — from Supabase dashboard → Project Settings → API
- `SUPABASE_SERVICE_ROLE_KEY` — same location
- `STRIPE_WEBHOOK_SECRET` — from Stripe dashboard → Developers → Webhooks
- `FERNET_ENCRYPTION_KEY` — generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- `ANTHROPIC_API_KEY`, `SENDGRID_API_KEY`, `WHATSAPP_API_TOKEN`, `WHATSAPP_APP_SECRET` — from respective dashboards

## Database URL Issues

- Stored in Secret Manager with **BOM** (`\ufeff`) prefix — stripped in `config.py` with `.lstrip("\ufeff")`
- Format in Secret Manager: `postgresql://postgres:...@db.ramenghkpvipxijhfptp.supabase.co:5432/postgres`
- Config auto-converts `postgresql://` → `postgresql+asyncpg://`
- When paused, DNS resolution fails for `db.ref.supabase.co`

## Test State

- **test_billing.py**: 7/7 pass (Stripe mocked entirely)
- **test_supabase.py**: 6/6 skip (4 auth tests need SUPABASE_SERVICE_ROLE_KEY; 2 DB tests skip when Supabase is paused)
- **Other integration tests**: 14 failing — all require a running PostgreSQL (either local Docker or unpaused Supabase)
- 27 tests pass, 11 skip, 14 fail (DB-dependent integration tests)

## Key Config Changes Made

- `config.py`: `database_url` default changed to `""` so Secret Manager loads it; BOM stripping added; postgresql:// conversion and fallback moved to AFTER Secret Manager fetch
- `conftest.py`: `setup_db` now wraps in try/except — billing tests pass even without a DB
- `pytest.ini`: Added `asyncio_mode = auto`
- `test_supabase.py`: Split skip guards — DB tests skip on connectivity failure, Auth tests skip on missing keys

## Running Tests

```bash
# Unit + mocked tests (always run):
cd backend && pytest tests/test_billing.py tests/test_bilingual.py tests/test_handoff.py -v

# Integration (need running DB — Docker or unpaused Supabase):
cd backend && pytest tests/test_channels.py tests/test_phase1.py -v

# Supabase live tests (need unpaused Supabase + secrets in GCP SM):
cd backend && pytest tests/test_supabase.py -v
```

## Next Steps Needed

1. **Unpause Supabase project** from dashboard (if paused)
2. **Add to GCP Secret Manager**: SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, STRIPE_WEBHOOK_SECRET, FERNET_ENCRYPTION_KEY
3. **Start Docker** for local integration testing: `docker-compose up -d`
