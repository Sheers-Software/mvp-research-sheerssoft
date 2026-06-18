
import json
from datetime import timedelta
from app.core.redis import get_redis

# TTL for active sessions (e.g., 1 hour)
SESSION_TTL = 3600 

class SessionService:
    def __init__(self):
        self.redis = None

    async def _get_redis(self):
        if not self.redis:
            self.redis = await get_redis()
        return self.redis

    async def get_session(self, session_key: str) -> dict | None:
        """
        Retrieve session data from Redis.
        """
        redis = await self._get_redis()
        data = await redis.get(session_key)
        if data:
            return json.loads(data)
        return None

    async def save_session(self, session_key: str, data: dict, ttl: int = SESSION_TTL):
        """
        Save/Update session data in Redis.
        """
        redis = await self._get_redis()
        await redis.set(session_key, json.dumps(data), expire=ttl)

    async def delete_session(self, session_key: str):
        redis = await self._get_redis()
        await redis.delete(session_key)

    def generate_key(self, business_id: str, channel: str, guest_identifier: str) -> str:
        """
        Generate a standardized session key.
        Format: session:{business_id}:{channel}:{guest_identifier}
        """
        return f"session:{business_id}:{channel}:{guest_identifier}"

session_service = SessionService()
