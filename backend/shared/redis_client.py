import redis.asyncio as redis
from typing import Optional
import os

class RedisClient:
    pool: Optional[redis.Redis] = None

redis_client = RedisClient()

async def get_redis() -> redis.Redis:
    return redis_client.pool

async def connect_to_redis():
    redis_client.pool = await redis.from_url(
        os.getenv("REDIS_URL", "redis://redis:6379"),
        encoding="utf-8",
        decode_responses=True
    )
    print("Подключение к Redis установлено")

async def close_redis_connection():
    if redis_client.pool:
        await redis_client.pool.close()
        print("Подключение к Redis закрыто")
