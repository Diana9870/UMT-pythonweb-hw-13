import redis
import json
from app.config import settings

r = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True
)


def set_user_cache(email: str, data: dict):
    r.setex(email, 300, json.dumps(data))


def get_user_cache(email: str):
    user = r.get(email)
    if user:
        return json.loads(user)
    return None