# backend/tests/test_database_schema.py

## 1. Purpose
One test that proves the database models create all the key tables. It builds an in-memory SQLite database, creates every table from the models, and checks that ten expected table names exist. It protects against forgetting to register a model. Models live in `backend/app/models/`; `Base` lives in `backend/app/db`.

## 2. Imports, one by one
Third party:
- `from sqlalchemy import create_engine, inspect` : SQLAlchemy is the ORM library. `create_engine(url)` makes the connection object (*Example:* `create_engine('sqlite://')`). `inspect(engine)` lets you read the real database structure (*Example:* `.get_table_names()`).

Project:
- `from app.db import Base` : `Base` is the parent class of all models. It keeps a list of every model's table in `Base.metadata`.
- `import app.models  # noqa: F401` : importing the package runs its files, which defines every model class and so registers it on `Base.metadata`. `# noqa: F401` tells ruff "I know this import looks unused, keep it". Without this import, `create_all` would create nothing.

## 3. Walk through the code, top to bottom
`test_core_ride_hailing_schema_is_connected` (`:7-12`)
- `create_engine('sqlite://')` : an SQLite database held only in memory. It disappears when the test ends (fast, no file, no PostgreSQL needed).
- `Base.metadata.create_all(engine)` : runs `CREATE TABLE` for every registered model.
- `inspect(engine).get_table_names()` : returns a list like `['audit_logs', 'drivers', ...]`. `set(...)` turns it into a set for easy comparing.
- `{...10 names...} <= tables` : the `<=` between sets means "is a subset of". It passes if all ten names are present, and extra tables are fine. Names: passengers, passenger_profiles, drivers, vehicles, rides, fare_quotes, payments, device_sessions, audit_logs, outbox_events.

## 4. How data flows
```
test -> import app.models (registers classes on Base.metadata)
     -> create_all(sqlite memory engine) -> tables exist
     -> inspect -> names set -> subset check -> pass/fail
```

## 5. Try it
```zsh
cd backend && uv run pytest tests/test_database_schema.py -v
```
Expected: `1 passed`.

## 6. Can it be better?
- Good: very cheap, catches missing model imports.
- Weak: only checks table names, not columns, foreign keys, or indexes. SQLite is looser than PostgreSQL, so a PostgreSQL-only problem (types, constraints) will not show. It does not check that Alembic migrations match the models. The single long line (`:12`) is hard to read.
- Cleaner way (opinion): split the names into a constant list, and add a test that runs `alembic upgrade head` on a test PostgreSQL.
- Security: none.

## 7. Check yourself
1. Why must the test import `app.models` even though it never uses it?
2. What does `a <= b` mean for two Python sets?
