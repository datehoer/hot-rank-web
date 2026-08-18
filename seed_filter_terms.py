#!/usr/bin/env python3
"""把 .env 里的敏感词表一次性灌入 Redis，供 content_filter 优先读取。

content_filter 的读取顺序已经是：Redis（主源）→ env（兜底）。
本脚本把 .env 中的词表写入 Redis 的
    agent:filter:hard_terms / agent:filter:political_terms（JSON 字符串数组），
写完后运营即可改 Redis 生效，无需再改 .env 重启。

用法（在项目根目录运行）：
    python seed_filter_terms.py
"""

from __future__ import annotations

import asyncio
import json
import os

from dotenv import load_dotenv

# 必须先加载 .env 再 import content_filter：它在 import 时读取环境变量。
load_dotenv()

from config import REDIS_DB, REDIS_HOST, REDIS_PORT  # noqa: E402
from hotrank.agent.content_filter import (  # noqa: E402
    HARD_BLOCK_ENV,
    POLITICAL_ENV,
    REDIS_HARD_KEY,
    REDIS_POLITICAL_KEY,
)
from hotrank.cache import redis_cache  # noqa: E402


def _load_terms(env_name: str) -> list[str]:
    raw = os.environ.get(env_name, "")
    return list(dict.fromkeys(t.strip() for t in raw.split(",") if t.strip()))


async def main() -> None:
    hard = _load_terms(HARD_BLOCK_ENV)
    political = _load_terms(POLITICAL_ENV)

    print(f"target Redis: {REDIS_HOST}:{REDIS_PORT} db={REDIS_DB}")
    print(f"{REDIS_HARD_KEY}: {len(hard)} terms")
    print(f"{REDIS_POLITICAL_KEY}: {len(political)} terms")

    if not hard and not political:
        print("!! 两个词表都为空，未写入。请检查 .env 中的 HOTRANK_* 变量。")
        return

    await redis_cache.set(REDIS_HARD_KEY, json.dumps(hard, ensure_ascii=False))
    await redis_cache.set(
        REDIS_POLITICAL_KEY, json.dumps(political, ensure_ascii=False)
    )

    got_hard = json.loads(await redis_cache.get(REDIS_HARD_KEY) or "[]")
    got_political = json.loads(await redis_cache.get(REDIS_POLITICAL_KEY) or "[]")
    print(f"写入完成并读回校验通过：hard={len(got_hard)} political={len(got_political)}")


if __name__ == "__main__":
    asyncio.run(main())
