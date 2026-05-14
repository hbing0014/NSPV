# 部署与环境变量

本文档记录 NSPV V1 在本地和托管环境运行所需的环境变量。

## 后端

运行时：

- FastAPI
- SQLAlchemy
- 生产环境使用 PostgreSQL
- 本地快速运行仍支持 SQLite

环境文件：

```text
backend/.env
```

使用 `backend/.env.example` 作为模板。

后端必需环境变量：

| 变量 | 示例 | 说明 |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://...` | PostgreSQL 连接串。大多数本地 IPv4 网络建议使用 Supabase Session Pooler。 |
| `FRONTEND_ORIGIN` | `http://localhost:3000` | CORS 允许的浏览器来源。生产环境设置为已部署的前端域名。 |
| `SCRAPER_PROVIDER` | `mock` | 可选值：`mock`、`playwright`、`brightdata`。V1 已实现 `mock` 和 `playwright`。 |
| `JWT_SECRET_KEY` | `replace-with-a-long-random-secret` | 非本地环境必须修改。请使用足够长的随机密钥。 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | 访问令牌有效期，单位为分钟。 |

本地启动后端：

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

生产后端启动命令：

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 前端

运行时：

- Next.js
- 浏览器通过 `NEXT_PUBLIC_API_BASE` 调用 FastAPI 后端。

环境文件：

```text
frontend/.env.local
```

使用 `frontend/.env.example` 作为模板。

前端必需环境变量：

| 变量 | 示例 | 说明 |
| --- | --- | --- |
| `NEXT_PUBLIC_API_BASE` | `http://127.0.0.1:8000` | FastAPI 基础 URL。生产环境设置为已部署的后端地址。 |

本地启动前端：

```powershell
cd frontend
npm install
npm run dev
```

生产前端：

- 部署到 Vercel 或其他 Next.js 托管平台。
- 在托管平台环境变量中设置 `NEXT_PUBLIC_API_BASE`。
- 将后端 `FRONTEND_ORIGIN` 设置为已部署前端来源。

## 数据库

V1 目标数据库：

- Supabase PostgreSQL

推荐的 Supabase 连接方式：

```text
Project Settings > Database > Connection string > Session pooler
```

SQLAlchemy URL 格式：

```env
DATABASE_URL=postgresql+psycopg://postgres.<project-ref>:[URL_ENCODED_DB_PASSWORD]@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres
```

仅在网络支持 IPv6 时使用 Supabase 直连地址：

```env
DATABASE_URL=postgresql+psycopg://postgres:[URL_ENCODED_DB_PASSWORD]@db.<project-ref>.supabase.co:5432/postgres
```

Alembic 是应用 schema 变更的迁移入口。

新空数据库：

```powershell
cd backend
.\.venv\Scripts\alembic upgrade head
```

对于已经通过 `backend/migrations/supabase/*.sql` 创建的现有 Supabase 数据库，只需标记一次当前版本：

```powershell
cd backend
.\.venv\Scripts\alembic stamp head
```

Alembic 迁移文件位于：

```text
backend/alembic/versions/
```

早期 Supabase SQL 迁移文件保留在以下目录作为参考：

```text
backend/migrations/supabase/
```

## 部署检查清单

1. 创建或更新 Supabase 数据库。
2. 新数据库在 `backend/` 下运行 `alembic upgrade head`。
3. 现有已手工迁移的 Supabase 数据库只运行一次 `alembic stamp head`。
4. 配置后端环境变量。
5. 部署 FastAPI 后端。
6. 配置前端 `NEXT_PUBLIC_API_BASE`。
7. 部署 Next.js 前端。
8. 将后端 `FRONTEND_ORIGIN` 设置为前端来源。
9. 验证 `GET /health`。
10. 从前端执行一次冒烟分析。

## 安全说明

- 不要提交 `.env` 或 `.env.local`。
- 如果 `JWT_SECRET_KEY` 泄露，需要立即轮换。
- 不要把 Supabase 数据库凭据暴露给前端。
- 当前 V1 前端只与 FastAPI 通信，Supabase 仅由后端访问。
