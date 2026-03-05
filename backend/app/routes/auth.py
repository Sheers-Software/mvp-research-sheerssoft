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
from app.models import User, TenantMembership
from app.schemas import (
    MagicLinkRequest, UserProfileResponse, TenantMembershipResponse,
    TokenResponse,
)

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
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.supabase_url}/auth/v1/magiclink",
                headers={
                    "apikey": settings.supabase_anon_key,
                    "Content-Type": "application/json",
                },
                json={
                    "email": body.email,
                    "options": {
                        "emailRedirectTo": settings.allowed_origins.split(",")[0]
                    }
                },
                timeout=10.0,
            )
            if response.status_code >= 400:
                logger.warning("Magic link request failed", status=response.status_code, body=response.text)
                raise HTTPException(
                    status_code=400,
                    detail="Could not send magic link. Please check your email address."
                )

        logger.info("Magic link sent", email=body.email)
        return {"message": "Magic link sent. Check your email inbox.", "email": body.email}

    except httpx.RequestError as e:
        logger.error("Supabase Auth request failed", error=str(e))
        raise HTTPException(status_code=503, detail="Authentication service unavailable")


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

    return UserProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        is_superadmin=user.is_superadmin,
        last_login_at=user.last_login_at,
        memberships=memberships,
    )
