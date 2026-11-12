# backend/app/schemas/emergency.py

## 1. Purpose
This file defines one **schema** (a class that describes the shape of data in an API answer) for an emergency contact. A passenger saves trusted people to call in danger. The emergency routes return this shape to the passenger app. It imports only Pydantic and calls nothing in the project.

## 2. Imports, one by one
- `from pydantic import BaseModel` (`emergency.py:1`). **Pydantic** is a library that checks data against a class. *Example:* `C(id="7")` turns `"7"` into `7` when `id: int`. `BaseModel` is the parent class that gives this behavior. Pydantic can also build JSON from the object.

## 3. Walk through the code, top to bottom

### `EmergencyContactResponse` (`emergency.py:4-8`)
- `id: int`: database id of the contact.
- `name: str`: the person's name. *Example:* `"Asha"`.
- `phone_number: str`: a string, not a number, so leading `+` and zeros are kept. *Example:* `"+919812345678"`.
- `relationship: str | None`: for example `"Mother"`. `| None` means it may be null. There is no default, so the caller must pass it (even as `None`).

Example: `EmergencyContactResponse(id=1, name="Asha", phone_number="9812345678", relationship=None)` is valid. Leaving out `relationship` raises an error.

## 4. How data flows
```
Passenger app --GET emergency contacts--> route --> database rows (EmergencyContact)
route --> EmergencyContactResponse(...) --> JSON --> Passenger app
```

## 5. Try it
From `backend/`:
```
uv run python -c "from app.schemas.emergency import EmergencyContactResponse as E; print(E(id=1,name='Asha',phone_number='98',relationship=None).model_dump())"
```
`model_dump()` turns the object into a plain dict. Expected: `{'id': 1, 'name': 'Asha', 'phone_number': '98', 'relationship': None}`.

## 6. Can it be better?
- Good: very small and clear.
- Weak: no length limit on `name` or `phone_number`; no `= None` default on `relationship`.
- Cleaner way: `relationship: str | None = None`.
- Security: phone numbers are personal data. Make sure the route only returns the logged-in passenger's own contacts (check the route file).

## 7. Check yourself
1. Why is `phone_number` a `str` and not an `int`?
2. What does `str | None` mean?
