# g5b0d4e80001_add_live_ride_tracking.py

## 1. Purpose
This **migration** (a script that changes the database layout one step at a time) prepares live tracking. It adds a new ride status `driver_arrived`, new columns for cancel actor, route, GPS accuracy and speed, and two rules that allow only **one active ride per passenger and per driver**. Before adding the rules, it cleans up existing duplicate active rides. Alembic runs it. No project file is called.

## 2. Imports, one by one
- `from alembic import op` (`g5b0d4e80001_add_live_ride_tracking.py:7`). Alembic actions. This file uses `op.batch_alter_table`, `op.execute`, `op.create_index`, `op.drop_index`.
- `import sqlalchemy as sa` (`:8`). Column types and `sa.text(...)`, which wraps raw SQL text. *Example:* `sa.text("SELECT 1")`.

## 3. Walk through the code, top to bottom
- `revision = 'g5b0d4e80001'`, `down_revision = 'f4a9c3d70001'` (`:11-12`).
- `ACTIVE_STATUSES = "'requested','searching',...,'in_progress'"` (`:16`). A string of SQL values for rides that are "still going". It is pasted into SQL with an f-string. It is a fixed constant, not user input, so this is safe.
- `upgrade()` (`:19`):
  - `with op.batch_alter_table('rides') as batch:` (`:20`). **Batch mode** is for SQLite, which cannot change constraints in place. Alembic copies the table, applies changes, and swaps it. On PostgreSQL it runs normal `ALTER`. Inside:
    - `batch.drop_constraint('ck_rides_status', type_='check')` (`:21`) removes the old status rule.
    - `batch.create_check_constraint('ck_rides_status', "status IN (...)")` (`:22-25`) adds the new rule that includes `driver_arrived`.
    - `batch.add_column` for `cancelled_by` (text 20) and `route_geojson` (JSON) (`:26-27`).
  - Second batch on `driver_current_locations` adds `accuracy_meters` and `speed_mps`, Numeric(7,2) (`:28-30`). Numeric(7,2) means up to 5 digits before and 2 after the dot.
  - First `op.execute(sa.text(...))` (`:31-39`): a SQL statement. `WITH ranked AS (...)` is a **CTE** (a named temporary result). `ROW_NUMBER() OVER (PARTITION BY passenger_id ORDER BY requested_at DESC, id DESC)` numbers each passenger's active rides, newest = 1. The `UPDATE` then cancels every ride with `position > 1`: sets status `cancelled`, `cancelled_at` now, `cancelled_by='system'`, and reason `duplicate_active_ride_migration`. Result: each passenger keeps only the newest active ride.
  - Second `op.execute` (`:40-48`): same, but per `driver_id` (only rows with a driver).
  - `op.create_index('uq_rides_one_active_passenger', 'rides', ['passenger_id'], unique=True, postgresql_where=..., sqlite_where=...)` (`:49-53`). A **partial unique index**: uniqueness is enforced only for rows matching the `WHERE`. So a passenger may have many finished rides but only one active one. The database itself blocks a second active ride, even in a race between two requests.
  - Same for drivers (`:54-58`), with `driver_id IS NOT NULL`.
- `downgrade()` (`:61-74`): drops both indexes, drops the new columns, restores the old status rule (without `driver_arrived`). It does not restore the rides cancelled by the cleanup.

Errors: downgrade fails if any ride has status `driver_arrived` (the old rule rejects it). The raw SQL uses `ROW_NUMBER()` window functions, which need SQLite 3.25+ or PostgreSQL.

## 4. How data flows
```
alembic upgrade head
  -> batch rebuild of rides (new check, 2 new columns)
  -> batch change driver_current_locations
  -> UPDATE: cancel duplicate active rides (passenger)
  -> UPDATE: cancel duplicate active rides (driver)
  -> CREATE UNIQUE INDEX ... WHERE status IN (active)   x2
```
At runtime a second "request ride" insert for the same passenger now fails with an integrity error, which the API code should turn into a clear message.

## 5. Try it
```zsh
cd backend
uv run alembic upgrade g5b0d4e80001
sqlite3 <your-db-file> ".indexes rides"   # if you use SQLite
```
`sqlite3 FILE ".indexes TABLE"` lists indexes; you should see `uq_rides_one_active_passenger` and `uq_rides_one_active_driver`. Not run by me.

## 6. Can it be better?
- Good: cleans data first so the unique index can be created; works on two databases; the constraint enforces the rule at the lowest level.
- Weak: `ACTIVE_STATUSES` and the check list are written by hand in three places and must match the app code. The cleanup silently cancels real rides. The downgrade is lossy and can fail. `cancelled_by` has no check constraint. `ROW_NUMBER` cleanup is duplicated twice.
- Cleaner way (opinion): one helper function `cancel_duplicates(column, extra_where, reason)` used twice.
- Security: f-string SQL is safe here only because the constant is fixed. Never do this with user input.

## 7. Check yourself
1. Why use `batch_alter_table` for the `rides` change?
2. How does the partial unique index allow many completed rides but only one active ride?
