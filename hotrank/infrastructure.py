import logging
from contextlib import asynccontextmanager

import asyncpg
from pgvector.asyncpg import register_vector
from slowapi import Limiter
from slowapi.util import get_remote_address

from config import (
    PG_DB,
    PG_HOST,
    PG_PASSWORD,
    PG_PORT,
    PG_USER,
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
)
from hotrank.cache import redis_cache


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["30 per minute"],
    storage_uri=f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}",
)

async def init_pg_connection(conn):
    """Register pgvector codecs after the vector extension is enabled."""
    await register_vector(conn)


async def init_pg_pool():
    return await asyncpg.create_pool(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        database=PG_DB,
        init=init_pg_connection,
    )


@asynccontextmanager
async def lifespan(app):
    logging.info("Application is starting up...")
    app.state.pg_pool = await init_pg_pool()
    await redis_cache.delete("today_top_news_task")
    try:
        yield
    finally:
        logging.info("Application is shutting down...")
        await app.state.pg_pool.close()
