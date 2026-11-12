# backend/app/schemas/notification.py

## 1. Purpose
This file defines how one in-app notification looks in an API answer. A **notification** is a short message for the user. *Example:* "Your driver is arriving". The notification routes return a list of these to the apps. It calls nothing in the project.

## 2. Imports, one by one
- `from datetime import datetime` (`notification.py:1`). Python's date-and-time type. *Example:* `datetime(2026,10,26,8,0)`. Used for `read_at` and `created_at`.
- `from pydantic import BaseModel` (`notification.py:3`). **Pydantic** checks data against a class. *Example:* a missing required field raises an error. `BaseModel` is the parent class giving that behavior.

## 3. Walk through the code, top to bottom

### `NotificationResponse` (`notification.py:6-13`)
- `id: int`: database id.
- `notification_type: str`: a kind label, for example `"ride_accepted"`. The app can pick an icon from it.
- `title: str`, `body: str`: the text shown.
- `data_json: dict | None`: extra data as a dict, or null. *Example:* `{"ride_id": 12}` so a tap can open that ride.
- `read_at: datetime | None`: when the user read it. `None` means unread.
- `created_at: datetime`: when it was made. Required, never null.

Example: `NotificationResponse(id=1, notification_type="x", title="Hi", body="Yo", data_json=None, read_at=None, created_at=datetime.now())`.

## 4. How data flows
```
App --GET notifications--> route --> database rows (Notification)
route --> NotificationResponse per row --> JSON list --> app inbox screen
```

## 5. Try it
From `backend/`:
```
uv run python -c "from datetime import datetime; from app.schemas.notification import NotificationResponse as N; print(N(id=1,notification_type='t',title='a',body='b',data_json=None,read_at=None,created_at=datetime.now()).read_at)"
```
Expected: `None`.

## 6. Can it be better?
- Good: `read_at` as a time doubles as a read flag and a timestamp.
- Weak: `notification_type` is a free string; `data_json` has no defined shape; no defaults on nullable fields.
- Cleaner way: use `Literal[...]` for known types and `= None` defaults.
- Security: `data_json` may carry ids. Make sure it never holds private data of other users.

## 7. Check yourself
1. How do you know from this schema that a notification is unread?
2. What is `data_json` for?
