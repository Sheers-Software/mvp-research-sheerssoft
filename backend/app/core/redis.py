"""
Redis client with graceful in-memory fallback.

When Redis is unavailable (no REDIS_URL configured, or connection fails),
all operations silently use an in-memory dict. This lets the app run on
Cloud Run without Memorystore during the pilot phase.

Limitations of the in-memory fallback:
  - Session data is lost on instance restart
  - Pub/sub events are dropped (no cross-instance broadcast)
  - Not suitable once multiple Cloud Run instances are needed (Tier 3+)
"""

import logging
import time
from typing import Any

import redis.asyncio as redis

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# ── In-memory fallback store ───────────────────────────────────────────────────

class _InMemoryStore:
    """Minimal Redis-compatible in-memory store with TTL support."""

    def __init__(self):
        self._data: dict[str, tuple[Any, float | None]] = {}  # key → (value, expires_at)

    def _expired(self, key: str) -> bool:
        if key not in self._data:
            return True
        _, expires_at = self._data[key]
        return expires_at is not None and time.time() > expires_at

    def get(self, key: str) -> str | None:
        if self._expired(key):
            self._data.pop(key, None)
            return None
        return self._data[key][0]

    def set(self, key: str, value: str, ex: int | None = None):
        expires_at = time.time() + ex if ex else None
        self._data[key] = (value, expires_at)

    def delete(self, key: str):
        self._data.pop(key, None)


_mem_store = _InMemoryStore()


# ── Redis client ───────────────────────────────────────────────────────────────

class RedisClient:
    def __init__(self):
        self.redis_url = settings.redis_url
        self.client = None
        self._unavailable = False  # set True after first failed connect attempt

    def _is_local_placeholder(self) -> bool:
        """True when the URL is the default localhost value (no real Redis configured)."""
        return "localhost" in self.redis_url or "127.0.0.1" in self.redis_url

    async def connect(self):
        if self._unavailable or self._is_local_placeholder():
            return
        try:
            self.client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=3,
            )
            await self.client.ping()
            logger.info("Redis connected: %s", self.redis_url.split("@")[-1])
        except Exception as exc:
            logger.warning("Redis unavailable (%s) — using in-memory fallback", exc)
            self.client = None
            self._unavailable = True

    async def close(self):
        if self.client:
            await self.client.close()
            self.client = None

    async def get(self, key: str) -> str | None:
        if self.client:
            try:
                return await self.client.get(key)
            except Exception:
                pass
        return _mem_store.get(key)

    async def set(self, key: str, value: str, expire: int | None = None):
        if self.client:
            try:
                return await self.client.set(key, value, ex=expire)
            except Exception:
                pass
        _mem_store.set(key, value, ex=expire)

    async def delete(self, key: str):
        if self.client:
            try:
                return await self.client.delete(key)
            except Exception:
                pass
        _mem_store.delete(key)

    async def publish(self, channel: str, message: str):
        """Publish to Redis pub/sub. No-op if Redis unavailable."""
        if self.client:
            try:
                return await self.client.publish(channel, message)
            except Exception:
                pass
        # In-memory fallback: no cross-instance broadcast; silently drop

    async def subscribe(self, channel: str):
        """Subscribe to a Redis channel. Returns None if Redis unavailable."""
        if self.client:
            try:
                pubsub = self.client.pubsub()
                await pubsub.subscribe(channel)
                return pubsub
            except Exception:
                pass
        return None


redis_client = RedisClient()


async def get_redis() -> RedisClient:
    if not redis_client.client and not redis_client._unavailable:
        await redis_client.connect()
    return redis_client
