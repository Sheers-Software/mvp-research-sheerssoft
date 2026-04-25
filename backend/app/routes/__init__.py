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
from app.routes.onboarding import router as onboarding_router
from app.routes.support import router as support_router
from app.routes.superadmin import router as superadmin_router
from app.routes.billing import router as billing_router
from app.routes.internal import router as internal_router
from app.routes.portal import router as portal_router
from app.routes.audit import router as audit_router
from app.routes.shadow_pilot_public import router as shadow_pilot_public_router

router = APIRouter(prefix="/api/v1")

router.include_router(channels_router, tags=["Guest Channels"])
router.include_router(staff_router, tags=["Staff"])
router.include_router(leads_router, tags=["Leads"])
router.include_router(analytics_router, tags=["Analytics"])
router.include_router(admin_router, tags=["Admin"])
router.include_router(auth_router, tags=["Auth"])
router.include_router(health_router, tags=["Health"])
router.include_router(onboarding_router, tags=["Onboarding"])
router.include_router(support_router, tags=["Support"])
router.include_router(superadmin_router, tags=["SuperAdmin"])
router.include_router(billing_router, tags=["Billing"])
router.include_router(internal_router, tags=["Internal"])
router.include_router(portal_router, tags=["Portal"])
router.include_router(audit_router, tags=["Audit"])
router.include_router(shadow_pilot_public_router, tags=["Shadow Pilot"])
