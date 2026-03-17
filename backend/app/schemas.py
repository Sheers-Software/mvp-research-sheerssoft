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


class StaffReplyRequest(BaseModel):
    """Staff sends a message from the dashboard back to the guest."""
    content: str = Field(..., min_length=1, max_length=4000)


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
    actual_revenue: float | None
    priority: str
    flag_reason: str | None
    captured_at: datetime

    class Config:
        from_attributes = True


class LeadConvertRequest(BaseModel):
    """Payload to convert a lead and log actual revenue."""
    actual_revenue: float = Field(..., ge=0)
    notes: str | None = None


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
    notification_email: str | None = None
    operating_hours: dict | None = None
    timezone: str | None = None
    adr: float | None = None
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


class MagicLinkRequest(BaseModel):
    """Request a magic link login email."""
    email: str = Field(..., min_length=5, max_length=255)


class UserProfileResponse(BaseModel):
    """Current user profile with tenant memberships."""
    id: uuid.UUID
    email: str
    full_name: str
    phone: str | None
    is_superadmin: bool
    last_login_at: datetime | None
    memberships: list["TenantMembershipResponse"]

    class Config:
        from_attributes = True


# ─── Tenants ───

class TenantResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    subscription_tier: str
    subscription_status: str
    pilot_start_date: datetime | None
    pilot_end_date: datetime | None
    assigned_account_manager: str | None
    is_active: bool
    created_at: datetime
    property_count: int | None = None

    class Config:
        from_attributes = True


class TenantMembershipResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    tenant_name: str | None = None
    role: str
    accessible_property_ids: list | None

    class Config:
        from_attributes = True


class TenantUpdateRequest(BaseModel):
    subscription_tier: str | None = None
    subscription_status: str | None = None
    is_active: bool | None = None
    assigned_account_manager: str | None = None


# ─── Onboarding ───

class ProvisionTenantRequest(BaseModel):
    """One-click tenant provisioning from SuperAdmin dashboard."""
    tenant_name: str = Field(..., min_length=1, max_length=255)
    property_name: str = Field(..., min_length=1, max_length=255)
    owner_email: str = Field(..., min_length=5, max_length=255)
    owner_name: str = Field(..., min_length=1, max_length=255)
    owner_phone: str | None = None
    timezone: str = "Asia/Kuala_Lumpur"
    subscription_tier: str = "pilot"
    pilot_duration_days: int = 30
    preferred_channels: list[str] = Field(default_factory=lambda: ["whatsapp", "email", "website"])
    whatsapp_provider: str = "meta"  # "meta" | "twilio"
    whatsapp_number: str | None = None
    twilio_phone_number: str | None = None
    reservation_email: str | None = None
    website_url: str | None = None
    assigned_account_manager: str | None = None


class ProvisionTenantResponse(BaseModel):
    tenant_id: uuid.UUID
    property_id: uuid.UUID
    user_id: uuid.UUID
    magic_link_sent: bool
    channels_setup_initiated: bool
    message: str


class OnboardingProgressResponse(BaseModel):
    """Gamified onboarding milestone status."""
    tenant_id: uuid.UUID
    property_id: uuid.UUID
    # Channel statuses
    whatsapp_status: str
    email_status: str
    website_status: str
    # Milestone flags
    kb_populated: bool
    first_inquiry_received: bool
    first_lead_captured: bool
    first_morning_report_sent: bool
    owner_first_login: bool
    # Computed
    completion_score: int = 0  # 0-100
    next_milestone: str | None = None

    class Config:
        from_attributes = True


class InviteUserRequest(BaseModel):
    """Invite a new user to an existing tenant."""
    email: str = Field(..., min_length=5, max_length=255)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: str = "staff"  # "owner" | "admin" | "staff"
    accessible_property_ids: list[uuid.UUID] | None = None  # null = all


# ─── Support ───

class SupportTicketCreateRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    priority: str = "medium"  # "low" | "medium" | "high" | "urgent"


class SupportTicketResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    subject: str
    description: str
    status: str
    priority: str
    created_by_name: str | None = None
    assigned_to_name: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupportTicketUpdateRequest(BaseModel):
    status: str | None = None
    priority: str | None = None
    assigned_to_user_id: uuid.UUID | None = None


class SupportChatRequest(BaseModel):
    """Message to the Nocturn AI support chatbot."""
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: uuid.UUID | None = None  # Existing conversation or start new


# ─── Applications ───

class ApplicationCreateRequest(BaseModel):
    """Intake from ai.sheerssoft.com/apply."""
    hotel_name: str = Field(..., min_length=1, max_length=255)
    contact_name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=5, max_length=255)
    phone: str | None = None
    property_name: str | None = None
    room_count: int | None = None
    current_channels: list[str] | None = None
    message: str | None = None


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    hotel_name: str
    contact_name: str
    email: str
    phone: str | None
    room_count: int | None
    status: str
    notes: str | None
    converted_to_tenant_id: uuid.UUID | None
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationUpdateRequest(BaseModel):
    status: str | None = None
    notes: str | None = None


# ─── SuperAdmin Metrics ───

class PlatformMetricsResponse(BaseModel):
    """Global platform metrics for the SheersSoft internal dashboard."""
    total_tenants: int
    active_tenants: int
    total_properties: int
    total_conversations_alltime: int
    total_conversations_mtd: int
    total_leads_mtd: int
    open_support_tickets: int
    pending_applications: int
