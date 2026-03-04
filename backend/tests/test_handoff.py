
import pytest
from unittest.mock import AsyncMock, patch
from app.services.email import notify_staff_handoff

@pytest.mark.asyncio
async def test_notify_staff_handoff():
    # Mock dependencies
    with patch("app.services.email.send_email", new_callable=AsyncMock) as mock_email:
        with patch("app.services.realtime.realtime_service.publish_handoff", new_callable=AsyncMock) as mock_redis:
            
            await notify_staff_handoff(
                property_id="prop-123",
                conversation_id="conv-456",
                guest_identifier="guest@example.com",
                channel="email",
                guest_name="Guest User",
                conversation_summary="Help me"
            )
            
            # Verify Email sent
            mock_email.assert_awaited_once()
            
            # Verify Redis published
            mock_redis.assert_awaited_once_with(
                property_id="prop-123",
                conversation_id="conv-456",
                guest_name="Guest User",
                channel="email",
                summary="Help me"
            )
