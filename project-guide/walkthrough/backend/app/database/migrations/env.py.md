# backend/app/database/migrations/env.py

## 1. Purpose
**Alembic** is a tool that changes your database layout step by step, using small scripts called **migrations** (*Example:* "add column X to table Y"). Alembic runs this `env.py` every time you run an `alembic` command. It tells Alembic which database to use and which tables the code expects. The migration scripts are in the `versions/` folder next to it.

## 2. Imports, one by one
**Third-party**
- `from alembic import context` (`env.py:1`). `context` is Alembic's live handle for the current run. *Example:* `context.is_offline_mode()` says whether `--sql` was used.
- `from sqlalchemy import engine_from_config, pool` (`:2`). **SQLAlchemy** is the database library. `engine_from_config` builds a database **engine** (the object that holds the connection settings) from a settings dict. `pool` has connection pool types. *Example:* `pool.NullPool` means "do not keep connections open".

**Project**
- `from app.core.config import get_settings` (`:4`): from `backend/app/core/config.py`. Gives `database_url`.
- `from app.db import Base` (`:5`): from `backend/app/db.py`. `Base` is the parent class of all model classes; it collects their table info in `Base.metadata`.
- `import app.models  # noqa: F401` (`:6`). Imported only for its side effect: importing it loads every model class so they register on `Base.metadata`. `# noqa: F401` tells the linter "yes, it looks unused, ignore it". Without this line, autogenerate would think there are no tables.

## 3. Walk through the code, top to bottom
- `config = context.config` (`:8`): the settings read from `alembic.ini`.
- `config.set_main_option('sqlalchemy.url', get_settings().database_url)` (`:9`): puts the real database URL into Alembic, so the URL lives only in `.env`/settings and not in `alembic.ini`.
- `target_metadata = Base.metadata` (`:11`): the "what tables should exist" list used by `--autogenerate` to compare against the real database.
- `run_migrations_offline()` (`:14-17`): **offline mode** does not connect. It prints SQL text. `context.configure(url=..., literal_binds=True, dialect_opts={'paramstyle': 'named'}, compare_type=True)` sets it up. `literal_binds=True` writes real values into the SQL. `compare_type=True` makes autogenerate notice column type changes. `context.begin_transaction()` and `context.run_migrations()` run the scripts.
- `run_migrations_online()` (`:20-25`): **online mode** really connects. `engine_from_config(config.get_section(...), prefix='sqlalchemy.', poolclass=pool.NullPool)` builds the engine. `connectable.connect()` opens a connection in a `with` block (closed after). The rest is the same: configure, begin transaction, run.
- `if context.is_offline_mode(): ... else: ...` (`:28-31`): picks the mode. This runs at import, which is how Alembic works.

## 4. How data flows
```
zsh: alembic upgrade head
  -> alembic reads alembic.ini -> runs env.py
  env.py: settings.database_url -> engine -> connection
  context.run_migrations() -> runs versions/*.py upgrade() in order
  -> database tables change; table alembic_version stores the last revision id
```

## 5. Try it
Run from the folder that holds `alembic.ini` (probably `backend/`; check with `fd alembic.ini`):
```zsh
uv run alembic current
uv run alembic upgrade head
uv run alembic upgrade head --sql
```
`current` shows the revision the database is on. `upgrade head` applies all new migrations. `--sql` uses offline mode and only prints SQL. Expected: lines like `Running upgrade e4ffba93f4c4 -> 28bc77a50115`.

## 6. Can it be better?
- Good: URL comes from settings; models are loaded; `compare_type` is on.
- Weak: no `compare_server_default=True`, so default changes are missed. No `render_as_batch` (only needed for SQLite). Runs at import time, normal for Alembic.
- Cleaner way: add `compare_server_default=True` to both `configure` calls. (Opinion.)
- Security: the database URL may hold a password. It is read from settings and never printed here. Do not use `literal_binds` output with secrets in shared logs.

## 7. Check yourself
1. Why does line 6 import `app.models` if the name is never used?
2. What is the difference between offline and online mode?
