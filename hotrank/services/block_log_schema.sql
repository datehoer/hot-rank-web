-- 一次性建表 + 授权（用写库账号 admin 执行）。
-- 只读账号 hotrank_readonly 仅被授予该表的 INSERT 和序列 USAGE/SELECT，
-- 其余表保持只读。

CREATE TABLE IF NOT EXISTS agent_block_log (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    stage TEXT NOT NULL,
    source TEXT NOT NULL,
    reason TEXT NOT NULL,
    suggestion TEXT,
    labels JSONB,
    content TEXT,
    platform JSONB
);

CREATE INDEX IF NOT EXISTS agent_block_log_created_at_idx
    ON agent_block_log (created_at);

GRANT INSERT ON agent_block_log TO hotrank_readonly;
GRANT USAGE, SELECT ON SEQUENCE agent_block_log_id_seq TO hotrank_readonly;
