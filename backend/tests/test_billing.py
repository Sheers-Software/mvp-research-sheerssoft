"""
Billing endpoint tests (Stripe integration).

Stripe API calls are mocked throughout — no live Stripe account required.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import stripe

from app.auth import get_current_user
from app.database import get_db
from app.main import app


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _mock_user():
    """Minimal authenticated user for dependency override."""
    user = MagicMock()
    user.is_superadmin = False
    user.memberships = []
    return user


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    """Ensure dependency overrides are cleaned up after each test."""
    yield
    app.dependency_overrides.clear()


# ── /checkout tests ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_checkout_requires_auth(client):
    """Unauthenticated requests to /checkout are rejected with 401."""
    resp = await client.post(
        "/api/v1/billing/checkout",
        json={
            "hotel_id": "tenant-abc",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
        },
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_checkout_returns_stripe_url(client):
    """Authenticated checkout returns the Stripe session URL."""
    app.dependency_overrides[get_current_user] = _mock_user

    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/pay/cs_test_abc123"

    with patch("stripe.checkout.Session.create", return_value=mock_session):
        resp = await client.post(
            "/api/v1/billing/checkout",
            json={
                "hotel_id": "tenant-abc",
                "success_url": "https://example.com/success",
                "cancel_url": "https://example.com/cancel",
            },
        )

    assert resp.status_code == 200
    assert resp.json()["checkout_url"] == "https://checkout.stripe.com/pay/cs_test_abc123"


@pytest.mark.asyncio
async def test_checkout_missing_stripe_key_returns_500(client):
    """When stripe_api_key is not configured, /checkout returns 500."""
    app.dependency_overrides[get_current_user] = _mock_user

    with patch("app.services.stripe_service.get_settings") as mock_cfg:
        mock_cfg.return_value.stripe_api_key = ""
        resp = await client.post(
            "/api/v1/billing/checkout",
            json={
                "hotel_id": "tenant-abc",
                "success_url": "https://example.com/success",
                "cancel_url": "https://example.com/cancel",
            },
        )

    assert resp.status_code == 500
    assert "API key" in resp.json()["detail"]


# ── /webhook tests ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_webhook_missing_secret_returns_500(client):
    """When stripe_webhook_secret is not configured, /webhook returns 500."""
    with patch("app.routes.billing.get_settings") as mock_cfg:
        mock_cfg.return_value.stripe_webhook_secret = ""
        resp = await client.post(
            "/api/v1/billing/webhook",
            content=b"{}",
            headers={"Content-Type": "application/json"},
        )

    assert resp.status_code == 500


@pytest.mark.asyncio
async def test_webhook_invalid_signature_returns_400(client):
    """Requests with an invalid Stripe-Signature header return 400."""
    with patch("app.routes.billing.get_settings") as mock_cfg, \
         patch(
             "stripe.Webhook.construct_event",
             side_effect=stripe.SignatureVerificationError("bad sig", "sig_header"),
         ):
        mock_cfg.return_value.stripe_webhook_secret = "whsec_test_secret"
        resp = await client.post(
            "/api/v1/billing/webhook",
            content=b'{"type": "test"}',
            headers={
                "Content-Type": "application/json",
                "stripe-signature": "t=1,v1=invalid",
            },
        )

    assert resp.status_code == 400
    assert "signature" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_webhook_checkout_completed_activates_tenant(client):
    """
    A verified checkout.session.completed event sets subscription_status=active
    and stores the Stripe customer ID on the tenant.
    """
    tenant_id = str(uuid.uuid4())

    mock_tenant = MagicMock()
    mock_tenant.id = uuid.UUID(tenant_id)
    mock_tenant.subscription_status = "trialing"
    mock_tenant.stripe_customer_id = None

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_tenant

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()

    async def _override_db():
        yield mock_db

    app.dependency_overrides[get_db] = _override_db

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": tenant_id,
                "customer": "cus_test_xyz",
            }
        },
    }

    with patch("app.routes.billing.get_settings") as mock_cfg, \
         patch("stripe.Webhook.construct_event", return_value=event):
        mock_cfg.return_value.stripe_webhook_secret = "whsec_test_secret"
        resp = await client.post(
            "/api/v1/billing/webhook",
            content=b'{"type": "checkout.session.completed"}',
            headers={
                "Content-Type": "application/json",
                "stripe-signature": "t=1,v1=valid",
            },
        )

    assert resp.status_code == 200
    assert resp.json()["status"] == "received"
    assert mock_tenant.subscription_status == "active"
    assert mock_tenant.stripe_customer_id == "cus_test_xyz"
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_webhook_unknown_event_type_is_ignored(client):
    """Unhandled event types return 200 without side effects."""
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()

    async def _override_db():
        yield mock_db

    app.dependency_overrides[get_db] = _override_db

    event = {"type": "payment_intent.created", "data": {"object": {}}}

    with patch("app.routes.billing.get_settings") as mock_cfg, \
         patch("stripe.Webhook.construct_event", return_value=event):
        mock_cfg.return_value.stripe_webhook_secret = "whsec_test_secret"
        resp = await client.post(
            "/api/v1/billing/webhook",
            content=b"{}",
            headers={
                "Content-Type": "application/json",
                "stripe-signature": "t=1,v1=valid",
            },
        )

    assert resp.status_code == 200
    mock_db.commit.assert_not_awaited()
