# Deployment and Environment

This document records the V1 environment variables required to run NSPV locally and in hosted environments.

## Backend

Runtime:

- FastAPI
- SQLAlchemy
- PostgreSQL in production
- SQLite is still supported for quick local runs

Environment file:

```text
backend/.env
```

Use `backend/.env.example` as the template.

Required backend variables:

| Variable | Example | Notes |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://...` | PostgreSQL connection string. Use Supabase Session Pooler for most local IPv4 networks. |
| `FRONTEND_ORIGIN` | `http://localhost:3000` | Allowed browser origin for CORS. Set to the deployed Vercel URL in production. |
| `SCRAPER_PROVIDER` | `mock` | Supported values: `mock`, `playwright`, `brightdata`. Only `mock` and `playwright` are implemented in V1. |
| `JWT_SECRET_KEY` | `replace-with-a-long-random-secret` | Must be changed outside local development. Use a long random secret. |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Access token lifetime in minutes. |

Local backend start:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Production backend command:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Frontend

Runtime:

- Next.js
- Browser calls the FastAPI backend through `NEXT_PUBLIC_API_BASE`

Environment file:

```text
frontend/.env.local
```

Use `frontend/.env.example` as the template.

Required frontend variables:

| Variable | Example | Notes |
| --- | --- | --- |
| `NEXT_PUBLIC_API_BASE` | `http://127.0.0.1:8000` | FastAPI base URL. For production, set this to the deployed backend URL. |

Local frontend start:

```powershell
cd frontend
npm install
npm run dev
```

Production frontend:

- Deploy to Vercel or another Next.js host.
- Set `NEXT_PUBLIC_API_BASE` in the host environment settings.
- Set backend `FRONTEND_ORIGIN` to the deployed frontend origin.

## Database

V1 target database:

- Supabase PostgreSQL

Recommended Supabase connection:

```text
Project Settings > Database > Connection string > Session pooler
```

SQLAlchemy URL format:

```env
DATABASE_URL=postgresql+psycopg://postgres.<project-ref>:[URL_ENCODED_DB_PASSWORD]@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres
```

Use the direct Supabase connection only when the network supports IPv6:

```env
DATABASE_URL=postgresql+psycopg://postgres:[URL_ENCODED_DB_PASSWORD]@db.<project-ref>.supabase.co:5432/postgres
```

Applied migration files are tracked under:

```text
backend/migrations/supabase/
```

Until Alembic is introduced in Task 6.2, production database changes are applied from these SQL files.

## Deployment Checklist

1. Create or update the Supabase database.
2. Apply all SQL files under `backend/migrations/supabase/` in order.
3. Configure backend environment variables.
4. Deploy the FastAPI backend.
5. Configure frontend `NEXT_PUBLIC_API_BASE`.
6. Deploy the Next.js frontend.
7. Set backend `FRONTEND_ORIGIN` to the frontend origin.
8. Verify `GET /health`.
9. Run a smoke analysis from the frontend.

## Security Notes

- Never commit `.env` or `.env.local`.
- Rotate `JWT_SECRET_KEY` if it is exposed.
- Do not expose Supabase database credentials to the frontend.
- Current V1 frontend talks only to FastAPI; Supabase remains backend-only.
