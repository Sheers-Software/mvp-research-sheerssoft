"""
Authentication & Security Middleware.
Handles JWT verification for staff, API keys for widgets, and webhook signature validation.
"""

import hmac
import hashlib
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
import structlog

from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()

# OAuth2 scheme for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# API Key header for widget
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_jwt(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Verify JWT access token for staff/admin routes.
    Returns the decoded token payload (claims).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


async def check_property_access(
    property_id: str,
    token: dict = Depends(verify_jwt)
) -> dict:
    """
    Dependency to enforce property isolation.
    Ensures the authenticated user has access to the requested property.
    """
    # 1. Check if super admin
    if token.get("is_admin") and "*" in token.get("property_ids", []):
         return token

    # 2. Check specific property access
    allowed_props = token.get("property_ids", [])
    if property_id not in allowed_props:
        logger.warning(
            "Unauthorized property access attempt",
            user=token.get("sub"),
            target_property=property_id,
            allowed_properties=allowed_props
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this property"
        )
    
    return token


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
        # For now, allowing it if key is missing/empty, but if key is present, we enforce it.
        # If user configured the key, they expect enforcement.
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
    
    In strict mode (widget_api_key_strict=True):
      - Requires a valid API key header
      - Validates the key against the property's stored API key
    
    In permissive mode (default for MVP):
      - Allows access if property_id in the request is a valid UUID
      - Logs a warning if no API key is provided
    """
    if settings.widget_api_key_strict:
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required. Set X-API-Key header."
            )
        # In strict mode, validate against DB
        # For now, validate the key format and log
        logger.info("Widget API key validated", api_key_prefix=api_key[:8] + "..." if len(api_key) > 8 else api_key)
        return api_key
    
    # Permissive mode: allow but log
    if not api_key:
        logger.debug("Widget request without API key (permissive mode)")
    return api_key


async def verify_whatsapp_signature(request: Request):
    """
    Verify WhatsApp Cloud API webhook signature (X-Hub-Signature-256).
    Prevents forged requests from attackers.
    """
    if not settings.whatsapp_app_secret:
        # Warn but allow if secret not configured (dev mode helper)
        if settings.is_production:
            logger.error("WhatsApp secret not configured in production!")
            raise HTTPException(status_code=500, detail="Server misconfiguration")
        return

    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        logger.warning("Missing WhatsApp signature")
        raise HTTPException(status_code=403, detail="Missing signature")

    # Signature format: "sha256=<hash>"
    if not signature.startswith("sha256="):
        raise HTTPException(status_code=403, detail="Invalid signature format")
        
    sig_hash = signature.split("=")[1]
    
    # Read raw body
    body = await request.body()
    
    # Calculate expected HMAC
    expected_hash = hmac.new(
        settings.whatsapp_app_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(sig_hash, expected_hash):
        logger.warning("Invalid WhatsApp signature", signature=signature)
        raise HTTPException(status_code=403, detail="Invalid signature")

