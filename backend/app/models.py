"""
SQLAlchemy models for all core entities.
Maps directly to the data model in the implementation plan.
"""

import uuid
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import (
    String,
    Text,
    Boolean,
    Integer,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    Index,
    JSON,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


# ─────────────────────────────────────────────────────────────
# Multi-Tenant Hierarchy: Tenant → Property → User
# ─────────────────────────────────────────────────────────────


class Tenant(Base):
    """
    Hotel group / billing entity. Top-level organizational unit.
    A single hotel company may have multiple Properties.
    """
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    subscription_tier: Mapped[str] = mapped_column(
        String(20), default="pilot", server_default="pilot"
    )  # "pilot" | "boutique" | "independent" | "premium"
    subscription_status: Mapped[str] = mapped_column(
        String(20), default="trialing", server_default="trialing"
    )  # "trialing" | "active" | "cancelled" | "past_due"
    pilot_start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    pilot_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255))
    assigned_account_manager: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    properties: Mapped[list["Property"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    memberships: Mapped[list["TenantMembership"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    support_tickets: Mapped[list["SupportTicket"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    onboarding_progress: Mapped[list["OnboardingProgress"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )


class User(Base):
    """
    Human account. Maps 1:1 to Supabase auth.users via UUID.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )  # Same UUID as supabase auth.users.id
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    is_superadmin: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )  # SheersSoft internal staff
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    memberships: Mapped[list["TenantMembership"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class TenantMembership(Base):
    """
    Links a User to a Tenant with a specific role and property access scope.
    """
    __tablename__ = "tenant_memberships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(20), default="staff", server_default="staff"
    )  # "owner" | "admin" | "staff"
    accessible_property_ids: Mapped[list | None] = mapped_column(JSON)
    # null = all properties, [...] = specific property UUIDs
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="memberships")
    tenant: Mapped["Tenant"] = relationship(back_populates="memberships")

    __table_args__ = (
        UniqueConstraint("user_id", "tenant_id", name="uq_user_tenant"),
        Index("ix_membership_tenant", "tenant_id"),
        Index("ix_membership_user", "user_id"),
    )


class OnboardingProgress(Base):
    """
    Tracks onboarding milestones for the gamified getting-started experience.
    One record per property provisioned.
    """
    __tablename__ = "onboarding_progress"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False
    )
    # Channel setup status: "pending" | "configuring" | "active" | "failed" | "skipped"
    whatsapp_status: Mapped[str] = mapped_column(
        String(20), default="pending", server_default="pending"
    )
    email_status: Mapped[str] = mapped_column(
        String(20), default="pending", server_default="pending"
    )
    website_status: Mapped[str] = mapped_column(
        String(20), default="pending", server_default="pending"
    )
    # Milestone flags
    kb_populated: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    first_inquiry_received: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    first_lead_captured: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    first_morning_report_sent: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    owner_first_login: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    # Error tracking
    channel_errors: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="onboarding_progress")
    property: Mapped["Property"] = relationship(back_populates="onboarding_progress")

    __table_args__ = (
        UniqueConstraint("tenant_id", "property_id", name="uq_onboarding_tenant_property"),
    )


class SupportTicket(Base):
    """
    Support ticket from a tenant user to the SheersSoft team.
    """
    __tablename__ = "support_tickets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="open", server_default="open"
    )  # "open" | "in_progress" | "resolved" | "closed"
    priority: Mapped[str] = mapped_column(
        String(20), default="medium", server_default="medium"
    )  # "low" | "medium" | "high" | "urgent"
    assigned_to_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )  # SheersSoft staff
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="support_tickets")
    created_by: Mapped["User"] = relationship(foreign_keys=[created_by_user_id])
    assigned_to: Mapped["User | None"] = relationship(foreign_keys=[assigned_to_user_id])

    __table_args__ = (
        Index("ix_tickets_tenant_status", "tenant_id", "status"),
    )


class Application(Base):
    """
    Intake application from the website (ai.sheerssoft.com/apply).
    Processed by SheersSoft onboarding team.
    """
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    hotel_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    property_name: Mapped[str | None] = mapped_column(String(255))
    room_count: Mapped[int | None] = mapped_column(Integer)
    current_channels: Mapped[list | None] = mapped_column(JSON)
    # E.g. ["whatsapp", "email", "phone"]
    message: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20), default="new", server_default="new"
    )  # "new" | "contacted" | "qualified" | "converted" | "rejected"
    notes: Mapped[str | None] = mapped_column(Text)  # Internal notes by SheersSoft
    converted_to_tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_applications_status", "status"),
    )


# ─────────────────────────────────────────────────────────────
# Property (Hotel Location) — Now scoped under Tenant
# ─────────────────────────────────────────────────────────────


class Property(Base):
    """
    A hotel property (location). Belongs to a Tenant.
    All operational data is scoped to a property via property_id foreign keys.
    """
    __tablename__ = "properties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id")
    )  # Nullable for migration of existing rows; will be backfilled
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    whatsapp_number: Mapped[str | None] = mapped_column(String(20))
    whatsapp_provider: Mapped[str] = mapped_column(
        String(20), default="meta", server_default="meta"
    )  # "meta" | "twilio"
    twilio_phone_number: Mapped[str | None] = mapped_column(String(20))
    notification_email: Mapped[str | None] = mapped_column(String(255))
    website_url: Mapped[str | None] = mapped_column(String(500))
    operating_hours: Mapped[dict | None] = mapped_column(JSON)
    # Example: {"start": "09:00", "end": "18:00", "timezone": "Asia/Kuala_Lumpur"}
    knowledge_base_config: Mapped[dict | None] = mapped_column(JSON)
    adr: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("230.00")
    )  # Average Daily Rate for revenue calculations
    ota_commission_pct: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("20.00")
    )  # OTA commission % for savings calculations
    conversion_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0.20"), server_default="0.20"
    ) # Assumed lead-to-booking conversion rate
    hourly_rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("25.00"), server_default="25.00"
    )  # Hourly rate for front desk staff (used for cost savings calculations)
    brand_vocabulary: Mapped[str | None] = mapped_column(Text)
    # E.g. "We say 'Welcome Home' instead of 'Hello'. We are formal but warm."
    required_questions: Mapped[list[str] | None] = mapped_column(JSON)
    # E.g. ["What is your booking reference?", "How many adults are staying?"]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    slug: Mapped[str | None] = mapped_column(String(255), unique=True)
    # Add server_default to avoid NotNullViolation on existing rows
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kuala_Lumpur", server_default="Asia/Kuala_Lumpur")
    plan_tier: Mapped[str] = mapped_column(String(20), default="pilot", server_default="pilot")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    tenant: Mapped["Tenant | None"] = relationship(back_populates="properties")
    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
    leads: Mapped[list["Lead"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
    kb_documents: Mapped[list["KBDocument"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
    analytics_daily: Mapped[list["AnalyticsDaily"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
    onboarding_progress: Mapped["OnboardingProgress | None"] = relationship(
        back_populates="property", uselist=False
    )


class Conversation(Base):
    """
    A conversation between a guest and the AI (or staff after handoff).
    Tracks channel, status, and whether it occurred after hours.
    """
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False
    )
    channel: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "whatsapp" | "web" | "email"
    guest_identifier: Mapped[str | None] = mapped_column(
        String(255)
    )  # Phone number, session ID, or email
    guest_name: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        String(20), default="active"
    )  # "active" | "resolved" | "handed_off" | "expired"
    is_after_hours: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_mode: Mapped[str] = mapped_column(
        String(20), default="concierge"
    )  # "concierge" | "lead_capture" | "handoff"
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_interaction_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    follow_up_stage: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    message_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Relationships
    property: Mapped["Property"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.sent_at",
    )
    lead: Mapped["Lead | None"] = relationship(
        back_populates="conversation", uselist=False
    )

    __table_args__ = (
        Index("ix_conversations_property_status", "property_id", "status"),
        Index("ix_conversations_property_after_hours", "property_id", "is_after_hours"),
        Index("ix_conversations_guest", "property_id", "guest_identifier"),
    )


class Message(Base):
    """
    A single message within a conversation.
    role: 'guest' | 'ai' | 'staff'
    """
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # "guest" | "ai" | "staff"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON)
    # Metadata can include: response_time_ms, llm_tokens_used, confidence_score
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation", "conversation_id", "sent_at"),
    )


class Lead(Base):
    """
    A captured lead from a conversation.
    Created when the AI successfully captures guest contact info + intent.
    """
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False
    )
    guest_name: Mapped[str | None] = mapped_column(String(255))
    guest_phone: Mapped[str | None] = mapped_column(String(20))
    guest_email: Mapped[str | None] = mapped_column(String(255))
    intent: Mapped[str] = mapped_column(
        String(30), default="general"
    )  # "room_booking" | "event" | "fb_inquiry" | "general"
    source_channel: Mapped[str | None] = mapped_column(String(20))
    is_after_hours: Mapped[bool | None] = mapped_column(Boolean)
    status: Mapped[str] = mapped_column(
        String(20), default="new"
    )  # "new" | "contacted" | "converted" | "lost"
    estimated_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    actual_revenue: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    notes: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(
        String(20), default="standard", server_default="standard"
    ) # "standard" | "high_value"
    flag_reason: Mapped[str | None] = mapped_column(String(255))
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="lead")
    property: Mapped["Property"] = relationship(back_populates="leads")

    __table_args__ = (
        Index("ix_leads_property_status", "property_id", "status"),
        Index("ix_leads_property_date", "property_id", "captured_at"),
    )


class KBDocument(Base):
    """
    A knowledge base document chunk for RAG retrieval.
    Uses pgvector for semantic similarity search.
    """
    __tablename__ = "kb_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False
    )
    doc_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # "rates" | "rooms" | "facilities" | "faqs" | "directions" | "policies"
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list] = mapped_column(
        Vector(settings.embedding_dimensions), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    property: Mapped["Property"] = relationship(back_populates="kb_documents")

    __table_args__ = (
        Index("ix_kb_property_type", "property_id", "doc_type"),
    )


class AnalyticsDaily(Base):
    """
    Pre-aggregated daily analytics per property.
    Populated by a nightly cron job or materialized view refresh.
    Powers the GM dashboard and daily email report.
    """
    __tablename__ = "analytics_daily"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False
    )
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_inquiries: Mapped[int] = mapped_column(Integer, default=0)
    after_hours_inquiries: Mapped[int] = mapped_column(Integer, default=0)
    after_hours_responded: Mapped[int] = mapped_column(Integer, default=0)
    leads_captured: Mapped[int] = mapped_column(Integer, default=0)
    handoffs: Mapped[int] = mapped_column(Integer, default=0)
    inquiries_handled_by_ai: Mapped[int] = mapped_column(Integer, default=0)
    inquiries_handled_manually: Mapped[int] = mapped_column(Integer, default=0)
    avg_response_time_sec: Mapped[Decimal] = mapped_column(
        Numeric(8, 2), default=Decimal("0")
    )
    estimated_revenue_recovered: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0")
    )
    actual_revenue_recovered: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0")
    )
    cost_savings: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0")
    )
    channel_breakdown: Mapped[dict | None] = mapped_column(JSON)
    # Example: {"whatsapp": 29, "web": 14, "email": 4, "facebook": 2, "instagram": 1, "tiktok": 0}

    # Relationships
    property: Mapped["Property"] = relationship(back_populates="analytics_daily")

    __table_args__ = (
        Index(
            "ix_analytics_property_date",
            "property_id",
            "report_date",
            unique=True,
        ),
    )
