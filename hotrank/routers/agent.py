import hashlib
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from hotrank.agent.source_config import (
    QUERY_SOURCES_REDIS_KEY,
    SOURCE_LABELS,
    get_allowed_query_sources,
)
from hotrank.schemas import AgentMessage
from hotrank.agent.events import agent_response
from hotrank.infrastructure import (
    AGENT_IP_RATE_LIMIT,
    AGENT_SESSION_RATE_LIMIT,
    limiter,
)


router = APIRouter()

AGENT_TEST_PAGE = (
    Path(__file__).resolve().parent.parent
    / "static"
    / "agent_test.html"
)


def agent_session_rate_limit_key(request: Request) -> str:
    """Return a bounded Redis key without exposing the client session ID."""
    session_id = str(request.path_params.get("session_id") or "")
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
    return f"agent-session:{digest}"


@router.get("/agent/test", include_in_schema=False)
async def get_agent_test_page():
    return FileResponse(AGENT_TEST_PAGE, media_type="text/html")


@router.get("/agent/config/sources")
async def get_agent_query_sources():
    sources = await get_allowed_query_sources()
    return {
        "sources": sources,
        "default_selected": sources,
        "labels": {
            source: SOURCE_LABELS.get(source, source)
            for source in sources
        },
        "redis_key": QUERY_SOURCES_REDIS_KEY,
    }


@router.get("/agent/sessions")
async def get_agent_sessions(request: Request):
    return {"message": "List of agent sessions"}


@router.post("/agent/sessions/{session_id}/message")
@limiter.limit(AGENT_IP_RATE_LIMIT)
@limiter.limit(
    AGENT_SESSION_RATE_LIMIT,
    key_func=agent_session_rate_limit_key,
)
async def post_agent_message(
    session_id: str,
    message: AgentMessage,
    request: Request,
):
    if message.session_id != session_id:
        raise HTTPException(
            status_code=400,
            detail="Session ID does not match the request path.",
        )

    allowed_sources = set(await get_allowed_query_sources())
    invalid_sources = [
        source for source in message.platform
        if source not in allowed_sources
    ]
    if invalid_sources:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "QUERY_SOURCE_NOT_ALLOWED",
                "message": "查询来源不可用。",
                "invalid_sources": invalid_sources,
            },
        )

    return StreamingResponse(
        agent_response(session_id, message, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.get("/agent/sessions/{session_id}")
async def get_agent_session(session_id: str, request: Request):
    return {"message": f"Details of session {session_id}"}


@router.delete("/agent/sessions/{session_id}")
async def delete_agent_session(session_id: str, request: Request):
    return {"message": f"Session {session_id} deleted"}


@router.post("/agent/sessions/{session_id}/cancel")
async def cancel_agent_session(session_id: str, request: Request):
    return {"message": f"Session {session_id} cancelled"}
