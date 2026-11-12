# backend/app/services/admin_operations_service.py

## 1. Purpose
This file holds what admins do day to day: list driver documents, list drivers, list support tickets, and update a ticket. A **service** is a class with business rules, so route files stay thin. Admin routes call it. It uses models (database table classes), `DriverRepository` (`app/repositories/driver_repository.py`) and admin schemas (`app/schemas/admin.py`).

## 2. Imports, one by one
Standard library:
- `from datetime import UTC, datetime` (`admin_operations_service.py:1`). Date-time type and the UTC zone. *Example:* `datetime.now(UTC)` is the current time in UTC. Used for `resolved_at`.

Third party:
- `from fastapi import HTTPException, status` (`:3`). **FastAPI** is the web framework. `HTTPException` becomes an HTTP error answer; `status.HTTP_404_NOT_FOUND` is `404`.
- `from sqlalchemy import select` (`:4`). **SQLAlchemy** is the database toolkit (ORM = Object-Relational Mapper: Python classes stand for tables). `select(Driver)` builds a query "get Driver rows". It can also build joins and filters.
- `from sqlalchemy.orm import Session` (`:5`). One conversation with the database, used as the type of `db`.

Project:
- `from app.models.ride_hailing import Driver, DriverDocument, SupportTicket, Vehicle` (`:7`): table classes. `Vehicle` is imported but I did not see it used in this file; it is likely unused (check with `rg Vehicle` in the file).
- `from app.models.user import Passenger` (`:8`): the passenger table class.
- `from app.repositories.driver_repository import DriverRepository` (`:9`): a class with ready database queries for drivers (`get_active_vehicle`, `get_documents`).
- `from app.schemas.admin import (...)` (`:10-15`): answer and input shapes for the admin pages.

## 3. Walk through the code, top to bottom

### `class AdminOperationsService` (`:18`)
**`__init__(driver_repository=None)`** (`:19-20`): `driver_repository or DriverRepository()` means "use the one given, else make a new one". This is **dependency injection** (passing a helper in from outside): tests can give a fake repository.

### `documents(db, review_status)` (`:22-36`)
Lists driver documents for review.
- `select(DriverDocument, Driver).join(Driver, DriverDocument.driver_id == Driver.id)` asks for each document together with its driver; the join links them by the driver id.
- `.order_by(DriverDocument.created_at.asc())` puts the oldest first (oldest waiting gets reviewed first).
- If `review_status` is given, `.where(DriverDocument.verification_status == review_status)` filters, for example to `'pending'`.
- `db.execute(query).all()` runs it and returns a list of `(document, driver)` pairs.
- For each pair, `self.driver_repository.get_active_vehicle(db, driver.id)` fetches the driver's current vehicle (or `None`). Then it builds an `AdminDriverDocumentResponse`. `vehicle.registration_number if vehicle else None` means "use the number, or None when no vehicle".
- Output: list of responses.
- Weak point: one extra query per row (see section 6).

### `drivers(db, driver_status)` (`:38-55`)
- `select(Driver).order_by(Driver.created_at.desc())` newest first; optional status filter.
- `db.scalars(query).all()` runs it and returns a list of `Driver` objects (scalars = the first column only).
- For each driver: gets the active vehicle and all documents, then builds `AdminDriverResponse`. `f'{vehicle.make} {vehicle.model}'` makes a name like `"Toyota Innova"`. `document_statuses` is a dict comprehension: `{document.document_type: document.verification_status for document in documents}` gives for example `{'license': 'approved', 'rc': 'pending'}`.

### `tickets(db, ticket_status)` (`:57-65`)
Joins `SupportTicket` to `Passenger` to get the passenger name, newest first, optional status filter, and returns a list built with a list comprehension (a one-line loop that builds a list).

### `update_ticket(db, ticket_id, request, admin_id)` (`:67-78`)
1. `db.get(SupportTicket, ticket_id)` asks for the row with that primary key, or `None`.
2. No row: `raise HTTPException(404, 'Support ticket was not found.')`.
3. Sets `status`, `assigned_admin_id` (the admin who handled it), and `resolution_note` (trimmed, or `None` if empty).
4. `resolved_at` is set to now if the status is `'resolved'` or `'closed'`, else `None` (re-opening clears it).
5. `db.add(ticket)` and `db.commit()` save it.
6. Loads the passenger and returns `AdminSupportTicketResponse`.
Example: request `status='resolved', resolution_note=' Refunded '` gives note `"Refunded"` and a `resolved_at` time.

## 4. How data flows
```
Admin web --GET /admin/tickets?status=open--> route --> AdminOperationsService.tickets(db, 'open')
   db: SELECT ticket, passenger JOIN ... ORDER BY created_at DESC
   build AdminSupportTicketResponse per row
route --> JSON list --> Admin web table
```

## 5. Try it
Not directly runnable: it needs a database session. To test, call it from a pytest with a test database, or start the backend and call the admin route with a valid admin token (route paths are in `backend/app/api/`; find them with `rg "AdminOperationsService" backend/app`).

## 6. Can it be better?
- Good: filters are optional; oldest-first for review; the repository can be replaced in tests; ticket resolved time is handled.
- Weak:
  - **N+1 queries**: `documents` and `drivers` run extra queries for every row. With 1000 drivers that is about 2000+ queries.
  - No paging: all rows are returned.
  - `Vehicle` import seems unused.
  - `update_ticket` does not check that `request.status` is allowed (the schema may); no audit log row (unlike admin login).
  - The response is built twice in different styles; `passenger` could be `None` and crash on `.full_name`.
- Cleaner way: load related rows in bulk, for example `select(Driver).options(selectinload(Driver.documents))` (SQLAlchemy loads all documents in one extra query), and add `limit`/`offset`. Add a helper `_ticket_response(ticket, passenger)` to remove the duplicated build.
- Security: these methods trust the route to check admin permissions (see `ROLE_PERMISSIONS` in `admin_auth_service.py`). `document_number` is sensitive data; confirm only the right roles can see it.

## 7. Check yourself
1. Why is a join used in `tickets`, and what does `db.execute(query).all()` return there?
2. When is `resolved_at` set, and when is it cleared?
