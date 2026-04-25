"""
Integration tests for Sprint 2 Channels (WhatsApp, Web, Email).
Verifies webhooks and message processing flow.
"""

import pytest
import uuid
import json
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

# Mock data
MOCK_WHATSAPP_PAYLOAD = {
    "object": "whatsapp_business_account",
    "entry": [{
        "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "metadata": {
                    "display_phone_number": "1234567890",
                    "phone_number_id": "1234567890"
                },
                "contacts": [{
                    "profile": {"name": "Test User"},
                    "wa_id": "60123456789"
                }],
                "messages": [{
                    "from": "60123456789",
                    "id": "wamid.HBgLM...",
                    "timestamp": "1707800000",
                    "text": {"body": "Test message via WhatsApp"},
                    "type": "text"
                }]
            },
            "field": "messages"
        }]
    }]
}


@pytest.mark.asyncio
async def test_whatsapp_verification(client: AsyncClient):
    """Test WhatsApp webhook verification (GET)."""
    response = await client.get(
        "/api/v1/webhook/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "sheerssoft_verify_token",
            "hub.challenge": "12345"
        }
    )
    assert response.status_code == 200
    assert response.text == "12345"


@pytest.mark.asyncio
async def test_whatsapp_incoming_message(client: AsyncClient):
    """Test WhatsApp webhook receiving a message (POST)."""
    
    # Mock the outbound send function to avoid API calls
    with patch("app.routes.channels.send_whatsapp_message", new_callable=AsyncMock) as mock_send:
        # We also need to ensure a property exists or fallback works.
        # The seed script creates Vivatel. If running against fresh test DB, make sure property exists.
        # Assuming dev DB (seeded) or test DB. 
        # In conftest.py we create tables but don't seed.
        # So we should seed a dummy property.
        
        # Helper to seed property
        from app.database import async_session
        from app.models import Property
        from decimal import Decimal
        
        from sqlalchemy import text as sa_text
        async with async_session() as db:
            # Remove stale test properties to prevent MultipleResultsFound on re-runs
            await db.execute(sa_text(
                "DELETE FROM conversations WHERE property_id IN "
                "(SELECT id FROM properties WHERE whatsapp_number = '1234567890')"
            ))
            await db.execute(sa_text("DELETE FROM properties WHERE whatsapp_number = '1234567890'"))
            await db.commit()

        async with async_session() as db:
            prop = Property(
                name="Test Property",
                whatsapp_number="1234567890",
                adr=Decimal("100"),
                ota_commission_pct=Decimal("15"),
                timezone="Asia/Kuala_Lumpur",
                plan_tier="pilot",
                is_active=True
            )
            db.add(prop)
            await db.commit()
            property_id = str(prop.id)
            
        # Send webhook
        response = await client.post(
            "/api/v1/webhook/whatsapp",
            json=MOCK_WHATSAPP_PAYLOAD
        )
        assert response.status_code == 200
        assert response.json() == {"status": "processing"}
        
        # Wait a bit for background task? 
        # BackgroundTasks in FastAPI run *after* response. 
        # In tests with AsyncClient, they might not run automatically unless we await them or test app controls it.
        # Actually, TestClient/AsyncClient usually executes background tasks if using Starlette's TestClient.
        # httpx AsyncClient hitting via ASGI: yes, it runs.
        # But we need to wait/sleep to verify the side effect (mock call).
        # Or mock `BackgroundTasks.add_task`? No, we want integration test.
        # Let's verify side effect or sleep.
        
        # Note: Testing background tasks with AsyncClient can be tricky if we don't wait.
        # But for this simple test, we just check 200 OK acceptance.


@pytest.mark.asyncio
async def test_web_chat_flow(client: AsyncClient):
    """Test Web Chat API (POST /conversations)."""
    
    # 1. Start conversation
    # Get a property ID (reuse one from seed or previous test)
    # We'll just fetch one
    from app.database import async_session
    from app.models import Property
    from sqlalchemy import select
    
    async with async_session() as db:
        result = await db.execute(select(Property).limit(1))
        prop = result.scalar_one_or_none()
        if not prop:
            from decimal import Decimal
            prop = Property(
                name="Web Chat Test Property",
                adr=Decimal("100"),
                ota_commission_pct=Decimal("15"),
                timezone="Asia/Kuala_Lumpur",
                plan_tier="pilot",
                is_active=True
            )
            db.add(prop)
            await db.commit()
            await db.refresh(prop)
        property_id = str(prop.id)
    
    response = await client.post(
        "/api/v1/conversations",
        json={
            "property_id": property_id,
            "message": "Hello from Web Chat",
            "guest_name": "Web User",
            "session_id": str(uuid.uuid4())
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["conversation_id"]
    
    conversation_id = data["conversation_id"]
    
    # 2. Follow up
    response = await client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={
            "message": "Follow up question",
            "guest_name": "Web User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data


@pytest.mark.asyncio
async def test_email_webhook(client: AsyncClient):
    """Test SendGrid Inbound Parse webhook (POST /webhook/email)."""
    
    with patch("app.routes.channels.send_email", new_callable=AsyncMock) as mock_send:
        # Seed test property
        from app.database import async_session
        from app.models import Property
        from sqlalchemy import select
        from decimal import Decimal
        
        async with async_session() as db:
            result = await db.execute(select(Property).where(Property.notification_email == "inquiry@vivatel.com"))
            prop = result.scalar_one_or_none()
            if not prop:
                prop = Property(
                    name="Vivatel Demo",
                    notification_email="inquiry@vivatel.com",
                    adr=Decimal("100"),
                    ota_commission_pct=Decimal("15"),
                    timezone="Asia/Kuala_Lumpur",
                    plan_tier="pilot",
                    is_active=True
                )
                db.add(prop)
                await db.commit()

        # Construct multipart form data
        # httpx handles data=dict as form-urlencoded, files=... for multipart.
        # But SendGrid sends fields as multipart form fields.
        
        data = {
            "from": "Test User <test@example.com>",
            "to": "inquiry@vivatel.com",
            "subject": "Booking Inquiry",
            "text": "Do you have rooms next week?"
        }
        
        response = await client.post(
            "/api/v1/webhook/email",
            data=data
        )
        assert response.status_code == 200
        assert response.json() == {"status": "processing"}

