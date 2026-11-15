# Virgo PostgreSQL handoff

## PostgreSQL migration changes

The backend is configured for PostgreSQL using SQLAlchemy and psycopg 3. PostgreSQL URLs beginning with `postgres://` or `postgresql://` are normalized to the psycopg 3 SQLAlchemy driver. The Virgo-specific settings in `config.py` (Firebase defaults, service-area configuration, storage settings, and production validation) are preserved.

Model timestamps now default to timezone-aware UTC values. Model metadata includes the active-ride partial unique indexes already defined by Virgo's migration history and keeps the admin email index consistent with its migration. Existing Virgo business fields and later schema migrations are retained.

## Configure a developer database

Create `backend/.env` from `backend/.env.example` and fill in a PostgreSQL/Supabase `DATABASE_URL`, a private random `JWT_SECRET_KEY`, and the provider keys required by your environment. Never commit the real `.env`, service-account JSON, access tokens, or database password. Do not place database credentials in a mobile or web frontend.

From `backend`, inspect and apply the existing full Virgo migration chain to the intended PostgreSQL database:

```powershell
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

This repository contains later Virgo migrations beyond the original CabSure branch. Review them and confirm the destination database is the intended Virgo database before applying them. The local SQLite database file is not part of PostgreSQL migrations; no SQLite records are copied automatically.

For production, set `ENVIRONMENT=production` and `AUTO_MIGRATE=false`; deploy migrations as a separate controlled step before starting the API.

## Running and checking

Start the backend from `backend` after configuring `.env` and applying migrations:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/docs` for API calls and `http://localhost:8000/health` for an API health response. Confirm database persistence by creating a development test account or other test record through the API, then reading it from Supabase SQL Editor. Frontends call FastAPI; only the backend connects to PostgreSQL.

SQLite references in engine setup and migration predicates are retained for isolated SQLite tests and cross-dialect migration support. They do not make SQLite the configured runtime database. Ignore and do not commit local `*.db` files.
