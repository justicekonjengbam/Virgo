# backend/app/database/migrations/versions/841c1f195299_add_static_location_catalog.py

## 1. Purpose
This **migration** (a script that moves the database from one layout to the next) creates a new table, `location_catalog`. It stores a fixed list of known places with names, addresses and coordinates. The map service can search it instead of calling an outside map provider. It was generated on 2026-07-30 (`:5`), right after `28bc77a50115`.

## 2. Imports, one by one
**Standard library**
- `from typing import Sequence, Union` (`:7`). Type-hint helpers for the id variables.

**Third-party**
- `from alembic import op` (`:9`). Alembic's schema command toolbox. *Example:* `op.create_table(...)`.
- `import sqlalchemy as sa` (`:10`). Column types and constraints. *Example:* `sa.Numeric(9, 6)` is an exact decimal number.

## 3. Walk through the code, top to bottom
- `revision = '841c1f195299'` (`:13`); `down_revision = '28bc77a50115'` (`:14`). It runs after the home-category migration. `branch_labels` and `depends_on` are `None` (`:15-16`).
- `upgrade()` (`:19-32`) calls `op.create_table('location_catalog', ...)` (`:21-31`), which runs `CREATE TABLE`:
  - `id` Integer, not null (`:22`), made the primary key by `sa.PrimaryKeyConstraint('id')` (`:29`). A **primary key** is the unique id of each row.
  - `name` String(160) (`:23`) and `sa.UniqueConstraint('name')` (`:30`). **Unique** means no two rows can share a name.
  - `formatted_address` String(512) (`:24`).
  - `latitude`, `longitude` `Numeric(precision=9, scale=6)` (`:25-26`). 9 digits in total, 6 after the point, like `-123.456789`. Six decimals is about 10 cm accuracy. Exact decimals avoid float rounding.
  - `created_at`, `updated_at` `DateTime(timezone=True)`, not null (`:27-28`). Stored with timezone.
- `downgrade()` (`:35-37`): `op.drop_table('location_catalog')` deletes the table and all its data.

Errors: the upgrade fails if the table already exists. `created_at` and `updated_at` are NOT NULL with no database default here, so the model code must fill them (the model file likely does; check `app/models`).

## 4. How data flows
```
alembic upgrade head -> 28bc77a50115 done -> this upgrade()
  CREATE TABLE location_catalog (...)
  alembic_version := '841c1f195299'
```

## 5. Try it
```zsh
uv run alembic upgrade head --sql
uv run alembic downgrade -1
```
First prints the SQL for pending migrations. `downgrade -1` goes back one step and runs `downgrade()`, which deletes this table, so use only on a dev database. Expected: a `CREATE TABLE location_catalog` statement.

## 6. Can it be better?
- Good: exact decimals for coordinates, unique name, timezone-aware times.
- Weak: unique `name` alone means two places with the same name in different cities collide. No index on `name` for search beyond the unique index. Generated comments remain.
- Cleaner way: make the unique key `(name, formatted_address)` and add a `server_default=sa.func.now()` for the times. (Opinion.)
- Security: no secrets. `downgrade` destroys data, so do not run it in production.

## 7. Check yourself
1. What does `Numeric(precision=9, scale=6)` allow?
2. What is lost when `downgrade()` runs?
