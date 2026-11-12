# docs/database-guidelines.md

## 1. Purpose
A short rulebook for how the project stores data. It sits in `docs/` and is for developers. The rules apply to the backend (`backend/`) database code and its Alembic migrations. No code reads this file.

## 2. Imports, one by one
None. It is a Markdown file.

## 3. Walk through the document

**Local development** (`docs/database-guidelines.md:3-5`). The API uses **SQLite** (a database stored in one file on your disk, no server needed. *Example:* `app.db`) by default, so the emulator runs without downloads. The schema (the list of tables and columns) is created by **Alembic** (a tool that applies versioned database changes called **migrations**. *Example:* "add column `rating` to `rides`") when the setting `AUTO_MIGRATE=true`. An **environment variable** is a setting read from outside the code, usually from `backend/.env`.

**Production** (lines 7-9).
- Use **PostgreSQL** (a strong server database) with **PostGIS** (an add-on for maps and distances. *Example:* "find drivers within 3 km").
- Set `AUTO_MIGRATE=false` and run `alembic upgrade head` (apply all migrations up to the newest) during release, with a dedicated migration user (a database account that may change tables, while the app account may not).
- Use **Redis** (a very fast in-memory store) for things that change often and may be lost: live driver presence, dispatch candidates, rate limits, ephemeral (short-lived) location updates. Keep ride records in PostgreSQL.

**Data rules** (lines 11-18).
- Money in integer **paise** (1/100 of a rupee; Rs 12.50 is `1250`). Integers avoid rounding errors. Timestamps in **UTC** (one world time zone).
- Store the Firebase UID and **E.164** phone numbers (the international format, *Example:* `+919876543210`). Never store Firebase OTPs or raw tokens.
- Store Google place IDs and route snapshots, never Maps API keys.
- KYC (identity check) files go to private object storage; the database keeps only the storage key (a file name or path).
- Use foreign keys (a column that must point at a real row in another table), **idempotency keys** (a unique id so a repeated request does not run twice), immutable ride events (never edited after saving), and audit/outbox records.
- Line 18: change the schema only through new Alembic migrations. Do not call `create_all()` (SQLAlchemy's shortcut that makes all tables directly) in runtime code.

## 4. How data flows
```
developer edits models --> alembic revision --> new migration file
release process --> alembic upgrade head --> PostgreSQL tables updated
API request --> PostgreSQL (durable) / Redis (live, temporary)
```

## 5. Try it
Not directly runnable. To apply migrations locally:
```zsh
cd backend && uv run alembic upgrade head
```
`uv run` runs a tool inside the project's Python environment. `alembic upgrade head` applies every migration. Expected: lines like `Running upgrade -> <revision>`. This assumes an `alembic.ini` exists in `backend/`; check with `fd alembic.ini backend`.

## 6. Can it be better?
- Good: clear, short, and the money, UTC, and secret rules are correct practice.
- Weak: it says "PostgreSQL with PostGIS" and "Redis", but the repo's real code may still use SQLite only. I am not sure; check `backend/app` for Redis and PostGIS use. The rules are not enforced by tests.
- Cleaner way: add a short "current status" line (what is built vs planned) and a checklist for new migrations.
- Security: the rules about no Maps keys, no raw tokens, and private KYC storage are good.

## 7. Check yourself
1. Why is `1250` paise safer than `12.50` for money?
2. Why must production set `AUTO_MIGRATE=false`?
