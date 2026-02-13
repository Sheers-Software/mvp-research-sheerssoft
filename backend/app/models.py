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


class Property(Base):
    """
    A hotel property. The top-level tenant entity.
    All data is scoped to a property via property_id foreign keys.
    """
    __tablename__ = "properties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    whatsapp_number: Mapped[str | None] = mapped_column(String(20))
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
    plan_tier: Mapped[str] = mapped_column(String(20), default="pilot", server_default="pilot")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
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
    avg_response_time_sec: Mapped[Decimal] = mapped_column(
        Numeric(8, 2), default=Decimal("0")
    )
    estimated_revenue_recovered: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0")
    )
    channel_breakdown: Mapped[dict | None] = mapped_column(JSON)
    # Example: {"whatsapp": 29, "web": 14, "email": 4}

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
