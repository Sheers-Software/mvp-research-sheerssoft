# 🚀 Deployment Guide (Railway/Fly.io)

This guide covers deploying the Nocturn AI Engine to a production environment. We recommend **Railway** for simplicity and built-in Postgres + Redis support.

## Prerequisites
- [Railway CLI](https://docs.railway.app/guides/cli) installed (`npm i -g @railway/cli`)
- GitHub repository connected to Railway (recommended) or use CLI.

## 1. Backend Deployment

1.  **Create a New Project** on Railway.
2.  **Add Database (PostgreSQL)**:
    - Add a PostgreSQL service.
    - Add `pgvector` extension: Connect to DB and run `CREATE EXTENSION vector;`.
3.  **Deploy Backend Service**:
    - select "Empty Service" or "GitHub Repo".
    - Set **Root Directory** to `/backend`.
    - **Variables**:
        - `DATABASE_URL`: `postgresql://...` (use Railway's internal variable `${{Postgres.DATABASE_URL}}`)
        - `OPENAI_API_KEY`: `sk-...`
        - `JWT_SECRET`: Generate a strong secret.
        - `ENVIRONMENT`: `production`
        - `WHATSAPP_VERIFY_TOKEN`: Set your token.
        - `WHATSAPP_API_TOKEN`: Set your token.
    - **Build Command**: (Leave empty if using Dockerfile)
    - **Start Command**: (Leave empty, Dockerfile `CMD` is used).

## 2. Frontend Deployment

1.  **Add Frontend Service**:
    - Connect same GitHub repo.
    - Set **Root Directory** to `/frontend`.
    - **Variables**:
        - `NEXT_PUBLIC_API_URL`: The URL of your deployed Backend service (e.g. `https://backend-production.up.railway.app`).
    - **Build Command**: (Leave empty, Dockerfile is used).
    - **Start Command**: (Leave empty).

## 3. Post-Deployment Steps

1.  **Run Migrations**:
    - Railway Console -> Backend Service -> Connect (Shell).
    - Run: `alembic upgrade head`.
2.  **Create Admin User / Seed Data**:
    - Run: `python -m scripts.seed_vivatel` (optional).

## Troubleshooting

- **Health Check**: Visit `https://<backend-url>/api/v1/health`.
- **Logs**: Check "Deploy Logs" in Railway.
- **CORS**: Ensure `NEXT_PUBLIC_API_URL` matches the frontend domain slightly if using strict CORS (currently set to `["*"]` in `main.py` for dev, update for prod).

## Docker Local Production Test
To test production builds locally:

```bash
# Backend
docker build -t nocturn-backend:prod ./backend
docker run --env-file .env -p 8000:8000 nocturn-backend:prod

# Frontend
docker build -t nocturn-frontend:prod ./frontend
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000 nocturn-frontend:prod
```
