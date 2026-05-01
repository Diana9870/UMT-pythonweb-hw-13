import redis
import os
import json
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379, decode_responses=True)


def get_cache(key: str):
    """Get data from cache"""
    data = r.get(key)
    return json.loads(data) if data else None


def set_cache(key: str, value: dict):
    """Set cache"""
    r.set(key, json.dumps(value), ex=300)