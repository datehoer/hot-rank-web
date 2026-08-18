import json
import logging
from hotrank.agent.tool_executor import ToolContext
from hotrank.agent.orchestrator import run_agent

def encode_sse(event: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"

async def agent_response(session_id, message, request):
    yield encode_sse("meta", {"session_id": session_id})

    context = ToolContext(
        pg_pool=request.app.state.pg_pool,
        message=message,
        session_id=session_id,
    )
    try:
        async for event in run_agent(message, context):
            event_type = event.pop("type")
            yield encode_sse(event_type, event)

    except Exception:
        logging.exception("Agent stream failed")
        yield encode_sse("error", {
            "code": "AGENT_FAILED",
            "message": "热点助手暂时无法完成请求，请稍后重试。",
            "retryable": True,
        })
