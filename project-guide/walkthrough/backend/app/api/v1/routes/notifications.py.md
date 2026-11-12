# backend/app/api/v1/routes/notifications.py

## 1. Purpose
This file lets a passenger list their notifications and mark one as read. Unlike most routes, it talks to the database directly and has no service class. It uses the `Notification` model from `backend/app/models/ride_hailing.py`.

## 2. Imports, one by one
**Standard library**
- `from datetime import UTC, datetime` (`notifications.py:1`). `datetime` is the date-and-time type. `UTC` is the timezone object for Coordinated Universal Time. *Example:* `datetime.now(UTC)` gives the current time with a timezone.

**Third-party**
- `from fastapi import APIRouter, Depends, HTTPException` (`notifications.py:3`). `HTTPException` stops the request and sends an error. *Example:* `raise HTTPException(status_code=404, detail='x')` sends 404.
- `from sqlalchemy import select` (`notifications.py:4`). **select** builds a SQL SELECT query in Python. *Example:* `select(User).where(User.id == 1)`.
- `from sqlalchemy.orm import Session` (`notifications.py:5`). A database session (type hint).

**Project**
- `get_current_passenger` (`app/api/dependencies/auth.py`), `get_db` (`app/db.py`), `Notification` (`app/models/ride_hailing.py`), `Passenger` (`app/models/user.py`), `NotificationResponse` (`app/schemas/notification.py`) at `notifications.py:7-11`.

## 3. Walk through the code, top to bottom
- `router = APIRouter(prefix='/passengers/me/notifications', ...)` (`notifications.py:13`).
- `@router.get('', response_model=list[NotificationResponse])` (`notifications.py:16`). The empty path `''` means exactly the prefix: `GET /passengers/me/notifications`. `list[...]` means a list of that schema.
- `list_notifications` (`notifications.py:17-18`). One long line:
  - `select(Notification).where(Notification.passenger_id == passenger.id)` picks only this passenger's rows. This is the ownership check.
  - `.order_by(Notification.created_at.desc())` newest first. `.limit(100)` at most 100 rows.
  - `db.scalars(query)` runs it and returns the first column of each row (here the whole `Notification` object). `.all()` collects them. `list(...)` makes a plain list.
- `@router.patch('/{notification_id}/read', ...)` (`notifications.py:21`). **PATCH** means "change part of something". `{notification_id}` is a **path parameter** (a piece of the URL FastAPI gives to the function). `notification_id: int` makes FastAPI turn the text into an integer, or send 422.
- `mark_read` (`notifications.py:22-28`):
  - `db.scalar(select(...).where(id == ..., passenger_id == passenger.id))` returns one object or `None`. Both conditions together mean a passenger cannot touch another passenger's row.
  - If `None`, `raise HTTPException(404)` (`notifications.py:24-25`).
  - `notification.read_at = notification.read_at or datetime.now(UTC)` keeps the old read time if it exists, else sets now (`notifications.py:26`). Calling it twice is safe.
  - `db.commit(); db.refresh(notification)` (`notifications.py:27`). **commit** saves the change permanently. **refresh** reloads the object from the database so it has fresh values. Two statements joined with `;` on one line.
  - Returns the row. FastAPI converts it to `NotificationResponse` (this needs the schema to allow reading from object attributes).

Example: `PATCH /passengers/me/notifications/5/read` returns the notification with `read_at` set. Wrong id gives `{"detail":"Notification was not found."}`.

## 4. How data flows
```
App --PATCH .../5/read + token--> get_current_passenger -> Passenger
  mark_read: SELECT ... WHERE id=5 AND passenger_id=me  -> row or None
    None -> 404
    row  -> set read_at -> COMMIT -> refresh -> JSON
```

## 5. Try it
```zsh
curl -s -H "Authorization: Bearer <token>" http://127.0.0.1:8000/passengers/me/notifications
curl -s -X PATCH -H "Authorization: Bearer <token>" http://127.0.0.1:8000/passengers/me/notifications/5/read
```
`-X PATCH` picks the HTTP method. Expected: a JSON list, then one JSON object.

## 6. Can it be better?
- Good: ownership check is in the query, 404 hides other people's ids, safe to repeat.
- Weak: database code lives in the route, unlike the other routes. Very long lines (`notifications.py:17`, `:22`). `;` on one line (`:27`). The 100 limit is a magic number. No paging, no "mark all read", no test visible here.
- Cleaner way: move queries into a `NotificationService`, and format lines normally:
  ```python
  rows = db.scalars(
      select(Notification).where(Notification.passenger_id == passenger.id)
      .order_by(Notification.created_at.desc()).limit(100)
  )
  return list(rows)
  ```
- Security: good, scoped to the current passenger.

## 7. Check yourself
1. Which part of the query stops passenger A from reading passenger B's notification?
2. What does `db.refresh` do after `db.commit`?
