import json
import logging
from typing import Any

from redis.asyncio import Redis

from app.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis cache service.

    Provides:
    - get
    - set
    - delete
    - exists
    - ttl
    - clear
    """

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get(self, key: str) -> Any | None:
        try:
            data = await self.redis.get(key)

            if data is None:
                return None

            return json.loads(data)

        except Exception as error:
            logger.error(
                f"Redis GET error ({key}): {error}"
            )
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 300,
    ) -> bool:
        try:
            await self.redis.set(
                key,
                json.dumps(value),
                ex=expire,
            )
            return True

        except Exception as error:
            logger.error(
                f"Redis SET error ({key}): {error}"
            )
            return False

    async def delete(self, key: str) -> bool:
        try:
            await self.redis.delete(key)
            return True

        except Exception as error:
            logger.error(
                f"Redis DELETE error ({key}): {error}"
            )
            return False

    async def exists(self, key: str) -> bool:
        try:
            return bool(
                await self.redis.exists(key)
            )

        except Exception as error:
            logger.error(
                f"Redis EXISTS error ({key}): {error}"
            )
            return False

    async def ttl(self, key: str) -> int | None:
        try:
            return await self.redis.ttl(key)

        except Exception as error:
            logger.error(
                f"Redis TTL error ({key}): {error}"
            )
            return None

    async def clear(self) -> bool:
        try:
            await self.redis.flushdb()
            return True

        except Exception as error:
            logger.error(
                f"Redis CLEAR error: {error}"
            )
            return False

    async def close(self) -> None:
        try:
            await self.redis.aclose()

        except Exception as error:
            logger.error(
                f"Redis CLOSE error: {error}"
            )


redis_client = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=0,
    decode_responses=True,
)

cache = RedisCache(redis_client)
