# backend/app/api/v1/router.py

## 1. Purpose
This file joins all the route files of API version 1 into one big router called `api_router`. `backend/app/main.py:8` imports it and `backend/app/main.py:33` mounts it under the prefix `/api/v1` (the value comes from `backend/app/core/config.py:14`). It calls every file in `backend/app/api/v1/routes/`.

## 2. Imports, one by one
**Third-party**
- `from fastapi import APIRouter` (`router.py:1`). **FastAPI** is the web framework. An **APIRouter** is a small bundle of URL routes that you can plug into the main app. *Example:* `r = APIRouter(); r.get('/ping')(lambda: 'pong')`. This file needs it to make the parent router. It can also add a shared prefix, for example `APIRouter(prefix='/admin')`.

**Project imports** (`router.py:3-16`). Each line has the shape `from app.api.v1.routes.X import router as X_router`. It takes the variable named `router` from the file `routes/X.py` and renames it `X_router`, so that 14 files that all use the name `router` do not clash. The files are: `auth`, `drivers_auth`, `booking`, `emergency_contacts`, `home`, `driver_dashboard`, `admin`, `driver_menu`, `driver_matching`, `passenger_profile`, `realtime`, `maps`, `outstation`, `notifications`. (`home`, `passenger_profile`, `realtime`, `maps`, `outstation`, `notifications` are not in this batch.)

## 3. Walk through the code, top to bottom
- `api_router = APIRouter()` (`router.py:18`). Makes an empty parent router. It has no prefix, because `main.py` adds `/api/v1`.
- `api_router.include_router(auth_router)` (`router.py:19`, and the same for lines 20-32). **include_router** copies all routes of a child router into the parent. *Example:* the child has `POST /auth/passengers/login`, so the parent now also serves it, and the full URL becomes `/api/v1/auth/passengers/login`.
- Order matters a little: FastAPI checks routes in the order they were added. If two routes could match the same URL, the first one wins. Here the files use different prefixes, so there is no clash I could see (I did not check the six files outside this batch).

Nothing is returned. The side effect is that `api_router` now holds every route.

## 4. How data flows
```
main.py  --import-->  router.py  --include_router-->  routes/*.py
request GET /api/v1/drivers/menu/support
   -> main.py strips prefix /api/v1
   -> api_router looks for a match
   -> driver_menu.router handles it
```

## 5. Try it
From `backend/`:
```
uv run python -c "from app.api.v1.router import api_router; print(len(api_router.routes))"
```
- `uv run` runs a command inside the project's Python environment.
- `python -c "..."` runs the quoted code.
- Expected output: one number, the count of routes. I did not run it, so I cannot say the number.

## 6. Can it be better?
- Good: one single place to see every route group.
- Weak: adding a new route file needs two edits (import and include). Imports are not sorted. Easy to forget the include line, and then the route silently does not exist.
- Cleaner way (opinion): a list loop.
```python
for r in (auth_router, drivers_auth_router, ...):
    api_router.include_router(r)
```
- Security: none here. Auth is enforced inside each route file.

## 7. Check yourself
1. What is the full URL of a route declared as `@router.get('/locations')` inside `booking.py`?
2. Why is each router renamed with `as`?
