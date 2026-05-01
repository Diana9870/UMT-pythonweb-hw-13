import json
import logging
from typing import Any, Optional
from redis.asyncio import Redis


logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis cache service for storing and retrieving data.

    This service provides a safe wrapper around Redis operations with:
    - JSON serialization
    - Error handling (fallback if Redis is unavailable)
    - TTL support
    """

    def __init__(self, redis_client: Redis):
        """
        Initialize Redis cache service.

        :param redis_client: Async Redis client instance
        """
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from Redis cache.

        :param key: Cache key
        :return: Deserialized Python object or None if not found / error
        """
        try:
            data = await self.redis.get(key)

            if data is None:
                return None

            if isinstance(data, bytes):
                data = data.decode("utf-8")

            return json.loads(data)

        except json.JSONDecodeError:
            logger.warning(f"[RedisCache] Invalid JSON for key={key}")
            return None

        except Exception as e:
            logger.error(f"[RedisCache] GET failed for key={key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 300,
    ) -> None:
        """
        Store a value in Redis cache.

        :param key: Cache key
        :param value: Any JSON-serializable object
        :param expire: Expiration time in seconds (default: 5 min)
        """
        try:
            serialized = json.dumps(value)

            await self.redis.set(
                key,
                serialized,
                ex=expire,
            )

        except (TypeError, ValueError) as e:
            logger.error(f"[RedisCache] Serialization error for key={key}: {e}")

        except Exception as e:
            logger.error(f"[RedisCache] SET failed for key={key}: {e}")

    async def delete(self, key: str) -> None:
        """
        Delete a key from Redis cache.

        :param key: Cache key
        """
        try:
            await self.redis.delete(key)

        except Exception as e:
            logger.error(f"[RedisCache] DELETE failed for key={key}: {e}")

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.

        :param key: Cache key
        :return: True if exists, False otherwise
        """
        try:
            result = await self.redis.exists(key)
            return result == 1

        except Exception as e:
            logger.error(f"[RedisCache] EXISTS failed for key={key}: {e}")
            return False

    async def ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL for a key.

        :param key: Cache key
        :return: TTL in seconds or None if error
        """
        try:
            ttl = await self.redis.ttl(key)
            return ttl

        except Exception as e:
            logger.error(f"[RedisCache] TTL failed for key={key}: {e}")
            return None

    async def clear(self) -> None:
        """
        Clear all cache (use carefully in production).
        """
        try:
            await self.redis.flushdb()

        except Exception as e:
            logger.error(f"[RedisCache] CLEAR failed: {e}")


redis_client = Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
)

cache = RedisCache(redis_client)