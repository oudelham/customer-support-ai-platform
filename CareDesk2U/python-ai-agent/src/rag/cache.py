import hashlib
import json
from redis.asyncio import Redis

from src.config import get_settings


class RetrievalCache:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.redis = Redis.from_url(self.settings.redis_url, decode_responses=True)

    def key(self, query: str, mode: str, top_k: int) -> str:
        digest = hashlib.sha256(f"{mode}|{top_k}|{query}".encode()).hexdigest()
        return f"rag:{digest}"

    async def get(self, query: str, mode: str, top_k: int):
        value = await self.redis.get(self.key(query, mode, top_k))
        return json.loads(value) if value else None

    async def set(self, query: str, mode: str, top_k: int, results) -> None:
        await self.redis.set(
            self.key(query, mode, top_k),
            json.dumps(results),
            ex=7 * 24 * 3600,
        )
