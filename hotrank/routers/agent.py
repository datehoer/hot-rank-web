from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, StreamingResponse
from hotrank.agent.source_config import (
    QUERY_SOURCES_REDIS_KEY,
    SOURCE_LABELS,
    get_allowed_query_sources,
)
from hotrank.schemas import AgentMessage
from hotrank.agent.events import agent_response
router = APIRouter()

AGENT_TEST_PAGE = (
    Path(__file__).resolve().parent.parent
    / "static"
    / "agent_test.html"
)


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
async def post_agent_message(
    session_id: str,
    message: AgentMessage,
    request: Request,
):
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
