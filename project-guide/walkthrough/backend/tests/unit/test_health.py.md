# backend/tests/unit/test_health.py

## 1. Purpose
A **health check** is a tiny web address (`/health`) that answers "is the server alive?". This test calls it and checks the answer. It exercises `app.main.app` (`backend/app/main.py:40`) and the router `health_router` (`main.py:9`, included at `:32`).

## 2. Imports, one by one
- `from fastapi.testclient import TestClient` (`:1`). **FastAPI** is the web framework used by the backend. `TestClient` is a fake web browser that calls the app directly in memory, without starting a real server on a port. *Example:* `TestClient(app).get('/health')`.
- `from app.main import app` (`:3`). The real FastAPI application object. Importing it runs `create_app()` (`main.py:21-37`), which initialises the database and creates the first admin if settings say so.

## 3. Walk through the code
`def test_health_check() -> None:` (`:6`) is the single test.
- `TestClient(app).get('/health')` (`:7`) sends an HTTP GET request (a "read" request, like opening a page). Returns a response object.
- `response.status_code == 200` (`:9`): 200 means "OK".
- `response.json() == {...}` (`:10-14`): the body must be exactly `{'status': 'OK', 'version': '1.0', 'environment': 'development'}`.

Fails if the status is not 200 or the JSON differs. Note that `environment: 'development'` depends on your settings: if `.env` sets another environment, the test fails. I am not sure of the setting name; check `backend/app/core/config.py`.

## 4. How data flows
```
pytest -> TestClient --GET /health--> FastAPI app --> health router
                                                  <-- 200 {"status":"OK",...}
assert status and body
```

## 5. Try it
```zsh
cd backend
uv run pytest tests/unit/test_health.py -v
```
Expected: `1 passed`. Or start the server and run `curl -s localhost:8000/health` (`curl` fetches a URL, `-s` hides progress) to see the same JSON.

## 6. Can it be better?
- Good: smallest useful smoke test (a quick check that "nothing is badly broken").
- Weak: it hardcodes the environment name, so it depends on the machine's config. Importing `app.main` touches the real database file at import time.
- Cleaner way (opinion): set the environment variable in the test (monkeypatch), or only assert `status == 'OK'`.
- Security: the health endpoint exposes version and environment; this is low risk but do not add secrets to it.

## 7. Check yourself
1. Why does `TestClient` not need a running server?
2. What can make this test fail even when the code is correct?
