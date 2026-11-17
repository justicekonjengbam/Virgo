# Virgo Supabase schema checklist

This is the expected application schema for the current Virgo Alembic chain (`head` = `m1f6a8b40001`). Use it to check the `public` schema in the Virgo Supabase project. The migration files under `backend/app/database/migrations/versions/` are the source of truth for column types, nullability, defaults, foreign keys, unique constraints, and indexes; this checklist is not a replacement for applying those migrations.

## Expected tables

- `admin_users`
- `audit_logs`
- `device_sessions`
- `driver_current_locations`
- `driver_documents`
- `driver_vehicle_assignments`
- `drivers`
- `emergency_contacts`
- `fare_line_items`
- `fare_quotes`
- `location_catalog`
- `notifications`
- `outbox_events`
- `outstation_bookings`
- `passenger_profiles`
- `passengers`
- `payments`
- `ratings`
- `rate_cards`
- `ride_categories`
- `ride_dispatch_offers`
- `ride_events`
- `ride_stops`
- `rides`
- `saved_places`
- `service_areas`
- `support_tickets`
- `vehicles`
- `alembic_version` (migration bookkeeping)

Virgo-specific later migrations add ride OTP security, driver document review metadata, document number and file metadata, online-driver status, outstation route data, admin operations fields, rate cards, and fare snapshot fields. Keep the complete Virgo migration chain; do not substitute a schema from the older CabSure repository.

## Apply and verify

From `backend`, after putting the intended Virgo Supabase URL in the ignored `.env` file:

```powershell
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic check
```

`alembic current` should report `m1f6a8b40001`. If the target database contains tables but has no matching Alembic revision, stop and inspect it before applying migrations; do not stamp it or drop tables to force a match.

Use this Supabase SQL Editor query to list each public table's columns, SQL types, and nullability and compare with the migration files:

```sql
SELECT table_name, ordinal_position, column_name, data_type,
       character_maximum_length, numeric_precision, numeric_scale,
       is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

Use this query to inspect indexes and uniqueness:

```sql
SELECT tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

`alembic check` compares the live PostgreSQL schema against SQLAlchemy model metadata; it is the final check for missing or unexpected columns and indexes. Review any existing Supabase data before migration. Alembic creates/changes schema; it does not copy records from a former SQLite database.
