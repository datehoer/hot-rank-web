"""本地 PostgreSQL 拦截日志。

用途：把「被内容安全拦截」的数据（文本 + 原因 + 审核标签）落到本地 PG，
供运营方后续分析、自建拦截规则，逐步减少对第三方审核（如阿里绿网）的依赖。

隐私边界：不存 session ID、原始 IP、来源 URL、完整消息历史；只存被拦截的
文本本身（自建过滤器所需）+ 拦截原因 / 审核标签。写入失败只记日志，绝不影响主流程。

表结构见同目录 ``block_log_schema.sql``（用写库账号 admin 执行一次建表 + 授权，
只读账号 hotrank_readonly 仅被授予该表的 INSERT 与序列 USAGE 权限）。
"""

from __future__ import annotations

import json
import logging

logger = logging.getLogger(__name__)

_INSERT_SQL = """
INSERT INTO agent_block_log
    (stage, source, reason, suggestion, labels, content, platform)
VALUES ($1, $2, $3, $4, $5::jsonb, $6, $7::jsonb)
"""


async def record_block(
    pg_pool,
    *,
    stage: str,
    source: str,
    reason: str,
    suggestion: str | None = None,
    labels: list | None = None,
    content: str | None = None,
    platform: list | None = None,
) -> None:
    """记录一条被拦截的内容。尽力而为，永不抛出异常。"""
    if pg_pool is None:
        return
    try:
        async with pg_pool.acquire() as conn:
            async with conn.transaction():
                # 连接默认是只读事务，此处临时切换为读写，仅对本事务生效。
                await conn.execute("SET TRANSACTION READ WRITE")
                await conn.execute(
                    _INSERT_SQL,
                    stage,
                    source,
                    reason,
                    suggestion,
                    (
                        json.dumps(labels, ensure_ascii=False)
                        if labels is not None
                        else None
                    ),
                    content,
                    (
                        json.dumps(platform, ensure_ascii=False)
                        if platform is not None
                        else None
                    ),
                )
    except Exception:  # noqa: BLE001 - 落库失败不影响主流程
        logger.exception("failed to record agent block log")
