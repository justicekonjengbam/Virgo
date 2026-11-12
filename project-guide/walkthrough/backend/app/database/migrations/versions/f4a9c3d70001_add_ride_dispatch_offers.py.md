# f4a9c3d70001_add_ride_dispatch_offers.py

## 1. Purpose
This **migration** (a script that changes the database layout one step at a time) creates the `ride_dispatch_offers` table. When a passenger asks for a ride, the server offers it to nearby drivers. This table stores each offer, so offers survive a server restart ("durable"). Alembic runs it. It calls no project file; the dispatch code in `backend/app/` reads and writes this table.

## 2. Imports, one by one
- `from alembic import op` (`f4a9c3d70001_add_ride_dispatch_offers.py:7`). Alembic's action set. *Example:* `op.create_table`.
- `import sqlalchemy as sa` (`:8`). Column and type descriptions. *Example:* `sa.ForeignKey('rides.id')`.

## 3. Walk through the code, top to bottom
- `revision = 'f4a9c3d70001'`, `down_revision = 'e3f8a2b60001'` (`:11-12`). Runs after the admin schema.
- `upgrade()` (`:17`):
  - `op.create_table('ride_dispatch_offers', ...)` (`:18-28`) columns:
    - `id` primary key (`:20`).
    - `ride_id` foreign key to `rides.id`, `CASCADE` (delete offers if the ride is deleted), required (`:21`).
    - `driver_id` foreign key to `drivers.id`, `CASCADE`, required (`:22`).
    - `status` text up to 20, default `'pending'` (`:23`). The code decides the other values (for example accepted, rejected, expired; I am not sure of the exact list, check the model).
    - `offered_at`, `expires_at` required times (`:24-25`). After `expires_at` the offer is dead.
    - `responded_at` optional (`:26`).
    - `sa.UniqueConstraint('ride_id', 'driver_id', name='uq_ride_dispatch_offer_driver')` (`:27`): the same driver cannot be offered the same ride twice.
  - `op.create_index('ix_ride_dispatch_offers_driver_status_expires', ..., ['driver_id', 'status', 'expires_at'])` (`:29`). Speeds up "show this driver's pending, not-expired offers".
- `downgrade()` (`:32-34`): drops the index, then the table.

## 4. How data flows
```
passenger requests ride
  -> dispatch code INSERT into ride_dispatch_offers (status='pending', expires_at=now+N s)
  -> driver app asks "my offers" -> query uses the composite index
  -> driver accepts -> status/responded_at updated
```

## 5. Try it
```zsh
cd backend
uv run alembic upgrade f4a9c3d70001
```
Expected: `Running upgrade e3f8a2b60001 -> f4a9c3d70001, add durable ride dispatch offers`. Not run by me.

## 6. Can it be better?
- Good: unique pair blocks duplicate offers, cascade keeps the table clean, index matches the query.
- Weak: `status` has no check constraint (other tables do). No `created_at/updated_at` like other tables. No retry-safety check.
- Cleaner way (opinion): add `sa.CheckConstraint("status IN ('pending','accepted','rejected','expired')", name='ck_dispatch_offer_status')` after confirming the real value list in the code.
- Security: none directly.

## 7. Check yourself
1. What stops a driver receiving two offers for one ride?
2. Why does the index start with `driver_id`?
