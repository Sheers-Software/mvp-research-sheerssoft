
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class NormalizedMessage(BaseModel):
    """
    Unified format for all incoming guest messages.
    Abstracts away channel-specific payload differences (WhatsApp vs Email vs Web).
    """
    channel: str = Field(..., description="Source channel: whatsapp, web, email")
    guest_identifier: str = Field(..., description="Unique ID: phone number, email, or session_id")
    guest_name: Optional[str] = None
    content: str = Field(..., description="Text content of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Context info
    business_id: str = Field(..., description="Target business UUID")
    
    # Raw metadata for debugging/logging
    metadata: Optional[Dict[str, Any]] = None
