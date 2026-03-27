# Authentication, RBAC & Portal Separation Plan
## Nocturn AI — Version 1.0 · 18 Mar 2026

---

## 1. Why the Magic Link Goes Straight to `/admin`

The current behaviour is a side-effect of emergency work done during the auth debugging session:

1. `a.basyir94@gmail.com` was added to the `SUPERADMIN_EMAILS` env var in `cloudbuild.yaml`
2. The `supabase-callback` endpoint auto-provisions any email in that list as `is_superadmin=True`
3. The `/auth/callback` page calls `/auth/me`, sees `is_superadmin=True`, and hard-redirects to `/admin`

There is **no onboarding step, no identity question, no role selection, and no contextual routing**. The system makes a single binary decision (superadmin or not) based entirely on email domain/list membership.

---

## 2. Security & Separation Audit

### 2.1 Current Architecture (Flawed)

```
All users → /login → magic link OR admin/password
    ↓
    JWT issued with is_admin flag
    ↓
    is_superadmin=True  →  /admin   (SheersSoft internal portal)
    is_superadmin=False →  /dashboard  (tenant property portal)
```

### 2.2 Identified Security Flaws

| # | Flaw | Severity | Impact |
|---|------|----------|--------|
| 1 | `SUPERADMIN_EMAILS` is a comma-separated env var committed to `cloudbuild.yaml` in the repo | **CRITICAL** | Any repo access exposes who has root access. Rotating admin emails requires a redeploy |
| 2 | Legacy `admin / password123` hardcoded in `config.py` default | **CRITICAL** | Plaintext superadmin credentials in source code. No MFA, no rate limit on the token endpoint |
| 3 | Auto-provisioning any Supabase-authenticated user with no tenant context | **HIGH** | Any email that can receive a magic link gets a user record created. No invitation gating |
| 4 | Single `is_superadmin` boolean conflates SheersSoft employees with all other access | **HIGH** | No internal RBAC — all SheersSoft staff have identical root access |
| 5 | `accessible_property_ids` on `TenantMembership` is stored but **not consistently enforced** across routes | **HIGH** | A staff user with scoped property access may be able to call endpoints for properties they shouldn't see |
| 6 | JWT contains `is_admin` claim. Role changes in DB don't invalidate existing tokens (24h TTL) | **MEDIUM** | Demoting a user takes up to 24h to take effect |
| 7 | No logout from Supabase on sign-out — only localStorage is cleared | **MEDIUM** | Supabase session remains valid after logout from the app |
| 8 | `/admin` and `/dashboard` portals share the same Supabase Auth project and user table | **MEDIUM** | A tenant user could theoretically attempt privilege escalation against the same auth system |
| 9 | Internal scheduler endpoints protected only by `X-Internal-Secret` header | **LOW** | Secret is a single string in env; no IP allowlist or additional auth |
| 10 | No audit log for superadmin actions (tenant creation, deletion, user management) | **LOW** | No forensics trail if misuse occurs |

### 2.3 Separation Gaps

- **No portal isolation**: `/admin` and `/dashboard` are routes on the same Next.js app, served from the same Cloud Run service. A determined client user can navigate to `/admin` routes directly; only server-side auth guards prevent access, and those are not consistently present on all pages.
- **No tenant context in JWT**: The JWT carries `property_ids` but not `tenant_id`. Routes that enforce tenant-level access (`check_tenant_access`) must re-query the DB; there is no fast-path enforcement.
- **No staff-level permission granularity**: Within a tenant, the only roles are `owner`, `admin`, and `staff`. There are no fine-grained permissions (e.g., a Revenue Manager who can see analytics but not conversations).

---

## 3. Correct User Taxonomy

### 3.1 User Types

```
┌─────────────────────────────────────────────────────────────────┐
│  PLANE 1 — SheersSoft Internal                                  │
│                                                                 │
│  System Admin (superadmin)                                      │
│  • Full platform access                                         │
│  • Provisions/suspends tenants                                  │
│  • Manages billing, system config, support tickets             │
│  • Portal: /admin (internal-only URL, ideally different domain) │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  PLANE 2 — Tenant Level                                         │
│                                                                 │
│  Tenant Owner (role=owner)                                      │
│  • Manages multiple properties under one billing entity         │
│  • Can invite/remove users                                      │
│  • Sees aggregate analytics across properties                   │
│  • Can update billing info (Stripe)                            │
│                                                                 │
│  Tenant Admin (role=admin)                                      │
│  • Delegated by owner (e.g., Regional Manager)                  │
│  • Can manage properties but not billing                        │
│  • Can invite staff, manage KB, configure channels             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  PLANE 3 — Property Level (scoped to accessible_property_ids)   │
│                                                                 │
│  Property Manager (role=staff, tier=manager)                    │
│  • Full access to assigned property(ies)                        │
│  • Can configure AI, manage KB, see all analytics               │
│  • e.g., General Manager                                        │
│                                                                 │
│  Property Staff — Revenue (role=staff, tier=revenue)            │
│  • Analytics + lead management only                             │
│  • Cannot access conversations or KB                            │
│  • e.g., Revenue Manager, Sales                                 │
│                                                                 │
│  Property Staff — Operations (role=staff, tier=ops)             │
│  • Conversations + escalation inbox only                        │
│  • Cannot access analytics or KB                                │
│  • e.g., Front Desk, Guest Services                             │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Portal Mapping

| User Type | Portal | URL Path | Access Gate |
|-----------|--------|----------|-------------|
| SheersSoft System Admin | Internal Admin Portal | `/admin/**` | `is_superadmin=True` |
| Tenant Owner / Admin | Tenant Portal | `/portal/**` | `TenantMembership.role IN (owner, admin)` |
| Property Manager | Property Dashboard | `/dashboard/**` | `TenantMembership` + `accessible_property_ids` |
| Revenue / Ops Staff | Property Dashboard (scoped) | `/dashboard/**` | `TenantMembership.role=staff` + `staff_tier` |

---

## 4. Correct Process Flow

### 4.1 First Login — Identity Resolution

```
User clicks magic link
    ↓
/auth/callback — Supabase PKCE exchange → backend JWT issued
    ↓
GET /auth/me → returns user + memberships
    ↓
┌──────────────────────────────────────────────────────────┐
│  Resolution logic (in order):                            │
│                                                          │
│  1. is_superadmin=True                                   │
│     → redirect /admin (SheersSoft internal portal)       │
│                                                          │
│  2. has TenantMembership with role=owner or role=admin   │
│     → redirect /portal (tenant management)               │
│                                                          │
│  3. has TenantMembership with role=staff                 │
│     → redirect /dashboard (property operations)          │
│                                                          │
│  4. no membership (newly invited, not yet onboarded)     │
│     → redirect /welcome (onboarding wizard)              │
│                                                          │
│  5. no user record (no invitation)                       │
│     → show error: "No account found. Request access."    │
└──────────────────────────────────────────────────────────┘
```

### 4.2 New Tenant Onboarding Flow (SheersSoft-triggered)

```
SheersSoft Admin → /admin/onboarding → fills form
    ↓
POST /onboarding/provision-tenant
    → Creates Tenant + Property + User (owner) + TenantMembership
    → Creates Supabase auth user (email_confirm=true)
    → Sends magic link with redirect_to=/auth/callback
    ↓
Owner receives email → clicks link
    ↓
/auth/callback → JWT issued → /auth/me resolves role=owner
    ↓
/welcome (onboarding wizard):
    Step 1: Confirm property details
    Step 2: Upload Knowledge Base (guided)
    Step 3: Test WhatsApp / Email channel
    Step 4: Invite staff members
    Step 5: Go live checklist
    ↓
/portal (tenant home)
```

### 4.3 Staff Invitation Flow (Tenant-triggered)

```
Tenant Owner/Admin → /portal/users → invite staff
    ↓
POST /onboarding/invite-user
    → Creates User + TenantMembership (role=staff, staff_tier=ops|revenue|manager)
    → Sets accessible_property_ids if scoped
    → Sends magic link
    ↓
Staff receives email → clicks link
    ↓
/auth/callback → JWT → /auth/me resolves role=staff + staff_tier
    ↓
/dashboard (scoped to their properties and tier)
```

---

## 5. Required Code Changes (Priority Ordered)

### P0 — Security Fixes (Before First Real Client)

1. **Remove `SUPERADMIN_EMAILS` from `cloudbuild.yaml`** — move to GCP Secret Manager as `SUPERADMIN_EMAILS` secret; never committed to repo
2. **Remove legacy `admin/password123`** — replace with a proper SheersSoft staff user record created once via a secure seed script; delete the `/auth/token` hardcoded-credentials endpoint or restrict to development only
3. **Gate auto-provisioning** — remove auto-creation of User records for unknown emails; only allow users who were explicitly invited (i.e., their email exists in `users` table pre-created by provisioning) OR whose email is in a server-side SUPERADMIN_EMAILS secret
4. **Add `staff_tier` to `TenantMembership`** — extend role model to `staff_tier: "manager" | "revenue" | "ops" | null`
5. **Enforce `accessible_property_ids`** — audit every dashboard endpoint to ensure property access checks respect this field

### P1 — Portal Separation

6. **Create `/portal` route group** — tenant-level management (users, billing, multi-property overview); separate from `/dashboard` (single-property operations)
7. **Add `/welcome` onboarding wizard** — replaces the raw redirect to `/admin` or `/dashboard` for first-time users
8. **Add `staff_tier` routing** — after identity resolution, scope the dashboard navigation items based on `staff_tier`

### P2 — Auth Hardening

9. **Shorter JWT TTL + refresh token** — reduce from 24h to 2h; issue refresh tokens; revoke on logout
10. **Logout also revokes Supabase session** — call `supabase.auth.signOut()` on logout to invalidate the Supabase session, not just clear localStorage
11. **Audit log table** — create `audit_logs` table; log all superadmin mutations (tenant create/delete, user role changes)
12. **Internal endpoint IP allowlist** — restrict `/api/v1/internal/*` to Cloud Scheduler's IP range in addition to the shared secret

---

## 6. Immediate Safe State (What To Do Now)

Until P0 changes are made, the following manual controls apply:

1. **SUPERADMIN_EMAILS** is set as a Cloud Run env var (not in git) — only accessible to people with GCP Console access to the `nocturn-aai` project
2. **Legacy admin** (`admin/password123`) is only accessible via the "SheersSoft Admin Login →" link on the login page — tenant users are never shown this path
3. **No real tenant clients are provisioned yet** — all current data is internal/test only; the security risk exposure is currently zero
4. First real client (Vivatel/Zul) should be provisioned **after** P0 items 1–3 are completed

---

## 7. Data Model Changes Required

```sql
-- Add staff_tier to tenant_memberships
ALTER TABLE tenant_memberships
  ADD COLUMN IF NOT EXISTS staff_tier VARCHAR(20);
  -- NULL = owner/admin (no tier), 'manager' | 'revenue' | 'ops' for staff

-- Add onboarding_completed flag to users
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE;

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_id UUID REFERENCES users(id),
  actor_email VARCHAR(255),
  action VARCHAR(100) NOT NULL,        -- 'tenant.create', 'user.role_change', etc.
  target_type VARCHAR(50),             -- 'tenant', 'user', 'property'
  target_id UUID,
  payload JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```
