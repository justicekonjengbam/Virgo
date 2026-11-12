# backend/app/services/emergency_contact_service.py

## 1. Purpose
This file gives a passenger their list of emergency contacts. In development it also fills in demo contacts when the passenger has none. The docstring (`emergency_contact_service.py:10`) says CRUD (create, read, update, delete) is intentionally deferred. An emergency route calls `list_for_passenger`.

## 2. Imports, one by one

### Third-party
- `from sqlalchemy import select` (`:1`). Builds a SELECT query.
- `from sqlalchemy.orm import Session` (`:2`). Session type.

### Project
- `from app.models.ride_hailing import EmergencyContact` (`:4`). The contacts table class.
- `from app.models.user import Passenger` (`:5`). The passenger class (type hint).
- `from app.schemas.emergency import EmergencyContactResponse` (`:6`). Answer shape.

## 3. Walk through the code

### `demo_contacts` (`:12-16`)
Tuples of `(name, phone, relationship)`: Mom, Dad, and a support line. These are demo values.

### `legacy_demo_names` (`:17`)
A set of three old demo names (`Ananya Sharma`, `Rahul Patil`, `Cab Sure Safety Desk`). Used to detect old seeded data to be replaced.

### `list_for_passenger(db, passenger)` (`:19-31`)
1. `db.scalars(select(EmergencyContact).where(passenger_id == ...).order_by(id)).all()` returns this passenger's contacts as a list (`:20`). `scalars` gives the objects themselves, not rows.
2. If the list is empty, or the set of names equals the legacy set (`{item.name for item in contacts}` is a set comprehension) (`:21`):
   - With old contacts: `zip(contacts, self.demo_contacts, strict=True)` pairs them one by one and overwrites name, phone, and relationship (`:22-26`). `strict=True` raises `ValueError` if lengths differ (3 and 3 here). The unpacking `(name, phone, relationship)` inside the loop reads each tuple.
   - With none: `db.add_all(...)` inserts three new rows (`:27-28`).
   - `db.commit()` saves, then the list is read again (`:29-30`).
3. Returns `EmergencyContactResponse` items (`:31`).
*Example:* a new passenger gets three demo contacts on the first call, and the same three later.

## 4. How data flows
```
Passenger app --GET emergency contacts--> route --> list_for_passenger
   SELECT contacts --> DB
   empty? -> INSERT 3 demo rows, COMMIT, SELECT again
Passenger app <-- list of 3 contacts
```

## 5. Try it
Not directly runnable. See the pairing rule:
```bash
python3 -c "print(list(zip([1,2,3],'abc',strict=True)))"
```
Expected `[(1, 'a'), (2, 'b'), (3, 'c')]`.

## 6. Can it be better?
- **Good:** scoped by `passenger_id`; ordered; the legacy migration is handled.
- **Weak:**
  - A GET request writes data and invents contacts. A real passenger would see "Mom" and "Dad" they never added, and fake phone numbers could be dialled in an emergency. That is dangerous in production.
  - Same query written twice (`:20`, `:30`).
  - `strict=True` fails if someone has only some contacts and they match the legacy names count differently.
  - Names, phones and the legacy rewrite logic are inside the service.
- **Cleaner way:** move seeding to a development-only script or a `settings.is_development` check; let the app have real add/edit screens.
- **Security:** the demo seeding should be off in production. Phone numbers here are demo data, not secrets.

## 7. Check yourself
1. When does `list_for_passenger` write to the database?
2. What does `strict=True` in `zip` do?
