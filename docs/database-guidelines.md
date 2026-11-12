# CabApp database guide

## Local development

The API uses SQLite by default so the emulator can run without external downloads. The schema is applied through Alembic migrations when `AUTO_MIGRATE=true`.

## Production

Use PostgreSQL with PostGIS, set `AUTO_MIGRATE=false`, and run `alembic upgrade head` from the deployment release process using a dedicated migration user. Use Redis for live driver presence, dispatch candidates, rate limits, and ephemeral location updates; keep durable ride records in PostgreSQL.

## Data rules

- Store money in integer paise and all timestamps in UTC.
- Store Firebase UID and E.164 phone numbers; never store Firebase OTPs or raw Firebase tokens.
- Store Google place IDs and route snapshots, never Maps API keys.
- Keep KYC files in private object storage and persist only their storage keys.
- Use foreign keys, idempotency keys, immutable ride events, and audit/outbox records for critical operations.
- Apply all schema changes through new Alembic migrations. Do not use `create_all()` in runtime code.
