import time
import uuid
import structlog
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


# Paths exempt from maintenance mode — internal ops and admin must always be accessible
_MAINTENANCE_EXEMPT_PREFIXES = (
    "/api/v1/superadmin",
    "/api/v1/internal",
    "/api/v1/system/info",
    "/api/v1/health",
    "/auth/",
    "/health",
    "/",
)

# Simple in-process cache so we don't hit the DB on every request
_maintenance_cache: dict = {"value": None, "expires_at": 0.0}


class MaintenanceModeMiddleware(BaseHTTPMiddleware):
    """
    When maintenance mode is enabled in system_config, return HTTP 503 to all
    non-exempt routes. The /admin portal and /internal scheduler endpoints are
    always reachable so SheersSoft staff can operate the platform during maintenance.
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Check exemptions first (no DB hit needed)
        for prefix in _MAINTENANCE_EXEMPT_PREFIXES:
            if path.startswith(prefix):
                return await call_next(request)

        # Check cache (refresh every 30 seconds)
        import time as _time
        now = _time.monotonic()
        if _maintenance_cache["value"] is None or now > _maintenance_cache["expires_at"]:
            try:
                from app.database import async_session
                from app.services.system_config import get_maintenance_config
                async with async_session() as db:
                    _maintenance_cache["value"] = await get_maintenance_config(db)
                    _maintenance_cache["expires_at"] = now + 30
            except Exception as e:
                logger.warning("Failed to check maintenance config", error=str(e))
                # On error, allow traffic through rather than false-blocking
                return await call_next(request)

        cfg = _maintenance_cache["value"]
        if cfg and cfg.get("enabled"):
            return JSONResponse(
                {
                    "maintenance": True,
                    "message": cfg.get("message") or "Scheduled maintenance in progress. We'll be back shortly.",
                    "eta": cfg.get("eta"),
                },
                status_code=503,
            )

        return await call_next(request)


class TelemetryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Bind context for structlog
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log successful request
            logger.info(
                "request_finished",
                status_code=response.status_code,
                process_time=process_time,
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                "request_failed",
                error=str(e),
                process_time=process_time,
            )
            raise e
