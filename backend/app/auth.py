"""
Authentication & Security Middleware.
Handles Supabase JWT verification, tenant RBAC, API keys for widgets, and webhook signatures.
"""

import hmac
import hashlib
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import structlog

from app.config import get_settings
from app.database import get_db

settings = get_settings()
logger = structlog.get_logger()

# OAuth2 scheme for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)

# API Key header for widget
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# ─────────────────────────────────────────────────────────────
# JWT Verification (Supabase-issued tokens)
# ─────────────────────────────────────────────────────────────

async def verify_jwt(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Verify JWT access token.
    Supports both Supabase-issued JWTs and legacy admin JWTs.
    Returns the decoded token payload (claims).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"verify_aud": False}  # Supabase tokens use 'authenticated' audience
        )
        # Supabase uses 'sub' for user UUID
        sub: str = payload.get("sub")
        if sub is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


# ─────────────────────────────────────────────────────────────
# User Resolution (JWT → User model)
# ─────────────────────────────────────────────────────────────

async def get_current_user(
    token: dict = Depends(verify_jwt),
    db: AsyncSession = Depends(get_db),
):
    """
    Resolve the JWT's 'sub' claim into a User model instance.
    Eagerly loads tenant memberships for RBAC checks.
    Falls back to legacy admin mode if no User record exists (migration period).
    """
    from app.models import User

    user_id = token.get("sub")

    # Legacy admin support: if 'sub' is a username (not UUID), treat as superadmin
    try:
        import uuid as uuid_mod
        uuid_mod.UUID(user_id)
    except (ValueError, AttributeError):
        # Legacy admin token (sub="admin")
        if token.get("is_admin") and "*" in token.get("property_ids", []):
            return {
                "_legacy": True,
                "sub": user_id,
                "is_admin": True,
                "is_superadmin": True,
                "property_ids": ["*"],
                "tenant_id": None,
            }
        raise HTTPException(status_code=401, detail="Invalid token format")

    from app.models import TenantMembership
    stmt = (
        select(User)
        .options(selectinload(User.memberships).selectinload(TenantMembership.tenant))
        .where(User.id == user_id)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found. Contact support.",
        )

    # Update last login timestamp — wrapped in try/except to avoid crashing on DB permission issues
    try:
        from datetime import datetime, timezone
        user.last_login_at = datetime.now(timezone.utc)
        await db.commit()
    except Exception as e:
        logger.warning("Could not update last login timestamp", error=str(e))
        await db.rollback() # Ensure transaction is cleared

    return user


# ─────────────────────────────────────────────────────────────
# Tenant & Property Access Control
# ─────────────────────────────────────────────────────────────

async def check_tenant_access(
    tenant_id: str,
    user=Depends(get_current_user),
):
    """
    Verify the authenticated user has access to the specified tenant.
    SuperAdmins can access any tenant.
    """
    # Legacy admin bypass
    if isinstance(user, dict) and user.get("_legacy"):
        return user

    if user.is_superadmin:
        return user

    # Check memberships
    for membership in user.memberships:
        if str(membership.tenant_id) == str(tenant_id):
            return user

    logger.warning(
        "Unauthorized tenant access attempt",
        user_id=str(user.id),
        target_tenant=tenant_id,
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have access to this organization"
    )


async def check_property_access(
    property_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict | object:
    """
    Verify the authenticated user has access to the specified property.
    Checks via the Tenant → Property → TenantMembership chain.
    """
    # Legacy admin bypass
    if isinstance(user, dict) and user.get("_legacy"):
        return user

    if user.is_superadmin:
        return user

    # Resolve property's tenant
    from app.models import Property
    stmt = select(Property.tenant_id).where(Property.id == property_id)
    result = await db.execute(stmt)
    prop_tenant_id = result.scalar_one_or_none()

    if not prop_tenant_id:
        raise HTTPException(status_code=404, detail="Property not found")

    # Check user has membership for this tenant
    for membership in user.memberships:
        if str(membership.tenant_id) == str(prop_tenant_id):
            # Check property-level scope
            if membership.accessible_property_ids is None:
                return user  # null = all properties
            if str(property_id) in [str(pid) for pid in membership.accessible_property_ids]:
                return user

    logger.warning(
        "Unauthorized property access attempt",
        user_id=str(user.id),
        target_property=property_id,
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have access to this property"
    )


async def require_superadmin(user=Depends(get_current_user)):
    """
    Gate routes to SheersSoft internal staff only.
    """
    # Legacy admin bypass
    if isinstance(user, dict) and user.get("_legacy"):
        return user

    if not user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SuperAdmin access required"
        )
    return user


# ─────────────────────────────────────────────────────────────
# Webhook Signature Verification (unchanged from original)
# ─────────────────────────────────────────────────────────────

async def verify_sendgrid_signature(request: Request):
    """
    Verify SendGrid Signed Webhook.
    Requires Ed25519 verification.
    """
    if not settings.sendgrid_webhook_public_key:
        if settings.is_production:
             logger.warning("SendGrid webhook signature verification disabled in production")
        return

    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    import base64

    signature = request.headers.get("X-Twilio-Email-Event-Webhook-Signature")
    timestamp = request.headers.get("X-Twilio-Email-Event-Webhook-Timestamp")

    if not signature or not timestamp:
        logger.warning("Missing SendGrid signature headers")
        raise HTTPException(status_code=403, detail="Missing signature")

    # Construct payload: timestamp + raw body
    body = await request.body()
    payload = timestamp.encode() + body

    try:
        public_key_bytes = base64.b64decode(settings.sendgrid_webhook_public_key)
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        decoded_signature = base64.b64decode(signature)
        
        public_key.verify(decoded_signature, payload)
    except Exception as e:
        logger.warning("Invalid SendGrid signature", error=str(e))
        raise HTTPException(status_code=403, detail="Invalid signature")


async def verify_api_key(
    request: Request,
    api_key: Optional[str] = Depends(api_key_header)
) -> Optional[str]:
    """
    Verify API Key for widget access.
    """
    if settings.widget_api_key_strict:
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required. Set X-API-Key header."
            )
        logger.info("Widget API key validated", api_key_prefix=api_key[:8] + "..." if len(api_key) > 8 else api_key)
        return api_key
    
    # Permissive mode: allow but log
    if not api_key:
        logger.debug("Widget request without API key (permissive mode)")
    return api_key


async def verify_whatsapp_signature(request: Request):
    """
    Verify WhatsApp Cloud API webhook signature (X-Hub-Signature-256).
    """
    if not settings.whatsapp_app_secret:
        if settings.is_production:
            logger.error("WhatsApp secret not configured in production!")
            raise HTTPException(status_code=500, detail="Server misconfiguration")
        return

    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        logger.warning("Missing WhatsApp signature")
        raise HTTPException(status_code=403, detail="Missing signature")

    if not signature.startswith("sha256="):
        raise HTTPException(status_code=403, detail="Invalid signature format")
        
    sig_hash = signature.split("=")[1]
    body = await request.body()
    
    expected_hash = hmac.new(
        settings.whatsapp_app_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(sig_hash, expected_hash):
        logger.warning("Invalid WhatsApp signature", signature=signature)
        raise HTTPException(status_code=403, detail="Invalid signature")


async def verify_twilio_signature(request: Request):
    """
    Verify Twilio webhook signature using the Twilio Python SDK RequestValidator.
    """
    if not settings.twilio_auth_token:
        if settings.is_production:
            logger.error("Twilio auth token not configured in production!")
            raise HTTPException(status_code=500, detail="Server misconfiguration")
        return

    if settings.is_demo:
        logger.info("Demo mode: skipping Twilio signature verification")
        return

    from twilio.request_validator import RequestValidator
    validator = RequestValidator(settings.twilio_auth_token)

    signature = request.headers.get("X-Twilio-Signature")
    if not signature:
        logger.warning("Missing Twilio signature")
        raise HTTPException(status_code=403, detail="Missing signature")

    forwarded_host = request.headers.get("X-Forwarded-Host")
    forwarded_proto = request.headers.get("X-Forwarded-Proto", "https")
    
    if forwarded_host:
        base_url = f"{forwarded_proto}://{forwarded_host}"
        path = request.url.path
        url_str = f"{base_url}{path}"
    else:
        url_str = str(request.url)
        if forwarded_proto and url_str.startswith("http://") and forwarded_proto == "https":
            url_str = url_str.replace("http://", "https://", 1)

    form_data = await request.form()
    post_vars = dict(form_data)

    if not validator.validate(url_str, post_vars, signature):
        logger.warning("Invalid Twilio signature", signature=signature, url=url_str)
        raise HTTPException(status_code=403, detail="Invalid signature")
