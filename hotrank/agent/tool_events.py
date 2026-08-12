from typing import Any


TOOL_LABELS = {
    "get_today_news": "获取今日热点",
    "get_rank_data": "搜索近期热点",
    "get_topic_detail": "读取新闻内容",
}


def _short_text(value: Any, limit: int = 120) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return f"{text[:limit].rstrip()}…"


def describe_tool_call(name: str, arguments: dict) -> dict:
    """Build a user-facing tool call without exposing raw internal arguments."""
    label = TOOL_LABELS.get(name, "调用热点工具")
    safe_arguments = {}
    detail = ""

    if name == "get_rank_data":
        query = _short_text(arguments.get("content"), 100)
        platforms = arguments.get("platform")
        source_count = len(platforms) if isinstance(platforms, list) else 0
        safe_arguments = {
            "query": query,
            "source_count": source_count,
        }
        detail_parts = []
        if query:
            detail_parts.append(f"“{query}”")
        if source_count:
            detail_parts.append(f"{source_count} 个来源")
        detail = " · ".join(detail_parts)
    elif name == "get_today_news":
        limit = arguments.get("limit", 10)
        safe_arguments = {"limit": limit}
        detail = f"最多 {limit} 条"
    elif name == "get_topic_detail":
        platform = _short_text(arguments.get("platform"), 40)
        safe_arguments = {"platform": platform}
        detail = platform

    return {
        "tool": name,
        "label": label,
        "detail": detail,
        "arguments": safe_arguments,
    }


def summarize_tool_result(name: str, result: dict, duration_ms: int) -> dict:
    """Reduce a tool result to non-sensitive progress metadata for the UI."""
    ok = bool(result.get("ok"))
    data = result.get("data")
    result_count = len(data) if isinstance(data, list) else 0
    meta = result.get("meta") if isinstance(result.get("meta"), dict) else {}

    if ok:
        if name == "get_today_news":
            summary = f"找到 {result_count} 条今日热点"
        elif name == "get_rank_data":
            summary = f"找到 {result_count} 条相关热点"
        elif name == "get_topic_detail":
            summary = "新闻内容读取完成" if result_count else "未读取到新闻内容"
        else:
            summary = "工具调用完成"
        status = "completed"
    else:
        summary = {
            "get_today_news": "今日热点获取失败",
            "get_rank_data": "热点检索未完成",
            "get_topic_detail": "新闻内容读取失败",
        }.get(name, "工具调用失败")
        status = "failed"

    return {
        "status": status,
        "summary": summary,
        "result_count": result_count,
        "duration_ms": duration_ms,
        "cached": bool(meta.get("cached", False)),
    }
