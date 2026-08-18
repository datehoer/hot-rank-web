"""阿里云内容安全（Green 2022-03-02）封装。

使用 `response_security_check_pro`（AI 输出内容安全检测 Pro 版），
覆盖内容合规（含涉政）、提示词攻击、敏感数据、模型幻觉等维度。

设计要点：

- SDK 为同步阻塞调用，所有网络调用通过 ``asyncio.to_thread`` 包装，
  避免阻塞 FastAPI 事件循环。
- 任何网络、鉴权、未知异常一律「降级放行」（``blocked=False``），
  由离线关键词规则继续兜底，绝不因审核服务故障拖垮 Agent。
- 凭证从环境变量 ``ALIBABA_CLOUD_ACCESS_KEY_ID`` /
  ``ALIBABA_CLOUD_ACCESS_KEY_SECRET`` 读取，禁止硬编码。
- 文本超过单次上限（2000 字符）时分块检测，任一块命中即拦截。
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

SERVICE = "response_security_check_pro"
REGION_ID = "cn-shanghai"
ENDPOINT = "green-cip.cn-shanghai.aliyuncs.com"
CONNECT_TIMEOUT_MS = 5000
READ_TIMEOUT_MS = 5000
MAX_CONTENT_CHARS = 2000

# 整体建议值：block > mask > watch > pass。仅 block 触发拦截，
# mask / watch 仅记录，不阻断（避免误伤正常内容）。
BLOCK_SUGGESTIONS = frozenset({"block"})

# 输出侧被拦截时，替换掉原始回答的安全文案。
OUTPUT_BLOCKED_REPLY = (
    "抱歉，这条回答未能通过内容安全检测，我无法展示。"
    "请换个问法，或换一个话题试试。"
)

_PASS_RESULT = {
    "blocked": False,
    "suggestion": "pass",
    "labels": [],
    "error": None,
}

_client = None
_warned: set[str] = set()


def _warn_once(key: str, message: str) -> None:
    if key not in _warned:
        _warned.add(key)
        logger.warning(message)


def _build_client():
    global _client
    if _client is not None:
        return _client

    ak = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
    sk = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()
    if not ak or not sk:
        raise RuntimeError("Alibaba Cloud content moderation credentials not configured")

    from alibabacloud_green20220302.client import Client
    from alibabacloud_tea_openapi.models import Config

    config = Config(
        access_key_id=ak,
        access_key_secret=sk,
        connect_timeout=CONNECT_TIMEOUT_MS,
        read_timeout=READ_TIMEOUT_MS,
        region_id=REGION_ID,
        endpoint=ENDPOINT,
    )
    _client = Client(config)
    return _client


def _to_dict(body: Any) -> dict:
    if isinstance(body, dict):
        return body
    if hasattr(body, "to_map"):
        mapped = body.to_map()
        if isinstance(mapped, dict):
            return mapped
    if hasattr(body, "__dict__"):
        return dict(body.__dict__)
    return {}


def _parse_response_body(body: dict) -> dict:
    """解析 SDK 响应体为统一结构（纯函数，便于单测）。"""
    code = body.get("Code")
    if code != 200:
        raise RuntimeError(
            f"green API code={code}, message={body.get('Message')}"
        )

    data = body.get("Data") or {}
    suggestion = str(data.get("Suggestion") or "pass").lower()

    labels = []
    for detail in data.get("Detail") or []:
        detail_type = detail.get("Type")
        for result in detail.get("Result") or []:
            label = result.get("Label")
            if label and label != "nonLabel":
                labels.append({
                    "type": detail_type,
                    "label": label,
                    "level": result.get("Level"),
                    "description": result.get("Description"),
                })

    return {
        "blocked": suggestion in BLOCK_SUGGESTIONS,
        "suggestion": suggestion,
        "labels": labels,
        "error": None,
    }


def _moderate_sync(text: str) -> dict:
    from alibabacloud_green20220302 import models

    client = _build_client()
    params = {"content": text}
    request = models.MultiModalGuardRequest(
        service=SERVICE,
        service_parameters=json.dumps(params, ensure_ascii=False),
    )
    response = client.multi_modal_guard(request)
    return _parse_response_body(_to_dict(response.body))


async def _moderate_once(text: str) -> dict:
    return await asyncio.to_thread(_moderate_sync, text)


async def moderate_text(content: str) -> dict:
    """检测一段文本；返回 ``{"blocked", "suggestion", "labels", "error"}``。

    任何异常都降级为放行，不影响主流程。
    """
    text = (content or "").strip()
    if not text:
        return dict(_PASS_RESULT)

    try:
        if len(text) <= MAX_CONTENT_CHARS:
            return await _moderate_once(text)

        chunks = [
            text[offset:offset + MAX_CONTENT_CHARS]
            for offset in range(0, len(text), MAX_CONTENT_CHARS)
        ]
        aggregated = dict(_PASS_RESULT)
        aggregated["labels"] = []
        for chunk in chunks:
            result = await _moderate_once(chunk)
            if result["blocked"]:
                return result
            aggregated["labels"].extend(result["labels"])
            if result["suggestion"] in {"mask", "watch"}:
                aggregated["suggestion"] = result["suggestion"]
        return aggregated

    except RuntimeError as exc:
        # 凭证缺失属于配置问题，只警告一次。
        _warn_once("credentials", f"content moderation unavailable: {exc}")
        return dict(_PASS_RESULT, error=str(exc))
    except Exception as exc:  # noqa: BLE001 - 审核失败一律降级放行
        _warn_once("general", f"content moderation degraded to pass: {exc}")
        return dict(_PASS_RESULT, error=str(exc))
