import pytest
import json
from unittest.mock import AsyncMock, patch

from app.services.redis_cache import RedisCache


@pytest.fixture
def mock_redis():
    """
    Мокаємо Redis клієнт (async)
    """
    redis = AsyncMock()
    return redis


@pytest.fixture
def cache(mock_redis):
    """
    Створюємо інстанс кешу з підміненим Redis
    """
    return RedisCache(redis_client=mock_redis)


@pytest.mark.asyncio
async def test_set_and_get_value(cache, mock_redis):
    key = "user:1"
    value = {"id": 1, "email": "test@test.com"}

    mock_redis.get.return_value = json.dumps(value)

    await cache.set(key, value, expire=300)
    result = await cache.get(key)

    mock_redis.set.assert_called_once()
    mock_redis.get.assert_called_once_with(key)

    assert result == value


@pytest.mark.asyncio
async def test_set_with_ttl(cache, mock_redis):
    key = "user:ttl"
    value = {"data": "test"}

    await cache.set(key, value, expire=600)

    mock_redis.set.assert_called_once()
    args, kwargs = mock_redis.set.call_args

    assert args[0] == key
    assert kwargs["ex"] == 600


@pytest.mark.asyncio
async def test_get_cache_miss(cache, mock_redis):
    mock_redis.get.return_value = None

    result = await cache.get("missing:key")

    assert result is None


@pytest.mark.asyncio
async def test_get_invalid_json(cache, mock_redis):
    mock_redis.get.return_value = "not-json"

    result = await cache.get("bad:key")

    assert result is None

@pytest.mark.asyncio
async def test_delete_key(cache, mock_redis):
    await cache.delete("user:1")

    mock_redis.delete.assert_called_once_with("user:1")

@pytest.mark.asyncio
async def test_overwrite_existing_key(cache, mock_redis):
    key = "user:1"
    value = {"id": 1}

    await cache.set(key, value)
    await cache.set(key, {"id": 2})

    assert mock_redis.set.call_count == 2


@pytest.mark.asyncio
async def test_redis_failure_on_get(cache, mock_redis):
    mock_redis.get.side_effect = Exception("Redis down")

    result = await cache.get("user:1")

    assert result is None  


@pytest.mark.asyncio
async def test_redis_failure_on_set(cache, mock_redis):
    mock_redis.set.side_effect = Exception("Redis down")

    await cache.set("key", {"a": 1})


@pytest.mark.asyncio
async def test_serialization_format(cache, mock_redis):
    key = "user:json"
    value = {"id": 1, "name": "John"}

    await cache.set(key, value)

    args, kwargs = mock_redis.set.call_args

    stored_value = args[1]
    assert isinstance(stored_value, str)

    parsed = json.loads(stored_value)
    assert parsed == value