# backend/app/schemas/profile.py

## 1. Purpose
This file defines the passenger profile answer and the request body for updating the profile. It also holds the rules: at least one field must change, and the email must look valid. The passenger profile route uses it. It imports only the standard library and Pydantic.

## 2. Imports, one by one
Standard library:
- `import re` (`profile.py:1`). **re** is Python's regular expression module. A **regular expression** is a pattern for matching text. *Example:* `re.fullmatch(r'\d+', '123')` matches, `'12a'` does not. Used to check the email shape.

Third party:
- `from pydantic import BaseModel, Field, field_validator, model_validator` (`profile.py:3`). **Pydantic** checks data against a class. `BaseModel` is the parent class. `Field` adds rules to one field. `field_validator` is a **decorator** (a `@` line that wraps a function) that checks or cleans one field. `model_validator` is a decorator that checks the whole object after all fields are read.

## 3. Walk through the code, top to bottom

### `PassengerProfileResponse` (`profile.py:6-10`)
Output: `full_name`, `phone_number`, `email` (nullable), `preferred_language` (a code like `"en"`).

### `PassengerProfileUpdateRequest` (`profile.py:13-32`)
Input for a partial update. All three fields are optional (`default=None`):
- `full_name`: 2 to 120 characters.
- `email`: max 254 characters (the common email size limit).
- `preferred_language`: 2 to 10 characters.
Note: `Field(min_length=...)` is only checked when a value is given. `None` is allowed.

**`at_least_one_field`** (`profile.py:18-22`)
- `@model_validator(mode='after')` runs after every field passed its own check. `self` is the finished object.
- If all three are `None`, it raises `ValueError('Choose at least one profile field to update.')`. Otherwise `return self`.
- The return type `'PassengerProfileUpdateRequest'` is in quotes because the class is not finished yet at that line. This is called a forward reference.
- Example: `PassengerProfileUpdateRequest()` raises an error. `PassengerProfileUpdateRequest(full_name="Asha")` works.

**`validate_email`** (`profile.py:24-32`)
- `@field_validator('email')` and `@classmethod`: runs for `email`; `cls` is the class.
- If `None`, return `None`.
- `value.strip().lower()` removes spaces at both ends and makes lowercase: `" Asha@X.com "` becomes `"asha@x.com"`.
- `re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', normalized)` demands the whole text be: one or more characters that are not space or `@`, then `@`, then the same, then a dot, then the same. `fullmatch` means the entire string must match, not just a part.
- If it does not match, raise `ValueError('Enter a valid email address.')`. Else return the clean email.
- Order note: Pydantic checks `max_length=254` first, then runs this function (I believe, since `field_validator` defaults to "after" mode).

## 4. How data flows
```
Passenger app --PATCH {"email":" Asha@X.com "}--> FastAPI
  -> PassengerProfileUpdateRequest: max_length check -> validate_email -> "asha@x.com"
  -> at_least_one_field passes
route/service saves -> PassengerProfileResponse -> JSON -> app
```

## 5. Try it
From `backend/`:
```
uv run python -c "from app.schemas.profile import PassengerProfileUpdateRequest as P; print(P(email=' Asha@X.com ').email); P()"
```
Expected: first prints `asha@x.com`, then `P()` raises a `ValidationError` with "Choose at least one profile field to update."

## 6. Can it be better?
- Good: normalizes the email; clear user messages; blocks empty updates.
- Weak: the regex accepts odd text like `a@b.c`; you cannot clear an email by sending `null` because `None` means "not changing"; name is not trimmed.
- Cleaner way: Pydantic offers `EmailStr` (needs the `email-validator` package) for stricter checks. Before: `email: str | None`. After: `email: EmailStr | None`. (Opinion: the regex is fine for a simple app.)
- Security: lowercasing prevents duplicate accounts by case. The regex is not a security measure; it only catches typos.

## 7. Check yourself
1. What does `at_least_one_field` stop, and when does it run compared with the field checks?
2. What does `re.fullmatch` do differently from checking only part of the text?
