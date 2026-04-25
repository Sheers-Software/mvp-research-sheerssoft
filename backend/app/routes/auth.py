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
    Request a magic link login email via Supabase Auth.
    The email contains a one-click login URL.
    """
    settings = get_settings()

    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(
            status_code=503,
            detail="Supabase Auth not configured. Contact support."
        )

    try:
        redirect_to = f"{settings.frontend_url.rstrip('/')}/auth/callback"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.supabase_url}/auth/v1/magiclink",
                headers={
                    "apikey": settings.supabase_anon_key,
                    "Content-Type": "application/json",
                },
                params={"redirect_to": redirect_to},
                json={"email": body.email},
                timeout=10.0,
            )
            logger.info("Magic link sent", email=body.email, redirect_to=redirect_to)
            if response.status_code >= 400:
                logger.warning("Magic link request failed", status=response.status_code, body=response.text)
                raise HTTPException(
                    status_code=400,
                    detail="Could not send magic link. Please check your email address."
                )

        return {"message": "Magic link sent. Check your email inbox.", "email": body.email}

    except httpx.RequestError as e:
        logger.error("Supabase Auth request failed", error=str(e))
        raise HTTPException(status_code=503, detail="Authentication service unavailable")


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
