import asyncio
import json
import logging
import traceback

import aiohttp

from config import (
    api_gemini_headers,
    api_gemini_url,
    api_headers,
    api_url,
)
from hotrank.infrastructure import redis_client


async def chat_with_model(messages, response_format):
    err = 10
    while err > 0:
        model = await redis_client.get("model")
        api_base_url = api_url
        api_base_headers = api_headers
        if not model:
            model_name = "gpt-4o"
            model_type = "openai"
        else:
            model_name = model.split(":")[1]
            model_type = model.split(":")[0]

        if model_type == "gemini":
            api_base_url = api_gemini_url + model_name + ":streamGenerateContent?alt=sse"
            api_base_headers = api_gemini_headers
            req_json = {
                "system_instruction": {
                    "parts": [
                        {"text": messages["system"]}
                    ]
                },
                "contents": [
                    {
                        "parts": [
                            {"text": messages["user"]}
                        ]
                    }
                ],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "response_json_schema": response_format,
                },
            }
        else:
            req_json = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": messages["system"],
                    },
                    {
                        "role": "user",
                        "content": messages["user"],
                    },
                ],
                "stream": True,
                "temperature": 0.1,
                "max_tokens": 4096,
                "top_p": 1.0,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "hot_topic",
                        "strict": True,
                        "schema": response_format,
                    },
                },
            }

        timeout = aiohttp.ClientTimeout(total=360.0)
        async with aiohttp.ClientSession(timeout=timeout) as client:
            try:
                async with client.post(
                    api_base_url,
                    headers=api_base_headers,
                    json=req_json,
                ) as response:
                    text = ""
                    try:
                        async for line in response.content:
                            line = line.decode("utf-8").strip()
                            if line and line.startswith("data: ") and not line.endswith("[DONE]"):
                                data = json.loads(line[len("data: "):])
                                if model_type == "openai" and "choices" in data:
                                    if (
                                        data["choices"]
                                        and len(data["choices"]) > 0
                                        and "delta" in data["choices"][0]
                                    ):
                                        chunk = data["choices"][0]["delta"].get("content", "")
                                        text += chunk
                                elif model_type == "gemini" and "candidates" in data:
                                    if (
                                        data["candidates"]
                                        and len(data["candidates"]) > 0
                                        and "content" in data["candidates"][0]
                                        and "parts" in data["candidates"][0]["content"]
                                    ):
                                        parts = data["candidates"][0]["content"]["parts"]
                                        if len(parts) > 0 and "text" in parts[0]:
                                            chunk = data["candidates"][0]["content"]["parts"][0].get("text", "")
                                            text += chunk
                    except (aiohttp.ServerTimeoutError, asyncio.TimeoutError):
                        logging.warning("Stream reading timed out, using partial response")
                        err -= 1
                        continue

                    if not text:
                        if response.status == 504:
                            logging.warning("time out")
                        elif response.status == 401:
                            logging.warning("no token")
                        else:
                            logging.warning(f"not text, code:{response.status}")
                        err -= 1
                        continue
                    return text
            except Exception as exc:
                logging.error(f"fetch ai error: {exc}\n{traceback.format_exc()}")
                err -= 1
    return ""
