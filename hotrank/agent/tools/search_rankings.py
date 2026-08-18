import hashlib
import json
import json_repair
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from hotrank.cache import redis_cache
from hotrank.agent.source_config import get_allowed_query_sources
from hotrank.schemas import AgentMessage
from hotrank.model_client import collect_model_text, embedding_with_model
from hotrank.schemas import ToolResult, ToolError, ToolMeta


class SearchPlan(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    search_query: str = Field(min_length=1, max_length=500)
    hours: int = Field(ge=1, le=24 * 30)
    need_hot: bool


def build_rank_result_cache_key(
    content: str,
    hours: int,
    platform: list[str],
    need_hot: bool,
    top_k: int,
) -> str:
    query_digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    result_scope = json.dumps(
        {
            "hours": hours,
            "need_hot": need_hot,
            "platform": sorted(platform),
            "top_k": top_k,
        },
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    scope_digest = hashlib.sha256(
        result_scope.encode("utf-8")
    ).hexdigest()
    return f"rank:result:{query_digest}:{scope_digest}"


async def get_rank_data(pg_pool, message: AgentMessage):
    original_content = message.content
    platform = message.platform

    allowed_sources = await get_allowed_query_sources()
    invalid_sources = [
        source for source in platform if source not in allowed_sources
    ]
    if invalid_sources:
        return ToolResult(
            ok=False,
            message="Query source is not enabled",
            error=ToolError(
                code=400,
                message=(
                    "Query source is not enabled: "
                    + ", ".join(invalid_sources)
                ),
                retryable=False
            ),
            meta=ToolMeta(
                tool_call_id="get_rank_data",
                duration_ms=0,
                cached=False
            )
        )
    prompt = f"""
            你是热点数据库的检索参数规划器，不是百科问答助手。

            任务：从用户原始问题中提取检索词和过滤条件，用于检索近期热点标题。

            规则：
            1. 必须保留用户输入中的核心实体词，不得替换、补充或猜测实体类型。
            2. 如果词语存在歧义，不要自行消歧。
            3. 不得加入用户未提到的限定词。例如：
            - “白海豚”不得改成“中华白海豚”“海洋保护”或“台风白海豚”。
            - “苹果”不得自行判断为水果或苹果公司。
            4. search_query 应尽量保留原始关键词，只删除“我想知道”“相关信息”等无意义表达。
            5. 是否代表台风、动物、公司、电影等含义，应由数据库中的候选热点标题决定。
            6. 用户没有明确时间范围时，默认查询最近 72 小时。

            用户原始问题：{original_content}

            请仅返回合法的 JSON 对象，不要输出 Markdown 代码块或其他文字：
            {{
            "search_query": "保留歧义的核心检索词",
            "exact_keywords": ["必须原样匹配的关键词"],
            "hours": 72,
            "need_hot": true,
            "ambiguous": true,
            "original_intent": "不猜测具体实体类型的用户意图"
            }}
    """
    response_format = {
        "type": "json_object"
    }
    messages = {
        "system": "You are a search planner. Always return a valid JSON object.",
        "user": prompt
    }
    model_content = await collect_model_text(messages, response_format)
    try:
        plan = SearchPlan.model_validate(json_repair.loads(model_content))
    except (ValidationError, ValueError, TypeError):
        plan = SearchPlan(
            search_query=original_content,
            hours=72,
            need_hot=True,
        )
    return await search_rank_data(
        pg_pool,
        plan.search_query,
        plan.hours,
        platform,
        plan.need_hot,
    )



async def search_rank_data(pg_pool, content: str, hours: int, platform: list[str], need_hot: bool, top_k: int = 8):
    query_digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    embedding_cache_key = f"emb:query:{query_digest}"
    embedding = await redis_cache.get(embedding_cache_key)
    if embedding is None:
        embedding = await embedding_with_model(content)
        await redis_cache.set(embedding_cache_key, json.dumps(embedding), ex=3600)  # cache for 1 hour
    else:
        embedding = json.loads(embedding)
    result_cache_key = build_rank_result_cache_key(
        content,
        hours,
        platform,
        need_hot,
        top_k,
    )
    data = await redis_cache.get(result_cache_key)
    if data is None:

        # check embedding
        if not embedding or not isinstance(embedding, list) or len(embedding) == 0:
            return ToolResult(
                ok=False,
                message="Invalid embedding",
                error=ToolError(
                    code=400,
                    message="Invalid embedding",
                    retryable=False
                ),
                meta=ToolMeta(
                    tool_call_id="search_rank_data",
                    duration_ms=0,
                    cached=False
                )
            )
        order_by = (
            "similarity DESC, hot_value DESC NULLS LAST"
            if need_hot
            else "similarity DESC"
        )
        async with pg_pool.acquire() as conn:
            sql = """
                    SELECT
                    id,
                    source,
                    title,
                    url,
                    hot_value,
                    1 - (embedding <=> $1) AS similarity
                    from hot_topic
                    WHERE NULLIF(BTRIM(url), '') IS NOT NULL
                    AND 1 - (embedding <=> $1) > 0.3
                    AND source = ANY($4)
                    AND last_seen >= EXTRACT(EPOCH FROM NOW() - ($3 * INTERVAL '1 hour'))::bigint
                    ORDER BY {}
                    LIMIT $2
            """.format(order_by)
            records = await conn.fetch(sql, embedding, top_k, hours, platform)
        data = [
            {
                "id": row["id"],
                "source": row["source"],
                "title": row["title"],
                "url": row["url"],
                "hot_value": row["hot_value"],
                "similarity": row["similarity"],
                "source": row["source"],
            }
            for row in records
        ]
        await redis_cache.set(result_cache_key, json.dumps(data, ensure_ascii=False, default=str), ex=60*3)  # cache for 1 hour
    else:
        data = json.loads(data)
    return ToolResult(
        ok=True,
        message="success",
        data=data,
        source=platform,
        meta=ToolMeta(
            tool_call_id="search_rank_data",
            duration_ms=0,
            cached=False
        )
    )
