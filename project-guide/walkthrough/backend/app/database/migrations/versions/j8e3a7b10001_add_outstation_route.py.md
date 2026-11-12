# j8e3a7b10001_add_outstation_route.py

## 1. Purpose
This **migration** (a script that changes the database layout one step at a time) adds map data to `outstation_bookings`: place ids, latitude and longitude for pickup and destination, and a saved route line. It is the latest migration in the chain (the "head"). Alembic runs it. The outstation code in `backend/app/` fills these columns.

## 2. Imports, one by one
- `from alembic import op` (`j8e3a7b10001_add_outstation_route.py:7`). Alembic actions; `op.add_column`, `op.drop_column`, `op.get_bind`.
- `import sqlalchemy as sa` (`:8`). Column types and `sa.inspect`. *Example:* `sa.JSON()` stores a JSON document in one column.

## 3. Walk through the code, top to bottom
- `revision = 'j8e3a7b10001'`, `down_revision = 'i7d2f6a00001'` (`:10-11`).
- `upgrade()` (`:16`):
  - `columns = {column['name'] for column in sa.inspect(op.get_bind()).get_columns('outstation_bookings')}` (`:17`). A set of column names that already exist.
  - `additions = {...}` (`:18-26`). A dict (name -> column object) of seven new columns: `pickup_place_id` and `destination_place_id` (a place id from the map service, text up to 255), `pickup_latitude/longitude` and `destination_latitude/longitude` (Numeric(9,6), about 10 cm precision), and `route_geojson` (JSON). **GeoJSON** is a standard JSON format for map shapes. *Example:* `{"type":"LineString","coordinates":[[77.1,28.6],[77.2,28.7]]}`.
  - `for name, column in additions.items(): if name not in columns: op.add_column('outstation_bookings', column)` (`:27-29`). Adds only the missing ones. All are nullable, so old rows stay valid.
- `downgrade()` (`:32-34`). A loop over a tuple of seven names (listed in reverse) calling `op.drop_column`. No existence check here.

## 4. How data flows
```
passenger picks places on map
  -> API stores place ids + lat/lng + route line in the new columns
  -> admin app draws route from route_geojson
```

## 5. Try it
```zsh
cd backend
uv run alembic upgrade head
uv run alembic current
```
`alembic current` prints the id stored in the database. After a full upgrade it should print `j8e3a7b10001 (head)`. Not run by me.

## 6. Can it be better?
- Good: retry-safe, loop avoids repeating seven lines, all new columns nullable.
- Weak: coordinates are optional, so old bookings have no map data and the app must handle `NULL`. Downgrade has no existence checks. Latitude/longitude have no range check (`-90..90`, `-180..180`).
- Cleaner way (opinion): add check constraints for the ranges, or give the booking one "route" table.
- Security: location data is personal; do not log it.

## 7. Check yourself
1. Why is `additions` a dict and not a list?
2. What does `alembic current` show after this migration is applied?
