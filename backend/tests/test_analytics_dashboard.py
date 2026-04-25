
import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import text
from app.models import Property, Conversation, Lead, Message
from app.database import async_session

@pytest.mark.asyncio
async def test_analytics_revenue_calculation(client):
    """
    Test that the money slide revenue is calculated correctly:
    - Sum of Lead.estimated_value for after-hours leads
    - Fallback to Property.ADR if estimated_value is None
    """
    # 1. Setup Data
    async with async_session() as db:
        # Clean up existing data (order matters for FK constraints)
        await db.execute(text("DELETE FROM leads"))
        await db.execute(text("DELETE FROM messages"))
        await db.execute(text("DELETE FROM shadow_pilot_conversations"))
        await db.execute(text("DELETE FROM shadow_pilot_analytics_daily"))
        await db.execute(text("DELETE FROM conversations"))
        await db.execute(text("DELETE FROM analytics_daily"))
        await db.execute(text("DELETE FROM kb_documents"))
        await db.execute(text("DELETE FROM onboarding_progress"))
        await db.execute(text("DELETE FROM properties"))
        await db.commit()

        # Create Property
        prop = Property(
            name="Revenue Hotel",
            adr=Decimal("200.00"),
            plan_tier="business"
        )
        db.add(prop)
        await db.flush()
        pid = prop.id
        
        # Create Conversations (After Hours)
        # Conv 1: High value lead
        conv1 = Conversation(property_id=pid, channel="web", is_after_hours=True, started_at=datetime.now(timezone.utc))
        db.add(conv1)
        await db.flush()
        
        lead1 = Lead(
            property_id=pid, conversation_id=conv1.id, 
            status="new", estimated_value=Decimal("500.00"),
            captured_at=datetime.now(timezone.utc)
        )
        db.add(lead1)
        
        # Conv 2: Standard lead (no value set -> fallback to ADR 200)
        conv2 = Conversation(property_id=pid, channel="web", is_after_hours=True, started_at=datetime.now(timezone.utc))
        db.add(conv2)
        await db.flush()
        
        lead2 = Lead(
            property_id=pid, conversation_id=conv2.id, 
            status="new", estimated_value=None, # Should use ADR
            captured_at=datetime.now(timezone.utc)
        )
        db.add(lead2)
        
        # Conv 3: Before hours (Should NOT count)
        conv3 = Conversation(property_id=pid, channel="web", is_after_hours=False, started_at=datetime.now(timezone.utc))
        db.add(conv3)
        await db.flush()
        
        lead3 = Lead(
            property_id=pid, conversation_id=conv3.id, 
            status="new", estimated_value=Decimal("1000.00"),
            captured_at=datetime.now(timezone.utc)
        )
        db.add(lead3)
        
        await db.commit()
        
    # 2. Call API
    # We need a token. Using the mock auth in tests or generic client if auth disabled/mocked.
    # conftest.py usually sets up client. 
    # If auth is required, we need to mock verify_jwt or user.
    # For now, let's assume the client fixture handles it or we mock the dependency.
    
    from app.auth import verify_jwt
    from app.main import app
    
    # Override auth to return a valid user
    app.dependency_overrides[verify_jwt] = lambda: {"sub": "admin"}
    
    response = await client.get("/api/v1/analytics/dashboard")
    
    assert response.status_code == 200
    data = response.json()
    
    # 3. Verify
    # Expected Revenue: 500 (lead1) + 200 (lead2 fallback) = 700
    # Lead 3 is ignored (not after hours)
    
    assert "estimated_revenue_recovered" in data
    # analytics.py applies 20% conversion rate: (500 + 200) * 0.20 = 140.0
    assert abs(data["estimated_revenue_recovered"] - 140.0) < 0.1
    assert data["leads_captured"] == 3 # All leads captured today

    assert data["after_hours_inquiries"] == 2 # Conv1, Conv2
    
    # Verify Operations View Metrics
    assert "active_conversations" in data
    assert "handed_off_conversations" in data
    
    # We created 3 conversations. 
    # By default status is "active". 
    # Conv1, Conv2, Conv3 are all active.
    assert data["active_conversations"] == 3
    assert data["handed_off_conversations"] == 0
