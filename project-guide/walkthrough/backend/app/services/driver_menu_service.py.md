# backend/app/services/driver_menu_service.py

## 1. Purpose
This file supplies the content for the driver app menu: a ride request card, the trip history, and support articles. The docstring (`driver_menu_service.py:9`) says it is backend-owned content "until live dispatch is introduced". Driver menu routes call `DriverMenuService`.

## 2. Imports, one by one

### Third-party
- `from sqlalchemy import select` (`:1`). Builds SELECT queries. *Example:* `select(Ride)`.
- `from sqlalchemy.orm import Session` (`:2`). Database session type.

### Project
- `from app.models.ride_hailing import FareQuote, Ride, RideCategory` (`:4`). Table classes.
- `from app.schemas.driver_menu import DriverRideRequestResponse, DriverSupportArticleResponse, DriverTripHistoryItemResponse` (`:5`). Answer shapes (Pydantic classes that check and convert data to JSON).

## 3. Walk through the code

### `support_articles` (`:11-16`)
A tuple of four 3-item tuples: `(id, title, body)`. A tuple is a fixed list. Plain text for the help screen.

### `current_ride_request()` (`:18-27`)
Returns a fixed fake `DriverRideRequestResponse` (pickup `MG Road, Hubballi`, 3.5 km, 18000 paise = Rs 180, 4 minutes away). The comment (`:19-21`) says it is a temporary fixture so the mobile screen keeps working when real matching arrives. No inputs. *Example:* every call returns the same card.

### `trip_history(db, driver_id)` (`:29-44`)
Gets the last 30 completed trips.
- `select(Ride, RideCategory, FareQuote)` asks for three tables at once, so each result row is a 3-tuple.
- `.join(RideCategory, Ride.category_id == RideCategory.id)` is an INNER JOIN (keep only matching rows).
- `.outerjoin(FareQuote, (FareQuote.ride_id == Ride.id) & FareQuote.is_final.is_(True))` is a LEFT JOIN: keep the ride even if no final fare exists, giving `None`. `&` is SQL AND.
- `.where(Ride.driver_id == driver_id, Ride.status == 'completed')`, `.order_by(Ride.completed_at.desc())` newest first, `.limit(30)`.
- `db.execute(...).all()` runs it and returns a list of rows.
- The list comprehension unpacks `for ride, category, fare in rows` and builds items. `fare.amount_paise if fare else 0` handles a missing fare (`:43`).

### `support()` (`:46-47`)
Turns each tuple into `DriverSupportArticleResponse(id=item[0], title=item[1], body=item[2])`.

## 4. How data flows
```
Driver app --GET trips--> route --> trip_history(db, driver.id)
    SELECT rides JOIN categories LEFT JOIN fare_quotes --> DB
    rows -> DriverTripHistoryItemResponse list
Driver app <-- JSON list (max 30)
```

## 5. Try it
Not directly runnable. The support content can be printed:
```bash
cd backend && uv run python -c "from app.services.driver_menu_service import DriverMenuService as S; print(S().support()[0])"
```
Expected: one article object with id `ride-requests`.

## 6. Can it be better?
- **Good:** the left join keeps trips whose fare is missing; limit protects the size; read-only.
- **Weak:**
  - `current_ride_request` returns fake data. A driver app could show a ride that does not exist. Mark clearly or remove when dispatch is real (`ride_matching_service.py` already exists, so this may already be unused).
  - `item[0]`, `item[1]` are unclear; use a `NamedTuple` or dataclass.
  - No paging for history, only a hard 30.
  - Article text mentions "Tier 2 and Tier 3 service areas" in the app text; keep text in one content place.
- **Cleaner way:**
```python
# before
DriverSupportArticleResponse(id=item[0], title=item[1], body=item[2])
# after
DriverSupportArticleResponse(**dict(zip(('id','title','body'), item)))
```
- **Security:** `driver_id` must come from the logged-in token. It does here (parameter), so no other driver's history can be read as long as the route passes `driver.id`.

## 7. Check yourself
1. Why `outerjoin` for `FareQuote` and not `join`?
2. What does the comment at `:19-21` promise about `current_ride_request`?
