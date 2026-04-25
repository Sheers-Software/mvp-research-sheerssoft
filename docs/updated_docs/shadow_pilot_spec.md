# Shadow Pilot Implementation Spec
## Nocturn AI — REQ-002: Shadow Pilot Deep Implementation
### Version 1.0 · 24 Apr 2026
### Status: Sprint 2.5 — Implementation Ready
### Cross-referenced with: prd.md v2.5 F10, architecture.md v2.5 Section 2.6, build_plan.md v2.5 Sprint 2.5

---

## 1. Purpose & Scope

This document is the canonical implementation reference for the Shadow Pilot feature (PRD F10). It defines every data model, service interface, API endpoint, scheduler job, email template, and frontend page required to go from zero to a working 7-day WhatsApp observation pipeline with a revenue leakage report.

It is written to be directly consumed by an LLM coding agent in a single context window — no external lookups required.

---

## 2. Architecture Overview

```
Hotel's WhatsApp Business Number (existing, unchanged)
        │
        │  Baileys multi-device linked session (QR scan, one time)
        ▼
┌────────────────────────────────────────────────────────────────┐
│  WhatsApp Bridge Service (Node.js — separate container)        │
│  baileys-bridge/                                               │
│                                                                │
│  - Maintains persistent session per property                   │
│  - Emits events: message.received, message.sent               │
│  - Forwards events → FastAPI backend via internal HTTP POST    │
│  - Reconnects automatically on session drop                    │
│  - QR endpoint: GET /qr/:propertySlug → base64 PNG            │
│  - Session status endpoint: GET /status/:propertySlug          │
└──────────────────────┬─────────────────────────────────────────┘
                       │ POST /api/v1/internal/shadow-event
                       ▼
┌────────────────────────────────────────────────────────────────┐
│  FastAPI Backend — Shadow Pilot Processor                      │
│                                                                │
│  shadow_pilot_processor.py                                     │
│  - Receives events from Baileys bridge                         │
│  - Creates/updates ShadowPilotConversation records             │
│  - Computes response times                                     │
│  - Runs intent classification (lightweight, async)             │
│  - Flags unanswered conversations after 24hr                   │
└──────────────────────┬─────────────────────────────────────────┘
                       │
            ┌──────────┴──────────┐
            ▼                     ▼
  ShadowPilotConversation    ShadowPilotAnalyticsDaily
  (per conversation)         (daily rollup per property)
            │
            ▼
  Cloud Scheduler jobs:
  - run_shadow_pilot_aggregation (daily, midnight local)
  - run_shadow_pilot_weekly_report (Day 7 + weekly)
            │
            ▼
  Weekly Report Email → GM
  Token-gated Dashboard → /shadow/[slug]?token=[jwt]
```

---

## 3. Data Models

### 3.1 Property Model Changes

**Alembic migration**: `add_shadow_pilot_v2_fields`

```python
# Add to existing Property model in backend/app/models/property.py

# Shadow pilot v2 fields — replaces audit_only_mode approach
shadow_pilot_mode: bool = Field(default=False)
shadow_pilot_start_date: Optional[datetime] = None
shadow_pilot_phone: Optional[str] = None          # Hotel's real WA number (e.g. +60123456789)
shadow_pilot_session_active: bool = Field(default=False)  # Is Baileys session live?
shadow_pilot_session_last_seen: Optional[datetime] = None  # Last heartbeat from bridge
shadow_pilot_dashboard_token: Optional[str] = None  # Signed JWT for token-gated dashboard
shadow_pilot_dashboard_token_expires: Optional[datetime] = None
avg_stay_nights: float = Field(default=1.0)       # Used in revenue formula; configurable per property
```

**SQL migration (incremental ALTER — safe to run on live DB):**
```sql
ALTER TABLE properties
  ADD COLUMN IF NOT EXISTS shadow_pilot_mode BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS shadow_pilot_start_date TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS shadow_pilot_phone VARCHAR(30),
  ADD COLUMN IF NOT EXISTS shadow_pilot_session_active BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS shadow_pilot_session_last_seen TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS shadow_pilot_dashboard_token TEXT,
  ADD COLUMN IF NOT EXISTS shadow_pilot_dashboard_token_expires TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS avg_stay_nights FLOAT DEFAULT 1.0;

-- Migrate existing audit_only_mode data to shadow_pilot_mode
UPDATE properties SET shadow_pilot_mode = audit_only_mode WHERE audit_only_mode = TRUE;
-- Keep audit_only_mode column — still used by hybrid co-pilot path
```

---

### 3.2 ShadowPilotConversation Model

**New table**: `shadow_pilot_conversations`

```python
# backend/app/models/shadow_pilot.py

class ShadowPilotConversation(Base):
    __tablename__ = "shadow_pilot_conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    property_id: uuid.UUID = Field(foreign_key="properties.id", index=True)

    # Guest identity (Fernet-encrypted at rest)
    guest_phone_encrypted: str          # Encrypted. Decrypt only for display.
    guest_phone_hash: str               # SHA-256 hash — used for deduplication, repeat-guest detection
    guest_name: Optional[str] = None    # Extracted from WA profile display name, if available

    # Timestamps (all in UTC, stored as timestamptz)
    first_guest_message_at: datetime    # When the conversation thread started
    last_guest_message_at: datetime     # Last message from guest (updated on each new message)
    first_staff_reply_at: Optional[datetime] = None   # When staff first replied; None = unanswered
    last_staff_reply_at: Optional[datetime] = None    # Most recent staff message

    # Computed from timestamps
    response_time_minutes: Optional[float] = None     # first_staff_reply_at - first_guest_message_at
    # None = unanswered

    # Flags
    is_after_hours: bool = Field(default=False)       # Was first_guest_message_at outside operating hours?
    is_unanswered: bool = Field(default=False)        # No staff reply after 24 hours
    is_booking_intent: bool = Field(default=False)    # AI classified as booking/rate/availability
    is_group_booking: bool = Field(default=False)     # AI classified as group_booking
    is_repeat_guest: bool = Field(default=False)      # guest_phone_hash seen before in this property

    # Intent & content
    intent: Optional[str] = None
    # Enum: "room_booking" | "rate_query" | "availability_check" | "group_booking"
    #       | "facilities_inquiry" | "complaint" | "general" | "unknown"
    intent_confidence: Optional[float] = None         # 0.0–1.0
    top_topic: Optional[str] = None                   # Short label from AI topic extraction
    message_count_guest: int = Field(default=1)       # Number of messages from guest
    message_count_staff: int = Field(default=0)       # Number of replies from staff
    language_detected: Optional[str] = None           # "bm" | "en" | "mixed"

    # Revenue estimation (computed on unanswered booking-intent conversations)
    estimated_value_rm: Optional[float] = None
    # = property.adr × property.avg_stay_nights × conversion_rate
    # conversion_rate = 0.20 for booking_intent, 0.15 for slow_response (>4hr), 0 otherwise

    # Status
    status: str = Field(default="open")
    # "open" | "staff_replied" | "abandoned" | "expired"
    # "abandoned" = no reply after 24hr AND after_hours = True
    # "expired" = conversation older than 30 days (for cleanup)

    # Raw snapshot (for the sample conversations in the weekly report)
    first_guest_message_preview: Optional[str] = None
    # First 200 chars of guest's first message (NEVER includes staff reply content)
    # Used to show "what they asked" in the weekly report email

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Indexes:**
```sql
CREATE INDEX IF NOT EXISTS idx_spc_property_id ON shadow_pilot_conversations(property_id);
CREATE INDEX IF NOT EXISTS idx_spc_first_message ON shadow_pilot_conversations(first_guest_message_at);
CREATE INDEX IF NOT EXISTS idx_spc_is_after_hours ON shadow_pilot_conversations(property_id, is_after_hours);
CREATE INDEX IF NOT EXISTS idx_spc_is_unanswered ON shadow_pilot_conversations(property_id, is_unanswered);
CREATE INDEX IF NOT EXISTS idx_spc_phone_hash ON shadow_pilot_conversations(property_id, guest_phone_hash);
```

---

### 3.3 ShadowPilotAnalyticsDaily Model

**New table**: `shadow_pilot_analytics_daily`

```python
class ShadowPilotAnalyticsDaily(Base):
    __tablename__ = "shadow_pilot_analytics_daily"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    property_id: uuid.UUID = Field(foreign_key="properties.id", index=True)
    report_date: date                               # The day this row covers (property-local date)

    # ── Group A: Inquiry Volume ───────────────────────────────────────────────
    total_inquiries: int = Field(default=0)
    after_hours_inquiries: int = Field(default=0)
    business_hours_inquiries: int = Field(default=0)
    booking_intent_inquiries: int = Field(default=0)
    group_booking_inquiries: int = Field(default=0)
    repeat_guest_contacts: int = Field(default=0)

    # ── Group B: Response Behaviour ──────────────────────────────────────────
    responded_count: int = Field(default=0)
    unanswered_count: int = Field(default=0)
    after_hours_unanswered: int = Field(default=0)
    after_hours_responded_next_day: int = Field(default=0)

    avg_response_time_minutes: Optional[float] = None        # Across all responded
    avg_response_time_business_hours: Optional[float] = None
    avg_response_time_after_hours: Optional[float] = None    # Only after-hours that DID get reply
    response_time_over_1hr: int = Field(default=0)
    response_time_over_4hr: int = Field(default=0)
    response_time_over_8hr: int = Field(default=0)
    response_time_over_24hr: int = Field(default=0)

    # ── Group C: Revenue Leakage ─────────────────────────────────────────────
    revenue_at_risk_total: float = Field(default=0.0)
    revenue_at_risk_conservative: float = Field(default=0.0)  # × 0.60
    ota_commission_equivalent: float = Field(default=0.0)      # × 0.18
    slow_response_revenue_at_risk: float = Field(default=0.0)
    daily_revenue_leakage: float = Field(default=0.0)          # total conservative + slow

    # ── Group D: Time-of-Day Patterns ────────────────────────────────────────
    peak_inquiry_hour: Optional[int] = None          # 0–23, property local time
    after_hours_peak_hour: Optional[int] = None
    inquiries_by_hour: Optional[dict] = None         # JSON: {"0": 2, "1": 0, ..., "23": 8}
    inquiries_by_day_of_week: Optional[dict] = None  # JSON: {"mon": 14, "tue": 18, ...}

    # ── Group E: Intent & Content Signals ────────────────────────────────────
    top_inquiry_topics: Optional[list] = None        # JSON: ["room rates", "pool", "parking"]
    top_unanswered_topics: Optional[list] = None     # JSON: topics from abandoned conversations
    booking_intent_rate: Optional[float] = None      # 0.0–1.0
    language_breakdown: Optional[dict] = None        # JSON: {"bm": 0.4, "en": 0.45, "mixed": 0.15}

    computed_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        unique_together = [("property_id", "report_date")]
```

---

### 3.4 ShadowPilotWeeklyRollup (Computed at Report Time)

Not stored as a separate table — computed on demand from `ShadowPilotAnalyticsDaily` for the 7-day window ending at report generation time.

```python
# backend/app/services/shadow_pilot_reporter.py

@dataclass
class ShadowPilotWeeklyRollup:
    property_id: uuid.UUID
    period_start: date
    period_end: date
    days_observed: int  # Actual days with data (may be <7 if pilot started recently)

    # Summed from ShadowPilotAnalyticsDaily
    total_inquiries: int
    after_hours_inquiries: int
    booking_intent_inquiries: int
    responded_count: int
    unanswered_count: int
    after_hours_unanswered: int

    # Averaged
    avg_response_time_minutes: float
    avg_response_time_after_hours: float

    # Worst-case counts
    response_time_over_4hr: int
    response_time_over_24hr: int

    # Revenue (summed daily leakage)
    weekly_revenue_leakage: float
    ota_commission_equivalent: float
    annualised_revenue_leakage: float
    nocturn_year_1_net_recovery: float  # annualised × 0.60 − (999 + 199×12)

    # Patterns (most common across the week)
    peak_inquiry_hour: int
    top_inquiry_topics: list[str]
    top_unanswered_topics: list[str]
    inquiries_by_hour_aggregate: dict  # Summed across all days

    # Sample unanswered conversations (for email body)
    sample_abandoned_conversations: list[dict]
    # Each: {time_received: str, topic: str, estimated_value_rm: float, preview: str (masked)}
```

---

## 4. Baileys Bridge Service

### 4.1 Service Overview

A standalone Node.js service (`baileys-bridge/`) that runs alongside the FastAPI backend as a separate Cloud Run container. It maintains one Baileys WhatsApp session per shadow-pilot property and forwards all message events to the FastAPI backend.

```
baileys-bridge/
├── src/
│   ├── index.ts              # Express app entry point
│   ├── session-manager.ts    # Manages multiple property sessions
│   ├── event-forwarder.ts    # POSTs events to FastAPI backend
│   └── qr-generator.ts       # Converts QR matrix to base64 PNG
├── sessions/                  # Persistent session files (mounted volume on Cloud Run)
│   └── {property_slug}/       # Baileys auth state per property
├── package.json
├── tsconfig.json
└── Dockerfile
```

### 4.2 Dependencies

```json
{
  "dependencies": {
    "@whiskeysockets/baileys": "^6.7.0",
    "express": "^4.18.0",
    "qrcode": "^1.5.3",
    "pino": "^9.0.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/express": "^4.17.0",
    "@types/node": "^20.0.0"
  }
}
```

### 4.3 Session Manager (session-manager.ts)

```typescript
import makeWASocket, {
  DisconnectReason,
  useMultiFileAuthState,
  fetchLatestBaileysVersion
} from '@whiskeysockets/baileys'
import { Boom } from '@hapi/boom'
import { EventForwarder } from './event-forwarder'
import QRCode from 'qrcode'

interface SessionState {
  socket: ReturnType<typeof makeWASocket> | null
  qrBase64: string | null
  status: 'waiting_qr' | 'connecting' | 'connected' | 'disconnected'
  lastHeartbeat: Date | null
  propertySlug: string
  propertyPhone: string
}

export class SessionManager {
  private sessions: Map<string, SessionState> = new Map()
  private forwarder: EventForwarder

  constructor(forwarder: EventForwarder) {
    this.forwarder = forwarder
  }

  async startSession(propertySlug: string, propertyPhone: string): Promise<void> {
    const sessionsDir = `./sessions/${propertySlug}`
    const { state, saveCreds } = await useMultiFileAuthState(sessionsDir)
    const { version } = await fetchLatestBaileysVersion()

    const sessionState: SessionState = {
      socket: null,
      qrBase64: null,
      status: 'waiting_qr',
      lastHeartbeat: null,
      propertySlug,
      propertyPhone
    }
    this.sessions.set(propertySlug, sessionState)

    const sock = makeWASocket({
      version,
      auth: state,
      printQRInTerminal: false,
      // Shadow pilot: observe only — do not send any messages
      // getMessage is required by Baileys but we return undefined to disable message sending
      getMessage: async () => undefined,
      logger: require('pino')({ level: 'warn' }),
    })

    sessionState.socket = sock

    // ── QR Code Event ──────────────────────────────────────────────────────
    sock.ev.on('connection.update', async (update) => {
      const { connection, lastDisconnect, qr } = update

      if (qr) {
        sessionState.qrBase64 = await QRCode.toDataURL(qr)
        sessionState.status = 'waiting_qr'
        // Notify backend so admin panel can show the QR
        await this.forwarder.sendSessionStatus(propertySlug, 'waiting_qr', sessionState.qrBase64)
      }

      if (connection === 'open') {
        sessionState.status = 'connected'
        sessionState.qrBase64 = null
        sessionState.lastHeartbeat = new Date()
        await this.forwarder.sendSessionStatus(propertySlug, 'connected', null)
        console.log(`[${propertySlug}] Session connected`)
      }

      if (connection === 'close') {
        const shouldReconnect = (lastDisconnect?.error as Boom)?.output?.statusCode
          !== DisconnectReason.loggedOut
        sessionState.status = 'disconnected'
        await this.forwarder.sendSessionStatus(propertySlug, 'disconnected', null)

        if (shouldReconnect) {
          console.log(`[${propertySlug}] Reconnecting in 5s...`)
          setTimeout(() => this.startSession(propertySlug, propertyPhone), 5000)
        } else {
          // Logged out — clean up session files
          console.log(`[${propertySlug}] Logged out. Session ended.`)
          this.sessions.delete(propertySlug)
        }
      }
    })

    // ── Credential Save ────────────────────────────────────────────────────
    sock.ev.on('creds.update', saveCreds)

    // ── Incoming Message Event ─────────────────────────────────────────────
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
      if (type !== 'notify') return  // Only process new incoming messages

      for (const msg of messages) {
        if (!msg.message) continue
        if (msg.key.fromMe) continue  // Skip messages sent BY the hotel (handled separately)

        const senderJid = msg.key.remoteJid
        if (!senderJid || senderJid.includes('@g.us')) continue  // Skip group chats

        const content = extractTextContent(msg)
        if (!content) continue  // Skip non-text media

        await this.forwarder.sendMessageEvent({
          event_type: 'message.received',
          property_slug: propertySlug,
          sender_jid: senderJid,
          message_id: msg.key.id!,
          content_preview: content.substring(0, 200),
          timestamp_unix: (msg.messageTimestamp as number) * 1000,
          has_media: hasMedia(msg),
        })
      }

      // ── Outgoing Message Event (staff reply) ─────────────────────────────
      for (const msg of messages) {
        if (!msg.key.fromMe) continue
        if (!msg.message) continue

        const recipientJid = msg.key.remoteJid
        if (!recipientJid || recipientJid.includes('@g.us')) continue

        await this.forwarder.sendMessageEvent({
          event_type: 'message.sent',
          property_slug: propertySlug,
          sender_jid: recipientJid,   // The guest who received this reply
          message_id: msg.key.id!,
          content_preview: null,       // We do NOT capture outgoing staff message content
          timestamp_unix: (msg.messageTimestamp as number) * 1000,
          has_media: false,
        })
      }
    })

    // ── Heartbeat ─────────────────────────────────────────────────────────
    setInterval(async () => {
      if (sessionState.status === 'connected') {
        sessionState.lastHeartbeat = new Date()
        await this.forwarder.sendHeartbeat(propertySlug)
      }
    }, 60_000)  // Every 60 seconds
  }

  getQR(propertySlug: string): string | null {
    return this.sessions.get(propertySlug)?.qrBase64 ?? null
  }

  getStatus(propertySlug: string): string {
    return this.sessions.get(propertySlug)?.status ?? 'not_started'
  }

  stopSession(propertySlug: string): void {
    const session = this.sessions.get(propertySlug)
    if (session?.socket) {
      session.socket.end(undefined)
      this.sessions.delete(propertySlug)
    }
  }
}

function extractTextContent(msg: any): string | null {
  return msg.message?.conversation
    ?? msg.message?.extendedTextMessage?.text
    ?? null
}

function hasMedia(msg: any): boolean {
  return !!(msg.message?.imageMessage
    || msg.message?.videoMessage
    || msg.message?.audioMessage
    || msg.message?.documentMessage)
}
```

### 4.4 Event Forwarder (event-forwarder.ts)

```typescript
import axios from 'axios'

const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || 'http://localhost:8000'
const INTERNAL_SECRET = process.env.INTERNAL_SECRET || ''

export class EventForwarder {
  private async post(path: string, payload: object): Promise<void> {
    try {
      await axios.post(`${BACKEND_URL}${path}`, payload, {
        headers: { 'X-Internal-Secret': INTERNAL_SECRET },
        timeout: 5000,
      })
    } catch (err) {
      // Log but do not crash — bridge must stay running even if backend is down
      console.error(`[EventForwarder] Failed to POST ${path}:`, (err as any).message)
    }
  }

  async sendMessageEvent(event: {
    event_type: 'message.received' | 'message.sent'
    property_slug: string
    sender_jid: string
    message_id: string
    content_preview: string | null
    timestamp_unix: number
    has_media: boolean
  }): Promise<void> {
    await this.post('/api/v1/internal/shadow-event', event)
  }

  async sendSessionStatus(
    propertySlug: string,
    status: string,
    qrBase64: string | null
  ): Promise<void> {
    await this.post('/api/v1/internal/shadow-session-status', {
      property_slug: propertySlug,
      status,
      qr_base64: qrBase64,
    })
  }

  async sendHeartbeat(propertySlug: string): Promise<void> {
    await this.post('/api/v1/internal/shadow-heartbeat', {
      property_slug: propertySlug,
    })
  }
}
```

### 4.5 Express API (index.ts)

```typescript
import express from 'express'
import { SessionManager } from './session-manager'
import { EventForwarder } from './event-forwarder'

const app = express()
app.use(express.json())

const forwarder = new EventForwarder()
const manager = new SessionManager(forwarder)

// Start sessions for all active shadow pilots on startup
async function loadActiveSessions() {
  const res = await fetch(`${process.env.BACKEND_INTERNAL_URL}/api/v1/internal/shadow-active-properties`, {
    headers: { 'X-Internal-Secret': process.env.INTERNAL_SECRET! }
  })
  const { properties } = await res.json()
  for (const p of properties) {
    await manager.startSession(p.slug, p.shadow_pilot_phone)
  }
}
loadActiveSessions()

// ── Internal API (called by FastAPI backend) ──────────────────────────────
app.post('/internal/start-session', async (req, res) => {
  const { property_slug, property_phone } = req.body
  await manager.startSession(property_slug, property_phone)
  res.json({ status: 'starting' })
})

app.post('/internal/stop-session', (req, res) => {
  const { property_slug } = req.body
  manager.stopSession(property_slug)
  res.json({ status: 'stopped' })
})

// ── Admin QR Polling (polled by frontend admin panel) ─────────────────────
app.get('/qr/:propertySlug', (req, res) => {
  const qr = manager.getQR(req.params.propertySlug)
  const status = manager.getStatus(req.params.propertySlug)
  res.json({ qr_base64: qr, status })
})

app.listen(3001, () => console.log('Baileys bridge running on :3001'))
```

---

## 5. FastAPI Backend — Shadow Pilot Processor

### 5.1 New File: backend/app/services/shadow_pilot_processor.py

```python
"""
Shadow Pilot Message Processor
Receives events from the Baileys bridge and updates ShadowPilotConversation records.
"""
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional
from cryptography.fernet import Fernet
import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.shadow_pilot import ShadowPilotConversation
from app.models.property import Property
from app.services.after_hours import is_after_hours
from app.services.shadow_pilot_classifier import classify_intent, extract_topic


FERNET = Fernet(os.environ["FERNET_ENCRYPTION_KEY"].encode())


def hash_phone(phone_jid: str) -> str:
    """Deterministic hash for deduplication. Never stored in plain text."""
    return hashlib.sha256(phone_jid.encode()).hexdigest()


def encrypt_phone(phone_jid: str) -> str:
    return FERNET.encrypt(phone_jid.encode()).decode()


def phone_from_jid(jid: str) -> str:
    """Extract E.164 phone number from WhatsApp JID (e.g. '60123456789@s.whatsapp.net')"""
    return "+" + jid.split("@")[0]


async def handle_message_received(
    db: AsyncSession,
    property_slug: str,
    sender_jid: str,
    message_id: str,
    content_preview: Optional[str],
    timestamp_ms: int,
    has_media: bool,
) -> None:
    """
    Process an incoming guest message during shadow pilot.
    Creates a new ShadowPilotConversation or updates an existing open one.
    NEVER sends any reply to the guest.
    """
    prop = await db.scalar(
        select(Property).where(Property.slug == property_slug)
    )
    if not prop or not prop.shadow_pilot_mode:
        return

    message_time = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    phone_hash = hash_phone(sender_jid)

    # Look for an existing open conversation from this guest within the last 24 hours
    existing = await db.scalar(
        select(ShadowPilotConversation)
        .where(
            ShadowPilotConversation.property_id == prop.id,
            ShadowPilotConversation.guest_phone_hash == phone_hash,
            ShadowPilotConversation.status == "open",
        )
        .order_by(ShadowPilotConversation.first_guest_message_at.desc())
    )

    after_hours = is_after_hours(prop, message_time)

    if existing:
        # Update existing conversation
        existing.last_guest_message_at = message_time
        existing.message_count_guest += 1
        existing.updated_at = datetime.utcnow()
    else:
        # Check if repeat guest (any previous conversation from this phone hash)
        prior = await db.scalar(
            select(ShadowPilotConversation)
            .where(
                ShadowPilotConversation.property_id == prop.id,
                ShadowPilotConversation.guest_phone_hash == phone_hash,
            )
        )
        is_repeat = prior is not None

        # Intent classification — async, lightweight
        intent, confidence, topic, language = await classify_intent(content_preview or "")

        conv = ShadowPilotConversation(
            property_id=prop.id,
            guest_phone_encrypted=encrypt_phone(sender_jid),
            guest_phone_hash=phone_hash,
            first_guest_message_at=message_time,
            last_guest_message_at=message_time,
            is_after_hours=after_hours,
            is_booking_intent=intent in ("room_booking", "rate_query", "availability_check"),
            is_group_booking=intent == "group_booking",
            is_repeat_guest=is_repeat,
            intent=intent,
            intent_confidence=confidence,
            top_topic=topic,
            language_detected=language,
            message_count_guest=1,
            first_guest_message_preview=content_preview[:200] if content_preview else None,
            status="open",
        )
        db.add(conv)

    await db.commit()


async def handle_message_sent(
    db: AsyncSession,
    property_slug: str,
    recipient_jid: str,
    message_id: str,
    timestamp_ms: int,
) -> None:
    """
    Process a staff outgoing reply during shadow pilot.
    Updates the ShadowPilotConversation with response time.
    We do NOT capture the content of staff replies.
    """
    prop = await db.scalar(
        select(Property).where(Property.slug == property_slug)
    )
    if not prop or not prop.shadow_pilot_mode:
        return

    reply_time = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    phone_hash = hash_phone(recipient_jid)

    # Find the open conversation for this guest
    conv = await db.scalar(
        select(ShadowPilotConversation)
        .where(
            ShadowPilotConversation.property_id == prop.id,
            ShadowPilotConversation.guest_phone_hash == phone_hash,
            ShadowPilotConversation.status == "open",
        )
        .order_by(ShadowPilotConversation.first_guest_message_at.desc())
    )

    if not conv:
        return  # Staff replied to a guest with no tracked incoming message — ignore

    if conv.first_staff_reply_at is None:
        # This is the FIRST staff reply — compute response time
        conv.first_staff_reply_at = reply_time
        conv.response_time_minutes = (
            reply_time - conv.first_guest_message_at
        ).total_seconds() / 60

    conv.last_staff_reply_at = reply_time
    conv.message_count_staff += 1
    conv.status = "staff_replied"
    conv.updated_at = datetime.utcnow()

    # Compute estimated value if this was a booking-intent conversation
    # and it's now been replied to (staff handled it, so it may convert)
    if conv.is_booking_intent and conv.estimated_value_rm is None:
        prop_adr = prop.adr or 230.0
        prop_nights = prop.avg_stay_nights or 1.0
        conv.estimated_value_rm = prop_adr * prop_nights * 0.20

    await db.commit()
```

### 5.2 New File: backend/app/services/shadow_pilot_classifier.py

```python
"""
Lightweight intent classifier for shadow pilot messages.
Uses the existing LLM chain but with a minimal, fast prompt.
Result is cached in Redis for 1 hour per message content hash.
"""
import hashlib
import json
from typing import Tuple
from app.core.llm import call_llm_simple  # Existing utility


CLASSIFY_PROMPT = """You are classifying a WhatsApp message sent to a Malaysian hotel.

Message: "{message}"

Classify into EXACTLY ONE of these intents:
- room_booking (guest wants to book a room)
- rate_query (asking about rates or prices)
- availability_check (asking if rooms are available on specific dates)
- group_booking (booking for 5+ people or an event)
- facilities_inquiry (pool, gym, parking, breakfast, etc.)
- complaint (dissatisfied guest)
- general (anything else)

Also extract:
- A short topic label (max 4 words, in English)
- Language: "bm", "en", or "mixed"
- Confidence: 0.0–1.0

Respond in JSON only:
{"intent": "...", "topic": "...", "language": "...", "confidence": 0.0}"""


async def classify_intent(
    message: str,
) -> Tuple[str, float, str, str]:
    """Returns (intent, confidence, topic, language)"""
    if not message.strip():
        return ("general", 0.5, "unknown", "unknown")

    try:
        raw = await call_llm_simple(CLASSIFY_PROMPT.format(message=message[:300]))
        result = json.loads(raw)
        return (
            result.get("intent", "general"),
            float(result.get("confidence", 0.5)),
            result.get("topic", "unknown"),
            result.get("language", "unknown"),
        )
    except Exception:
        # If classification fails, mark as general rather than blocking
        return ("general", 0.0, "unknown", "unknown")
```

### 5.3 New File: backend/app/services/shadow_pilot_aggregator.py

```python
"""
Daily aggregation job for shadow pilot analytics.
Run by Cloud Scheduler at midnight property-local time.
Covers: POST /api/v1/internal/run-shadow-pilot-aggregation
"""
from datetime import date, datetime, timezone, timedelta
from collections import Counter
from sqlalchemy import select, func
from app.models.shadow_pilot import ShadowPilotConversation, ShadowPilotAnalyticsDaily
from app.models.property import Property


async def run_daily_aggregation(db, target_date: date = None):
    """
    Aggregate yesterday's ShadowPilotConversation rows into
    ShadowPilotAnalyticsDaily for all active shadow pilot properties.
    """
    if target_date is None:
        target_date = (datetime.now(timezone.utc) - timedelta(days=1)).date()

    # Get all properties currently in shadow_pilot_mode
    properties = await db.scalars(
        select(Property).where(
            Property.shadow_pilot_mode == True,
            Property.shadow_pilot_session_active == True,
        )
    )

    for prop in properties:
        await _aggregate_property(db, prop, target_date)


async def _aggregate_property(db, prop: Property, report_date: date):
    # Fetch all conversations for this property on target_date (property-local time)
    convs = await db.scalars(
        select(ShadowPilotConversation).where(
            ShadowPilotConversation.property_id == prop.id,
            func.date(ShadowPilotConversation.first_guest_message_at
                      .op('AT TIME ZONE')(prop.timezone)) == report_date,
        )
    )
    convs = list(convs)

    if not convs:
        return  # No data for this day — skip

    responded = [c for c in convs if c.first_staff_reply_at is not None]
    unanswered = [c for c in convs if c.first_staff_reply_at is None]
    after_hours = [c for c in convs if c.is_after_hours]
    ah_unanswered = [c for c in convs if c.is_after_hours and c.first_staff_reply_at is None]
    booking_intent = [c for c in convs if c.is_booking_intent]

    # Mark conversations that have been open > 24hr with no reply as abandoned
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    for c in unanswered:
        if c.first_guest_message_at < cutoff and c.status == "open":
            c.is_unanswered = True
            c.status = "abandoned"

    # Response times
    rt_values = [c.response_time_minutes for c in responded if c.response_time_minutes]
    ah_rt = [c.response_time_minutes for c in responded
             if c.is_after_hours and c.response_time_minutes]

    avg_rt = sum(rt_values) / len(rt_values) if rt_values else None
    avg_ah_rt = sum(ah_rt) / len(ah_rt) if ah_rt else None

    # Revenue
    prop_adr = prop.adr or 230.0
    prop_nights = prop.avg_stay_nights or 1.0
    bi_unanswered = [c for c in ah_unanswered if c.is_booking_intent]
    slow_resp = [c for c in responded if c.is_booking_intent
                 and c.response_time_minutes and c.response_time_minutes > 240]

    rev_at_risk = len(bi_unanswered) * prop_adr * prop_nights * 0.20
    rev_conservative = rev_at_risk * 0.60
    ota_equiv = rev_conservative * 0.18
    slow_rev = len(slow_resp) * prop_adr * prop_nights * 0.15
    daily_leakage = rev_conservative + slow_rev

    # Hour-by-hour
    hour_counts: dict[str, int] = {str(h): 0 for h in range(24)}
    for c in convs:
        local_hour = c.first_guest_message_at.astimezone(
            __import__('zoneinfo').ZoneInfo(prop.timezone)
        ).hour
        hour_counts[str(local_hour)] += 1

    peak_hour = int(max(hour_counts, key=lambda h: hour_counts[h]))
    ah_hours = {k: v for k, v in hour_counts.items()
                if int(k) not in range(*_business_hour_range(prop))}
    ah_peak = int(max(ah_hours, key=lambda h: ah_hours[h])) if ah_hours else None

    # Topics
    all_topics = [c.top_topic for c in convs if c.top_topic]
    unanswered_topics = [c.top_topic for c in ah_unanswered if c.top_topic]
    top_topics = [t for t, _ in Counter(all_topics).most_common(5)]
    top_unanswered = [t for t, _ in Counter(unanswered_topics).most_common(5)]

    # Language breakdown
    langs = Counter(c.language_detected for c in convs if c.language_detected)
    total_lang = sum(langs.values()) or 1
    lang_breakdown = {k: round(v / total_lang, 2) for k, v in langs.items()}

    # Upsert into ShadowPilotAnalyticsDaily
    existing = await db.scalar(
        select(ShadowPilotAnalyticsDaily).where(
            ShadowPilotAnalyticsDaily.property_id == prop.id,
            ShadowPilotAnalyticsDaily.report_date == report_date,
        )
    )

    row_data = dict(
        total_inquiries=len(convs),
        after_hours_inquiries=len(after_hours),
        business_hours_inquiries=len(convs) - len(after_hours),
        booking_intent_inquiries=len(booking_intent),
        group_booking_inquiries=sum(1 for c in convs if c.is_group_booking),
        repeat_guest_contacts=sum(1 for c in convs if c.is_repeat_guest),
        responded_count=len(responded),
        unanswered_count=len(unanswered),
        after_hours_unanswered=len(ah_unanswered),
        after_hours_responded_next_day=sum(
            1 for c in responded if c.is_after_hours
            and c.response_time_minutes and c.response_time_minutes > 480
        ),
        avg_response_time_minutes=avg_rt,
        avg_response_time_after_hours=avg_ah_rt,
        response_time_over_1hr=sum(1 for t in rt_values if t > 60),
        response_time_over_4hr=sum(1 for t in rt_values if t > 240),
        response_time_over_8hr=sum(1 for t in rt_values if t > 480),
        response_time_over_24hr=sum(1 for t in rt_values if t > 1440),
        revenue_at_risk_total=rev_at_risk,
        revenue_at_risk_conservative=rev_conservative,
        ota_commission_equivalent=ota_equiv,
        slow_response_revenue_at_risk=slow_rev,
        daily_revenue_leakage=daily_leakage,
        peak_inquiry_hour=peak_hour,
        after_hours_peak_hour=ah_peak,
        inquiries_by_hour=hour_counts,
        top_inquiry_topics=top_topics,
        top_unanswered_topics=top_unanswered,
        booking_intent_rate=len(booking_intent) / len(convs) if convs else 0,
        language_breakdown=lang_breakdown,
        computed_at=datetime.utcnow(),
    )

    if existing:
        for k, v in row_data.items():
            setattr(existing, k, v)
    else:
        db.add(ShadowPilotAnalyticsDaily(
            property_id=prop.id,
            report_date=report_date,
            **row_data,
        ))

    await db.commit()


def _business_hour_range(prop: Property):
    """Returns (open_hour, close_hour) for the property based on today's schedule."""
    schedule = prop.operating_hours or {}
    today = datetime.now().strftime('%A').lower()
    day_sched = schedule.get(today, {})
    open_h = int(str(day_sched.get('open', '09:00')).split(':')[0])
    close_h = int(str(day_sched.get('close', '18:00')).split(':')[0])
    return (open_h, close_h)
```

---

## 6. API Endpoints

### 6.1 New Internal Endpoints (FastAPI — backend/app/routes/internal.py)

```python
# ── Shadow pilot event receiver (from Baileys bridge) ─────────────────────
POST /api/v1/internal/shadow-event
# Body: {event_type, property_slug, sender_jid, message_id,
#        content_preview, timestamp_unix, has_media}
# Auth: X-Internal-Secret
# Action: Calls shadow_pilot_processor.handle_message_received/sent

POST /api/v1/internal/shadow-session-status
# Body: {property_slug, status, qr_base64}
# Auth: X-Internal-Secret
# Action: Updates Property.shadow_pilot_session_active + session_last_seen

POST /api/v1/internal/shadow-heartbeat
# Body: {property_slug}
# Auth: X-Internal-Secret
# Action: Updates Property.shadow_pilot_session_last_seen

GET  /api/v1/internal/shadow-active-properties
# Returns: {properties: [{slug, shadow_pilot_phone}, ...]}
# Auth: X-Internal-Secret
# Action: Used by Baileys bridge on startup to reload all active sessions

# ── Shadow pilot scheduled jobs ───────────────────────────────────────────
POST /api/v1/internal/run-shadow-pilot-aggregation
# No body. Auth: X-Internal-Secret.
# Runs daily aggregation for all active shadow pilot properties (yesterday's date).

POST /api/v1/internal/run-shadow-pilot-weekly-report
# No body. Auth: X-Internal-Secret.
# Sends weekly report email to GMs where shadow_pilot_start_date is 7, 14, 21... days ago.
# Also sends SheersSoft AM notification.
```

### 6.2 New SuperAdmin Endpoints

```python
# ── Shadow pilot provisioning ─────────────────────────────────────────────
POST /api/v1/superadmin/shadow-pilots
# Body: {property_id, hotel_phone, gm_email, adr, avg_stay_nights, operating_hours}
# Auth: require_superadmin
# Action: Sets shadow_pilot_mode=True, generates dashboard token, POSTs to Baileys bridge

GET  /api/v1/superadmin/shadow-pilots/{property_id}/qr
# Returns: {qr_base64, status}
# Auth: require_superadmin
# Proxies to Baileys bridge GET /qr/:propertySlug

DELETE /api/v1/superadmin/shadow-pilots/{property_id}
# Auth: require_superadmin
# Stops session, sets shadow_pilot_mode=False

GET  /api/v1/superadmin/shadow-pilots
# Auth: require_superadmin
# Returns list of all active shadow pilots with 7-day metric summary

GET  /api/v1/superadmin/shadow-pilots/{property_id}/analytics
# Auth: require_superadmin
# Returns full ShadowPilotAnalyticsDaily rows for this property
```

### 6.3 New Public Endpoint (Token-Gated GM Dashboard)

```python
GET  /api/v1/shadow/{property_slug}/summary?token={jwt}
# No session auth — token-only
# Validates signed JWT in query param (expires 30 days after issue)
# Returns: ShadowPilotWeeklyRollup + last 7 days of ShadowPilotAnalyticsDaily
# Used by: /shadow/[slug] Next.js page (no auth required)
```

---

## 7. Frontend Pages

### 7.1 Admin — /admin/shadow-pilots (Updated)

**Existing page** — update to support Baileys QR flow:

```
┌─────────────────────────────────────────────────────────────────┐
│  Shadow Pilots                           [+ New Shadow Pilot]   │
├─────────────────────────────────────────────────────────────────┤
│  Active Pilots (3)                                              │
│                                                                 │
│  Hotel Seri KL    ●  Connected    Day 4    23 msgs / RM 4,200  │
│  Taman Inn        ●  Connected    Day 1    3 msgs  / RM 690    │
│  Grand Palace     ○  Awaiting QR  Day 0    —                   │
│                              [Show QR]                          │
└─────────────────────────────────────────────────────────────────┘
```

**New Shadow Pilot Modal — fields:**
- Hotel name (auto-populated from Property)
- Hotel's WhatsApp number (confirmation)
- ADR (RM, default from Property.adr)
- Avg stay nights (default 1.0)
- Operating hours (start time / end time)
- GM email for weekly report

**After submission:**
1. API call → `POST /api/v1/superadmin/shadow-pilots`
2. Modal transitions to QR display step
3. QR code shown (polled every 3 seconds from `GET /qr/:slug`)
4. On session connected → modal shows "✓ Connected to [Hotel Name]'s WhatsApp"

### 7.2 Public — /shadow/[slug] (New Page)

Token-gated. No auth required. Renders ShadowPilotWeeklyRollup for the GM.

**This is the page GMs land on from the weekly report email CTA.**

Layout:
1. **Header**: Property name + "Your WhatsApp: 7 Days of Data"
2. **Hero KPIs** (6 cards): total inquiries / after-hours unanswered / weekly leakage / avg after-hours response / annualised leakage / booking intent rate
3. **Hour-by-hour chart** (HTML/CSS bar chart — no external image dependency)
4. **Response time breakdown** (stacked bar)
5. **Sample unanswered conversations** (3–5 rows, phone masked)
6. **"What If" comparison table**: Current state vs With Nocturn AI
7. **CTA section**: "Start 48-Hour Implementation — RM 999" → `/apply`

---

## 8. Weekly Report Email Template

### 8.1 Subject Line

```
[Hotel Name]: You left RM [weekly_revenue_leakage] on the table this week.
```

Example: `Taman Inn: You left RM 8,400 on the table this week.`

### 8.2 Full Email Spec

```
FROM: Ahmad Basyir <basyir@sheerssoft.com>
SUBJECT: [Hotel Name]: You left RM X on the table this week.

──────────────────────────────────────────────────────────────
[Hotel Name]
WhatsApp Performance Report · [Date Range]
──────────────────────────────────────────────────────────────

This week, your WhatsApp received [total_inquiries] inquiries.

Your team responded to [responded_count] of them.

The other [unanswered_count] went unanswered.

──────────────────────────────────────────────────────────────
REVENUE LEAKED THIS WEEK: RM [weekly_revenue_leakage]
(Conservative estimate — 40% discount applied)
──────────────────────────────────────────────────────────────

Here's the breakdown:

  After-hours inquiries           [after_hours_inquiries]
  After-hours — no response       [after_hours_unanswered]
  Booking intent (unanswered)     [booking_intent_unanswered]
  Avg response time (after-hrs)   [avg_response_time_after_hours] hrs
  Slowest response time           [worst_response_time] hrs

──────────────────────────────────────────────────────────────
WHEN IT HAPPENED  (inquiries by hour)
──────────────────────────────────────────────────────────────

[HTML/CSS bar chart — 24 bars, coloured green/red]

Most active after-hours period: [after_hours_peak_hour]:00–[+1]:00

──────────────────────────────────────────────────────────────
WHAT THEY WERE ASKING (that went unanswered)
──────────────────────────────────────────────────────────────

[Conversation 1]
  10:47 PM · Booking enquiry
  "Ada bilik untuk hujung minggu ni? Berapa..."
  Estimated value: RM [estimated_value_rm]
  Response: Never

[Conversation 2]
  11:23 PM · Rate query
  "Hi, how much for 2 nights? Checking in Friday..."
  Estimated value: RM [estimated_value_rm]
  Response: Next morning (6.4 hrs later)

[Conversation 3]
  2:14 AM · Availability check
  "Boleh check ada bilik tak for this Saturday..."
  Estimated value: RM [estimated_value_rm]
  Response: Never

──────────────────────────────────────────────────────────────
IF NOCTURN AI HAD BEEN ACTIVE THIS WEEK
──────────────────────────────────────────────────────────────

  ✓ All [after_hours_inquiries] after-hours inquiries answered instantly
  ✓ Response time: under 30 seconds (vs your current [avg_response_time_after_hours] hrs)
  ✓ Est. RM [recovery_estimate] in captured direct bookings
  ✓ RM 0 in OTA commissions paid on those bookings
  ✓ Your team wakes up to [unanswered_count] warm leads, not silence

  Nocturn AI cost for the same period:
  Platform fee: RM 199/month
  Performance fee: 3% only on confirmed bookings we close
  Net position: You keep ~15% per booking that would have gone to OTA

──────────────────────────────────────────────────────────────
PROJECTED ANNUAL IMPACT
──────────────────────────────────────────────────────────────

  Weekly leakage × 52 weeks = RM [annualised_revenue_leakage]
  Nocturn AI annual cost      = RM [nocturn_annual_cost]
  Net year-1 recovery         = RM [nocturn_year_1_net_recovery]
  ROI multiple                = [roi_multiple]×

──────────────────────────────────────────────────────────────

  [VIEW YOUR FULL DASHBOARD]

  Or reply to this email to speak with Ahmad Basyir directly.

──────────────────────────────────────────────────────────────
Sheers Software Sdn Bhd · SSM 202501033756
Unsubscribe · Privacy Policy
```

---

## 9. Cloud Scheduler Jobs

Two new jobs to create on next GCP deploy (in addition to the 5 existing jobs):

| Job Name | Schedule | Endpoint | Description |
|---|---|---|---|
| `shadow-pilot-daily-aggregation` | `0 0 * * *` (midnight UTC) | `POST /api/v1/internal/run-shadow-pilot-aggregation` | Aggregates yesterday's conversations into ShadowPilotAnalyticsDaily for all active pilots |
| `shadow-pilot-weekly-report` | `0 8 * * 1` (Monday 8am UTC) | `POST /api/v1/internal/run-shadow-pilot-weekly-report` | Checks all shadow pilots, sends report to any GM whose pilot is 7 days old (or multiple of 7) |

Both jobs require `X-Internal-Secret` header.

**Report trigger logic** (weekly report job):
```python
async def run_weekly_report(db):
    today = date.today()
    properties = await db.scalars(
        select(Property).where(Property.shadow_pilot_mode == True)
    )
    for prop in properties:
        if prop.shadow_pilot_start_date is None:
            continue
        days_active = (today - prop.shadow_pilot_start_date.date()).days
        if days_active > 0 and days_active % 7 == 0:
            rollup = await compute_weekly_rollup(db, prop, today)
            await send_weekly_report_email(prop, rollup)
            await notify_sheers_am(prop, rollup)
```

---

## 10. Quality Gates

All items must pass before Sprint 2.5 is considered complete:

**Baileys Bridge:**
- [ ] QR code renders in admin panel within 5 seconds of provisioning
- [ ] Hotel GM scans QR → session status changes to "connected" in admin panel within 60 seconds
- [ ] Session auto-reconnects within 10 seconds of a drop
- [ ] Bridge restarts clean on Docker container restart (session files persisted to mounted volume)
- [ ] Heartbeat fires every 60 seconds — admin panel shows "last seen" timestamp

**Message Observation:**
- [ ] Incoming guest message → `ShadowPilotConversation` created within 3 seconds
- [ ] Outgoing staff reply → `first_staff_reply_at` set and `response_time_minutes` computed correctly
- [ ] After-hours flag set correctly against property operating hours (test: message at 11pm vs 10am)
- [ ] Intent classified on all incoming messages — `is_booking_intent = True` on at least 60% of rate/availability queries
- [ ] **Zero messages sent to any guest at any point during shadow pilot mode**
- [ ] Phone numbers encrypted at rest — plaintext phone never appears in any database column except `guest_phone_encrypted`

**Aggregation:**
- [ ] Daily aggregation job runs clean for a property with 0 conversations (no crash)
- [ ] Daily aggregation job produces correct totals for a property with 20 test conversations
- [ ] Revenue formula: `booking_intent_unanswered × 230 × 1.0 × 0.20 × 0.60` matches expected output
- [ ] `unanswered_count` matches manual count of conversations with no `first_staff_reply_at` after 24hrs

**Dashboard & Email:**
- [ ] Token-gated dashboard loads at `/shadow/[slug]?token=[valid_jwt]` — all 6 KPIs visible
- [ ] Invalid token returns 401
- [ ] Expired token (>30 days) returns 401
- [ ] Weekly report email sends to correct GM email
- [ ] Email renders correctly on mobile (tested at 375px width)
- [ ] SheersSoft AM notification fires within 60 seconds of report send

---

## 11. Security Considerations

- **No guest message content is stored long-term.** `first_guest_message_preview` stores only the first 200 characters of the first message, only for display in the report, and is purged 90 days after shadow pilot ends.
- **Staff message content is never captured.** The bridge listens to outgoing messages only for the timestamp — no content is forwarded.
- **Phone numbers are Fernet-encrypted at field level.** `guest_phone_hash` (SHA-256) is used for all deduplication logic.
- **Token-gated dashboard uses signed JWTs** (HS256, signed with `SECRET_KEY`). Payload: `{property_id, type: "shadow_dashboard", exp: now + 30 days}`.
- **Baileys session files are stored on a Cloud Run mounted volume** (`/sessions`), not in the database. If the volume is lost, the hotel simply re-scans the QR.
- **WhatsApp ToS note:** Shadow pilot uses Baileys in read-observe-only mode. No messages are sent. This is the lowest-risk usage profile. For production co-pilot (Stage 2), migrate to official BSP (Wati/360dialog) after pilot proves ROI.

---

*This document is LLM-consumable. All model field names, service method signatures, and API paths are exact — use them verbatim in code generation. For implementation sequence, see build_plan.md v2.5 Sprint 2.5.*
