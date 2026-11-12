# backend/tests/test_driver_auth_contract.py

## 1. Purpose
Tests the "contract" (the agreed shape of data) of the driver login and signup requests. They check that login needs only a Firebase token and that signup rejects an empty name. The schemas are in `backend/app/schemas/auth.py:50-59`. No database or network is used.

## 2. Imports, one by one
Third party:
- `import pytest` : the test tool; here `pytest.raises` is used (`:14`).
- `from pydantic import ValidationError` : Pydantic is the library that checks data against typed classes. It raises `ValidationError` when data breaks a rule. *Example:* a field with `min_length=2` given `"a"` raises it.

Project:
- `DriverFirebaseLoginRequest`, `DriverFirebaseSignupRequest` from `app/schemas/auth.py`. A **schema** is a class that describes the allowed fields of a request body.

## 3. Walk through the code, top to bottom
`test_driver_login_request_accepts_only_a_firebase_token` (`:7-10`)
- `DriverFirebaseLoginRequest(id_token="firebase-token")` builds the object. Pydantic checks it. `id_token` has `min_length=1` (`auth.py:53`).
- `assert request.id_token == "firebase-token"` checks the value was kept.
- The name says "only a token": the login schema has no phone or password field.

`test_driver_signup_requires_a_real_name` (`:13-18`)
- `with pytest.raises(ValidationError):` expects an error for `full_name=""`. The rule is `Field(min_length=2, max_length=120)` (`auth.py:59`), so an empty name is invalid.
- Then a valid signup with `"Asha Driver"` must succeed and keep the name.
- Note: `DriverFirebaseSignupRequest` extends the login class (`auth.py:56`), so `id_token` is inherited.

## 4. How data flows
```
test -> DriverFirebaseSignupRequest(id_token, full_name="")
     -> pydantic checks min_length=2 -> ValidationError -> pytest.raises catches -> pass
```

## 5. Try it
```zsh
cd backend && uv run pytest tests/test_driver_auth_contract.py -v
```
Expected: `2 passed`. For a quick look:
```zsh
uv run python -c "from app.schemas.auth import DriverFirebaseSignupRequest as R; R(id_token='x', full_name='')"
```
It prints a `ValidationError` mentioning `full_name`.

## 6. Can it be better?
- Good: tests the bad case and the good case; tiny and fast.
- Weak: does not test a one-letter name (`"A"`), a 121-character name, a missing token, or an empty token. The first test name says "only", but nothing proves extra fields are refused. I did not verify whether the schema forbids extra fields; check `auth.py:50-59`.
- Cleaner way (opinion): use `parametrize` with several bad names.
```python
@pytest.mark.parametrize('name', ['', 'A', 'x' * 121])
def test_bad_names(name): ...
```
- Security: the token values are fake strings, which is correct. Never put a real token in a test.

## 7. Check yourself
1. Which error class does Pydantic raise for bad data?
2. Why does the signup class also need `id_token`?
