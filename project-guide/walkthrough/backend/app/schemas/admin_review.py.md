# backend/app/schemas/admin_review.py

## 1. Purpose
This file holds the two message shapes for an admin who reviews a driver's document: the request (verify or reject) and the response. The admin route that reviews documents uses them, and the admin-app calls that route. It only calls `pydantic`.

## 2. Imports, one by one
- `from datetime import datetime` (`admin_review.py:1`). A date+time type, used by `reviewed_at`.
- `from typing import Literal` (2). Limits a value to exact choices.
- `from pydantic import BaseModel, Field, model_validator` (4). **Pydantic** checks data against type hints. `BaseModel` is the base class, `Field` adds limits, `model_validator` checks the whole object. *Example:* `Field(max_length=500)` rejects a 600-letter note.

## 3. Walk through the code, top to bottom
- `DocumentReviewStatus = Literal['verified','rejected']` (7). Only these two values are allowed. A reviewer cannot send `'pending'`.
- `DriverDocumentReviewRequest` (10-18). `status` and optional `review_note` (default `None`, max 500). `rejected_documents_need_a_reason` (14-18) is a model validator that runs after the fields are valid. If status is `rejected` and the note is empty or blank, it raises `ValueError('Provide a review note when rejecting a document.')`. Otherwise it returns `self`. Example: `{"status":"verified"}` is fine; `{"status":"rejected"}` fails with a 422 response.
- `DriverDocumentReviewResponse` (21-27). Returns `driver_id`, `document_type`, `document_status`, `vehicle_verification_status`, `reviewed_at` (may be `None`), `review_note`.

## 4. How data flows
```
admin-app --PATCH {status:'rejected', review_note:'blurry'}--> route
   -> DriverDocumentReviewRequest ok -> service updates DriverDocument
   -> DriverDocumentReviewResponse -> JSON back
```

## 5. Try it
```zsh
cd backend
uv run python -c "
from app.schemas.admin_review import DriverDocumentReviewRequest as R
print(R(status='verified'))
R(status='rejected')"
```
The first prints `status='verified' review_note=None`. The second raises `ValidationError`.

## 6. Can it be better?
- Good: short, and the rule "reject needs a reason" is enforced before any database work.
- Weak: `document_status` and `vehicle_verification_status` in the response are plain `str`. The note is not stripped before saving. The model's real statuses (`pending`, `expired`) differ from this Literal, which is fine but easy to forget.
- Cleaner way: reuse a shared `Literal` for statuses in one file.
- Security: none directly. The route must check the admin's permission.

## 7. Check yourself
1. Which `status` values can the request carry?
2. When is `review_note` required?
