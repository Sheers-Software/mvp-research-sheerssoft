"""
Circuit Breaker — Protects against cascading failures from external APIs.

When an external service (OpenAI, SendGrid, WhatsApp) fails repeatedly,
the circuit opens and requests fail fast instead of timing out.

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Service is down, requests fail immediately
- HALF_OPEN: Testing if service recovered
"""

import time
from enum import Enum
from collections import defaultdict

import structlog

logger = structlog.get_logger()


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Per-service circuit breaker.

    Usage:
        breaker = CircuitBreaker("openai", failure_threshold=3, recovery_timeout=60)

        if not breaker.can_execute():
            return fallback_response()

        try:
            result = await call_openai(...)
            breaker.record_success()
            return result
        except Exception:
            breaker.record_failure()
            return fallback_response()
    """

    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.success_count = 0

    def can_execute(self) -> bool:
        """Check if the circuit allows a request."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info(
                    "CIRCUIT_HALF_OPEN",
                    service=self.service_name,
                )
                return True
            return False

        # HALF_OPEN: allow one test request
        return True

    def record_success(self):
        """Record a successful request."""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            logger.info("CIRCUIT_CLOSED", service=self.service_name)
        self.success_count += 1

    def record_failure(self):
        """Record a failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("CIRCUIT_REOPENED", service=self.service_name)
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                "CIRCUIT_OPEN",
                service=self.service_name,
                failures=self.failure_count,
            )

    def get_status(self) -> dict:
        """Get circuit breaker status for monitoring."""
        return {
            "service": self.service_name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
        }


# ─── Global Circuit Breakers ────────────────────────────────

_breakers: dict[str, CircuitBreaker] = {}


def get_breaker(service_name: str, **kwargs) -> CircuitBreaker:
    """Get or create a circuit breaker for a service."""
    if service_name not in _breakers:
        _breakers[service_name] = CircuitBreaker(service_name, **kwargs)
    return _breakers[service_name]


def get_all_breaker_statuses() -> list[dict]:
    """Get status of all circuit breakers (for health/monitoring)."""
    return [b.get_status() for b in _breakers.values()]


# Pre-initialize common breakers
openai_breaker = get_breaker("openai", failure_threshold=3, recovery_timeout=30)
anthropic_breaker = get_breaker("anthropic", failure_threshold=3, recovery_timeout=30)
sendgrid_breaker = get_breaker("sendgrid", failure_threshold=5, recovery_timeout=60)
whatsapp_breaker = get_breaker("whatsapp", failure_threshold=5, recovery_timeout=60)
