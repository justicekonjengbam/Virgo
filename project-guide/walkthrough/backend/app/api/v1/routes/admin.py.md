# backend/app/api/v1/routes/admin.py

## 1. Purpose
This file holds the HTTP routes for the admin web app (`admin-app/`). Admins log in, change their password, list drivers, review driver documents and manage support tickets. It is mounted by `backend/app/api/v1/router.py:22`. It calls three service classes and two auth helpers (see imports). Final URLs start with `/api/v1/admin`.

## 2. Imports, one by one
**Third-party**
- `from fastapi import APIRouter, Depends` (`admin.py:1`). **FastAPI** is the web framework. `APIRouter` groups routes. **Depends** (dependency injection: FastAPI runs a helper function for you and hands the result to your function. *Example:* `def f(db = Depends(get_db))` gives `f` a ready database session).
- `from sqlalchemy.orm import Session` (`admin.py:2`). **SQLAlchemy** is an ORM (Object Relational Mapper: it lets you use Python classes instead of SQL text). A `Session` is one conversation with the database. Here it is only used as a type hint. *Example:* `db.get(Driver, 1)`.

**Project imports**
- `get_current_admin, require_admin_permission` from `app/api/dependencies/admin_auth.py` (`admin.py:4`). The first reads the login token and returns the admin. The second builds a checker for one permission string, such as `'drivers:read'`.
- `get_db` from `app/db` (`admin.py:5`). Gives each request a database session and closes it after.
- `AdminUser` from `app/models/user.py` (`admin.py:6`). The database table class for admins. Used as a type hint.
- Schemas (`admin.py:7-12`) from `app/schemas/admin.py` and `app/schemas/admin_review.py`. A **schema** is a Pydantic class that describes the shape of JSON. *Example:* `AdminLoginRequest` expects `{"email": ..., "password": ...}` (I am not sure of the exact field names; check the schema file).
- `AdminAuthService`, `AdminOperationsService`, `DriverDocumentReviewService` (`admin.py:13-15`) from `app/services/`. They hold the real business logic.

## 3. Walk through the code, top to bottom
**Setup** (`admin.py:17-20`)
- `router = APIRouter(prefix='/admin', tags=['admin'])`: every route below starts with `/admin`. `tags` only groups them in the auto docs page `/docs`.
- `auth_service`, `operations_service`, `document_service`: one shared object of each service, made when the file is imported. They are reused for all requests.

**Decorator idea.** `@router.post('/x', response_model=Y)` registers the function under `POST /x`. `response_model` tells FastAPI to turn the return value into the JSON shape of `Y` and hide extra fields. The function parameters are filled by FastAPI: a Pydantic-type parameter is read from the JSON body, a plain type like `int` with the same name as `{x}` in the path comes from the URL, and other simple types come from the query string (`?a=b`).

**`login`** `POST /admin/auth/login` (`admin.py:23-25`). Input: body `AdminLoginRequest`, a db session. Calls `auth_service.login(db, request)`, which checks the password and returns tokens. Output: `AdminAuthResponse`. Public route (no auth dependency). Errors come from the service (likely 401).

**`me`** `GET /admin/auth/me` (`admin.py:28-30`). `Depends(get_current_admin)` reads the `Authorization: Bearer <token>` header and loads the admin; no token gives 401. It returns `auth_service._profile(admin)`. Note the leading underscore: it is a private method used from outside.

**`change_password`** `POST /admin/auth/change-password` (`admin.py:33-36`). Needs a logged-in admin. `auth_service.change_password` does the check and update. Then the route returns a fixed message telling the admin to sign in again.

**`list_drivers`** `GET /admin/drivers` (`admin.py:39-41`). `driver_status: str | None = None` is an optional query parameter: `/admin/drivers?driver_status=pending`. `_: AdminUser = Depends(require_admin_permission('drivers:read'))` runs the permission check. The name `_` means "I need the check but not the value". Returns a list from `operations_service.drivers`. Permission missing gives 403 (my guess; see `admin_auth.py`).

**`list_driver_documents`** `GET /admin/driver-documents` (`admin.py:44-46`). Same pattern, optional `status_filter`, permission `drivers:read`.

**`review_driver_document`** `PUT /admin/drivers/{driver_id}/documents/{document_type}/review` (`admin.py:49-51`). Path values `driver_id` (int) and `document_type` (str), a body `DriverDocumentReviewRequest`. Needs `documents:review`. Passes `admin.email` so the service can record who reviewed. *Example:* `PUT /api/v1/admin/drivers/7/documents/license/review` with `{"status":"approved"}` (field names unverified).

**`list_support_tickets`** `GET /admin/support-tickets` (`admin.py:54-56`) with optional `ticket_status`, permission `support:manage`.

**`update_support_ticket`** `PATCH /admin/support-tickets/{ticket_id}` (`admin.py:59-61`). PATCH means a partial update. Calls `operations_service.update_ticket(db, ticket_id, request, admin.id)`.

## 4. How data flows
```
admin-app (browser) --PUT .../review + Bearer token--> FastAPI
  -> require_admin_permission('documents:review')  (checks token + permission)
  -> get_db (opens session)
  -> review_driver_document()
  -> DriverDocumentReviewService.review()  --SQL--> database
  <- DriverDocumentReviewResponse (JSON) -- back to browser
```

## 5. Try it
With the server running (`cd backend && uv run uvicorn app.main:app --reload`; `uv run` runs inside the project env, `uvicorn` is the server program, `--reload` restarts on code change):
```
curl -s localhost:8000/api/v1/admin/auth/me
```
`curl -s` sends a GET quietly. With no token, expect a JSON error like `{"detail":"Not authenticated"}` and status 401 or 403 (exact text unverified). Port 8000 is uvicorn's default.

## 6. Can it be better?
- Good: routes are thin; logic sits in services. Permissions are named strings.
- Weak: `me` calls the private `_profile`. Lines are very long. Services are created at import time as globals, which makes tests harder to swap. `driver_status` and `document_type` are plain `str`, so bad values are not rejected at the edge.
- Cleaner way (opinion): use `Literal['pending','approved']` or an Enum for status params, and make `profile` a public method.
- Security: `login` has no visible rate limit here; check the service or add one against password guessing.

## 7. Check yourself
1. Which dependency decides whether an admin may review documents, and what string does it use?
2. What is the final URL to update ticket 3?
