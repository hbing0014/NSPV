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
- `scraper_runs`

The migrations applied through Supabase MCP are tracked in:

```text
backend/migrations/supabase/001_create_nspv_v1_schema.sql
backend/migrations/supabase/002_add_project_crud_fields.sql
backend/migrations/supabase/003_add_analysis_persistence_fields.sql
backend/migrations/supabase/004_add_scraper_runs.sql
backend/migrations/supabase/005_add_user_auth.sql
```

Migration `002_add_project_crud_fields.sql` adds the Project CRUD fields:

- `projects.target_price_min`
- `projects.target_price_max`
- `projects.status`

Migration `003_add_analysis_persistence_fields.sql` adds the report persistence fields:

- `selection_reports.input_payload`
- `selection_reports.scoring_version`
- `selection_reports.analysis_status`
- `selection_reports.error_message`

Migration `004_add_scraper_runs.sql` adds scraper execution logging:

- `scraper_runs`
- `selection_reports.scraper_run_id`

Migration `005_add_user_auth.sql` adds user authentication storage:

- `users.password_hash`

## Backend Connection

The FastAPI backend uses SQLAlchemy and reads `DATABASE_URL`.

Create `backend/.env` locally with the connection string from Supabase.

Recommended for most local networks:

```text
Project Settings > Database > Connection string > Session pooler
```

Use this format:

```env
DATABASE_URL=postgresql+psycopg://postgres.ntwdxwogqqkxrlauejth:[URL_ENCODED_DB_PASSWORD]@[POOLER_HOST]:5432/postgres
FRONTEND_ORIGIN=http://localhost:3000
```

Direct connection format:

```env
DATABASE_URL=postgresql+psycopg://postgres:[URL_ENCODED_DB_PASSWORD]@db.ntwdxwogqqkxrlauejth.supabase.co:5432/postgres
FRONTEND_ORIGIN=http://localhost:3000
```

Use direct connection only if your local network supports IPv6. In this environment, the direct host resolves only to an IPv6 address, so the pooler connection string is the safer local development default.

Replace `[URL_ENCODED_DB_PASSWORD]` with the database password from Supabase:

```text
Project Settings > Database > Database Password / Connection string
```

If the password contains special URL characters such as `/`, `?`, `#`, `@`, or `:`, URL-encode it before placing it in `DATABASE_URL`.

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
