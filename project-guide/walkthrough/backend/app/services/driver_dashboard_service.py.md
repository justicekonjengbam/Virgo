# backend/app/services/driver_dashboard_service.py

## 1. Purpose
This file builds the numbers on the driver home screen: online time, rating, safety score, earnings, ride counts, and the current vehicle. It is a "read model": it mostly reads and adds things up. It also switches the driver online or offline. Driver dashboard routes call it. It calls `DriverReadinessService` and the database.

## 2. Imports, one by one

### Standard library
- `from datetime import UTC, datetime, timedelta` (`driver_dashboard_service.py:1`). Date/time tools. `timedelta` is imported but I do not see it used in this file (it is unused; check with `rg timedelta`).

### Third-party
- `from sqlalchemy import func, select` (`:3`). `select` builds queries. `func` calls SQL functions. *Example:* `func.count(Ride.id)` is SQL `COUNT(rides.id)`.
- `from sqlalchemy.orm import Session` (`:4`). Database session (type hint).

### Project
- `from app.models.ride_hailing import (Driver, DriverVehicleAssignment, FareQuote, Rating, Ride, Vehicle)` (`:6-13`). Table classes.
- `from app.schemas.driver_dashboard import DriverDashboardResponse, DriverVehicleStatusResponse` (`:14`). Answer shapes.
- `from app.services.driver_readiness_service import DriverReadinessService` (`:15`). Promotes a pending driver to active when all is verified.

## 3. Walk through the code

### `class DriverDashboardService` (`:18`)
Docstring: money stays in paise. `readiness_service = DriverReadinessService()` (`:21`) is a shared helper.

**`dashboard(db, driver)`** (`:23-40`)
1. `self.readiness_service.reconcile(db, driver)` first checks if a pending driver can now be active (`:24`).
2. `now`, then `today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)` is midnight UTC today (`:25-26`). `month_start = today_start.replace(day=1)` is the first of this month (`:27`). Note: this is UTC midnight, not India midnight, so "today" starts at 05:30 India time. This is a possible bug.
3. Returns a `DriverDashboardResponse` filled by the private helpers below (`:29-40`).

**`set_availability(db, driver, is_online)`** (`:42-50`). Reconciles, sets `driver.is_online`, and records `last_online_at` when going online. `db.add(driver)`, `db.commit()`, `db.refresh(driver)` save and reload. Returns a new dashboard. It does not block going online when the driver is not `active`; I am not sure whether the route does. Check `backend/app/api` for the caller.

**`_completed_rides(db, driver_id, since)`** (`:52-55`). `select(func.count(Ride.id)).where(...)` counts rides with this driver, status `completed`, and `completed_at >= since`. `db.scalar(...)` returns the first column of the first row. `or 0` handles `None`. *Example:* 3 rides today returns `3`.

**`_earnings(...)`** (`:57-66`). `func.coalesce(func.sum(FareQuote.amount_paise), 0)` sums fares, and `coalesce` replaces NULL with 0. `.join(Ride, FareQuote.ride_id == Ride.id)` links each quote to its ride. Only final quotes count (`FareQuote.is_final.is_(True)`; `.is_()` makes SQL `IS TRUE`). Returns an int in paise. *Example:* two rides of 18000 returns `36000`.

**`_rating(...)`** (`:68-72`). `func.avg(Rating.score)` averages scores that passengers gave this driver (`rater_type == "passenger"`). Returns a number rounded to one decimal, or `None` when no ratings.

**`_safety_score(...)`** (`:74-82`). Counts completed and cancelled rides; the score is `completed / total * 100`, rounded. `None` if no rides. Note this is really a "completion rate", not a real safety measure. It also counts rides cancelled by the passenger against the driver (the query does not check who cancelled).

**`_online_minutes(driver, now)`** (`:84-93`). Returns 0 if offline. Makes `last_online_at` time-zone aware if it is naive (`:88-89`). `(now - started_at).total_seconds() // 60` gives whole minutes. `% (24 * 60)` wraps at 24 hours (comment `:91-92`).

**`_vehicle(db, driver_id)`** (`:95-112`). Finds the newest assignment with no end date (`ended_at.is_(None)`) and the vehicle behind it (`.order_by(started_at.desc())` newest first). Returns `None` if none, else a `DriverVehicleStatusResponse`.

## 4. How data flows
```
Driver app --GET dashboard--> route --> DriverDashboardService.dashboard
   readiness_service.reconcile --> DB (maybe set status=active)
   6 small SELECT queries (count, sum, avg, vehicle) --> DB
Driver app <-- DriverDashboardResponse
```

## 5. Try it
Not directly runnable. Look at the SQL SQLAlchemy would make:
```bash
cd backend && uv run python -c "from sqlalchemy import select,func; from app.models.ride_hailing import Ride; print(select(func.count(Ride.id)).where(Ride.status=='completed'))"
```
Expected: `SELECT count(rides.id) AS count_1 FROM rides WHERE rides.status = :status_1` (table name may differ).

## 6. Can it be better?
- **Good:** small helpers, each with one query; money in paise; `coalesce` and `or 0` avoid None errors.
- **Weak:**
  - `_safety_score` runs two queries that one `CASE` query could do.
  - A dashboard load runs about 8 queries.
  - "today" uses UTC, not India time (`:25-26`).
  - Unused import `timedelta` (`:1`).
  - `dashboard` writes to the database through `reconcile`, even on a GET.
  - Magic number `24 * 60` and the odd "wrap" in online minutes.
  - No tests are visible for these queries.
- **Cleaner way:**
```python
# before: two count queries
# after: one
select(func.count().filter(Ride.status=='completed'), func.count().filter(Ride.status=='cancelled')).where(Ride.driver_id==driver_id)
```
- **Security:** it only reads the logged-in driver's data via `driver.id`, good.

## 7. Check yourself
1. Why does `_earnings` filter on `FareQuote.is_final`?
2. What does `db.scalar(...) or 0` protect against?
