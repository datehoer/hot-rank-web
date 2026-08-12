# pgvector 安装与初始化

Agent 向量检索同时依赖两部分：

1. FastAPI 镜像中的 Python `pgvector` 客户端包；
2. PostgreSQL 服务器中的 `vector` extension。

只安装 Python 包不足以执行 `embedding <=> query_vector`
等 SQL。

## 1. Python 依赖

项目当前使用 `python:3.12-slim`，并锁定：

```text
pgvector==0.5.0
```

`pgvector` 0.5.0 需要 Python 3.10 或更高，Python 3.12 满足该
要求。Python 客户端包版本与 PostgreSQL 服务端 extension 版本
独立管理。

## 2. PostgreSQL 服务器扩展

先确认 PostgreSQL 主版本：

```sql
SHOW server_version;
```

### Ubuntu / Debian

使用 PostgreSQL 官方 APT 仓库时，安装与数据库主版本一致的
包。例如 PostgreSQL 16：

```bash
sudo apt install postgresql-16-pgvector
```

PostgreSQL 15 则将 `16` 替换为 `15`。

### Docker

如果 PostgreSQL 本身由 Docker 管理，使用对应主版本的官方
pgvector 镜像，例如：

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
```

替换已有 PostgreSQL 镜像前必须确认数据目录、主版本和备份，
不能用不同 PostgreSQL 主版本直接打开原数据目录。

## 3. 在目标数据库启用 extension

安装服务器扩展文件后，对应用实际使用的每个数据库执行：

```bash
psql -h <pg-host> -U <admin-user> -d <database> \
  -f migrations/001_enable_pgvector.sql
```

或手动执行：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

这一步通常需要 PostgreSQL 管理员权限。应用运行账号不建议
长期持有创建 extension 的权限。

## 4. 验证

```sql
SELECT extname, extversion
FROM pg_extension
WHERE extname = 'vector';
```

预期返回一行 `vector` 及其版本。

再验证类型：

```sql
SELECT '[1,2,3]'::vector;
```

## 5. 部署顺序

1. 备份数据库；
2. 安装与 PostgreSQL 主版本一致的 pgvector 服务器扩展；
3. 对 HotDay 使用的数据库执行 migration；
4. 用 SQL 验证 extension；
5. 再构建并启动 FastAPI 镜像；
6. 检查应用日志中没有 `vector type not found` 或 codec 注册错误。

## 6. 注意

- Python `pgvector` 包和 PostgreSQL 服务器 extension 是独立版本；
- `CREATE EXTENSION` 需要对每个目标 database 执行；
- 本 migration 只启用 extension，不会创建 `hot_topic`、
  `embedding` 列或向量索引；
- `hot_topic` 表及索引仍需要单独的数据模型 migration。
