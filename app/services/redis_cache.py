import json
import logging
from typing import Any, Optional

from redis.asyncio import Redis

from app.config import settings


logger = logging.getLogger(__name__)


class RedisCache:
    """
    Service for working with Redis cache.

    Supports:
    - storing JSON serializable data
    - retrieving cached data
    - deleting cache entries
    - checking key existence
    - clearing cache
    - TTL management
    """

    def __init__(self, redis_client: Redis):
        """
        Initialize Redis cache service.

        :param redis_client: Async Redis client instance.
        """
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from Redis cache.

        :param key: Cache key.
        :return: Deserialized Python object or None.
        """
        try:
            data = await self.redis.get(key)

            if data is None:
                return None

            if isinstance(data, bytes):
                data = data.decode("utf-8")

            return json.loads(data)

        except json.JSONDecodeError:
            logger.warning(
                f"Invalid JSON in Redis for key: {key}"
            )
            return None

        except Exception as error:
            logger.error(
                f"Redis GET error for key {key}: {error}"
            )
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 300,
    ) -> bool:
        """
        Save value to Redis cache.

        :param key: Cache key.
        :param value: JSON serializable value.
        :param expire: Expiration time in seconds.
        :return: True if successful.
        """
        try:
            serialized = json.dumps(value)

            await self.redis.set(
                key,
                serialized,
                ex=expire,
            )

            return True

        except (TypeError, ValueError) as error:
            logger.error(
                f"Serialization error for key {key}: {error}"
            )
            return False

        except Exception as error:
            logger.error(
                f"Redis SET error for key {key}: {error}"
            )
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete cache entry.

        :param key: Cache key.
        :return: True if deleted.
        """
        try:
            await self.redis.delete(key)
            return True

        except Exception as error:
            logger.error(
                f"Redis DELETE error for key {key}: {error}"
            )
            return False

    async def exists(self, key: str) -> bool:
        """
        Check whether key exists.

        :param key: Cache key.
        :return: True if key exists.
        """
        try:
            result = await self.redis.exists(key)
            return result == 1

        except Exception as error:
            logger.error(
                f"Redis EXISTS error for key {key}: {error}"
            )
            return False

    async def ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL.

        :param key: Cache key.
        :return: TTL in seconds.
        """
        try:
            return await self.redis.ttl(key)

        except Exception as error:
            logger.error(
                f"Redis TTL error for key {key}: {error}"
            )
            return None

    async def clear(self) -> bool:
        """
        Clear Redis database.

        :return: True if successful.
        """
        try:
            await self.redis.flushdb()
            return True

        except Exception as error:
            logger.error(
                f"Redis CLEAR error: {error}"
            )
            return False

    async def close(self) -> None:
        """
        Close Redis connection.
        """
        try:
            await self.redis.close()

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