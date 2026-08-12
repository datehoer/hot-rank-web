import json
import logging
import traceback

import aiohttp

from config import (
    api_headers,
    api_response_url,
    base_url,
)


MODEL_TIMEOUT = aiohttp.ClientTimeout(
    total=None,
    sock_connect=15,
    sock_read=60,
)

TERMINAL_EVENT_TYPES = {
    "response.completed",
    "response.incomplete",
    "response.failed",
    "error",
}

RETRYABLE_HTTP_STATUSES = {
    408,
    409,
    425,
    429,
}


class ModelHTTPError(RuntimeError):
    def __init__(self, status: int, body: str):
        super().__init__(f"HTTP {status}: {body[:2000]}")
        self.status = status

    @property
    def retryable(self) -> bool:
        return (
            self.status in RETRYABLE_HTTP_STATUSES
            or self.status >= 500
        )


async def iter_sse(response):
    """正确解析 Server-Sent Events，兼容多行 data。"""
    data_lines = []

    async for raw_line in response.content:
        line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")

        if not line:
            if data_lines:
                yield "\n".join(data_lines)
                data_lines.clear()
            continue

        if line.startswith("data:"):
            data_lines.append(line[5:].lstrip())

    if data_lines:
        yield "\n".join(data_lines)


def _responses_text_format(response_format):
    if response_format is None:
        return None

    if response_format.get("type") in {"json_object", "json_schema"}:
        return response_format

    return {
        "type": "json_schema",
        "name": response_format.get("title", "structured_response"),
        "strict": True,
        "schema": response_format,
    }


async def stream_model_events(
    input_items,
    session,
    tools=None,
    response_format=None,
):
    """Stream raw semantic events from the Responses-compatible endpoint."""
    for attempt in range(3):
        emitted = False
        terminal_received = False
        model_name = "deepseek-v4-flash"
        req_json = {
            "model": model_name,
            "input": input_items,
            "reasoning": {
                "effort": "low",
                "summary": "auto",
            },
            "stream": True,
            "temperature": 0.1,
            "max_output_tokens": 8012,
            "top_p": 1.0,
        }
        if tools:
            req_json["tools"] = tools
            req_json["tool_choice"] = "auto"

        text_format = _responses_text_format(response_format)
        if text_format:
            req_json["text"] = {"format": text_format}

        try:
            async with session.post(api_response_url, json=req_json) as response:
                content_type = response.headers.get("Content-Type", "")

                if response.status >= 400:
                    body = await response.text()
                    raise ModelHTTPError(response.status, body)

                if "text/event-stream" not in content_type:
                    body = await response.text()
                    raise RuntimeError(
                        f"服务端没有返回 SSE 流，Content-Type={content_type!r}\n"
                        f"响应内容：{body[:2000]}"
                    )

                async for data in iter_sse(response):
                    if not data:
                        continue

                    if data == "[DONE]":
                        break

                    try:
                        event = json.loads(data)
                    except json.JSONDecodeError as exc:
                        logging.warning("Invalid Responses SSE payload: %s", exc)
                        continue

                    event_type = event.get("type")

                    emitted = True
                    yield event

                    if event_type in TERMINAL_EVENT_TYPES:
                        terminal_received = True
                        return

                if not terminal_received:
                    raise RuntimeError(
                        "Responses stream ended without a terminal event"
                    )
        except Exception as exc:
            logging.error(f"fetch ai error: {exc}\n{traceback.format_exc()}")
            retryable = not isinstance(exc, ModelHTTPError) or exc.retryable
            if emitted or attempt == 2 or not retryable:
                raise


async def collect_model_text(messages, response_format=None):
    """Consume a Responses stream and return its complete text output."""
    input_items = [
        {
            "role": "system",
            "content": messages["system"],
        },
        {
            "role": "user",
            "content": messages["user"],
        },
    ]
    text_parts = []

    async with aiohttp.ClientSession(
        headers=api_headers,
        timeout=MODEL_TIMEOUT,
    ) as session:
        async for event in stream_model_events(
            input_items=input_items,
            session=session,
            response_format=response_format,
        ):
            event_type = event.get("type")

            if event_type == "response.output_text.delta":
                text_parts.append(event.get("delta", ""))
            elif event_type == "response.incomplete":
                response = event.get("response") or {}
                details = response.get("incomplete_details") or {}
                reason = details.get("reason", "unknown")
                raise RuntimeError(f"Model response incomplete: {reason}")
            elif event_type in {"error", "response.failed"}:
                raise RuntimeError(f"AI model error: {event}")

    return "".join(text_parts)


async def embedding_with_model(text: list[str], model: str = "text-embedding-3-small"):
    embedding_api_url = base_url + "/embeddings"
    err = 10
    while err > 0:
        try:
            async with aiohttp.ClientSession() as client:
                async with client.post(
                    embedding_api_url,
                    headers=api_headers,
                    json={
                        "model": model,
                        "input": text,
                        "dimensions": 1536,
                        "encoding_format": "float",
                    },
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["data"][0]["embedding"]
                    else:
                        logging.warning(f"embedding error, code:{response.status}")
                        err -= 1
        except Exception as exc:
            logging.error(f"embedding error: {exc}\n{traceback.format_exc()}")
            err -= 1
    return []
