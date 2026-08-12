-- pgvector must be installed on the PostgreSQL server before this migration
-- is executed. Run this once for every database used by hot-rank-web.

CREATE EXTENSION IF NOT EXISTS vector;

SELECT extname, extversion
FROM pg_extension
WHERE extname = 'vector';
