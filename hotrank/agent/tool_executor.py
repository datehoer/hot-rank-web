from dataclasses import dataclass
from hotrank.schemas import AgentMessage
from hotrank.agent.tools.get_today_news import get_today_news
from hotrank.agent.tools.get_topic_detail import get_topic_detail
from hotrank.agent.tools.search_rankings import get_rank_data

@dataclass
class ToolContext:
    pg_pool: object
    message: AgentMessage
    session_id: str


async def execute_tool(
    name: str,
    arguments: dict,
    context: ToolContext,
):
    if name == "get_today_news":
        return await get_today_news(
            context.pg_pool,
            limit=arguments.get("limit", 10),
        )

    if name == "get_topic_detail":
        return await get_topic_detail(
            topic_id=arguments["topic_id"],
            platform=arguments["platform"],
            pg_pool=context.pg_pool,
        )

    if name == "get_rank_data":
        tool_message = context.message.model_copy(
            update={
                "content": arguments.get(
                    "content",
                    context.message.content,
                ),
                "platform": arguments.get(
                    "platform",
                    context.message.platform,
                ),
                "session_id": context.session_id,
            }
        )

        return await get_rank_data(
            context.pg_pool,
            tool_message,
        )

    raise ValueError(f"Unknown tool: {name}")