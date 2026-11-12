# h6c1e5f90001_harden_admin_accounts.py

## 1. Purpose
This **migration** (a script that changes the database layout one step at a time) adds four security columns to `admin_users`: a token version, a failed-login counter, a lock time, and a password-change time. They support safer admin login (lockout after many wrong passwords, and the ability to cancel old login tokens). Alembic runs it. The admin login code in `backend/app/` reads these columns.

## 2. Imports, one by one
- `from alembic import op` (`h6c1e5f90001_harden_admin_accounts.py:7`). Alembic actions; `op.get_bind()` gives the database connection, `op.add_column` adds a column.
- `import sqlalchemy as sa` (`:8`). Column types, and `sa.inspect(...)` to read the real database. *Example:* `sa.inspect(conn).get_columns('t')` returns a list of column info.

## 3. Walk through the code, top to bottom
- `revision = 'h6c1e5f90001'`, `down_revision = 'g5b0d4e80001'` (`:10-11`).
- `upgrade()` (`:16`):
  - `inspector = sa.inspect(op.get_bind())` (`:17`) reads what exists now.
  - `columns = {column['name'] for column in inspector.get_columns('admin_users')}` (`:18`) is a set of current column names.
  - Four guarded adds (`:19-26`), each only if missing:
    - `token_version` Integer, required, default `'1'`. A **token version** is a number stored in the account and copied into the login token (JWT, a signed login pass). Raising the number makes all older tokens invalid, so you can force logout.
    - `failed_login_attempts` Integer, required, default `'0'`. Counts wrong passwords.
    - `locked_until` optional time. While now is before it, login is refused.
    - `password_changed_at` optional time.
  Defaults are strings (`'1'`, `'0'`) because `server_default` is sent as SQL text.
- `downgrade()` (`:29-33`) drops the four columns.

## 4. How data flows
```
admin logs in with wrong password
  -> app increments failed_login_attempts; at limit sets locked_until
admin logs out everywhere / changes password
  -> app increments token_version -> old tokens no longer match
```
This file only creates the columns; the logic lives in the admin auth code.

## 5. Try it
```zsh
cd backend
uv run alembic upgrade h6c1e5f90001
```
Expected: `Running upgrade g5b0d4e80001 -> h6c1e5f90001, harden admin accounts`. Not run by me.

## 6. Can it be better?
- Good: retry-safe checks, safe defaults for old rows, good security idea.
- Weak: no unique or check rules (for example `failed_login_attempts >= 0`). `admin_users` must exist (made in `e3f8a2b60001`).
- Cleaner way (opinion): add `sa.CheckConstraint('failed_login_attempts >= 0')`; keep the lock logic in one function.
- Security: this file improves security; the real protection depends on the login code actually using these columns. Check that the lock also stops valid passwords while locked.

## 7. Check yourself
1. How does `token_version` let you log out an admin everywhere?
2. Why are the `server_default` values written as strings?
