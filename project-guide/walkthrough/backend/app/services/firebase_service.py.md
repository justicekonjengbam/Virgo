# backend/app/services/firebase_service.py

## 1. Purpose
This tiny file starts the Firebase Admin library one time. Firebase is Google's service that sends the SMS code and proves a phone number is real. Both `auth_service.py` and `driver_auth_service.py` call `initialize_firebase()` before they verify a token. It reads `config.py` for the path of the credential file.

## 2. Imports, one by one

### Standard library
- `from pathlib import Path` (`firebase_service.py:1`). A class for file paths. *Example:* `Path('a.json').is_file()` is `True` if that file exists. Used to check the credential file.

### Third-party
- `import firebase_admin` (`:3`). Google's server-side Firebase library. *Example:* `firebase_admin.initialize_app(cred)` connects the app to a project.
- `from fastapi import HTTPException, status` (`:4`). HTTP error and named codes. Used for a 503.
- `from firebase_admin import credentials` (`:5`). Loads a service-account file (a JSON key file for a robot account). *Example:* `credentials.Certificate('key.json')`.

### Project
- `from app.core.config import get_settings` (`:7`) from `backend/app/core/config.py`. Gives `firebase_credentials_path`, set by the environment variable `FIREBASE_CREDENTIALS_PATH`.

## 3. Walk through the code

### `initialize_firebase() -> None` (`:10-20`)
**What it does:** makes sure Firebase Admin is started exactly once.
1. `if firebase_admin._apps: return` (`:12-13`). `_apps` is a private dict of started apps. An empty dict is false. If an app exists, do nothing. (A leading underscore means "internal, may change"; see "Can it be better?".)
2. Read the credential path from settings (`:14`).
3. If the path is empty or not a real file, raise 503 Service Unavailable with a message naming the setting (`:15-19`). The message does not reveal the path or file contents.
4. `firebase_admin.initialize_app(credentials.Certificate(credential_path))` starts the app (`:20`). `Certificate(path)` reads the JSON key. It raises `ValueError` if the JSON is invalid; that error is not caught here.
Input: none. Output: none. *Example:* first call starts Firebase; later calls return at once.

## 4. How data flows
```
AuthService / DriverAuthService
   -> initialize_firebase()
        _apps non-empty? -> return
        get_settings().firebase_credentials_path
        file exists? no -> HTTP 503
        initialize_app(Certificate(<secret file>))
```

## 5. Try it
```bash
cd backend && uv run python -c "from app.services.firebase_service import initialize_firebase as f; f()"
```
`uv run python -c` runs one Python line inside the project environment. With no credentials set, expected: a `HTTPException` 503 "Firebase Admin is not configured...". With a valid file, no output.

## 6. Can it be better?
- **Good:** safe to call many times; clear error; no secret in the message.
- **Weak:**
  - Uses private `firebase_admin._apps`. A cleaner way is `try: firebase_admin.get_app() except ValueError: ...`.
  - Not thread-safe: two requests at the first moment could both call `initialize_app` (the second raises `ValueError`). Initialise once at app start instead.
  - A bad key file raises an uncaught `ValueError` (500 error).
  - Throws an HTTP error from a non-HTTP helper, which ties it to FastAPI.
- **Cleaner way:**
```python
# before
if firebase_admin._apps:
    return
# after
try:
    firebase_admin.get_app(); return
except ValueError:
    pass
```
- **Security:** the key file is a secret (`<secret>`). Never commit it. Keep it outside git and set `FIREBASE_CREDENTIALS_PATH`.

## 7. Check yourself
1. Why is it safe to call `initialize_firebase()` many times?
2. What status code does a missing credential file produce, and why that code?
