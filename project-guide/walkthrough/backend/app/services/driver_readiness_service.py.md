# backend/app/services/driver_readiness_service.py

## 1. Purpose
This file answers "is this pending driver ready to be active?". If the vehicle is verified and all four documents are verified, it sets the driver to `active`. `DriverDashboardService` calls it every time the dashboard loads or availability changes (`driver_dashboard_service.py:24`, `:43`). It is a safety net: it fixes the driver status if the review service missed it.

## 2. Imports, one by one

### Third-party
- `from sqlalchemy import select` (`driver_readiness_service.py:1`). Builds queries.
- `from sqlalchemy.orm import Session` (`:2`). Session type.

### Project
- `from app.models.ride_hailing import Driver, DriverDocument, DriverVehicleAssignment, Vehicle` (`:4`). Table classes.

## 3. Walk through the code

### `required_document_types` (`:10-12`)
A set of four document names (same as in `driver_document_review_service.py:14`).

### `reconcile(db, driver) -> bool` (`:14-36`)
**What it does:** returns `True` if the driver is active (now or already), else `False`. It may change the driver.
1. If `driver.status != 'pending'`, return right away: `True` only if status is `active` (`:15-16`). So suspended drivers are never re-activated here. Good.
2. Find the newest open vehicle assignment (`ended_at.is_(None)`) and its vehicle (`:17-22`). `db.scalar` returns one object or `None`.
3. No vehicle or not `verified`: return `False` (`:23-24`).
4. `db.execute(select(type, status).where(driver_id == ...)).all()` returns rows like `[('aadhaar', 'verified'), ...]`; `dict(...)` turns them into `{'aadhaar': 'verified'}` (`:25-27`).
5. If any required type is missing or not `verified`, return `False` (`:28-32`).
6. Otherwise set `driver.status = 'active'`, `db.add(driver)`, `db.flush()` (send the change to the database without final commit), and return `True` (`:33-36`). The caller commits. In `dashboard` there is no commit after reconcile, so the change may be lost unless something else commits. Check this: `set_availability` commits, `dashboard` does not (I am not fully sure how the session closes; check `db` dependency in `backend/app/db`).

## 4. How data flows
```
DriverDashboardService.dashboard
   -> reconcile(db, driver)
        status != pending ? --> return
        SELECT vehicle (open assignment) --> DB
        SELECT doc types/status --> DB
        all verified? -> driver.status='active'; flush
```

## 5. Try it
Not directly runnable (needs database rows). Rule check in Python:
```bash
python3 -c "need={'a','b'}; s={'a':'verified','b':'pending'}; print(need<=s.keys() and all(s[n]=='verified' for n in need))"
```
Expected `False`.

## 6. Can it be better?
- **Good:** quick exit for non-pending drivers; clear invariant; returns a bool.
- **Weak:**
  - A function named `reconcile` that returns a bool and writes is easy to misuse.
  - `flush` without commit: the result may not persist on read-only requests.
  - The required set and the vehicle rule are duplicated with `driver_document_review_service.py`.
  - The vehicle query is copied in `driver_dashboard_service._vehicle`.
- **Cleaner way:** one shared `REQUIRED_DOCUMENT_TYPES` constant and a repository method `get_active_vehicle` (it already exists in `DriverRepository`, used by the review service); use it here.
- **Security:** it never activates `suspended` or `deactivated` drivers (`:15-16`), which is correct.

## 7. Check yourself
1. Why does `reconcile` return early when the status is not `pending`?
2. What is the difference between `db.flush()` and `db.commit()`?
