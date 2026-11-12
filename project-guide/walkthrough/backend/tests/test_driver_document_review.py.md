# backend/tests/test_driver_document_review.py

## 1. Purpose
Tests one business rule: a vehicle becomes `verified` only after every required driver document is verified by an admin. It builds a temporary database with a driver, a vehicle, and four documents, then reviews each one through `DriverDocumentReviewService` (`backend/app/services/driver_document_review_service.py`).

## 2. Imports, one by one
Third party:
- `from sqlalchemy import create_engine` : makes the database connection (`:1`).
- `from sqlalchemy.orm import sessionmaker` : a factory that makes **sessions**. A session is a work area for talking to the database; you add objects and then commit. *Example:* `Session = sessionmaker(bind=engine); s = Session()`.

Project:
- `Base` from `app/db`: parent of all models.
- `Driver, DriverDocument, DriverVehicleAssignment, Vehicle` from `app/models/ride_hailing.py`: table classes. The assignment links a driver to a vehicle.
- `DriverDocumentReviewRequest` from `app/schemas/admin_review.py`: the request body an admin sends (`status='verified'`).
- `DriverDocumentReviewService` from `app/services/driver_document_review_service.py`: the logic under test.
- `import app.models  # noqa: F401` registers all models; ruff would call it unused (`:8`).

## 3. Walk through the code, top to bottom
`test_vehicle_is_approved_only_after_every_required_document_is_verified` (`:11-30`)
1. `create_engine('sqlite://')` and `Base.metadata.create_all(engine)` build an empty in-memory database with all tables (`:12-13`).
2. `session = sessionmaker(bind=engine)()` : the trailing `()` calls the factory to get one session (`:14`).
3. `Driver(...)` and `Vehicle(...)` are plain Python objects for new rows (`:15-16`). Values are fake. `session.add_all([...])` queues them. `session.flush()` sends the SQL now, without finishing the transaction, so `driver.id` and `vehicle.id` get filled (`:17-18`).
4. `DriverVehicleAssignment(driver_id=..., vehicle_id=...)` links them (`:19`).
5. The loop (`:20-21`) adds one `DriverDocument` per name in `required_document_types`. In the service this is `{'driving_licence','vehicle_registration','aadhaar','vehicle_insurance'}` (`driver_document_review_service.py:14-16`). `session.commit()` saves all (`:22`).
6. `service = DriverDocumentReviewService()` : no repository given, so it makes its own `DriverRepository` (`service:18-19`).
7. The second loop (`:25-26`) calls `service.review(session, driver.id, document_type, DriverDocumentReviewRequest(status='verified'), 'test-admin')`. It sets that document to verified, records the admin name, and re-computes the vehicle status. It returns a result object (kept from the last loop turn).
8. Assertions (`:28-30`): the last result says `document_status == 'verified'` and `vehicle_verification_status == 'verified'`; `session.get(Vehicle, vehicle.id)` reloads the row from the database to prove it was saved.

Important: the test only proves the final state. It does not check the vehicle was still *not* verified after 1, 2, or 3 documents, even though the test name says "only after every". That check is missing.

## 4. How data flows
```
test -> session.add(driver, vehicle, assignment, 4 documents) -> commit
     -> service.review(doc1..doc4)  -> repository updates doc + vehicle status in session
     -> after doc4: all required verified -> vehicle.verification_status = 'verified'
     -> session.get(Vehicle) -> 'verified'
```

## 5. Try it
```zsh
cd backend && uv run pytest tests/test_driver_document_review.py -v
```
Expected: `1 passed`.

## 6. Can it be better?
- Good: a real end-to-end check through the service and database; fake data only.
- Weak: no "not yet verified" check in the middle; no rejected-document case; no test with a missing document; long lines (`:15-16`, `:21`); setup is copied across test files.
- Cleaner way (opinion): add inside the loop:
```python
for i, t in enumerate(types):
    result = service.review(...)
    assert (result.vehicle_verification_status == 'verified') == (i == len(types) - 1)
```
and move the session setup into a shared `conftest.py` fixture (a reusable setup function pytest provides to tests).
- Security: fake phone and registration values only. Good.

## 7. Check yourself
1. What is the difference between `session.flush()` and `session.commit()`?
2. Which part of the test is missing to really prove "only after every document"?
