# i7d2f6a00001_add_outstation_bookings.py

## 1. Purpose
This **migration** (a script that changes the database layout one step at a time) creates the `outstation_bookings` table. An **outstation booking** is a scheduled trip to another city, which an admin confirms and assigns to a driver by hand, unlike an instant city ride. Alembic runs it. The outstation API code in `backend/app/` uses this table.

## 2. Imports, one by one
- `from alembic import op` (`i7d2f6a00001_add_outstation_bookings.py:7`). Alembic actions. *Example:* `op.create_table`; `op.get_bind()` gives the connection.
- `import sqlalchemy as sa` (`:8`). Column types and `sa.inspect`. *Example:* `sa.Numeric(8, 2)` is a decimal with 8 digits, 2 after the dot (like `1234.50`).

## 3. Walk through the code, top to bottom
- `revision = 'i7d2f6a00001'`, `down_revision = 'h6c1e5f90001'` (`:10-11`).
- `upgrade()` (`:16`):
  - `if 'outstation_bookings' in sa.inspect(op.get_bind()).get_table_names(): return` (`:17-18`). If the table exists, do nothing (retry safety).
  - `op.create_table('outstation_bookings', ...)` (`:19-41`) columns:
    - `id` primary key.
    - `passenger_id` foreign key to `passengers.id`, `RESTRICT` (cannot delete a passenger who has bookings), required (`:22`).
    - `driver_id`, `vehicle_id` optional foreign keys, `SET NULL` (`:23-24`). Empty until an admin assigns them.
    - `scheduled_at` required: pickup time (`:25`).
    - `pickup_address`, `destination_address` required, up to 512 chars (`:26-27`).
    - `preferred_vehicle_type` optional (`:28`).
    - `status` default `'requested'` (`:29`), limited by check `ck_outstation_booking_status` to requested/confirmed/driver_assigned/completed/cancelled/rejected (`:40`).
    - `estimated_distance_km` Numeric(8,2), `estimated_fare_paise` Integer (money in paise, 100 paise = 1 rupee) (`:30-31`).
    - `support_note` text; `assigned_admin_id` foreign key to `admin_users.id`, `SET NULL` (`:32-33`).
    - `confirmed_at`, `assigned_at`, `cancelled_at`, `cancellation_reason` (`:34-37`).
    - `created_at`, `updated_at` required (`:38-39`).
  - Three indexes (`:42-44`): by passenger and time, by driver and time, by status and time. Each matches a list screen ("my trips", "driver schedule", "admin queue by status").
- `downgrade()` (`:47-48`): `op.drop_table('outstation_bookings')` also removes its indexes.

## 4. How data flows
```
passenger app -> POST outstation booking -> row status='requested'
admin app     -> confirm / assign driver -> status='confirmed' / 'driver_assigned', assigned_at set
driver app    -> sees booking via driver_id + scheduled_at index
```

## 5. Try it
```zsh
cd backend
uv run alembic upgrade i7d2f6a00001
```
Expected: `Running upgrade h6c1e5f90001 -> i7d2f6a00001, add outstation bookings`. Not run by me.

## 6. Can it be better?
- Good: check constraint on status, sensible nullable fields, indexes for each list, safe retry.
- Weak: `preferred_vehicle_type` is free text. Fare is only an estimate, no final fare or payment link. The first migration for this table has no coordinates; `j8e3a7b10001` adds them next (that split is a sign the first design was incomplete).
- Cleaner way (opinion): store times of every status change in a separate events table, like `ride_events`.
- Security: bookings hold addresses (personal data); make sure only the owner passenger and admins can read them.

## 7. Check yourself
1. Why are `driver_id` and `vehicle_id` nullable?
2. What is the difference between `RESTRICT` and `SET NULL` for foreign keys here?
