# Supabase 数据库配置

NSPV V1 schema 已迁移到 Supabase 项目：

```text
https://ntwdxwogqqkxrlauejth.supabase.co
```

## 已创建数据表

`public` schema 中存在以下数据表：

- `users`
- `projects`
- `keywords`
- `products`
- `keyword_product_snapshots`
- `selection_reports`
- `scraper_runs`

通过 Supabase MCP 执行过的历史迁移记录在：

```text
backend/migrations/supabase/001_create_nspv_v1_schema.sql
backend/migrations/supabase/002_add_project_crud_fields.sql
backend/migrations/supabase/003_add_analysis_persistence_fields.sql
backend/migrations/supabase/004_add_scraper_runs.sql
backend/migrations/supabase/005_add_user_auth.sql
```

迁移 `002_add_project_crud_fields.sql` 添加 Project CRUD 字段：

- `projects.target_price_min`
- `projects.target_price_max`
- `projects.status`

迁移 `003_add_analysis_persistence_fields.sql` 添加报告持久化字段：

- `selection_reports.input_payload`
- `selection_reports.scoring_version`
- `selection_reports.analysis_status`
- `selection_reports.error_message`

迁移 `004_add_scraper_runs.sql` 添加抓取执行日志：

- `scraper_runs`
- `selection_reports.scraper_run_id`

迁移 `005_add_user_auth.sql` 添加用户认证存储：

- `users.password_hash`

新的 schema 变更应使用 Alembic：

```powershell
cd backend
.\.venv\Scripts\alembic upgrade head
```

对于已执行过 SQL 迁移的现有 Supabase 数据库，在后续 Alembic 迁移前先运行一次：

```powershell
cd backend
.\.venv\Scripts\alembic stamp head
```

## 后端连接

FastAPI 后端使用 SQLAlchemy，并读取 `DATABASE_URL`。

在本地创建 `backend/.env`，填入 Supabase 连接串。

大多数本地网络推荐使用：

```text
Project Settings > Database > Connection string > Session pooler
```

使用以下格式：

```env
DATABASE_URL=postgresql+psycopg://postgres.ntwdxwogqqkxrlauejth:[URL_ENCODED_DB_PASSWORD]@[POOLER_HOST]:5432/postgres
FRONTEND_ORIGIN=http://localhost:3000
```

直连格式：

```env
DATABASE_URL=postgresql+psycopg://postgres:[URL_ENCODED_DB_PASSWORD]@db.ntwdxwogqqkxrlauejth.supabase.co:5432/postgres
FRONTEND_ORIGIN=http://localhost:3000
```

仅当本地网络支持 IPv6 时使用直连。在当前环境中，直连 host 只解析到 IPv6 地址，因此 pooler 连接串是更稳妥的本地开发默认选择。

将 `[URL_ENCODED_DB_PASSWORD]` 替换为 Supabase 数据库密码：

```text
Project Settings > Database > Database Password / Connection string
```

如果密码包含 `/`、`?`、`#`、`@`、`:` 等 URL 特殊字符，写入 `DATABASE_URL` 前需要先进行 URL 编码。

不要提交 `backend/.env`。

## 安全说明

所有 NSPV 数据表均已启用 RLS。

当前 V1 访问模型：

- FastAPI 后端通过 `DATABASE_URL` 直连 Postgres。
- 前端不直接访问 Supabase 数据表。
- 当前尚未定义公开 RLS policy。

Supabase 可能显示 INFO 级 advisor 提示：

```text
RLS Enabled No Policy
```

这符合当前仅后端访问的模型。后续如果引入用户认证和 Supabase 客户端直连，需要先添加明确的 RLS policy，再向 anon 或 authenticated client 暴露数据表。
