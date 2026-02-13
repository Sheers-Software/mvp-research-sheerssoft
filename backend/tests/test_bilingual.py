import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.conversation import process_guest_message
from app.models import Conversation, Message, Property
import uuid

# Mock data
MOCK_PROPERTY_ID = uuid.uuid4()
MOCK_CONVERSATION_ID = uuid.uuid4()

@pytest.fixture
async def setup_db():
    pass

@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = AsyncMock()
    
    # Mock property
    mock_prop = Property(
        id=MOCK_PROPERTY_ID,
        name="Hotel A",
        operating_hours={"start": "09:00", "end": "18:00"},
        adr=250.00,
        conversion_rate=0.20
    )
    
    # Setup execute side effect to handle Property query
    async def execute_side_effect(statement):
        # We only expect Property query here because we mock get_or_create_conversation
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_prop
        mock_result.scalar_one_or_none.return_value = mock_prop
        mock_result.scalars.return_value.all.return_value = [] # For history query
        return mock_result

    session.execute.side_effect = execute_side_effect
    return session

@pytest.fixture
def mock_conversation():
    """Mock Conversation object."""
    conv = Conversation(
        id=MOCK_CONVERSATION_ID,
        property_id=MOCK_PROPERTY_ID,
        guest_identifier="60123456789",
        channel="whatsapp",
        status="active",
        ai_mode="concierge",
        message_count=5, # arbitrary
        is_after_hours=False,
        guest_name="Test Guest"
    )
    return conv

@pytest.mark.asyncio
async def test_bilingual_greeting_bm(mock_db_session, mock_conversation):
    """Test basic Malay greeting."""
    with patch("app.services.conversation.get_or_create_conversation", new_callable=AsyncMock) as mock_get_conv, \
         patch("app.services.conversation.search_knowledge_base", new_callable=AsyncMock) as mock_kb, \
         patch("app.services.conversation.openai_client.chat.completions.create", new_callable=AsyncMock) as mock_llm:
        
        mock_get_conv.return_value = mock_conversation
        mock_kb.return_value = [] # No KB docs
        
        mock_llm.return_value.choices = [
            MagicMock(message=MagicMock(content="Selamat pagi! Ada apa-apa yang boleh saya bantu?"))
        ]
        mock_llm.return_value.usage.total_tokens = 100
        
        result = await process_guest_message(
            db=mock_db_session,
            property_id=MOCK_PROPERTY_ID,
            guest_identifier="60123456789",
            channel="whatsapp",
            message_text="Selamat pagi, ada bilik kosong tak?",
        )
        
        response = result["response"]
        assert "Selamat pagi" in response

@pytest.mark.asyncio
async def test_manglish_price_inquiry(mock_db_session, mock_conversation):
    """Test Manglish price inquiry."""
    with patch("app.services.conversation.get_or_create_conversation", new_callable=AsyncMock) as mock_get_conv, \
         patch("app.services.conversation.search_knowledge_base", new_callable=AsyncMock) as mock_kb, \
         patch("app.services.conversation.openai_client.chat.completions.create", new_callable=AsyncMock) as mock_llm:
        
        mock_get_conv.return_value = mock_conversation
        mock_kb.return_value = []
        
        mock_llm.return_value.choices = [
            MagicMock(message=MagicMock(content="Hi! For weekday dates, harga kita start dari RM250 semalam."))
        ]
        mock_llm.return_value.usage.total_tokens = 100
        
        result = await process_guest_message(
            db=mock_db_session,
            property_id=MOCK_PROPERTY_ID,
            guest_identifier="60123456789",
            channel="whatsapp",
            message_text="Hi boss, berapa price satu malam? Weekday got promo ah?",
        )
        
        response = result["response"]
        assert "RM250" in response

@pytest.mark.asyncio
async def test_bm_availability_check(mock_db_session, mock_conversation):
    """Test standard Malay availability check."""
    with patch("app.services.conversation.get_or_create_conversation", new_callable=AsyncMock) as mock_get_conv, \
         patch("app.services.conversation.search_knowledge_base", new_callable=AsyncMock) as mock_kb, \
         patch("app.services.conversation.openai_client.chat.completions.create", new_callable=AsyncMock) as mock_llm:
        
        mock_get_conv.return_value = mock_conversation
        mock_kb.return_value = []
        
        mock_llm.return_value.choices = [
            MagicMock(message=MagicMock(content="Boleh saya tahu tarikh penginapan cik?"))
        ]
        mock_llm.return_value.usage.total_tokens = 100
        
        result = await process_guest_message(
            db=mock_db_session,
            property_id=MOCK_PROPERTY_ID,
            guest_identifier="60123456789",
            channel="whatsapp",
            message_text="Nak check in esok, ada kosong?",
        )
        
        response = result["response"]
        assert "tarikh" in response or "bila" in response or "check-in" in response

@pytest.mark.asyncio
async def test_mixed_code_switching(mock_db_session, mock_conversation):
    """Test complex code-switching (Manglish)."""
    with patch("app.services.conversation.get_or_create_conversation", new_callable=AsyncMock) as mock_get_conv, \
         patch("app.services.conversation.search_knowledge_base", new_callable=AsyncMock) as mock_kb, \
         patch("app.services.conversation.openai_client.chat.completions.create", new_callable=AsyncMock) as mock_llm:
        
        mock_get_conv.return_value = mock_conversation
        mock_kb.return_value = []
        
        mock_llm.return_value.choices = [
            MagicMock(message=MagicMock(content="Pool kita buka sampai 8pm je. Nak book bilik ke?"))
        ]
        mock_llm.return_value.usage.total_tokens = 100
        
        result = await process_guest_message(
            db=mock_db_session,
            property_id=MOCK_PROPERTY_ID,
            guest_identifier="60123456789",
            channel="whatsapp",
            message_text="Pool buka sampai pukul berapa? My kids want to mandi swimming pool la.",
        )
        
        assert result["response"] is not None

