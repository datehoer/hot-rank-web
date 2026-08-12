from typing import Any

import redis.asyncio as redis
from redis.asyncio import ConnectionPool
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff

from config import (
    REDIS_DB,
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
)


class RedisCache:
    """Thin async Redis wrapper used by application code.

    Methods intentionally delegate to redis-py without changing arguments,
    return values, key names, serialization, or expiration behavior.
    """

    def __init__(self) -> None:
        backoff = ExponentialBackoff(cap=2, base=2)
        retry = Retry(backoff=backoff, retries=10)
        self._pool = ConnectionPool(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True,
            retry=retry,
            socket_timeout=60,
            socket_connect_timeout=60,
            socket_keepalive=True,
            health_check_interval=60,
            max_connections=100,
        )
        self._client = redis.Redis(connection_pool=self._pool)

    async def get(self, *args: Any, **kwargs: Any) -> Any:
        return await self._client.get(*args, **kwargs)

    async def set(self, *args: Any, **kwargs: Any) -> Any:
        return await self._client.set(*args, **kwargs)

    async def setex(self, *args: Any, **kwargs: Any) -> Any:
        return await self._client.setex(*args, **kwargs)

    async def delete(self, *args: Any, **kwargs: Any) -> Any:
        return await self._client.delete(*args, **kwargs)

    async def ttl(self, *args: Any, **kwargs: Any) -> Any:
        return await self._client.ttl(*args, **kwargs)

    async def hget(self, *args: Any, **kwargs: Any) -> Any:
        return await self._client.hget(*args, **kwargs)

    async def hset(self, *args: Any, **kwargs: Any) -> Any:
        return await self._client.hset(*args, **kwargs)

    async def hdel(self, *args: Any, **kwargs: Any) -> Any:
        return await self._client.hdel(*args, **kwargs)

    async def srandmember(self, *args: Any, **kwargs: Any) -> Any:
        return await self._client.srandmember(*args, **kwargs)


redis_cache = RedisCache()
