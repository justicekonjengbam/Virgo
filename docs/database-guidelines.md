# Virgo database guide

## Local development

The API uses PostgreSQL through psycopg 3. Configure `DATABASE_URL` in `backend/.env` with your Supabase PostgreSQL connection string. `backend/.env.example` shows the required format. Use the direct database host from the correct Virgo Supabase project and URL-encode reserved characters in the password. The backend uses PostgreSQL only; SQLite is not a supported application database.

The schema is managed by Alembic. In development, `AUTO_MIGRATE=true` applies the existing migration chain at startup. For production, use `AUTO_MIGRATE=false` and apply migrations as a deployment step.

## Production

Use PostgreSQL, set `AUTO_MIGRATE=false`, and run `alembic upgrade head` from the deployment release process using an appropriately scoped migration user. Use Redis for live driver presence, dispatch candidates, rate limits, and ephemeral location updates; keep durable ride records in PostgreSQL.

## Data rules

- Store money in integer paise and all timestamps in UTC.
- Store Firebase UID and E.164 phone numbers; never store Firebase OTPs or raw Firebase tokens.
- Store Google place IDs and route snapshots, never Maps API keys.
- Keep KYC files in private object storage and persist only their storage keys.
- Use foreign keys, idempotency keys, immutable ride events, and audit/outbox records for critical operations.
- Apply all schema changes through new Alembic migrations. Do not use `create_all()` in runtime code.
