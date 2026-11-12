# backend/app/schemas/admin.py

## 1. Purpose
This file describes the JSON shapes (requests and responses) of the admin API: login, profile, password change, driver documents, driver list and support tickets. **Schema** (a class that says which fields a message has and checks them. *Example:* `AdminLoginRequest(email='a@b.co', password='12345678')`). The admin routes in `backend/app/api/...` use these classes, and the admin web app (`admin-app/`) sends and reads this JSON. This file calls only `pydantic`.

## 2. Imports, one by one
Standard library:
- `from datetime import datetime` (`admin.py:1`). A date+time type. Used for `last_login_at`, `created_at`.
- `from typing import Literal` (2). `Literal['a','b']` means "only these exact values". *Example:* `Literal['open','closed']` rejects `'done'`.

Third party:
- `from pydantic import BaseModel, Field, field_validator, model_validator` (4). **Pydantic** (a library that checks data against type hints and turns JSON into Python objects. *Example:* `BaseModel` subclass with `id: int` rejects `"abc"`).
  - `BaseModel`: the parent class of every schema.
  - `Field(...)`: adds rules such as `min_length` and `max_length`.
  - `field_validator('x')`: a function that checks or changes one field.
  - `model_validator(mode='after')`: a function that runs after all fields are valid and can compare fields.

## 3. Walk through the code, top to bottom
- `AdminLoginRequest` (7-14). `email` 5-320 characters, `password` 8-128. `normalize_email` (11-14) is a `@field_validator('email')` with `@classmethod` (a method that receives the class as `cls`; pydantic needs this form). It returns `value.strip().lower()`. Example: `' Admin@X.com '` becomes `'admin@x.com'`. Note: it does not check that the text is a real email.
- `AdminProfileResponse` (17-23). `id`, `email`, `full_name`, `role`, `permissions: list[str]`, and `last_login_at` that may be `None` (default `None`).
- `AdminAuthResponse` (26-29). `access_token`, `token_type` default `'bearer'`, and nested `admin`. **Bearer token** (a login string that the client sends in a header `Authorization: Bearer <token>`).
- `AdminPasswordChangeRequest` (32-40). Current password 8-128, new one 12-128. `passwords_must_differ` (36-40) is a model validator: if both are equal, `raise ValueError(...)`. Pydantic turns that into a 422 error response. It returns `self` on success.
- `AdminPasswordChangeResponse` (43-44). Only `message`.
- `AdminDriverDocumentResponse` (47-56). A row for the document review list: driver id and name, city, vehicle plate, document type, number, status, note, `created_at`. Fields like `str | None` have no default, so the code must pass them explicitly (even as `None`).
- `AdminDriverResponse` (59-69). Driver list row. `document_statuses: dict[str, str]`, for example `{'aadhaar': 'verified'}`.
- `TicketStatus = Literal['open','in_progress','resolved','closed']` (72). A reusable type name.
- `AdminSupportTicketResponse` (75-84). Ticket data, with `passenger_name`.
- `AdminSupportTicketUpdate` (87-95). `status: TicketStatus`, `resolution_note` up to 1000 characters. `resolution_needs_a_note` (91-95): if status is `resolved` or `closed` and the note is empty or only spaces, raise `ValueError`. `(self.resolution_note or '').strip()` turns `None` into `''` first.

Errors: any failed rule gives a 422 response from FastAPI, with the message.

## 4. How data flows
```
admin-app --POST /admin/login {"email":" A@x.com ","password":"..."}--> FastAPI
   -> AdminLoginRequest validates, lowercases email -> route function
   -> route returns AdminAuthResponse -> JSON back to admin-app
```

## 5. Try it
```zsh
cd backend
uv run python -c "
from app.schemas.admin import AdminSupportTicketUpdate, AdminLoginRequest
print(AdminLoginRequest(email=' A@b.co ', password='12345678').email)
AdminSupportTicketUpdate(status='closed')"
```
First line prints `a@b.co`. The second call raises `ValidationError` with "Add a resolution note...".

## 6. Can it be better?
- Good: business rules live in the schema; `Literal` blocks bad status values.
- Weak: `email: str` accepts any text; pydantic has `EmailStr` (needs the `email-validator` package). `AdminSupportTicketResponse.status` is `str`, not `TicketStatus`. The new-password rule only checks length, not strength. Passwords are not stripped. The same "needs a note" idea is repeated in `admin_review.py`.
- Cleaner way:
```python
# before
email: str = Field(min_length=5, max_length=320)
# after
from pydantic import EmailStr
email: EmailStr
```
- Security: the 12-character rule and the "must differ" check are good. Response models never include `password_hash`, which is good.

## 7. Check yourself
1. What does `model_validator(mode='after')` let you do that `field_validator` cannot?
2. What HTTP status does the client get if `status='closed'` is sent with no note?
