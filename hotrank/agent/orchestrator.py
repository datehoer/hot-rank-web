import json
import logging
from time import perf_counter
import aiohttp

from config import api_headers
from hotrank.agent.prompts import SYSTEM_PROMPT
from hotrank.agent.source_config import get_allowed_query_sources
from hotrank.agent.tool_registry import tools_for_query_sources
from hotrank.model_client import stream_model_events
from hotrank.agent.tool_executor import execute_tool
from hotrank.agent.tool_events import describe_tool_call, summarize_tool_result


async def run_agent(message, context):
    yield {
        "type": "status",
        "stage": "planning",
    }
    allowed_sources = await get_allowed_query_sources()
    available_tools = tools_for_query_sources(allowed_sources)
    input_items = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": message.content,
        },
    ]
    timeout = aiohttp.ClientTimeout(
        total=None,
        sock_connect=15,
        sock_read=60,
    )
    async with aiohttp.ClientSession(
        headers=api_headers,
        timeout=timeout,
    ) as session:
        tool_call_limits = {
            "get_today_news": 1,
            "get_rank_data": 2,
            "get_topic_detail": 3,
        }

        tool_call_counts = {}
        seen_tool_calls = set()
        force_final_answer = False
        for round_number in range(8):
            if round_number > 0:
                yield {
                    "type": "status",
                    "stage": "planning",
                    "message": "正在分析工具结果",
                }
            response_output = []
            function_calls = []
            completed_response = None
            generating_status_sent = False

            active_tools = None if force_final_answer else available_tools
            async for event in stream_model_events(
                input_items=input_items,
                session=session,
                tools=active_tools,
            ):
                event_type = event.get("type")
                if event_type == "response.reasoning_summary_text.delta":
                    delta = event.get("delta", "")
                    if delta:
                        yield {
                            "type": "reasoning",
                            "id": f"{round_number + 1}:{event.get('item_id', 'summary')}",
                            "round": round_number + 1,
                            "delta": delta,
                            "status": "running",
                        }

                elif event_type == "response.reasoning_summary_text.done":
                    yield {
                        "type": "reasoning",
                        "id": f"{round_number + 1}:{event.get('item_id', 'summary')}",
                        "round": round_number + 1,
                        "text": event.get("text", ""),
                        "status": "completed",
                    }

                elif event_type == "response.output_text.delta":
                    if not generating_status_sent:
                        yield {
                            "type": "status",
                            "stage": "generating",
                        }
                        generating_status_sent = True
                    yield {
                        "type": "delta",
                        "text": event.get("delta", ""),
                    }

                elif event_type == "response.output_item.done":
                    item = event.get("item", {})

                    if item.get("type") == "function_call":
                        function_calls.append(item)

                elif event_type == "response.completed":
                    completed_response = event["response"]
                    response_output = completed_response.get(
                        "output",
                        [],
                    )

                elif event_type == "response.incomplete":
                    raise RuntimeError("Model response incomplete")

                elif event_type in {"error", "response.failed"}:
                    raise RuntimeError(str(event))

            if not completed_response:
                raise RuntimeError("Missing completed response")

            if not function_calls:
                yield {
                    "type": "done",
                    "usage": completed_response.get("usage"),
                }
                return

            input_items.extend(response_output)

            for call in function_calls:
                arguments = json.loads(call.get("arguments") or "{}")
                call_id = call.get("call_id") or call.get("id")
                presentation = describe_tool_call(call["name"], arguments)
                tool_stage = (
                    "fetching"
                    if call["name"] == "get_topic_detail"
                    else "searching"
                )
                yield {
                    "type": "status",
                    "stage": tool_stage,
                    "message": presentation["label"],
                }
                yield {
                    "type": "tool_call",
                    "call_id": call_id,
                    **presentation,
                }
                signature = (
                    call["name"],
                    json.dumps(
                        arguments,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                )
                limit = tool_call_limits.get(call["name"], 1)
                count = tool_call_counts.get(call["name"], 0)
                if signature in seen_tool_calls or count >= limit:
                    input_items.append({
                        "type": "function_call_output",
                        "call_id": call["call_id"],
                        "output": json.dumps({
                            "ok": False,
                            "error": {
                                "code": "tool_call_limit_reached",
                                "message": "工具已调用过或达到调用上限，请根据已有结果回答。",
                                "retryable": False,
                            },
                        }, ensure_ascii=False),
                    })
                    yield {
                        "type": "tool_result",
                        "call_id": call_id,
                        "tool": call["name"],
                        "status": "skipped",
                        "summary": "已使用已有结果，避免重复调用",
                        "result_count": 0,
                        "duration_ms": 0,
                        "cached": False,
                    }
                    force_final_answer = True
                    continue
                started_at = perf_counter()
                try:
                    result = await execute_tool(
                        name=call["name"],
                        arguments=arguments,
                        context=context,
                    )
                except Exception as exc:
                    logging.exception(
                        "Tool execution failed: tool=%s",
                        call["name"],
                    )
                    reason = str(exc).strip() or type(exc).__name__
                    result = {
                        "ok": False,
                        "message": f"Tool execution failed: {reason}",
                        "error": {
                            "code": 500,
                            "message": reason,
                            "retryable": True,
                        },
                    }

                if hasattr(result, "model_dump"):
                    result = result.model_dump(mode="json")

                duration_ms = round((perf_counter() - started_at) * 1000)
                yield {
                    "type": "tool_result",
                    "call_id": call_id,
                    "tool": call["name"],
                    **summarize_tool_result(
                        call["name"],
                        result,
                        duration_ms,
                    ),
                }

                input_items.append({
                    "type": "function_call_output",
                    "call_id": call["call_id"],
                    "output": json.dumps(
                        result,
                        ensure_ascii=False,
                    ),
                })
                seen_tool_calls.add(signature)
                tool_call_counts[call["name"]] = count + 1

        raise RuntimeError("Tool call limit exceeded")
