# backend/app/api/v1/routes/home.py

## 1. Purpose
This file gives the passenger app its home screen data: `GET /passengers/me/home`. It is a thin route. It only checks who is calling, opens a database session, and hands the work to `HomeService` (`backend/app/services/home_service.py`).

## 2. Imports, one by one
**Third-party**
- `from fastapi import APIRouter, Depends` (`home.py:1`). `APIRouter` is a group of routes. **Depends** marks a function argument as "FastAPI must compute this for me by calling another function first" (this is called **dependency injection**). *Example:* `db: Session = Depends(get_db)` means "call `get_db()` and give me its result".
- `from sqlalchemy.orm import Session` (`home.py:2`). **SQLAlchemy** is a Python library for databases. A **Session** is one conversation with the database (read rows, add rows, commit). Here it is only used as a type hint.

**Project**
- `get_current_passenger` from `backend/app/api/dependencies/auth.py` (`home.py:4`). Reads the login token from the request and returns the matching `Passenger`. It raises a 401 error if the token is bad.
- `get_db` from `backend/app/db.py` (`home.py:5`). Opens a session for this request and closes it after.
- `Passenger` from `backend/app/models/user.py` (`home.py:6`). The database table class for passengers. Used as a type hint.
- `HomeResponse` from `backend/app/schemas/home.py` (`home.py:7`). The JSON shape of the answer.
- `HomeService` from `backend/app/services/home_service.py` (`home.py:8`). The class that builds the home data.

## 3. Walk through the code, top to bottom
- `router = APIRouter(prefix='/passengers/me', tags=['passenger-home'])` (`home.py:10`). `prefix` is added in front of every path here. `tags` is just a label for the auto docs page.
- `service = HomeService()` (`home.py:11`). One shared service object is made when the file is imported.
- `@router.get('/home', response_model=HomeResponse)` (`home.py:14`). Registers `GET /passengers/me/home`.
- `def get_home(passenger=Depends(get_current_passenger), db=Depends(get_db))` (`home.py:15-18`). A normal (not async) function. FastAPI runs normal functions in a worker thread, which is right here because SQLAlchemy calls block. Inputs come only from the two dependencies. Output is a `HomeResponse`.
- `return service.get_home(db, passenger)` (`home.py:19`). Asks the service to build the home data for this passenger using this session.

Errors: 401 from `get_current_passenger` if the token is missing or wrong. Other errors come from the service.

## 4. How data flows
```
Passenger app --GET /passengers/me/home + Bearer token--> FastAPI
  FastAPI -> get_current_passenger(token) -> Passenger
  FastAPI -> get_db() -> Session
  get_home -> HomeService.get_home(db, passenger) -> HomeResponse
Passenger app <-- JSON
```

## 5. Try it
```zsh
curl -s -H "Authorization: Bearer <token>" http://127.0.0.1:8000/passengers/me/home
```
`-H` adds a header. `<token>` is the access token you get after login. Expected: JSON with home data such as ride categories (the exact fields are in `schemas/home.py`). Add the API prefix if your app uses one.

## 6. Can it be better?
- Good: the route has no logic. All rules live in the service. That is easy to test.
- Weak: `service = HomeService()` is a module global, so tests cannot swap it easily.
- Cleaner way: `def get_service() -> HomeService` used with `Depends`, so tests can override it. (Opinion.)
- Security: auth is enforced by the dependency. Good.

## 7. Check yourself
1. What does `Depends(get_db)` do before `get_home` runs?
2. Why is the real work in `HomeService` and not in this route?
