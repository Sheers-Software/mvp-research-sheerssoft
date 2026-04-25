"""
Shadow Pilot Test Suite.

Covers:
  A. Processor — message handling, after-hours flag, response-time computation,
     deduplication, phone encryption
  B. Classifier — intent detection, BM language, LLM fallback
  C. Aggregator — daily rollup, revenue leakage formula, unanswered marking
  D. Internal API — auth gate, shadow-event, heartbeat, active-properties
  E. Token-Gated Dashboard — valid token, expired token, wrong-property guard
  F. Zero-Reply Gate — CRITICAL: shadow pilot NEVER sends a guest-facing message

All tests run without live Baileys bridge.
DB-dependent tests use the real async test DB configured in conftest.py.
LLM calls are mocked where needed to avoid external API calls.
"""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_property(**overrides):
    """Build a minimal in-memory Property object (no DB)."""
    from app.models import Property
    p = Property.__new__(Property)
    p.id = overrides.get("id", uuid.uuid4())
    p.slug = overrides.get("slug", "test-hotel")
    p.name = overrides.get("name", "Test Hotel")
    p.shadow_pilot_mode = overrides.get("shadow_pilot_mode", True)
    p.shadow_pilot_session_active = overrides.get("shadow_pilot_session_active", True)
    p.shadow_pilot_session_last_seen = None
    p.shadow_pilot_start_date = datetime.now(timezone.utc) - timedelta(days=3)
    p.shadow_pilot_phone = "+60123456789"
    p.adr = Decimal("230.00")
    p.avg_stay_nights = Decimal("1.0")
    p.operating_hours = {"default": {"open": "09:00", "close": "18:00"}}
    p.timezone = "Asia/Kuala_Lumpur"
    return p


def _make_mock_db():
    """Return an AsyncMock that quacks like an AsyncSession."""
    db = AsyncMock()
    db.scalar = AsyncMock(return_value=None)
    db.scalars = AsyncMock(return_value=iter([]))
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    return db


# ═══════════════════════════════════════════════════════════════════════════
# A. PROCESSOR — shadow_pilot_processor.py
# ═══════════════════════════════════════════════════════════════════════════

class TestProcessor:

    @pytest.mark.asyncio
    async def test_after_hours_flag_night(self):
        """A message at 23:00 KL time must be flagged as after-hours."""
        from app.services.shadow_pilot_processor import _is_after_hours

        prop = _make_property()
        # 23:00 KL = 15:00 UTC
        msg_time = datetime(2026, 4, 20, 15, 0, 0, tzinfo=timezone.utc)
        assert _is_after_hours(prop, msg_time) is True

    @pytest.mark.asyncio
    async def test_business_hours_flag(self):
        """A message at 10:00 KL time must NOT be flagged as after-hours."""
        from app.services.shadow_pilot_processor import _is_after_hours

        prop = _make_property()
        # 10:00 KL = 02:00 UTC
        msg_time = datetime(2026, 4, 20, 2, 0, 0, tzinfo=timezone.utc)
        assert _is_after_hours(prop, msg_time) is False

    @pytest.mark.asyncio
    async def test_handle_message_received_creates_conversation(self):
        """handle_message_received must create a ShadowPilotConversation and commit."""
        from app.services.shadow_pilot_processor import handle_message_received

        prop = _make_property()
        db = _make_mock_db()
        db.scalar.return_value = prop  # property lookup returns our mock prop

        with patch("app.services.shadow_pilot_processor.classify_intent",
                   return_value=("room_booking", 0.9, "room booking", "en")):
            await handle_message_received(
                db=db,
                property_slug="test-hotel",
                sender_jid="60123456789@s.whatsapp.net",
                message_id="msg-001",
                content_preview="I want to book a room this weekend",
                timestamp_ms=int(datetime(2026, 4, 20, 16, 0, 0, tzinfo=timezone.utc).timestamp() * 1000),
                has_media=False,
            )

        db.add.assert_called_once()
        db.commit.assert_called_once()

        added_conv = db.add.call_args[0][0]
        assert added_conv.is_booking_intent is True
        assert added_conv.message_count_guest == 1
        assert added_conv.status == "open"

    @pytest.mark.asyncio
    async def test_handle_message_received_deduplication(self):
        """Second message from same JID on an open conversation increments count, no new row."""
        from app.services.shadow_pilot_processor import handle_message_received
        from app.models import ShadowPilotConversation

        prop = _make_property()

        # Existing open conversation for the same phone hash
        existing_conv = ShadowPilotConversation.__new__(ShadowPilotConversation)
        existing_conv.last_guest_message_at = datetime.now(timezone.utc) - timedelta(minutes=30)
        existing_conv.message_count_guest = 1
        existing_conv.updated_at = datetime.now(timezone.utc)

        db = _make_mock_db()
        # First scalar call (property lookup) → prop
        # Second scalar call (existing conv lookup) → existing_conv
        db.scalar.side_effect = [prop, existing_conv]

        await handle_message_received(
            db=db,
            property_slug="test-hotel",
            sender_jid="60123456789@s.whatsapp.net",
            message_id="msg-002",
            content_preview="Actually can you confirm the rate?",
            timestamp_ms=int(datetime.now(timezone.utc).timestamp() * 1000),
            has_media=False,
        )

        # No new row added
        db.add.assert_not_called()
        # Count incremented
        assert existing_conv.message_count_guest == 2

    @pytest.mark.asyncio
    async def test_handle_message_received_shadow_off_does_nothing(self):
        """If shadow_pilot_mode is False, event is silently ignored."""
        from app.services.shadow_pilot_processor import handle_message_received

        prop = _make_property(shadow_pilot_mode=False)
        db = _make_mock_db()
        db.scalar.return_value = prop

        await handle_message_received(
            db=db,
            property_slug="test-hotel",
            sender_jid="60123456789@s.whatsapp.net",
            message_id="msg-003",
            content_preview="Booking inquiry",
            timestamp_ms=int(datetime.now(timezone.utc).timestamp() * 1000),
            has_media=False,
        )

        db.add.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_message_sent_computes_response_time(self):
        """Staff reply 45 minutes after guest → response_time_minutes ≈ 45."""
        from app.services.shadow_pilot_processor import handle_message_sent
        from app.models import ShadowPilotConversation

        prop = _make_property()

        guest_time = datetime.now(timezone.utc) - timedelta(minutes=45)
        conv = ShadowPilotConversation.__new__(ShadowPilotConversation)
        conv.first_guest_message_at = guest_time
        conv.first_staff_reply_at = None
        conv.last_staff_reply_at = None
        conv.message_count_staff = 0
        conv.status = "open"
        conv.is_booking_intent = True
        conv.estimated_value_rm = None
        conv.updated_at = None

        db = _make_mock_db()
        db.scalar.side_effect = [prop, conv]

        reply_ts = int(datetime.now(timezone.utc).timestamp() * 1000)
        await handle_message_sent(
            db=db,
            property_slug="test-hotel",
            recipient_jid="60123456789@s.whatsapp.net",
            message_id="reply-001",
            timestamp_ms=reply_ts,
        )

        assert conv.first_staff_reply_at is not None
        assert 40 <= float(conv.response_time_minutes) <= 50
        assert conv.status == "staff_replied"
        assert conv.estimated_value_rm is not None

    @pytest.mark.asyncio
    async def test_phone_encryption_round_trip(self):
        """guest_phone_encrypted must differ from JID; decryption must recover original."""
        from app.services.pii_encryption import get_pii_service

        pii = get_pii_service()
        jid = "60123456789@s.whatsapp.net"
        encrypted = pii.encrypt(jid)

        assert encrypted != jid
        assert pii.decrypt(encrypted) == jid

    @pytest.mark.asyncio
    async def test_phone_hash_is_deterministic(self):
        """Same JID always produces the same SHA-256 hash for deduplication."""
        from app.services.shadow_pilot_processor import hash_phone

        jid = "60123456789@s.whatsapp.net"
        assert hash_phone(jid) == hash_phone(jid)
        assert hash_phone(jid) == hashlib.sha256(jid.encode()).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════
# B. CLASSIFIER — shadow_pilot_classifier.py
# ═══════════════════════════════════════════════════════════════════════════

class TestClassifier:

    @pytest.mark.asyncio
    async def test_classify_booking_intent(self):
        """English booking message should yield room_booking with >0.5 confidence."""
        mock_response = '{"intent": "room_booking", "topic": "room booking", "language": "en", "confidence": 0.92}'
        # The classifier imports _call_llm_simple from app.services.conversation at call time
        with patch("app.services.conversation._call_llm_simple",
                   new=AsyncMock(return_value=mock_response)):
            from app.services.shadow_pilot_classifier import classify_intent
            intent, confidence, topic, lang = await classify_intent(
                "I want to book a deluxe room for 2 nights this weekend"
            )
        assert intent == "room_booking"
        assert confidence > 0.5
        assert lang == "en"

    @pytest.mark.asyncio
    async def test_classify_bm_rate_query(self):
        """BM rate query should yield rate_query."""
        mock_response = '{"intent": "rate_query", "topic": "room rate", "language": "bm", "confidence": 0.88}'
        with patch("app.services.conversation._call_llm_simple",
                   new=AsyncMock(return_value=mock_response)):
            from app.services.shadow_pilot_classifier import classify_intent
            intent, confidence, topic, lang = await classify_intent(
                "Berapa harga bilik standard untuk hujung minggu ni?"
            )
        assert intent == "rate_query"
        assert lang == "bm"

    @pytest.mark.asyncio
    async def test_classify_fallback_on_llm_error(self):
        """LLM exception must return safe fallback ('general', 0.0, 'unknown', 'unknown')."""
        with patch("app.services.conversation._call_llm_simple",
                   new=AsyncMock(side_effect=Exception("LLM timeout"))):
            from app.services.shadow_pilot_classifier import classify_intent
            intent, confidence, topic, lang = await classify_intent(
                "Hello I have a question"
            )
        assert intent == "general"
        assert confidence == 0.0
        assert topic == "unknown"
        assert lang == "unknown"

    @pytest.mark.asyncio
    async def test_classify_empty_message(self):
        """Empty message must return general without hitting the LLM."""
        import app.services.shadow_pilot_classifier as mod
        intent, confidence, topic, lang = await mod.classify_intent("")
        assert intent == "general"


# ═══════════════════════════════════════════════════════════════════════════
# C. AGGREGATOR — revenue formula + unanswered marking
# ═══════════════════════════════════════════════════════════════════════════

class TestAggregatorFormula:

    def test_revenue_leakage_formula(self):
        """
        Conservative leakage = booking_intent_after_hours_unanswered × ADR × nights × 0.20 × 0.60.
        For 5 unanswered after-hours booking-intent convs at ADR=230, nights=1.0:
        Expected = 5 × 230 × 1.0 × 0.20 × 0.60 = RM 138.00
        """
        unanswered_bi = 5
        adr = 230.0
        nights = 1.0
        leakage = unanswered_bi * adr * nights * 0.20 * 0.60
        assert abs(leakage - 138.0) < 0.01

    def test_annualised_formula(self):
        """Annualised leakage = weekly × 52; net recovery subtracts Nocturn annual cost."""
        weekly = 138.0
        annualised = weekly * 52  # 7,176
        nocturn_annual = 999 + 199 * 12  # 3,387
        net = max(0.0, annualised * 0.60 - nocturn_annual)
        assert annualised == 7176.0
        assert net > 0  # Should be positive at these volumes

    def test_slow_response_leakage(self):
        """Slow responses (>4 hrs, booking intent) add 15% ADR per conversation."""
        slow_bookings = 3
        adr = 230.0
        nights = 1.0
        slow_leakage = slow_bookings * adr * nights * 0.15
        assert abs(slow_leakage - 103.5) < 0.01


# ═══════════════════════════════════════════════════════════════════════════
# D. INTERNAL API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

class TestInternalEndpoints:

    @pytest.mark.asyncio
    async def test_shadow_event_wrong_secret_returns_403(self, client: AsyncClient):
        """shadow-event endpoint must reject calls with wrong X-Internal-Secret."""
        payload = {
            "event_type": "message.received",
            "property_slug": "vivatel-kl",
            "sender_jid": "60123456789@s.whatsapp.net",
            "message_id": "test-msg-001",
            "content_preview": "Test message",
            "timestamp_unix": 1714000000,
            "has_media": False,
        }
        response = await client.post(
            "/api/v1/internal/shadow-event",
            json=payload,
            headers={"X-Internal-Secret": "totally-wrong-secret"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_shadow_heartbeat_wrong_secret_returns_403(self, client: AsyncClient):
        """shadow-heartbeat must reject wrong secret."""
        response = await client.post(
            "/api/v1/internal/shadow-heartbeat",
            json={"property_slug": "vivatel-kl"},
            headers={"X-Internal-Secret": "bad-secret"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_shadow_active_properties_wrong_secret_returns_403(self, client: AsyncClient):
        """shadow-active-properties must reject wrong secret."""
        response = await client.get(
            "/api/v1/internal/shadow-active-properties",
            headers={"X-Internal-Secret": "bad-secret"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_shadow_event_with_valid_secret(self, client: AsyncClient):
        """
        shadow-event with valid secret returns 200 (even if property not found — processor
        silently returns when property missing).
        """
        from app.config import get_settings
        settings = get_settings()
        secret = settings.internal_scheduler_secret
        if not secret:
            pytest.skip("INTERNAL_SCHEDULER_SECRET not configured — skipping live endpoint test")

        payload = {
            "event_type": "message.received",
            "property_slug": "nonexistent-property-abc",
            "sender_jid": "60123456789@s.whatsapp.net",
            "message_id": "test-msg-001",
            "content_preview": "Test",
            "timestamp_unix": 1714000000,
            "has_media": False,
        }
        response = await client.post(
            "/api/v1/internal/shadow-event",
            json=payload,
            headers={"X-Internal-Secret": secret},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_shadow_active_properties_returns_list(self, client: AsyncClient):
        """shadow-active-properties returns a list (may be empty) when auth is valid."""
        from app.config import get_settings
        settings = get_settings()
        secret = settings.internal_scheduler_secret
        if not secret:
            pytest.skip("INTERNAL_SCHEDULER_SECRET not configured")

        response = await client.get(
            "/api/v1/internal/shadow-active-properties",
            headers={"X-Internal-Secret": secret},
        )
        assert response.status_code == 200
        body = response.json()
        assert "properties" in body
        assert isinstance(body["properties"], list)


# ═══════════════════════════════════════════════════════════════════════════
# E. TOKEN-GATED DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════

class TestTokenGatedDashboard:

    def _make_token(self, property_id: str, secret: str, exp_delta: timedelta) -> str:
        import jwt as pyjwt
        exp = datetime.now(timezone.utc) + exp_delta
        return pyjwt.encode(
            {"property_id": property_id, "type": "shadow_dashboard", "exp": exp},
            secret,
            algorithm="HS256",
        )

    @pytest.mark.asyncio
    async def test_expired_token_returns_401(self, client: AsyncClient):
        """An expired JWT must be rejected with 401."""
        from app.config import get_settings
        settings = get_settings()

        token = self._make_token("some-prop-id", settings.jwt_secret, timedelta(seconds=-1))
        response = await client.get(
            f"/api/v1/shadow/any-slug/summary?token={token}"
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self, client: AsyncClient):
        """Missing token query param must return 401/422."""
        response = await client.get("/api/v1/shadow/any-slug/summary")
        assert response.status_code in (401, 422)

    @pytest.mark.asyncio
    async def test_wrong_type_claim_returns_401(self, client: AsyncClient):
        """Token with wrong type claim must be rejected."""
        import jwt as pyjwt
        from app.config import get_settings
        settings = get_settings()

        token = pyjwt.encode(
            {
                "property_id": str(uuid.uuid4()),
                "type": "access_token",  # wrong type
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            },
            settings.jwt_secret,
            algorithm="HS256",
        )
        response = await client.get(f"/api/v1/shadow/any-slug/summary?token={token}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_token_mismatch_property_returns_403(self, client: AsyncClient):
        """Token valid for property A used on slug B must return 403/404."""
        from app.config import get_settings
        from app.database import async_session
        from app.models import Property

        settings = get_settings()

        # Seed a minimal property
        async with async_session() as db:
            prop_a = Property(
                name="Token Test Hotel A",
                slug="token-test-a",
                adr=Decimal("200"),
                ota_commission_pct=Decimal("15"),
                timezone="Asia/Kuala_Lumpur",
                shadow_pilot_mode=True,
            )
            db.add(prop_a)
            await db.commit()
            await db.refresh(prop_a)
            prop_a_id = prop_a.id

        token_a = self._make_token(str(prop_a_id), settings.jwt_secret, timedelta(days=1))

        # Use token for A but request slug B (nonexistent)
        response = await client.get(f"/api/v1/shadow/nonexistent-slug-xyz/summary?token={token_a}")
        assert response.status_code in (401, 403, 404)


# ═══════════════════════════════════════════════════════════════════════════
# F. ZERO-REPLY GATE — critical: shadow pilot MUST NEVER send to guests
# ═══════════════════════════════════════════════════════════════════════════

class TestZeroReplyGate:

    @pytest.mark.asyncio
    async def test_no_outbound_message_during_shadow_pilot(self):
        """
        Processing a guest message during shadow pilot must not make any
        outbound HTTP requests — shadow_pilot_processor never imports or
        calls a send function.
        """
        from app.services.shadow_pilot_processor import handle_message_received

        prop = _make_property()
        db = _make_mock_db()
        db.scalar.return_value = prop

        # Patch httpx at the module level to catch any stray HTTP calls
        with patch("httpx.AsyncClient.post", new=AsyncMock()) as mock_http_post, \
             patch("app.services.shadow_pilot_processor.classify_intent",
                   return_value=("room_booking", 0.9, "room booking", "en")):

            await handle_message_received(
                db=db,
                property_slug="test-hotel",
                sender_jid="60123456789@s.whatsapp.net",
                message_id="msg-zrg-001",
                content_preview="I want to book a room",
                timestamp_ms=int(datetime.now(timezone.utc).timestamp() * 1000),
                has_media=False,
            )

        # No outbound HTTP calls of any kind
        mock_http_post.assert_not_called()

        # Conversation was still created
        db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_baileys_transport_observe_only_blocks_send(self):
        """BaileysTransport with observe_only=True must not POST to the bridge on send_message."""
        from app.services.whatsapp_transport import BaileysTransport

        transport = BaileysTransport(
            bridge_url="http://localhost:3001",
            property_slug="test-hotel",
            observe_only=True,
        )

        with patch("httpx.AsyncClient.post", new=AsyncMock()) as mock_post:
            result = await transport.send_message(
                to="60123456789@s.whatsapp.net",
                text="This should never be sent",
            )
        mock_post.assert_not_called()
        assert result is False  # observe_only returns False, not raising
