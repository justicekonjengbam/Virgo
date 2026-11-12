# backend/app/services/driver_document_review_service.py

## 1. Purpose
An admin reviews one driver document (for example a driving licence) and marks it verified or rejected. This file saves that decision, then works out if the driver's vehicle is now verified, and activates the driver if everything is done. The admin API route calls `DriverDocumentReviewService.review`. It uses `DriverRepository` and the models.

## 2. Imports, one by one

### Standard library
- `from datetime import UTC, datetime` (`driver_document_review_service.py:1`). Used to stamp `reviewed_at`. *Example:* `datetime.now(UTC)`.

### Third-party
- `from fastapi import HTTPException, status` (`:3`). Raises a 404 error when the document does not exist.
- `from sqlalchemy.orm import Session` (`:4`). Database session type.

### Project
- `from app.repositories.driver_repository import DriverRepository` (`:6`). Queries: `get_document`, `get_active_vehicle`, `get_documents`.
- `from app.models.ride_hailing import Driver` (`:7`). Driver table class.
- `from app.schemas.admin_review import DriverDocumentReviewRequest, DriverDocumentReviewResponse` (`:8`). Request and answer shapes.

## 3. Walk through the code

### `class DriverDocumentReviewService` (`:11`)
Docstring: apply an admin decision and derive vehicle verification "atomically" (all saved together or not at all).

**`required_document_types`** (`:14-16`). A `set` of four names: `driving_licence`, `vehicle_registration`, `aadhaar`, `vehicle_insurance`. A set is an unordered list with no repeats, good for "is everything present?" checks. The same set is copied in `driver_readiness_service.py:10`.

**`__init__`** (`:18-19`). Takes an optional repository (dependency injection) or makes `DriverRepository()`.

**`review(db, driver_id, document_type, request, reviewer)`** (`:21-66`)
Inputs: session, the driver id, which document, the decision (`request.status`, `request.review_note`), and the admin's name `reviewer`. Output: `DriverDocumentReviewResponse`.
1. `self.repository.get_document(db, driver_id, document_type)` finds the row; none gives 404 (`:29-31`).
2. Set `verification_status`, a trimmed note (or `None`), `reviewed_by`, `reviewed_at` (`:33-36`).
3. Load the active vehicle, the driver, and all documents (`:38-40`).
4. If a vehicle exists (`:41`): build `statuses`, a dict `{document_type: status}` with a dict comprehension (`:42`).
   - Any `rejected` document makes the vehicle `rejected` (`:43-44`).
   - Else if all four required types exist and all are `verified`, the vehicle is `verified`. `A <= B` on sets means "A is a subset of B" (`:45-48`).
   - Otherwise `pending` (`:49-50`).
5. If the vehicle became verified and the driver was `pending`, the driver becomes `active` (`:52-54`).
6. `db.add(document)` and `db.commit()` save all changes in one transaction; `db.refresh(document)` reloads (`:56-58`).
7. Returns the response (`:59-66`); if there is no vehicle, vehicle status is shown as `'pending'`.
*Example:* licence verified, others still pending: vehicle stays `pending`. Last document verified: vehicle `verified`, driver `active`.

Note: the `document` is changed before `db.add`. The session already tracks it because it was loaded from the session, so `db.add` is harmless.

## 4. How data flows
```
Admin app --PATCH review--> route --> review()
   get_document -> DB
   set status/note/reviewer -> in memory
   get_active_vehicle, get_documents -> DB
   decide vehicle status, maybe driver.status='active'
   COMMIT -> DB
Admin app <-- DriverDocumentReviewResponse
```

## 5. Try it
Not directly runnable. You can test the subset rule:
```bash
python3 -c "r={'a','b'}; print(r <= {'a':1,'b':2,'c':3}.keys())"
```
Expected `True`. It means every required name is present.

## 6. Can it be better?
- **Good:** one commit for all changes; clear rules; 404 on unknown document.
- **Weak:**
  - `required_document_types` is duplicated in `driver_readiness_service.py`. If one changes and the other does not, the rules disagree.
  - The vehicle rule is also similar to `DriverReadinessService.reconcile`.
  - A driver who is `active` and later has a document rejected stays active; only the vehicle status changes.
  - If `vehicle` is `None`, a verified document does nothing for the driver status.
  - No check that `request.status` is only a valid value here (the schema in `schemas/admin_review.py` should do it; check).
- **Cleaner way:** put `REQUIRED_DOCUMENT_TYPES` in one module and import it in both services.
- **Security:** `reviewer` should come from the logged-in admin token, not from the request body. Check the route.

## 7. Check yourself
1. When does the vehicle become `verified`?
2. Why is `db.commit()` called once at the end and not after every change?
