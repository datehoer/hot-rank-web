import copy
from dataclasses import dataclass, field

from pydantic import ValidationError

from hotrank.agent.citations import CitationRegistry
from hotrank.agent.tool_arguments import (
    GetRankDataArguments,
    GetTodayNewsArguments,
    GetTopicDetailArguments,
    TOOL_ARGUMENT_MODELS,
)
from hotrank.agent.tools.get_today_news import get_today_news
from hotrank.agent.tools.get_topic_detail import get_topic_detail
from hotrank.agent.tools.search_rankings import get_rank_data
from hotrank.schemas import (
    AgentMessage,
    ToolError,
    ToolMeta,
    ToolResult,
)


@dataclass
class AllowedTopic:
    platform: str
    url: str


@dataclass
class ToolContext:
    pg_pool: object
    message: AgentMessage
    session_id: str
    allowed_sources: frozenset[str] = field(default_factory=frozenset)
    allowed_topics: dict[int, AllowedTopic] = field(default_factory=dict)
    citations: CitationRegistry = field(default_factory=CitationRegistry)

    def prepare_tool_result(self, name: str, result: dict) -> dict:
        secured_result = copy.deepcopy(result)
        if not secured_result.get("ok"):
            return secured_result

        data = secured_result.get("data")
        if not isinstance(data, list):
            return secured_result

        result_sources = secured_result.get("source")
        fallback_platform = (
            result_sources[0]
            if isinstance(result_sources, list) and result_sources
            else None
        )

        secured_items = []
        for item in data:
            if not isinstance(item, dict):
                continue

            topic_id = item.get("id")
            platform = item.get("source") or fallback_platform
            if not isinstance(topic_id, int) or not isinstance(platform, str):
                continue

            raw_url = item.get("url") or item.get("hot_url")
            if name in {"get_today_news", "get_rank_data"}:
                if (
                    platform not in self.allowed_sources
                    or not isinstance(raw_url, str)
                ):
                    continue
                self.allowed_topics[topic_id] = AllowedTopic(
                    platform=platform,
                    url=raw_url,
                )

            source_id = self.citations.register(
                topic_id=topic_id,
                title=item.get("title") or item.get("hot_label"),
                url=raw_url,
                platform=platform,
                hot_value=item.get("hot_value"),
                rank_updated_at=item.get("last_seen"),
                detail_status=(
                    "fetched" if name == "get_topic_detail" else "title_only"
                ),
            )
            if source_id is not None:
                item["source_id"] = source_id

            # Raw URLs are not model-authorized citations. The server retains
            # them in CitationRegistry and emits them only after validation.
            item.pop("url", None)
            item.pop("hot_url", None)
            secured_items.append(item)

        secured_result["data"] = secured_items
        return secured_result


def tool_error(
    *,
    name: str,
    code: str,
    message: str,
    retryable: bool = False,
) -> ToolResult:
    return ToolResult(
        ok=False,
        message=message,
        data=[],
        error=ToolError(
            code=code,
            message=message,
            retryable=retryable,
        ),
        meta=ToolMeta(
            tool_call_id=name,
            duration_ms=0,
            cached=False,
        ),
    )


async def execute_tool(
    name: str,
    arguments: dict,
    context: ToolContext,
) -> dict:
    argument_model = TOOL_ARGUMENT_MODELS.get(name)
    if argument_model is None:
        return tool_error(
            name=name or "unknown",
            code="UNKNOWN_TOOL",
            message="该工具未注册。",
        ).model_dump(mode="json")

    try:
        parsed_arguments = argument_model.model_validate(arguments)
    except ValidationError:
        return tool_error(
            name=name,
            code="INVALID_TOOL_ARGUMENTS",
            message="工具参数无效或超出允许范围。",
        ).model_dump(mode="json")

    if isinstance(parsed_arguments, GetTodayNewsArguments):
        if not context.allowed_sources:
            result = tool_error(
                name=name,
                code="NO_ALLOWED_SOURCES",
                message="本轮没有可查询的数据来源。",
            )
        else:
            result = await get_today_news(
                context.pg_pool,
                limit=parsed_arguments.limit,
                platforms=sorted(context.allowed_sources),
            )

    elif isinstance(parsed_arguments, GetTopicDetailArguments):
        allowed_topic = context.allowed_topics.get(
            parsed_arguments.topic_id
        )
        if allowed_topic is None:
            result = tool_error(
                name=name,
                code="TOPIC_NOT_IN_CURRENT_RUN",
                message="只能读取本轮检索结果中的新闻正文。",
            )
        elif allowed_topic.platform != parsed_arguments.platform:
            result = tool_error(
                name=name,
                code="TOPIC_PLATFORM_MISMATCH",
                message="热点来源与本轮检索结果不一致。",
            )
        else:
            result = await get_topic_detail(
                topic_id=parsed_arguments.topic_id,
                platform=parsed_arguments.platform,
                pg_pool=context.pg_pool,
                expected_url=allowed_topic.url,
            )

    elif isinstance(parsed_arguments, GetRankDataArguments):
        requested_sources = set(parsed_arguments.platform)
        if not requested_sources.issubset(context.allowed_sources):
            result = tool_error(
                name=name,
                code="QUERY_SOURCE_NOT_ALLOWED",
                message="查询来源不在本轮用户允许范围内。",
            )
        else:
            tool_message = context.message.model_copy(
                update={
                    "content": parsed_arguments.content,
                    "platform": parsed_arguments.platform,
                    "session_id": context.session_id,
                }
            )
            result = await get_rank_data(context.pg_pool, tool_message)
    else:  # pragma: no cover - the registry and union are kept in sync.
        result = tool_error(
            name=name,
            code="UNKNOWN_TOOL",
            message="该工具未注册。",
        )

    payload = (
        result.model_dump(mode="json")
        if hasattr(result, "model_dump")
        else result
    )
    return context.prepare_tool_result(name, payload)
