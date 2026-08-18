import json
import logging
from time import perf_counter
import aiohttp

from hotrank.agent.prompts import SYSTEM_PROMPT
from hotrank.agent.content_filter import (
    BLOCKED_NOTICE,
    BLOCKED_REPLY,
    check_hard_block,
    check_message,
)
from hotrank.agent.green_moderation import (
    OUTPUT_BLOCKED_REPLY,
    moderate_text,
)
from hotrank.agent.source_config import get_allowed_query_sources
from hotrank.agent.tool_registry import tools_for_query_sources
from hotrank.model_client import (
    AGENT_API_HEADERS,
    AGENT_API_RESPONSE_URL,
    AGENT_MODEL,
    stream_model_events,
)
from hotrank.agent.tool_executor import execute_tool
from hotrank.agent.tool_events import describe_tool_call, summarize_tool_result


def _citation_retry_instruction(source_ids: list[str]) -> str:
    ids = ", ".join(source_ids)
    return (
        "你上一条回答没有使用任何引用标记。"
        "请重新输出回答，并为每一个事实性结论紧跟着补上引用标记 "
        "[[source:SOURCE_ID]]。"
        f"本次可用的 source_id 仅限：{ids}。"
        "不要编造其他 source_id 或 URL；"
        "如果某个结论确实没有对应来源，请明确说明该结论缺少来源。"
    )


def _blocked_reply_events(
    code: str,
    notice: str,
    reply: str = BLOCKED_REPLY,
):
    """统一的拒答事件序列（不调用模型）。"""
    yield {
        "type": "status",
        "stage": "planning",
    }
    for offset in range(0, len(reply), 512):
        yield {
            "type": "delta",
            "text": reply[offset:offset + 512],
        }
    yield {
        "type": "warning",
        "code": code,
        "message": notice,
    }
    yield {
        "type": "done",
        "usage": {},
    }


async def run_agent(message, context):
    decision = check_message(message.content)
    if decision.blocked:
        for event in _blocked_reply_events("CONTENT_BLOCKED", decision.notice):
            yield event
        return

    moderation = await moderate_text(message.content)
    if moderation["blocked"]:
        for event in _blocked_reply_events("CONTENT_BLOCKED", BLOCKED_NOTICE):
            yield event
        return

    yield {
        "type": "status",
        "stage": "planning",
    }
    configured_sources = set(await get_allowed_query_sources())
    requested_sources = set(message.platform)
    invalid_sources = requested_sources - configured_sources
    if invalid_sources:
        raise ValueError("请求包含未启用的数据来源。")

    context.allowed_sources = frozenset(requested_sources)
    available_tools = tools_for_query_sources(
        sorted(context.allowed_sources)
    )
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
        headers=AGENT_API_HEADERS,
        timeout=timeout,
    ) as session:
        tool_call_limits = {
            "get_today_news": 1,
            "get_rank_data": 2,
            "get_topic_detail": 3,
        }

        tool_call_counts = {}
        total_tool_calls = 0
        seen_tool_calls = set()
        force_final_answer = False
        citation_retried = False
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
            response_text_parts = []

            active_tools = None if force_final_answer else available_tools
            async for event in stream_model_events(
                input_items=input_items,
                session=session,
                tools=active_tools,
                model_name=AGENT_MODEL,
                response_url=AGENT_API_RESPONSE_URL,
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
                    delta = event.get("delta", "")
                    if delta:
                        response_text_parts.append(delta)
                    if not generating_status_sent:
                        yield {
                            "type": "status",
                            "stage": "generating",
                        }
                        generating_status_sent = True

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
                raw_answer = "".join(response_text_parts)[:12_000]
                answer, citations = context.citations.resolve_answer(raw_answer)

                available_source_ids = context.citations.registered_source_ids()
                missing_citations = bool(
                    not citations and available_source_ids
                )
                if missing_citations and not citation_retried:
                    citation_retried = True
                    input_items.append(
                        {"role": "assistant", "content": raw_answer}
                    )
                    input_items.append({
                        "role": "user",
                        "content": _citation_retry_instruction(
                            available_source_ids
                        ),
                    })
                    force_final_answer = True
                    yield {
                        "type": "status",
                        "stage": "generating",
                        "message": "正在补充引用",
                    }
                    continue

                output_blocked = False
                if check_hard_block(answer).blocked:
                    output_blocked = True
                else:
                    output_moderation = await moderate_text(answer)
                    output_blocked = output_moderation["blocked"]

                if output_blocked:
                    answer = OUTPUT_BLOCKED_REPLY
                    citations = []
                    yield {
                        "type": "warning",
                        "code": "OUTPUT_BLOCKED",
                        "message": "回答未通过内容安全检测，已替换为安全提示。",
                    }

                for offset in range(0, len(answer), 512):
                    yield {
                        "type": "delta",
                        "text": answer[offset:offset + 512],
                    }
                for citation in citations:
                    yield {
                        "type": "citation",
                        "citation": citation,
                    }
                if missing_citations and not output_blocked:
                    yield {
                        "type": "warning",
                        "code": "MISSING_CITATIONS",
                        "message": (
                            "本回答未能附上可验证的来源引用，"
                            "请谨慎参考并查看原始榜单。"
                        ),
                    }
                yield {
                    "type": "done",
                    "usage": completed_response.get("usage"),
                }
                return

            input_items.extend(response_output)

            for call in function_calls:
                name = str(call.get("name") or "")
                try:
                    arguments = json.loads(call.get("arguments") or "{}")
                    if not isinstance(arguments, dict):
                        arguments = {}
                except (json.JSONDecodeError, TypeError):
                    arguments = {}
                call_id = call.get("call_id") or call.get("id")
                presentation = describe_tool_call(name, arguments)
                tool_stage = (
                    "fetching"
                    if name == "get_topic_detail"
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
                    name,
                    json.dumps(
                        arguments,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                )
                limit = tool_call_limits.get(name, 1)
                count = tool_call_counts.get(name, 0)
                if (
                    signature in seen_tool_calls
                    or count >= limit
                    or total_tool_calls >= 4
                ):
                    input_items.append({
                        "type": "function_call_output",
                        "call_id": call_id,
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
                        "tool": name,
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
                        name=name,
                        arguments=arguments,
                        context=context,
                    )
                except Exception as exc:
                    logging.exception(
                        "Tool execution failed: tool=%s",
                        name,
                    )
                    result = {
                        "ok": False,
                        "message": "工具执行失败。",
                        "data": [],
                        "error": {
                            "code": "INTERNAL_TOOL_ERROR",
                            "message": "工具执行失败。",
                            "retryable": True,
                        },
                    }

                duration_ms = round((perf_counter() - started_at) * 1000)
                yield {
                    "type": "tool_result",
                    "call_id": call_id,
                    "tool": name,
                    **summarize_tool_result(
                        name,
                        result,
                        duration_ms,
                    ),
                }

                input_items.append({
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(
                        result,
                        ensure_ascii=False,
                    ),
                })
                seen_tool_calls.add(signature)
                tool_call_counts[name] = count + 1
                total_tool_calls += 1

        raise RuntimeError("Tool call limit exceeded")
