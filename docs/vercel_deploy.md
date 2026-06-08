# Deploying the Investor Demo to Vercel (free, $0)

This deploys **only the Next.js frontend** in **demo mode** — a fully self-contained
product demo with seeded data. No backend, no database, no Redis, no API keys, nothing
to pay for. It runs on Vercel's free **Hobby** tier and cannot break mid-pitch because it
has no live dependencies.

> How it works: when `NEXT_PUBLIC_DEMO_MODE=true`, every API call in the app is served
> from `frontend/src/lib/demo/` (seeded data) instead of a backend. See
> `frontend/src/lib/api.ts` and `frontend/src/lib/auth.tsx`.

## One-time setup

1. Push this branch to GitHub (the demo lives on `refactor/investor-ready-vercel`,
   or merge it to `main` first).
2. Go to <https://vercel.com> → sign in with GitHub → **Add New… → Project**.
3. Import this repository.
4. In the import screen, set:
   - **Root Directory**: `frontend`  ← important (the repo root is not the app)
   - **Framework Preset**: Next.js (auto-detected)
   - **Build Command / Install Command**: leave as default (defined in `frontend/vercel.json`)
5. Under **Environment Variables**, add exactly one:

   | Name | Value |
   |------|-------|
   | `NEXT_PUBLIC_DEMO_MODE` | `true` |

   (Do **not** set `NEXT_PUBLIC_API_URL` — in demo mode it is never used.)
6. Click **Deploy**. After ~1–2 minutes you get a live URL like
   `https://your-project.vercel.app`.

## What investors will see

- **Landing page** (`/`) — value prop + an interactive AI concierge chat to try.
- **Demo banner** at the top — switch between the three user planes live:
  - **Property Staff** → `/dashboard` (live ops, leads, ROI)
  - **Hotel Owner** → `/portal` (KB, team, channels, billing, analytics)
  - **SheersSoft Admin** → `/admin` (tenants, pipeline, tickets, system health)

## Updating the demo

Every push to the connected branch triggers an automatic redeploy. To change the seeded
story (numbers, conversations, hotel name), edit `frontend/src/lib/demo/data.ts`.

## Running it locally

```powershell
cd frontend
$env:NEXT_PUBLIC_DEMO_MODE = 'true'
npm install
npm run dev   # http://localhost:3000
```

## Reverting to the real (backend-connected) app

Deploy without `NEXT_PUBLIC_DEMO_MODE` (or set it to anything other than `true`) and set
`NEXT_PUBLIC_API_URL` to your deployed FastAPI backend URL. The demo layer is completely
inert when the flag is off — no behavioral change to the production app.
```
