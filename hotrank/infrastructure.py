import logging
from contextlib import asynccontextmanager

import asyncpg
import redis.asyncio as redis
from redis.asyncio import ConnectionPool
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from slowapi import Limiter
from slowapi.util import get_remote_address

from config import (
    PG_DB,
    PG_HOST,
    PG_PASSWORD,
    PG_PORT,
    PG_USER,
    REDIS_DB,
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
)


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["30 per minute"],
    storage_uri=f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}",
)

backoff = ExponentialBackoff(cap=2, base=2)
retry = Retry(backoff=backoff, retries=10)
redis_pool = ConnectionPool(
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
redis_client = redis.Redis(connection_pool=redis_pool)


async def init_pg_pool():
    return await asyncpg.create_pool(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        database=PG_DB,
    )


@asynccontextmanager
async def lifespan(app):
    logging.info("Application is starting up...")
    app.state.pg_pool = await init_pg_pool()
    await redis_client.delete("today_top_news_task")
    try:
        yield
    finally:
        logging.info("Application is shutting down...")
        await app.state.pg_pool.close()
