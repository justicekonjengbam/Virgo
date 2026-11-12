# e3f8a2b60001_add_admin_operations_schema.py

## 1. Purpose
This **migration** (a script that changes the database layout one step at a time) creates the `admin_users` table for the admin app. It also adds three columns to `support_tickets` so an admin can be assigned and a ticket can be resolved. It is written to be safe to run twice. Alembic runs it. It calls no project file.

## 2. Imports, one by one
- `from alembic import op` (`e3f8a2b60001_add_admin_operations_schema.py:7`). Alembic's action set. *Example:* `op.create_table(...)`. `op.get_bind()` gives the live database connection.
- `import sqlalchemy as sa` (`:8`). Describes columns, and `sa.inspect(...)` reads the real database. *Example:* `sa.inspect(conn).get_table_names()` returns `['drivers', ...]`.

## 3. Walk through the code, top to bottom
- `revision = 'e3f8a2b60001'`, `down_revision = 'd2f7e1a50001'` (`:11-12`). Chain position.
- `upgrade()` (`:17`):
  - Comment (`:18-19`): two dev reload processes may both run the migration, so each step checks first.
  - `inspector = sa.inspect(op.get_bind())` (`:20`). An **inspector** reads what already exists in the database (tables, columns, indexes).
  - `if 'admin_users' not in inspector.get_table_names():` (`:21`) creates the table only if missing.
  - `op.create_table('admin_users', ...)` (`:22-33`) columns: `id` primary key (unique row number); `email` up to 320 chars, required, unique; `full_name`; `password_hash` (a one-way scramble of the password, never the password itself); `role` default `'operations_admin'`; `is_active` default true (`sa.true()`); `last_login_at` optional; `created_at` and `updated_at` required.
  - Second inspector (`:34`) refreshes the view after the create.
  - `ix_admin_users_email` index (`:35-36`). An **index** is a lookup shortcut, like a book index. Created only if absent. *Example:* finding an admin by email becomes fast.
  - `support_columns = {...}` (`:37`) is a set of existing column names of `support_tickets`.
  - Three `if ... not in support_columns` blocks add `assigned_admin_id` (a foreign key to `admin_users.id`, `ondelete='SET NULL'` means: if the admin is deleted, set it to empty), `resolution_note` (text), and `resolved_at` (time) (`:38-43`).
- `downgrade()` (`:46-51`) reverses: drops the three columns, the index, then the table. Order matters: the foreign key column goes before the table it points to.

Note: the downgrade has no existence checks, so it fails if something is already gone.

## 4. How data flows
```
alembic upgrade head
  -> inspector looks at DB
  -> admin_users missing? create table
  -> index missing? create index
  -> each support_tickets column missing? add it
  -> alembic_version = e3f8a2b60001
```

## 5. Try it
```zsh
cd backend
uv run alembic upgrade e3f8a2b60001
uv run alembic upgrade e3f8a2b60001   # run twice: second time should still be fine
```
Not run by me. Note that alembic itself skips an already applied revision; the inner checks matter only when a half-finished run left changes behind.

## 6. Can it be better?
- Good: retry-safe, clear comment about why, indexes and foreign keys defined.
- Weak: `unique=True` on `email` already makes the database create a unique index, so `ix_admin_users_email` is a second, duplicate index. `role` is free text with no check constraint. On SQLite, `op.add_column` with a foreign key can be limited (SQLite cannot add constraints to existing tables this way). The retry logic is a workaround; running migrations from one place only is cleaner.
- Cleaner way (opinion): run `alembic upgrade head` once in a start script instead of on app reload, then drop the inspector checks.
- Security: stores only `password_hash`; good. The default role name is fine, but make sure the first admin is not created with a known password (see the seed code).

## 7. Check yourself
1. Why does this file inspect the database before every change?
2. What happens to a ticket's `assigned_admin_id` when the admin row is deleted?
