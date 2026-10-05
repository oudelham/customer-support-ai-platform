import json
from redis.asyncio import Redis

from src.config import get_settings


class SessionStore:
    def __init__(self):
        settings = get_settings()
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True)
        self.ttl = settings.session_ttl_seconds

    async def get(self, session_id: str) -> dict:
        value = await self.redis.get(f"session:{session_id}")
        return json.loads(value) if value else {}

    async def save(self, session_id: str, state: dict) -> None:
        await self.redis.set(
            f"session:{session_id}",
            json.dumps(state, default=str),
            ex=self.ttl,
        )
