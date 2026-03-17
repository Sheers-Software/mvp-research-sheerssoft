# Portal Architecture — Nocturn AI
## Version 1.0 · 18 Mar 2026

---

## 1. Philosophy

### Internal Portal (`/admin`) — SheersSoft Operators
> "Keep the platform healthy, inform tenants proactively, and ship with confidence."

The internal portal is an **ops and observability tool**. Its job is to surface platform health, detect problems before tenants do, and give SheersSoft staff the controls to act — maintenance mode, announcements, tenant provisioning, support escalations. It is never seen by hotel clients.

### Client Portal — Hotel Teams
> "Hotel staff should walk away from every session feeling like the AI is working for them and that revenue is being protected."

The client side is split into two distinct experiences by role:

- **`/portal`** — Tenant management layer (owners and admins). Configure the business: manage properties, team, KB, channels, billing, and subscription.
- **`/dashboard`** — Property operations layer (all staff). Work the day-to-day: conversations, leads, analytics, performance insights.

These two layers serve different mental models. An owner checking whether the AI is configured well is a different task from a front-desk agent resolving a guest inquiry.

---

## 2. Deployment Separation Decision

### Current State
Both portals are route groups in a single Next.js app deployed on one Cloud Run service. The security boundary is `is_superadmin` enforced at the API level.

### Recommendation: Stay Monorepo, Separate by Domain (Later)

| Option | When | Trade-off |
|--------|------|-----------|
| **Route groups in one app** (current) | Now → first 10 tenants | Fast to build; no infra overhead |
| **Subdomain split** (`admin.sheerssoft.com` / `app.sheerssoft.com`) | Before first enterprise client | Stronger isolation; separate deploys; separate autoscaling |
| **Separate Next.js apps** | At scale (50+ tenants) | Full isolation; independent release cadence |

**Decision:** Keep single Next.js app for now. Route-group separation (`/admin`, `/portal`, `/dashboard`, `/welcome`) is sufficient. Add subdomain routing (via Cloud Run custom domain + Cloud Load Balancer path rules) when the first enterprise client is onboarded.

The backend API already enforces the authorization model correctly — `require_superadmin()`, `check_tenant_access()`, `check_property_access()` — so a URL separation is cosmetic until the client list grows.

---

## 3. Route Map (Full Target State)

```
/                           → Auth redirect
/login                      → Magic link + legacy admin login
/auth/callback              → Supabase PKCE handler

── INTERNAL PORTAL ───────────────────────────────────────────────
/admin                      → Platform overview (KPIs, live badge)
/admin/onboarding           → Provision new tenant
/admin/tenants              → Tenant list
/admin/tenants/[id]         → Tenant detail + utilization
/admin/pipeline             → Onboarding kanban
/admin/tickets              → Support ticket queue
/admin/applications         → Intake applications
/admin/system               → System config, maintenance mode, scheduler
/admin/announcements        → Compose + manage announcements      [NEW]
/admin/health               → Service health dashboard            [NEW]

── TENANT MANAGEMENT PORTAL ──────────────────────────────────────
/portal                     → Tenant home (multi-property summary) [NEW]
/portal/properties          → Property list + per-property settings [NEW]
/portal/kb/[propertyId]     → Knowledge base upload + management   [NEW]
/portal/team                → Team members + invite + roles        [NEW]
/portal/channels            → Channel status + reconfigure         [NEW]
/portal/announcements       → Inbox: SheersSoft maintenance notices [NEW]
/portal/support             → Submit support ticket + history      [NEW]
/portal/billing             → Subscription + Stripe portal         [NEW]

── PROPERTY OPERATIONS PORTAL ─────────────────────────────────────
/dashboard                  → Home: today's KPIs + 30-day summary
/dashboard/conversations    → Inbox: list + detail + staff reply
/dashboard/leads            → Lead pipeline + convert flow
/dashboard/analytics        → Charts (7/30/90-day)
/dashboard/settings         → Property config (operating hours, revenue, brand voice)
/dashboard/insights         → AI monthly insights + FAQ trends     [NEW]

── ONBOARDING WIZARD ──────────────────────────────────────────────
/welcome                    → Step-by-step first-time setup        [NEW]
/welcome/property           → Step 1: Confirm property details
/welcome/kb                 → Step 2: Upload knowledge base
/welcome/channels           → Step 3: Test channel connection
/welcome/team               → Step 4: Invite staff
/welcome/golive             → Step 5: Go-live checklist
```

---

## 4. Internal Portal — Feature Specification

### 4.1 Existing (Keep + Enhance)

| Page | Enhancement Needed |
|------|--------------------|
| `/admin` (Overview) | Add maintenance mode banner when active |
| `/admin/tenants/[id]` | Add utilization section (conversations/month vs plan cap) |
| `/admin/system` | Add maintenance mode toggle; add global AI model selector |

### 4.2 NEW: Service Health Dashboard (`/admin/health`)

**Purpose:** Real-time status of every external dependency. SheersSoft staff should know before tenants do when something is degraded.

**Services to monitor:**
| Service | Check method | Healthy threshold |
|---------|-------------|-------------------|
| PostgreSQL (Supabase) | SELECT 1 query via pool | < 200ms |
| Redis | PING | < 50ms (or "in-memory fallback" notice) |
| Supabase Auth | GET /auth/v1/health | HTTP 200 |
| Gemini API | Probe model list or embed | HTTP 200 |
| OpenAI API | /models endpoint | HTTP 200 |
| Anthropic API | /models endpoint | HTTP 200 |
| SendGrid | /v3/user/profile | HTTP 200 |
| WhatsApp Cloud API | graph.facebook.com token check | HTTP 200 |
| Stripe API | retrieve balance | HTTP 200 |

**UI:** Status grid with green/amber/red indicators, latency readout, last-checked timestamp. Auto-refreshes every 30 seconds. Amber = degraded/slow; Red = unreachable.

**Backend:** `GET /api/v1/superadmin/service-health` — runs all checks in parallel (asyncio.gather), returns structured status per service. Timeouts of 3s per check. Results cached for 20s.

### 4.3 NEW: Maintenance Mode

**Purpose:** One toggle to gracefully pause the platform for maintenance without breaking guest experience or confusing hotel staff.

**Behaviour when ON:**
- Channel webhooks (WhatsApp, email, web chat) receive a canned maintenance message reply to guests: "Our reservation system is undergoing scheduled maintenance. We'll be back shortly. For urgent requests please call [property phone]."
- Tenant `/dashboard` and `/portal` show a full-screen maintenance banner with estimated resolution time
- Internal `/admin` remains fully accessible
- All API endpoints not protected by `require_superadmin` return HTTP 503 with `{"maintenance": true, "message": "...", "eta": "..."}`

**Implementation:**
- `maintenance_mode` key stored in `system_config` table (already exists as key-value store)
- Value: `{"enabled": true, "message": "Scheduled maintenance", "eta": "2026-03-18T14:00:00Z"}`
- FastAPI middleware (`app/middleware.py`) checks this key on each request; skip for `/admin/*` and `/api/v1/internal/*`
- Frontend polls `GET /api/v1/system/info` (already exists) every 60s; if `maintenance: true` → show banner
- **Endpoints:**
  - `GET /api/v1/superadmin/maintenance` — returns current state
  - `PUT /api/v1/superadmin/maintenance` — set enabled/disabled + message + eta

### 4.4 NEW: Announcements (`/admin/announcements`)

**Purpose:** Proactively inform hotel clients of scheduled maintenance windows, new features, or service incidents without requiring a support ticket from them.

**Announcement types:**
- `maintenance` — Scheduled downtime. Shown with amber warning styling.
- `incident` — Active service degradation. Shown with red alert styling.
- `feature` — New capability available. Shown with indigo info styling.
- `billing` — Subscription or payment-related notice. Shown with amber styling.

**Targeting:**
- All tenants
- By subscription tier (e.g., only `pilot` tenants)
- Specific tenant (by tenant_id)

**Delivery:**
- In-app banner in `/portal` and `/dashboard` (primary)
- Optional email to tenant owner(s) on create

**Lifecycle:** `draft` → `scheduled` → `active` → `resolved` → `archived`

**Backend endpoints:**
- `POST /api/v1/superadmin/announcements` — create announcement
- `GET /api/v1/superadmin/announcements` — list all (admin only)
- `PATCH /api/v1/superadmin/announcements/{id}` — update / resolve / archive
- `GET /api/v1/announcements/active` — list active announcements for the authenticated tenant (no superadmin required; scoped by tenant_id in JWT)

**Data model:**
```sql
CREATE TABLE announcements (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type        VARCHAR(20) NOT NULL,          -- maintenance|incident|feature|billing
    status      VARCHAR(20) NOT NULL DEFAULT 'draft', -- draft|scheduled|active|resolved|archived
    title       VARCHAR(255) NOT NULL,
    body        TEXT NOT NULL,
    target_type VARCHAR(20) NOT NULL DEFAULT 'all',  -- all|tier|tenant
    target_tier VARCHAR(20),                   -- populated when target_type='tier'
    target_tenant_id UUID REFERENCES tenants(id),    -- populated when target_type='tenant'
    scheduled_at TIMESTAMPTZ,                  -- when to go active (null = immediate)
    resolved_at  TIMESTAMPTZ,
    send_email   BOOLEAN NOT NULL DEFAULT FALSE,
    created_by   UUID REFERENCES users(id),
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 5. Client Portal — Feature Specification

### 5.1 `/portal` — Tenant Management Layer

**Access:** `TenantMembership.role IN ('owner', 'admin')` only. Staff are redirected to `/dashboard`.

#### 5.1.1 Portal Home (`/portal`)
- Multi-property summary: each property as a card showing status, today's inquiry count, active conversations, AI handling rate
- Onboarding completion score (0–100) with next recommended action
- Active announcements from SheersSoft (if any)
- Quick links: Team, KB, Channels, Support

#### 5.1.2 Knowledge Base Management (`/portal/kb/[propertyId]`)
- List of uploaded documents (type, title, character count, last updated)
- Add new document (type dropdown: faq, rates, facilities, policies, promotions, custom)
- Edit existing document content inline
- Delete document with confirmation
- Live character count and embedding status indicator
- **Backend:** `GET /api/v1/properties/{id}/knowledge-base` (list), `PUT /api/v1/properties/{id}/knowledge-base` (bulk replace, already exists)

#### 5.1.3 Team Management (`/portal/team`)
- List all team members with role, property access scope, last login
- Invite member: email + role + staff_tier + property_ids
- Role badges: Owner (gold), Admin (indigo), Manager (green), Revenue (blue), Ops (orange)
- Remove member (confirmation required)
- **Backend:** `GET /api/v1/onboarding/team/{tenant_id}` (new), `POST /api/v1/onboarding/invite-user/{tenant_id}` (exists), `DELETE /api/v1/portal/team/{membership_id}` (new)

#### 5.1.4 Channel Status (`/portal/channels`)
- Per-property channel status cards: WhatsApp, Email, Web Widget
- Status: active (green), configuring (amber), failed (red), skipped (grey)
- Failed channels: error detail + "Retry Setup" button
- Web widget: copy-paste embed snippet
- **Backend:** Uses existing `GET /api/v1/system/integrations` and `POST /api/v1/superadmin/tenants/{id}/retry-channel/{channel}`

#### 5.1.5 Announcements Inbox (`/portal/announcements`)
- List of active + historical announcements
- Type icons + severity colour coding
- Mark as read / dismiss
- **Backend:** `GET /api/v1/announcements/active`

#### 5.1.6 Billing (`/portal/billing`)
- Current plan: tier, status (trialing/active/past_due), pilot end date
- "Upgrade Plan" → Stripe Checkout session (`POST /api/v1/billing/checkout`)
- Subscription history (from Stripe webhook synced data)

#### 5.1.7 Support (`/portal/support`)
- Submit support ticket (subject + priority + description)
- List own open tickets with status
- **Backend:** `POST /api/v1/support/tickets` (new endpoint for tenant self-service; distinct from existing `/superadmin/tickets` which is the admin side)

### 5.2 `/dashboard` — Property Operations Layer (Enhanced)

Keep all existing pages. Add:

#### 5.2.1 AI Insights (`/dashboard/insights`)
- Monthly summary: top 5 guest FAQs, sentiment distribution, most common inquiry intents
- KB gap suggestions: "Guests asked about spa facilities 23 times — your KB has no entry for this"
- Trend: which inquiry types are increasing/decreasing
- **Backend:** Existing `services/insights.py` already generates this data via Gemini. Needs `GET /api/v1/properties/{id}/insights` endpoint to surface the last run result.

#### 5.2.2 Announcements Banner
- Non-blocking top-of-page banner in `/dashboard/layout.tsx`
- Polls `GET /api/v1/announcements/active` on load
- Dismissable per session; re-appears for `maintenance` type announcements

#### 5.2.3 Maintenance Mode Banner
- Full-screen overlay (non-dismissable) when `maintenance_mode` is active
- Shows message + ETA from system config
- Fetched via existing `GET /api/v1/system/info`

### 5.3 `/welcome` — Onboarding Wizard

**Trigger:** New tenant user who has `TenantMembership.role = 'owner'` and `onboarding_completed = false`.

**Resolution logic in `/auth/callback`:**
```
role=owner AND onboarding_completed=false → /welcome
role=owner AND onboarding_completed=true  → /portal
role=admin                                → /portal
role=staff                                → /dashboard
```

**Steps:**
1. **Property Details** — Review auto-populated name, address, star rating, website, phone
2. **Knowledge Base** — Guided KB entry: drag-and-drop rate card PDF or paste text per category. Minimum: Rates + FAQs to unlock "Go Live"
3. **Channel Test** — Send a test WhatsApp / email to yourself, confirm it comes back correctly
4. **Invite Team** — Invite at least one staff member (skippable)
5. **Go Live** — Checklist showing completion; "Activate AI" button flips `property.is_active = true`; sends welcome email to account manager

**Backend:** Uses existing `GET /api/v1/onboarding/checklist/{tenant_id}` for progress state. New: `POST /api/v1/onboarding/complete` to set `onboarding_completed = true` on the User record and `is_active = true` on the Property.

---

## 6. New Backend Endpoints Required

| Priority | Method | Path | Description |
|----------|--------|------|-------------|
| P0 | GET | `/api/v1/superadmin/maintenance` | Get maintenance mode state |
| P0 | PUT | `/api/v1/superadmin/maintenance` | Set maintenance mode on/off |
| P0 | GET | `/api/v1/system/info` | Add `maintenance` key to existing response |
| P1 | GET | `/api/v1/superadmin/service-health` | Parallel health checks of all dependencies |
| P1 | POST | `/api/v1/superadmin/announcements` | Create announcement |
| P1 | GET | `/api/v1/superadmin/announcements` | List announcements (admin) |
| P1 | PATCH | `/api/v1/superadmin/announcements/{id}` | Update/resolve announcement |
| P1 | GET | `/api/v1/announcements/active` | Fetch active announcements for tenant |
| P2 | GET | `/api/v1/onboarding/team/{tenant_id}` | List team members for tenant |
| P2 | DELETE | `/api/v1/portal/team/{membership_id}` | Remove team member |
| P2 | GET | `/api/v1/properties/{id}/knowledge-base` | List KB documents |
| P2 | GET | `/api/v1/properties/{id}/insights` | Fetch latest insights run result |
| P2 | POST | `/api/v1/support/tickets` | Tenant self-service ticket create |
| P3 | POST | `/api/v1/onboarding/complete` | Mark onboarding done, activate property |

---

## 7. Data Model Changes Required

```sql
-- Announcements table (new)
CREATE TABLE IF NOT EXISTS announcements (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type             VARCHAR(20) NOT NULL,      -- maintenance|incident|feature|billing
    status           VARCHAR(20) NOT NULL DEFAULT 'draft',
    title            VARCHAR(255) NOT NULL,
    body             TEXT NOT NULL,
    target_type      VARCHAR(20) NOT NULL DEFAULT 'all',
    target_tier      VARCHAR(20),
    target_tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    scheduled_at     TIMESTAMPTZ,
    resolved_at      TIMESTAMPTZ,
    send_email       BOOLEAN NOT NULL DEFAULT FALSE,
    created_by       UUID REFERENCES users(id),
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Staff tier on TenantMembership (referenced in auth_rbac_plan.md)
ALTER TABLE tenant_memberships
    ADD COLUMN IF NOT EXISTS staff_tier VARCHAR(20);
-- NULL = owner/admin (no tier), 'manager'|'revenue'|'ops' for role=staff

-- Onboarding completion flag on users (referenced in auth_rbac_plan.md)
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE;

-- Maintenance mode lives in existing system_config table as a JSON key
-- Key: 'maintenance_mode'
-- Value: {"enabled": false, "message": "", "eta": null}
-- No schema change needed.
```

---

## 8. Middleware: Maintenance Mode Check

New middleware in `app/middleware.py` (added alongside existing `TelemetryMiddleware`):

```python
# Pseudocode
class MaintenanceModeMiddleware(BaseHTTPMiddleware):
    EXEMPT_PREFIXES = ["/api/v1/admin", "/api/v1/internal", "/api/v1/superadmin",
                       "/api/v1/system/info", "/api/v1/announcements/active",
                       "/auth/", "/health"]

    async def dispatch(self, request, call_next):
        if not any(request.url.path.startswith(p) for p in EXEMPT_PREFIXES):
            config = await get_maintenance_config()  # cached, 30s TTL
            if config.get("enabled"):
                return JSONResponse(
                    {"maintenance": True, "message": config["message"], "eta": config["eta"]},
                    status_code=503
                )
        return await call_next(request)
```

The frontend checks `system/info` on layout load and renders the maintenance banner independently of the 503 — this covers the case where a hotel staff member has the dashboard open before maintenance mode is activated.

---

## 9. Implementation Priority

### Phase 1 — Internal Controls (P0, ~1 day backend + 1 day frontend)
1. Add `maintenance_mode` to `system_config` seed and `system/info` response
2. `PUT /superadmin/maintenance` endpoint
3. Maintenance mode middleware
4. `/admin/system` — add maintenance toggle UI
5. `/dashboard/layout.tsx` — add maintenance banner (polls `system/info`)

### Phase 2 — Observability (P1, ~2 days backend + 1 day frontend)
6. `GET /superadmin/service-health` endpoint (parallel checks)
7. `/admin/health` page — status grid with auto-refresh

### Phase 3 — Announcements (P1, ~2 days backend + 2 days frontend)
8. `announcements` table + migration in `main.py` lifespan
9. Announcement CRUD endpoints (superadmin)
10. `GET /announcements/active` endpoint (tenant-scoped)
11. `/admin/announcements` — composer + list page
12. `/portal/announcements` + announcement banner in `/dashboard/layout.tsx`

### Phase 4 — Tenant Portal (P2, ~4 days frontend + 1 day backend)
13. `/portal` layout + home page (multi-property summary)
14. `/portal/kb/[propertyId]` — KB management
15. `/portal/team` — team management
16. `/portal/channels` — channel status
17. `/portal/billing` — subscription info + Stripe checkout link
18. `/portal/support` — ticket submission

### Phase 5 — Onboarding Wizard (P3, ~3 days frontend + 0.5 day backend)
19. `/welcome` step flow
20. `POST /onboarding/complete` endpoint
21. Auth callback routing update (welcome vs portal redirect logic)

### Phase 6 — Dashboard Enhancements (P2–P3, ~2 days)
22. `/dashboard/insights` — AI insights + KB gap suggestions
23. `GET /properties/{id}/insights` endpoint

---

## 10. Auth Callback Routing (Updated)

```
/auth/callback → exchange Supabase token → GET /auth/me
    ↓
is_superadmin=True          →  /admin
role=owner, onboarding=false →  /welcome
role=owner, onboarding=true  →  /portal
role=admin                   →  /portal
role=staff                   →  /dashboard
no membership                →  /welcome (or error page if no invitation)
```

This replaces the current binary `is_superadmin → /admin, else → /dashboard` logic.
