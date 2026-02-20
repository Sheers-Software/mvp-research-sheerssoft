"""
API route aggregator.
All route modules are registered here and combined into a single router.
"""

from fastapi import APIRouter

from app.routes.channels import router as channels_router
from app.routes.staff import router as staff_router
from app.routes.leads import router as leads_router
from app.routes.analytics import router as analytics_router
from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router
from app.routes.health import router as health_router

router = APIRouter(prefix="/api/v1")

router.include_router(channels_router, tags=["Guest Channels"])
router.include_router(staff_router, tags=["Staff"])
router.include_router(leads_router, tags=["Leads"])
router.include_router(analytics_router, tags=["Analytics"])
router.include_router(admin_router, tags=["Admin"])
router.include_router(auth_router, tags=["Auth"])
router.include_router(health_router, tags=["Health"])
