# Supabase Database Setup

NSPV V1 schema has been migrated to the Supabase project:

```text
https://ntwdxwogqqkxrlauejth.supabase.co
```

## Created Tables

The following tables exist in the `public` schema:

- `users`
- `projects`
- `keywords`
- `products`
- `keyword_product_snapshots`
- `selection_reports`

The migration applied through Supabase MCP is tracked in:

```text
backend/migrations/supabase/001_create_nspv_v1_schema.sql
```

## Backend Connection

The FastAPI backend uses SQLAlchemy and reads `DATABASE_URL`.

Create `backend/.env` locally with:

```env
DATABASE_URL=postgresql+psycopg://postgres:[DB_PASSWORD]@db.ntwdxwogqqkxrlauejth.supabase.co:5432/postgres
FRONTEND_ORIGIN=http://localhost:3000
```

Replace `[DB_PASSWORD]` with the database password from Supabase:

```text
Project Settings > Database > Database Password / Connection string
```

Do not commit `backend/.env`.

## Security Notes

RLS is enabled on all NSPV tables.

Current V1 access model:

- FastAPI backend connects directly to Postgres using `DATABASE_URL`.
- Frontend does not access Supabase tables directly.
- No public RLS policies are defined yet.

Supabase may show an INFO advisor warning:

```text
RLS Enabled No Policy
```

This is expected for the current backend-only access model. When user auth and direct Supabase client access are introduced, add explicit RLS policies before exposing tables to anon or authenticated clients.

