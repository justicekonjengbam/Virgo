# backend/app/api/v1/routes/emergency_contacts.py

## 1. Purpose
One route that lists a passenger's emergency contacts (people to alert in an emergency). Used by `passenger-app/`. Mounted at `router.py:28`. Calls `EmergencyContactService`. URL: `/api/v1/passengers/me/emergency-contacts`.

## 2. Imports, one by one
- `from fastapi import APIRouter, Depends` (`emergency_contacts.py:1`): router and dependency injection.
- `from sqlalchemy.orm import Session` (`:2`): session type.
- `get_current_passenger` (`:4`, `app/api/dependencies/auth.py`), `get_db` (`:5`), `Passenger` (`:6`, `app/models/user.py`).
- `EmergencyContactResponse` from `app/schemas/emergency.py` (`:7`): JSON shape of one contact.
- `EmergencyContactService` (`:8`, `app/services/emergency_contact_service.py`).

## 3. Walk through the code, top to bottom
- `router = APIRouter(prefix='/passengers/me/emergency-contacts', ...)` (`:10`) and `service` (`:11`).
- **`get_emergency_contacts`** `GET ''` (`:14-16`). The empty path means the URL is the prefix itself. `service.list_for_passenger(db, passenger)` returns the contacts of the logged-in passenger as `list[EmergencyContactResponse]`. *Example result:* `[{"name":"Mum","phone":"..."}]` (field names unverified).
- Only a list route exists. There is no add, edit or delete route in this file.

## 4. How data flows
```
passenger-app --GET + Bearer--> get_current_passenger -> Passenger
   -> service.list_for_passenger --SELECT--> database
   <- list of contacts (JSON)
```

## 5. Try it
`curl -s -H "Authorization: Bearer <secret>" localhost:8000/api/v1/passengers/me/emergency-contacts`. Expect a JSON list, maybe `[]`.

## 6. Can it be better?
- Good: very small; data tied to the token's passenger.
- Weak: read-only. If the app needs to add contacts, routes are missing (check `rg emergency passenger-app/` and other route files such as `passenger_profile.py`).
- Security: login-only; contact phone numbers are personal data, so avoid logging them.

## 7. Check yourself
1. Why is the route path an empty string?
2. How does the service know whose contacts to return?
