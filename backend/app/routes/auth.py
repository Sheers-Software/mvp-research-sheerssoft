"""
Authentication routes — Login, token management.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import get_settings

logger = structlog.get_logger()
router = APIRouter()


@router.post("/auth/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint for dashboard access.
    MVP: Hardcoded admin check.
    """
    settings = get_settings()
    user_ok = False

    # Check: Master Admin
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
    expire = datetime.utcnow() + access_token_expires

    to_encode = {
        "sub": form_data.username,
        "exp": expire,
        "is_admin": True,
        "property_ids": ["*"]
    }
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    return {"access_token": encoded_jwt, "token_type": "bearer"}
