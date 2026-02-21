"""
API route schemas — Pydantic models for request/response validation.
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


# ─── Conversations ───

class MessageRequest(BaseModel):
    """Incoming message from any channel."""
    message: str = Field(..., min_length=1, max_length=4000)
    guest_name: str | None = None


class ConversationResponse(BaseModel):
    response: str
    conversation_id: uuid.UUID
    mode: str
    is_after_hours: bool
    response_time_ms: int
    lead_created: bool


class WebChatStartRequest(BaseModel):
    """Start a new web chat conversation."""
    property_id: str
    message: str = Field(..., min_length=1, max_length=4000)
    guest_name: str | None = None
    session_id: str | None = None  # Browser session ID for continuity


class ConversationListItem(BaseModel):
    """Single item in conversation list for staff dashboard."""
    id: uuid.UUID
    channel: str
    guest_name: str | None
    guest_identifier: str
    status: str
    ai_mode: str
    is_after_hours: bool
    message_count: int
    started_at: datetime
    last_message_at: datetime | None
    has_lead: bool
    lead_intent: str | None

    class Config:
        from_attributes = True


class MessageDetail(BaseModel):
    """Single message in conversation detail view."""
    id: uuid.UUID
    role: str
    content: str
    sent_at: datetime
    metadata: dict | None = None


class ConversationDetailResponse(BaseModel):
    """Full conversation with messages (staff drill-down)."""
    id: uuid.UUID
    channel: str
    guest_name: str | None
    guest_identifier: str
    status: str
    ai_mode: str
    is_after_hours: bool
    message_count: int
    started_at: datetime
    last_message_at: datetime | None
    messages: list[MessageDetail]
    lead: Optional["LeadResponse"] = None


# ─── Leads ───

class LeadResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    guest_name: str | None
    guest_phone: str | None
    guest_email: str | None
    intent: str
    status: str
    estimated_value: float | None
    priority: str
    flag_reason: str | None
    captured_at: datetime

    class Config:
        from_attributes = True


class LeadUpdateRequest(BaseModel):
    status: str | None = None  # "new" | "contacted" | "converted" | "lost"
    notes: str | None = None


# ─── Properties ───

class PropertyResponse(BaseModel):
    id: uuid.UUID
    name: str
    whatsapp_number: str | None
    website_url: str | None
    adr: float
    ota_commission_pct: float
    hourly_rate: float
    brand_vocabulary: str | None = None
    required_questions: list[str] | None = None
    created_at: datetime | None = None
    deleted_at: datetime | None = None

    class Config:
        from_attributes = True


PropertyInDB = PropertyResponse


class PropertyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    whatsapp_number: str | None = None
    website_url: str | None = None
    operating_hours: dict | None = None
    adr: float = 230.00
    ota_commission_pct: float = 20.00
    hourly_rate: float = 25.00
    brand_vocabulary: str | None = None
    required_questions: list[str] | None = None


class PropertySettingsUpdateRequest(BaseModel):
    hourly_rate: float | None = None
    brand_vocabulary: str | None = None
    required_questions: list[str] | None = None


# ─── Knowledge Base ───

class KBDocumentInput(BaseModel):
    doc_type: str = Field(..., pattern="^(rates|rooms|facilities|faqs|directions|policies|dining)$")
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)


class KBIngestRequest(BaseModel):
    documents: list[KBDocumentInput]


class KBIngestResponse(BaseModel):
    documents_ingested: int
    property_id: str


# ─── Analytics ───

class AnalyticsSummaryResponse(BaseModel):
    total_inquiries: int
    after_hours_inquiries: int
    after_hours_responded: int
    leads_captured: int
    handoffs: int
    inquiries_handled_by_ai: int
    inquiries_handled_manually: int
    avg_response_time_sec: float
    estimated_revenue_recovered: float
    cost_savings: float
    channel_breakdown: dict | None


class DashboardStatsResponse(BaseModel):
    """Hero stats for the Money Slide dashboard view."""
    total_inquiries: int = 0
    after_hours_inquiries: int = 0
    after_hours_responded: int = 0
    after_hours_recovery_rate: float = 0.0
    leads_captured: int = 0
    lead_capture_rate: float = 0.0
    handoffs: int = 0
    handoff_rate: float = 0.0
    ai_handled_rate: float = 0.0
    avg_response_time_sec: float = 0.0
    estimated_revenue_recovered: float = 0.0
    channel_breakdown: dict = {}


class AnalyticsDailyResponse(BaseModel):
    """Single day analytics record for trend charts."""
    report_date: date
    total_inquiries: int
    after_hours_inquiries: int
    leads_captured: int
    handoffs: int
    inquiries_handled_by_ai: int
    inquiries_handled_manually: int
    avg_response_time_sec: float
    estimated_revenue_recovered: float
    cost_savings: float
    channel_breakdown: dict | None

    class Config:
        from_attributes = True


class HandoffAlertResponse(BaseModel):
    """Handoff notification payload for dashboard."""
    conversation_id: uuid.UUID
    guest_name: str
    channel: str
    summary: str
    timestamp: datetime | None


# ─── Auth ───

class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
