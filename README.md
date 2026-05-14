# NSPV - New Seller Product Validator

Amazon 新店选品工具 V1。目标是帮助亚马逊美国站新卖家判断一个关键词是否适合新店进入。

## Structure

- `backend/` FastAPI API, scoring engine, persistence
- `frontend/` Next.js UI
- `docker-compose.yml` local PostgreSQL

## Local Development

Backend:

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

The backend uses SQLite by default for quick local runs. Copy the environment templates before using PostgreSQL or a deployed API:

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env.local
```

Set `DATABASE_URL` to use PostgreSQL:

```powershell
$env:DATABASE_URL="postgresql+psycopg://nspv:nspv@localhost:5432/nspv"
```

Supabase is configured as the target hosted database. See `docs/supabase.md` for the migrated schema and connection string format.

See `docs/deployment.md` for the complete environment variable and deployment checklist.
