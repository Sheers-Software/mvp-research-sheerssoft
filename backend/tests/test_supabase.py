"""
Supabase connectivity integration tests.

Auth API tests (create/delete users, magic links) are skipped when
SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY are not available.

DB connectivity tests (postgres reachable, pgvector) run whenever the
DATABASE_URL resolves to a Supabase host (i.e. GCP Secret Manager is
reachable). They are skipped only if the DATABASE_URL still points to
localhost (no real DB configured).

Credentials are never hardcoded — they are loaded via app.config (which
resolves from env vars or GCP Secret Manager project=nocturn-ai-487207).
"""

import uuid

import httpx
import pytest
from sqlalchemy import text

from app.config import get_settings

settings = get_settings()

# ── Skip guards ────────────────────────────────────────────────────────────────

_supabase_auth_configured = bool(
    settings.supabase_url and settings.supabase_service_role_key
)

def _db_is_reachable() -> bool:
    """Quick TCP check: is the Supabase DB hostname resolvable?"""
    import socket
    if "localhost" in settings.database_url or "127.0.0.1" in settings.database_url:
        return False
    try:
        from urllib.parse import urlparse
        parsed = urlparse(settings.database_url)
        socket.getaddrinfo(parsed.hostname, parsed.port or 5432)
        return True
    except Exception:
        return False


_db_is_remote = _db_is_reachable()

_skip_auth = pytest.mark.skipif(
    not _supabase_auth_configured,
    reason="Supabase Auth not configured (SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY missing)",
)

_skip_db = pytest.mark.skipif(
    not _db_is_remote,
    reason="Supabase DB unreachable — project may be paused or DATABASE_URL points to localhost",
)

# ── Shared headers ────────────────────────────────────────────────────────────

def _admin_headers() -> dict:
    return {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
    }


def _anon_headers() -> dict:
    return {
        "apikey": settings.supabase_anon_key,
        "Content-Type": "application/json",
    }


# ── Auth API tests ─────────────────────────────────────────────────────────────

@_skip_auth
@pytest.mark.asyncio
async def test_supabase_auth_health():
    """Supabase Auth service is reachable and returns a healthy status."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.supabase_url}/auth/v1/health",
            headers=_anon_headers(),
            timeout=10.0,
        )

    assert resp.status_code == 200, f"Unexpected status: {resp.status_code} — {resp.text}"
    data = resp.json()
    assert data.get("status") == "ok" or "version" in data


@_skip_auth
@pytest.mark.asyncio
async def test_supabase_admin_api_list_users():
    """Service role key can list users via the Admin Users API."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.supabase_url}/auth/v1/admin/users",
            headers=_admin_headers(),
            params={"page": 1, "per_page": 10},
            timeout=10.0,
        )

    assert resp.status_code == 200, f"Admin API error: {resp.status_code} — {resp.text}"
    data = resp.json()
    assert "users" in data, f"Expected 'users' key in response: {data}"


@_skip_auth
@pytest.mark.asyncio
async def test_supabase_admin_create_and_delete_user():
    """
    End-to-end Admin API: creates a test user then immediately deletes it.
    Verifies the full provisioning path used by /onboarding/provision-tenant.
    """
    test_email = f"ci-test-{uuid.uuid4().hex[:10]}@nocturn-ai-ci.local"
    created_id = None

    async with httpx.AsyncClient() as client:
        # Create
        create_resp = await client.post(
            f"{settings.supabase_url}/auth/v1/admin/users",
            headers=_admin_headers(),
            json={
                "email": test_email,
                "email_confirm": True,
                "user_metadata": {
                    "full_name": "CI Test User",
                    "tenant_id": "ci-test-tenant",
                },
            },
            timeout=10.0,
        )
        assert create_resp.status_code in (200, 201), (
            f"User creation failed: {create_resp.status_code} — {create_resp.text}"
        )
        created_id = create_resp.json().get("id")
        assert created_id, "No user ID returned from Supabase"

        # Confirm the user appears
        get_resp = await client.get(
            f"{settings.supabase_url}/auth/v1/admin/users/{created_id}",
            headers=_admin_headers(),
            timeout=10.0,
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["email"] == test_email

        # Delete
        del_resp = await client.delete(
            f"{settings.supabase_url}/auth/v1/admin/users/{created_id}",
            headers=_admin_headers(),
            timeout=10.0,
        )
        assert del_resp.status_code in (200, 204), (
            f"User deletion failed: {del_resp.status_code} — {del_resp.text}"
        )


@_skip_auth
@pytest.mark.asyncio
async def test_supabase_magic_link_send():
    """
    Magic link endpoint accepts a valid email and returns 200.
    (No email is actually delivered in CI — Supabase queues it.)
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.supabase_url}/auth/v1/magiclink",
            headers=_anon_headers(),
            json={"email": "ci-magiclink-test@nocturn-ai-ci.local"},
            timeout=10.0,
        )

    # 200 = queued, 422 = email not allowed by Supabase settings (also acceptable for CI)
    assert resp.status_code in (200, 422), (
        f"Unexpected magic link response: {resp.status_code} — {resp.text}"
    )


# ── Database connectivity ──────────────────────────────────────────────────────

@_skip_db
@pytest.mark.asyncio
async def test_supabase_postgres_reachable():
    """
    Async SQLAlchemy can execute a trivial query against the Supabase Postgres.
    Confirms DATABASE_URL (loaded from GCP Secret Manager) is valid and reachable.
    """
    from app.database import engine

    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1 AS heartbeat"))
        row = result.fetchone()

    assert row is not None
    assert row[0] == 1


@_skip_db
@pytest.mark.asyncio
async def test_supabase_postgres_pgvector_extension():
    """
    Confirms the pgvector extension is enabled on the Supabase database,
    which is required for KB semantic search.
    """
    from app.database import engine

    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        )
        row = result.fetchone()

    assert row is not None, (
        "pgvector extension is not installed. "
        "Run: CREATE EXTENSION IF NOT EXISTS vector;"
    )
    assert row[0] == "vector"
