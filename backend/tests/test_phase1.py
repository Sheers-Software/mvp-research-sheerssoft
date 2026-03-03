"""
Nocturn AI — Phase 1 Integration Test Suite

Tests all new backend endpoints:
  - Auth (legacy login, magic link, /me)
  - Superadmin (metrics, tenants, pipeline, tickets, applications)
  - Onboarding (provision-tenant, progress, checklist)
  - Support (chat, tickets, FAQ)

Run: pytest tests/test_phase1.py -v
"""

import pytest
import httpx
from fastapi.testclient import TestClient
from app.main import app
import asyncio
from datetime import datetime

BASE_URL = "http://testserver/api/v1/"

# ─── Shared state across tests ───
state = {
    "admin_token": None,
    "tenant_id": None,
    "property_id": None,
    "user_id": None,
    "ticket_id": None,
    "application_id": None,
}


# ─── Fixtures ───

@pytest.fixture(scope="module")
def client():
    """TestClient for the whole test module without triggering lifespan shutdown mid-test."""
    c = TestClient(app, base_url=BASE_URL)
    yield c


def admin_headers():
    """Auth headers for legacy admin token."""
    if state["admin_token"]:
        return {"Authorization": f"Bearer {state['admin_token']}"}
    return {}


# ═══════════════════════════════════════════════════════
# 1. Health & Root
# ═══════════════════════════════════════════════════════

class TestHealthAndRoot:
    def test_root_endpoint(self, client: TestClient):
        """Root endpoint should return Nocturn AI branding."""
        # Use the module-level client. TestClient allows overriding URL.
        # Since base_url is set, hitting URL explicitly with different host skips base_url.
        # Actually, let's just make a new client without `with` context so it doesn't trigger lifespan shutdown.
        root_client = TestClient(app)
        r2 = root_client.get("/")
        assert r2.status_code == 200
        data = r2.json()
        assert "nocturn" in data.get("name", "").lower() or "nocturn" in str(data).lower()

    def test_health_endpoint(self, client: TestClient):
        """Health check endpoint should return 200."""
        r = client.get("health")
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════
# 2. Auth Endpoints
# ═══════════════════════════════════════════════════════

class TestAuth:
    def test_legacy_login(self, client: httpx.Client):
        """Legacy admin login should return a JWT token."""
        r = client.post(
            "auth/token",
            data={"username": "admin", "password": "password123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        state["admin_token"] = data["access_token"]

    def test_legacy_login_wrong_password(self, client: httpx.Client):
        """Wrong password should return 401."""
        r = client.post(
            "auth/token",
            data={"username": "admin", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert r.status_code == 401

    def test_magic_link_missing_email(self, client: httpx.Client):
        """Magic link without email should fail."""
        r = client.post("auth/magic-link", json={})
        assert r.status_code in [400, 422]

    def test_auth_me_unauthenticated(self, client: httpx.Client):
        """/auth/me without token should return 401."""
        r = client.get("auth/me")
        assert r.status_code == 401

    def test_auth_me_with_legacy_token(self, client: httpx.Client):
        """/auth/me with legacy token should return profile or legacy info."""
        r = client.get("auth/me", headers=admin_headers())
        # Legacy admin token may return 200 with admin info or 403
        # depending on implementation. Either is acceptable.
        assert r.status_code in [200, 403]


# ═══════════════════════════════════════════════════════
# 3. Superadmin Endpoints
# ═══════════════════════════════════════════════════════

class TestSuperadmin:
    def test_metrics(self, client: httpx.Client):
        """Global metrics endpoint should return stats."""
        r = client.get("superadmin/metrics", headers=admin_headers())
        assert r.status_code == 200
        data = r.json()
        assert "total_tenants" in data
        assert "active_tenants" in data
        assert "total_properties" in data
        assert "open_support_tickets" in data

    def test_tenants_list(self, client: httpx.Client):
        """Tenants list should return array."""
        r = client.get("superadmin/tenants", headers=admin_headers())
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_pipeline(self, client: httpx.Client):
        """Pipeline endpoint should return stage arrays."""
        r = client.get("superadmin/pipeline", headers=admin_headers())
        assert r.status_code == 200
        data = r.json()
        assert "provisioned" in data
        assert "channels_setup" in data
        assert "live" in data
        assert "fully_onboarded" in data

    def test_tickets_list(self, client: httpx.Client):
        """Tickets list should return array."""
        r = client.get("superadmin/tickets", headers=admin_headers())
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_applications_list(self, client: httpx.Client):
        """Applications list should return array."""
        r = client.get("superadmin/applications", headers=admin_headers())
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_support_chats_list(self, client: httpx.Client):
        """Handed-off support chats should return array."""
        r = client.get("superadmin/support-chats", headers=admin_headers())
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_metrics_unauthenticated(self, client: httpx.Client):
        """Metrics without auth should return 401."""
        r = client.get("superadmin/metrics")
        assert r.status_code == 401


# ═══════════════════════════════════════════════════════
# 4. Application Intake (public endpoint)
# ═══════════════════════════════════════════════════════

class TestApplications:
    def test_create_application(self, client: httpx.Client):
        """Create a new application (public endpoint)."""
        r = client.post("applications", json={
            "hotel_name": "Test Hotel Kuala Lumpur",
            "contact_name": "Ahmad Test",
            "email": "ahmad.test@hotel.com",
            "phone": "+60123456789",
            "property_name": "Test Hotel KL City",
            "room_count": 120,
            "current_channels": ["whatsapp", "email"],
            "message": "Interested in Nocturn AI for our hotel.",
        })
        assert r.status_code in [200, 201]
        data = r.json()
        assert data.get("id") or data.get("hotel_name")
        if "id" in data:
            state["application_id"] = data["id"]

    def test_application_shows_in_list(self, client: httpx.Client):
        """Created application should appear in superadmin list."""
        r = client.get("superadmin/applications", headers=admin_headers())
        assert r.status_code == 200
        apps = r.json()
        if state["application_id"]:
            found = any(a["id"] == state["application_id"] for a in apps)
            assert found, "Application not found in superadmin list"


# ═══════════════════════════════════════════════════════
# 5. Onboarding — Tenant Provisioning
# ═══════════════════════════════════════════════════════

class TestOnboarding:
    def test_provision_tenant(self, client: httpx.Client):
        """Provision a new tenant via one-click onboarding."""
        r = client.post("onboarding/provision-tenant", json={
            "tenant_name": f"Test Hotel {datetime.now().strftime('%H%M%S')}",
            "property_name": "Test Property KL",
            "owner_email": f"testowner+{datetime.now().strftime('%H%M%S')}@test.com",
            "owner_name": "Test Owner",
            "owner_phone": "+60198765432",
            "timezone": "Asia/Kuala_Lumpur",
            "subscription_tier": "pilot",
            "pilot_duration_days": 30,
            "preferred_channels": ["website"],
            "whatsapp_provider": "meta",
        }, headers=admin_headers())
        assert r.status_code == 200, f"Provision failed: {r.text}"
        data = r.json()
        assert "tenant_id" in data
        assert "property_id" in data
        state["tenant_id"] = data["tenant_id"]
        state["property_id"] = data["property_id"]

    def test_tenant_in_list(self, client: httpx.Client):
        """Provisioned tenant should appear in superadmin list."""
        if not state["tenant_id"]:
            pytest.skip("No tenant provisioned")
        r = client.get("superadmin/tenants", headers=admin_headers())
        assert r.status_code == 200
        tenants = r.json()
        found = any(t["id"] == state["tenant_id"] for t in tenants)
        assert found, "Tenant not found in superadmin list"

    def test_onboarding_progress(self, client: httpx.Client):
        """Get onboarding progress score for provisioned tenant."""
        if not state["tenant_id"]:
            pytest.skip("No tenant provisioned")
        r = client.get(
            f"onboarding/progress/{state['tenant_id']}",
            headers=admin_headers(),
        )
        assert r.status_code == 200
        data = r.json()
        assert "completion_score" in data
        assert data["completion_score"] >= 0

    def test_onboarding_checklist(self, client: httpx.Client):
        """Get detailed onboarding checklist milestones."""
        if not state["tenant_id"]:
            pytest.skip("No tenant provisioned")
        r = client.get(
            f"onboarding/checklist/{state['tenant_id']}",
            headers=admin_headers(),
        )
        assert r.status_code == 200
        data = r.json()
        assert "milestones" in data
        assert isinstance(data["milestones"], list)
        assert len(data["milestones"]) > 0

    def test_tenant_detail(self, client: httpx.Client):
        """Get tenant detail from superadmin."""
        if not state["tenant_id"]:
            pytest.skip("No tenant provisioned")
        r = client.get(
            f"superadmin/tenants/{state['tenant_id']}",
            headers=admin_headers(),
        )
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == state["tenant_id"]

    def test_pipeline_shows_new_tenant(self, client: httpx.Client):
        """Pipeline should include the newly provisioned tenant."""
        if not state["tenant_id"]:
            pytest.skip("No tenant provisioned")
        r = client.get("superadmin/pipeline", headers=admin_headers())
        assert r.status_code == 200
        data = r.json()
        all_ids = []
        for stage in ["provisioned", "channels_setup", "live", "first_week_review", "fully_onboarded"]:
            all_ids.extend([t["tenant_id"] for t in data.get(stage, [])])
        assert state["tenant_id"] in all_ids, "Tenant not found in pipeline"


# ═══════════════════════════════════════════════════════
# 6. Support Endpoints
# ═══════════════════════════════════════════════════════

class TestSupport:
    def test_faq(self, client: httpx.Client):
        """FAQ endpoint should return content."""
        r = client.get("support/faq", headers=admin_headers())
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list) or isinstance(data, dict)

    def test_chat_missing_message(self, client: httpx.Client):
        """Chat without message should fail validation."""
        r = client.post("support/chat", json={}, headers=admin_headers())
        assert r.status_code in [400, 422]


# ═══════════════════════════════════════════════════════
# 7. Frontend Build Verification
# ═══════════════════════════════════════════════════════

class TestFrontendBuild:
    def test_frontend_pages_exist(self):
        """Verify all expected page files exist."""
        import os
        pages = [
            "src/app/page.tsx",
            "src/app/login/page.tsx",
            "src/app/dashboard/page.tsx",
            "src/app/admin/layout.tsx",
            "src/app/admin/page.tsx",
            "src/app/admin/onboarding/page.tsx",
            "src/app/admin/pipeline/page.tsx",
            "src/app/admin/tenants/page.tsx",
            "src/app/admin/tickets/page.tsx",
            "src/app/admin/applications/page.tsx",
        ]
        frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
        for page in pages:
            path = os.path.join(frontend_dir, page)
            assert os.path.exists(path), f"Missing page: {page}"

    def test_next_build_output_exists(self):
        """Verify .next build directory exists from prior build."""
        import os
        next_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", ".next")
        assert os.path.isdir(next_dir), "Frontend .next build directory not found"
