"""Agent 输入内容安全过滤（Option B：软区分策略）。

策略目标：
- 拒绝「立场性 / 评价性」的敏感政治问题（例如“你怎么看……”“某某对不对”）。
- 保留「事实性」的热点检索 / 转述请求（例如“今天有什么时政热点”“这条新闻讲了什么”），
  让产品继续发挥热点研究的价值；这类回答由 System Prompt 约束为客观转述、不表态。

实现方式：
- 纯规则、确定性的前置过滤，在调用模型之前执行，不依赖模型自觉。
- 分两层：
  1. 硬拦截名单：命中即拒绝，不论措辞（最敏感、明确越界的特定人物 / 事件 / 组织）。
  2. 立场词（STANCE_PATTERNS）+ 政治敏感域关键词：同时命中判定为立场性政治问题，拒绝。

敏感词来源（重要）：
- 硬拦截词与政治域关键词均从 **Redis** 读取（主源，可热更新）：
  ``agent:filter:hard_terms`` / ``agent:filter:political_terms``（JSON 字符串数组）。
- Redis 不可用或 key 缺失时回退到环境变量
  ``HOTRANK_HARD_BLOCK_TERMS`` / ``HOTRANK_POLITICAL_KEYWORDS``（逗号分隔，本地 .env 提供）。
- 内存缓存 60 秒，避免每条消息都打 Redis。
- 真实敏感词只存在于 Redis / 本地 .env，**不入库、不出现在公开仓库**。
- ``STANCE_PATTERNS`` 是通用立场 / 评价意图词，不含敏感词，保留在代码中。

说明：
- 关键词表是「可调起点」，运营方应根据自身政策在 Redis / .env 中增删。
  命中口径为归一化后的子串匹配，会去掉空白字符（可拦截拆字写法）。
- ``reason`` 只用于内部日志与测试，不发送给前端。
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# 环境变量名（兜底词表）
HARD_BLOCK_ENV = "HOTRANK_HARD_BLOCK_TERMS"
POLITICAL_ENV = "HOTRANK_POLITICAL_KEYWORDS"

# Redis key（主源，可热更新）
REDIS_HARD_KEY = "agent:filter:hard_terms"
REDIS_POLITICAL_KEY = "agent:filter:political_terms"

# 内存缓存 TTL（秒）：改完词表后最多该时长内全量生效。
CACHE_TTL_SECONDS = 60.0

# 拒绝时返回给用户的话术（作为回答正文，引导回热点场景）。
BLOCKED_REPLY = (
    "抱歉，这类话题我不方便展开讨论。"
    "我是热点研究助手，可以帮你检索、总结和对比当前热榜上的科技、财经、娱乐等热点内容，"
    "换个话题试试？"
)

# 前端 warning 横幅里的简短提示。
BLOCKED_NOTICE = "已识别为敏感话题，未生成回答。"


def _load_env_terms(env_name: str) -> tuple[str, ...]:
    """从环境变量读取逗号分隔的词表，返回去重、去空后的元组。"""
    raw = os.environ.get(env_name, "")
    terms = []
    for part in raw.split(","):
        part = part.strip()
        if part:
            terms.append(part)
    return tuple(dict.fromkeys(terms))


# ---------------------------------------------------------------------------
# 兜底词表：Redis 不可用时的回退值（import 时从环境变量 / .env 加载）。
# ---------------------------------------------------------------------------
ENV_HARD_BLOCK_TERMS = _load_env_terms(HARD_BLOCK_ENV)
ENV_POLITICAL_KEYWORDS = _load_env_terms(POLITICAL_ENV)

# ---------------------------------------------------------------------------
# 立场 / 评价意图模式（不含敏感词，保留在代码中）。
# ---------------------------------------------------------------------------
STANCE_PATTERNS = (
    # 直接询问看法 / 评价
    "怎么看",
    "如何看",
    "怎么评价",
    "如何评价",
    "评价一下",
    "评价",
    "你怎么想",
    "你的看法",
    "你的观点",
    "你认为",
    "你觉得",
    "你认同",
    "你同意",
    "你支持",
    "你反对",
    "你站",
    "什么立场",
    "什么观点",
    "站队",
    "站哪边",
    "定性",
    # 是非 / 好坏 / 对错判断
    "是不是",
    "好不好",
    "对不对",
    "行不行",
    "正确吗",
    "错误吗",
    "对吗",
    "错吗",
    "该不该",
    "应不应该",
    "值不值得",
    "支不支持",
    "反不反对",
    "支持还是",
    "反对还是",
    "谁对",
    "谁错",
    "哪个对",
    "哪个错",
    "哪方对",
    "是好是坏",
    "是好人",
    "是坏人",
    "怎么样",
    "如何",
)


@dataclass(frozen=True)
class FilterDecision:
    """过滤结果。``blocked=True`` 表示应拒绝并返回 ``reply``。"""

    blocked: bool
    reason: str = ""
    reply: str = ""
    notice: str = ""


_WS_RE = re.compile(r"\s+")

# 内存缓存：{"ts": monotonic, "hard": tuple, "political": tuple}
_cache: dict = {"ts": 0.0, "hard": (), "political": ()}
_cache_lock = asyncio.Lock()


def _normalize(text: str) -> str:
    """去掉空白并转小写，用于统一口径的匹配。"""
    return _WS_RE.sub("", text or "").lower()


def _contains_any(normalized: str, terms: tuple[str, ...]) -> bool:
    return any(term in normalized for term in terms)


def _block(reason: str) -> FilterDecision:
    return FilterDecision(
        blocked=True,
        reason=reason,
        reply=BLOCKED_REPLY,
        notice=BLOCKED_NOTICE,
    )


def _parse_terms(raw: str | None) -> tuple[str, ...] | None:
    """解析 Redis 中的 JSON 字符串数组词表。

    - ``raw`` 为 ``None``（key 缺失）或解析失败时返回 ``None``，由调用方回退 env；
    - 合法空数组返回空元组（表示管理员有意清空词表）。
    """
    if raw is None:
        return None
    try:
        data = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        logger.warning("Invalid JSON for filter terms: %r", str(raw)[:200])
        return None
    if not isinstance(data, list) or not all(isinstance(x, str) for x in data):
        logger.warning(
            "Filter terms must be a JSON string array: %r",
            str(raw)[:200],
        )
        return None
    return tuple(dict.fromkeys(t.strip() for t in data if t.strip()))


async def _load_terms_from_redis() -> tuple[tuple[str, ...], tuple[str, ...]]:
    """从 Redis 读取词表；读取失败或 key 缺失时回退 env。"""
    from hotrank.cache import redis_cache

    hard: tuple[str, ...] | None = None
    political: tuple[str, ...] | None = None
    try:
        raw_hard = await redis_cache.get(REDIS_HARD_KEY)
        raw_political = await redis_cache.get(REDIS_POLITICAL_KEY)
        hard = _parse_terms(raw_hard)
        political = _parse_terms(raw_political)
    except Exception as exc:  # noqa: BLE001 - 任何异常都回退 env
        logger.warning("Unable to read filter terms from Redis: %s", exc)
        hard = None
        political = None

    if hard is None:
        hard = ENV_HARD_BLOCK_TERMS
    if political is None:
        political = ENV_POLITICAL_KEYWORDS
    return hard, political


async def get_filter_terms() -> tuple[tuple[str, ...], tuple[str, ...]]:
    """返回 ``(hard_terms, political_terms)``，带内存缓存与 TTL。

    主源 Redis，回退 env；失败不抛异常，确保过滤永不拖垮主流程。
    """
    now = time.monotonic()
    if _cache["ts"] and (now - _cache["ts"]) < CACHE_TTL_SECONDS:
        return _cache["hard"], _cache["political"]

    async with _cache_lock:
        now = time.monotonic()
        if _cache["ts"] and (now - _cache["ts"]) < CACHE_TTL_SECONDS:
            return _cache["hard"], _cache["political"]
        hard, political = await _load_terms_from_redis()
        _cache["ts"] = now
        _cache["hard"] = hard
        _cache["political"] = political
        return hard, political


def _evaluate(
    content: str,
    hard_terms: tuple[str, ...],
    political_terms: tuple[str, ...],
) -> FilterDecision:
    """纯函数：根据词表对文本做判定（便于单测）。"""
    text = _normalize(content)
    if not text:
        return FilterDecision(blocked=False)

    if _contains_any(text, hard_terms):
        return _block("hard_block")

    if _contains_any(text, STANCE_PATTERNS) and _contains_any(
        text, political_terms
    ):
        return _block("stance_politics")

    return FilterDecision(blocked=False)


async def check_message(content: str) -> FilterDecision:
    """对用户输入做前置内容安全判定（异步，词表取自 Redis / env）。"""
    hard_terms, political_terms = await get_filter_terms()
    return _evaluate(content, hard_terms, political_terms)


async def check_hard_block(content: str) -> FilterDecision:
    """仅检查硬拦截名单（模型输出侧的离线兜底）。

    输出侧只做硬拦截，不套用「立场词 + 政治词」的组合规则，
    避免误伤模型对热点事实的正常转述。
    """
    hard_terms, _ = await get_filter_terms()
    text = _normalize(content)
    if not text:
        return FilterDecision(blocked=False)

    if _contains_any(text, hard_terms):
        return _block("hard_block")

    return FilterDecision(blocked=False)
