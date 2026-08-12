import json
from hotrank.cache import redis_cache
from hotrank.schemas import ToolResult, ToolError, ToolMeta


async def get_today_news(pg_pool, limit=10):
    cache_key = f"today_news:{limit}"
    today_news = await redis_cache.get(cache_key)
    if today_news is None:
        async with pg_pool.acquire() as conn:
            records = await conn.fetch("""
                SELECT
                    id,
                    source,
                    title,
                    url,
                    hot_value,
                    last_seen
                FROM hot_topic
                WHERE last_seen >= EXTRACT(EPOCH FROM DATE_TRUNC('day', NOW()))::bigint
                ORDER BY last_seen DESC
                LIMIT $1
            """, limit)
            today_news = [
                {
                    "id": row["id"],
                    "source": row["source"],
                    "title": row["title"],
                    "url": row["url"],
                    "hot_value": row["hot_value"],
                    "last_seen": row["last_seen"],
                }
                for row in records
            ]
            await redis_cache.set(cache_key, json.dumps(today_news, ensure_ascii=False, default=str), ex=3600)  # cache for 1 hour
    else:
        today_news = json.loads(today_news)
    return ToolResult(
        ok=True,
        message="Success",
        data=today_news,
        meta=ToolMeta(
            tool_call_id="get_today_news",
            duration_ms=0,
            cached=False
        )
    )
