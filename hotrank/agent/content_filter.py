"""Agent 输入内容安全过滤（Option B：软区分策略）。

策略目标：
- 拒绝「立场性 / 评价性」的敏感政治问题（例如“你怎么看……”“某某对不对”）。
- 保留「事实性」的热点检索 / 转述请求（例如“今天有什么时政热点”“这条新闻讲了什么”），
  让产品继续发挥热点研究的价值；这类回答由 System Prompt 约束为客观转述、不表态。

实现方式：
- 纯规则、确定性的前置过滤，在调用模型之前执行，不依赖模型自觉。
- 分两层：
  1. ``HARD_BLOCK_TERMS``：命中即拒绝，不论措辞（最敏感、明确越界的特定人物 / 事件 / 组织）。
  2. ``STANCE_PATTERNS`` 与 ``POLITICAL_KEYWORDS`` 同时命中：判定为立场性政治问题，拒绝。

敏感词来源（重要）：
- ``HARD_BLOCK_TERMS`` 与 ``POLITICAL_KEYWORDS`` 均从环境变量读取
  （``HOTRANK_HARD_BLOCK_TERMS`` / ``HOTRANK_POLITICAL_KEYWORDS``，逗号分隔），
  实际值保存在部署环境的 ``.env`` 中，**不入库、不出现在公开仓库**。
- ``STANCE_PATTERNS`` 是通用立场 / 评价意图词，不含敏感词，保留在代码中。

说明：
- 关键词表是「可调起点」，运营方应根据自身政策在 .env 中增删。
  命中口径为归一化后的子串匹配，会去掉空白字符（可拦截拆字写法）。
- ``reason`` 只用于内部日志与测试，不发送给前端。
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

# 拒绝时返回给用户的话术（作为回答正文，引导回热点场景）。
BLOCKED_REPLY = (
    "抱歉，这类话题我不方便展开讨论。"
    "我是热点研究助手，可以帮你检索、总结和对比当前热榜上的科技、财经、娱乐等热点内容，"
    "换个话题试试？"
)

# 前端 warning 横幅里的简短提示。
BLOCKED_NOTICE = "已识别为敏感话题，未生成回答。"


def _load_terms(env_name: str) -> tuple[str, ...]:
    """从环境变量读取逗号分隔的词表，返回去重、去空后的元组。"""
    raw = os.environ.get(env_name, "")
    terms = []
    for part in raw.split(","):
        part = part.strip()
        if part:
            terms.append(part)
    return tuple(dict.fromkeys(terms))


# ---------------------------------------------------------------------------
# 第一层：硬拦截名单（命中即拒，不论事实性还是立场性措辞）。
# 由部署环境变量 HOTRANK_HARD_BLOCK_TERMS 提供，不硬编码在代码中。
# ---------------------------------------------------------------------------
HARD_BLOCK_TERMS = _load_terms("HOTRANK_HARD_BLOCK_TERMS")

# ---------------------------------------------------------------------------
# 第二层：立场 / 评价意图模式。与 POLITICAL_KEYWORDS 同时命中才拦截。
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

# ---------------------------------------------------------------------------
# 第二层：政治敏感域关键词（宽口径）。与 STANCE_PATTERNS 同时命中才拦截。
# 由部署环境变量 HOTRANK_POLITICAL_KEYWORDS 提供，不硬编码在代码中。
# 事实性提问（无立场意图）不受影响。
# ---------------------------------------------------------------------------
POLITICAL_KEYWORDS = _load_terms("HOTRANK_POLITICAL_KEYWORDS")


@dataclass(frozen=True)
class FilterDecision:
    """过滤结果。``blocked=True`` 表示应拒绝并返回 ``reply``。"""

    blocked: bool
    reason: str = ""
    reply: str = ""
    notice: str = ""


_WS_RE = re.compile(r"\s+")


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


def check_message(content: str) -> FilterDecision:
    """对用户输入做前置内容安全判定。

    返回 ``FilterDecision``：
    - ``blocked=False`` 表示放行，正常进入模型流程；
    - ``blocked=True`` 表示拒绝，调用方应直接返回 ``reply``，不再调用模型。
    """
    text = _normalize(content)
    if not text:
        return FilterDecision(blocked=False)

    if _contains_any(text, HARD_BLOCK_TERMS):
        return _block("hard_block")

    if _contains_any(text, STANCE_PATTERNS) and _contains_any(
        text, POLITICAL_KEYWORDS
    ):
        return _block("stance_politics")

    return FilterDecision(blocked=False)


def check_hard_block(content: str) -> FilterDecision:
    """仅检查硬拦截名单（模型输出侧的离线兜底）。

    输出侧只做硬拦截，不套用「立场词 + 政治词」的组合规则，
    避免误伤模型对热点事实的正常转述。
    """
    text = _normalize(content)
    if not text:
        return FilterDecision(blocked=False)

    if _contains_any(text, HARD_BLOCK_TERMS):
        return _block("hard_block")

    return FilterDecision(blocked=False)
