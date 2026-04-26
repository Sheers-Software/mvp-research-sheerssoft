"""
Authentication routes — Magic link login, token management, user profile.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
import structlog
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.config import get_settings
from app.auth import get_current_user
from app.models import User, TenantMembership, OnboardingProgress
from app.schemas import (
    MagicLinkRequest, UserProfileResponse, TenantMembershipResponse,
    TokenResponse,
)
from pydantic import BaseModel

class SupabaseCallbackRequest(BaseModel):
    access_token: str

logger = structlog.get_logger()
router = APIRouter()


@router.post("/auth/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Legacy login endpoint for backward compatibility.
    MVP: Hardcoded admin check. Will be deprecated once Supabase Auth is fully active.
    """
    settings = get_settings()
    user_ok = False

    # Check: Master Admin (legacy)
    if form_data.username == settings.admin_user and form_data.password == settings.admin_password:
        user_ok = True

    if not user_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT
    access_token_expires = timedelta(hours=settings.jwt_expiry_hours)
    expire = datetime.now(timezone.utc) + access_token_expires

    to_encode = {
        "sub": form_data.username,
        "exp": expire,
        "is_admin": True,
        "property_ids": ["*"]
    }
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    return {"access_token": encoded_jwt, "token_type": "bearer"}


@router.post("/auth/magic-link")
async def request_magic_link(body: MagicLinkRequest):
    """
    Request a magic link login email.
    Uses Supabase Admin API to generate the link (bypasses Supabase SMTP quota),
    then delivers the email via SendGrid.
    """
    settings = get_settings()

    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(
            status_code=503,
            detail="Supabase Auth not configured. Contact support."
        )

    redirect_to = f"{settings.frontend_url.rstrip('/')}/auth/callback"

    # Step 1: generate the magic link URL via Supabase Admin API (no SMTP involved)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.supabase_url}/auth/v1/admin/generate_link",
                headers={
                    "apikey": settings.supabase_service_role_key,
                    "Authorization": f"Bearer {settings.supabase_service_role_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "type": "magiclink",
                    "email": body.email,
                    "options": {"redirect_to": redirect_to},
                },
                timeout=10.0,
            )
    except httpx.RequestError as e:
        logger.error("Supabase generate_link request failed", error=str(e))
        raise HTTPException(status_code=503, detail="Authentication service unavailable")

    if response.status_code >= 400:
        err = {}
        try:
            err = response.json()
        except Exception:
            pass
        logger.warning("Supabase generate_link failed", status=response.status_code, body=response.text, email=body.email)
        detail = err.get("msg") or err.get("message") or "Could not generate login link."
        raise HTTPException(status_code=400, detail=detail)

    action_link = response.json().get("action_link")
    if not action_link:
        logger.error("Supabase generate_link returned no action_link", email=body.email)
        raise HTTPException(status_code=500, detail="Failed to generate login link")

    # Step 2: deliver via SendGrid (uses our own quota, not Supabase's)
    from app.services.email import send_email
    email_result = await send_email(
        to_email=body.email,
        subject="Your Nocturn AI sign-in link",
        content=_magic_link_email_html(action_link),
        is_html=True,
        hotel_name="Nocturn AI",
    )

    if email_result.get("status") == "error":
        logger.error("Magic link email delivery failed", email=body.email, error=email_result.get("detail"))
        raise HTTPException(status_code=503, detail="Could not deliver sign-in email. Please try again.")

    logger.info("Magic link delivered via SendGrid", email=body.email, redirect_to=redirect_to)
    return {"message": "Magic link sent. Check your email inbox.", "email": body.email}


def _magic_link_email_html(action_link: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1e293b;margin:0;padding:20px;background:#f8fafc;}}
    .wrap{{max-width:480px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.1);}}
    .hdr{{background:#0f172a;padding:24px 32px;}}
    .hdr h1{{color:#fff;margin:0;font-size:20px;font-weight:700;letter-spacing:-.3px;}}
    .hdr p{{color:#94a3b8;margin:4px 0 0;font-size:13px;}}
    .bdy{{padding:32px;}}
    .bdy p{{color:#475569;margin:0 0 16px;font-size:15px;line-height:1.6;}}
    .btn{{display:block;background:#0f172a;color:#fff!important;text-decoration:none;padding:14px 24px;border-radius:8px;text-align:center;font-weight:600;font-size:15px;margin:24px 0;}}
    .note{{font-size:12px;color:#94a3b8;margin-top:8px;}}
    .ftr{{background:#f8fafc;padding:16px 32px;font-size:12px;color:#94a3b8;border-top:1px solid #e2e8f0;}}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hdr"><h1>Nocturn AI</h1><p>Hotel Concierge Intelligence · SheersSoft</p></div>
    <div class="bdy">
      <p>Click the button below to sign in to your Nocturn AI account. No password needed.</p>
      <a href="{action_link}" class="btn">Sign in to Nocturn AI →</a>
      <p class="note">This link expires in 24 hours and can only be used once.</p>
      <p style="font-size:13px;color:#94a3b8;">Didn't request this? You can safely ignore this email.</p>
    </div>
    <div class="ftr">SheersSoft Sdn Bhd · <a href="https://ai.sheerssoft.com" style="color:#94a3b8">ai.sheerssoft.com</a></div>
  </div>
</body>
</html>"""


@router.post("/auth/supabase-callback")
async def supabase_token_exchange(
    body: SupabaseCallbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Exchange a Supabase access token for a backend JWT.
    Called by the frontend /auth/callback page after a magic link redirect.
    """
    settings = get_settings()

    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    # Verify the Supabase token and retrieve the user profile
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.supabase_url}/auth/v1/user",
                headers={
                    "apikey": settings.supabase_service_role_key,
                    "Authorization": f"Bearer {body.access_token}",
                },
                timeout=10.0,
            )
    except httpx.RequestError as e:
        logger.error("Supabase user lookup failed", error=str(e))
        raise HTTPException(status_code=503, detail="Authentication service unavailable")

    if resp.status_code != 200:
        logger.warning("Supabase token rejected", status=resp.status_code)
        raise HTTPException(status_code=401, detail="Invalid or expired magic link token")

    supabase_user = resp.json()
    supabase_id = supabase_user.get("id")
    email = supabase_user.get("email")

    # Look up user in our DB by Supabase UUID first, then by email
    result = await db.execute(
        select(User)
        .options(selectinload(User.memberships))
        .where(User.id == supabase_id)
    )
    user = result.scalar_one_or_none()

    if not user and email:
        result = await db.execute(
            select(User)
            .options(selectinload(User.memberships))
            .where(User.email == email)
        )
        user = result.scalar_one_or_none()

    # Determine if this email should be superadmin — explicit list only, no domain wildcards
    superadmin_list = [e.strip().lower() for e in settings.superadmin_emails.split(",") if e.strip()]
    is_super = (email.lower() in superadmin_list) if email else False

    if not user:
        # Auto-provision: create a local User record for first-time magic link logins.
        display_name = (supabase_user.get("user_metadata") or {}).get("full_name") or (email.split("@")[0] if email else "User")
        user = User(
            id=supabase_id,
            email=email,
            full_name=display_name,
            is_superadmin=is_super,
        )
        db.add(user)
        await db.flush()
        # Reload with memberships relationship
        result = await db.execute(
            select(User)
            .options(selectinload(User.memberships))
            .where(User.id == supabase_id)
        )
        user = result.scalar_one()
        logger.info("Auto-provisioned user from magic link", email=email, is_superadmin=is_super)
    elif user.is_superadmin != is_super:
        # Sync superadmin flag — upgrade OR downgrade based on current SUPERADMIN_EMAILS list
        user.is_superadmin = is_super
        logger.info("Synced superadmin flag", email=email, is_superadmin=is_super)

    # Issue our own backend JWT
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiry_hours)
    property_ids: list = []
    for m in user.memberships:
        if m.accessible_property_ids:
            property_ids.extend([str(p) for p in m.accessible_property_ids])
    to_encode = {
        "sub": str(user.id),
        "exp": expire,
        "is_admin": user.is_superadmin,
        "property_ids": ["*"] if user.is_superadmin else property_ids,
    }
    token = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    logger.info("Supabase magic link exchange succeeded", email=email)
    return {"access_token": token, "token_type": "bearer"}


def _compute_onboarding_score(progress: OnboardingProgress) -> int:
    """Compute onboarding completion score (0-100) from OnboardingProgress record."""
    score = 10  # account_created always true
    # channels_connected: at least one channel active, OR all channels active/skipped
    channel_statuses = [progress.whatsapp_status, progress.email_status, progress.website_status]
    has_active_channel = any(s == "active" for s in channel_statuses)
    all_resolved = all(s in ("active", "skipped") for s in channel_statuses)
    if has_active_channel or all_resolved:
        score += 20
    if progress.kb_populated:
        score += 20
    if progress.first_inquiry_received:
        score += 15
    if progress.first_morning_report_sent:
        score += 15
    if progress.first_lead_captured:
        score += 10
    if progress.owner_first_login:
        score += 10
    return score


@router.get("/auth/me", response_model=UserProfileResponse)
async def get_my_profile(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's profile including tenant memberships and accessible properties.
    """
    # Legacy admin support
    if isinstance(user, dict) and user.get("_legacy"):
        return UserProfileResponse(
            id="00000000-0000-0000-0000-000000000000",
            email="admin@sheerssoft.com",
            full_name="SheersSoft Admin (Legacy)",
            phone=None,
            is_superadmin=True,
            last_login_at=None,
            memberships=[],
        )

    # Build membership list with tenant names
    memberships = []
    for m in user.memberships:
        memberships.append(TenantMembershipResponse(
            id=m.id,
            tenant_id=m.tenant_id,
            tenant_name=m.tenant.name if m.tenant else None,
            role=m.role,
            accessible_property_ids=m.accessible_property_ids,
        ))

    # Derive primary membership role, tenant_id, and onboarding_completed
    primary_role: str | None = None
    primary_tenant_id = None
    onboarding_completed = False

    if user.memberships:
        # Primary membership: first one ordered by created_at
        sorted_memberships = sorted(user.memberships, key=lambda m: m.created_at)
        primary = sorted_memberships[0]
        primary_role = primary.role
        primary_tenant_id = primary.tenant_id

        # Load OnboardingProgress for this tenant
        progress_result = await db.execute(
            select(OnboardingProgress)
            .where(OnboardingProgress.tenant_id == primary.tenant_id)
            .order_by(OnboardingProgress.created_at)
        )
        progress = progress_result.scalar_one_or_none()
        if progress:
            score = _compute_onboarding_score(progress)
            onboarding_completed = score >= 60
            logger.info("Onboarding score", email=user.email, score=score, completed=onboarding_completed)

    return UserProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        is_superadmin=user.is_superadmin,
        last_login_at=user.last_login_at,
        memberships=memberships,
        role=primary_role,
        tenant_id=primary_tenant_id,
        onboarding_completed=onboarding_completed,
    )
