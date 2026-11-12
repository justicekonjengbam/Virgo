# homeTypes.ts

## 1. Purpose
Pure TypeScript type definitions for the Home data. No code runs here. `homeApi.ts` uses `PassengerHome`. The Home screen uses the smaller types. Field names are snake_case because the backend sends them that way.

## 2. Imports, one by one
None.

## 3. Walk through the code, top to bottom
**Type alias** (a name for a shape. *Example:* `type P = { x: number }` means a P has a number x).
- Line 1: `SavedPlace`: `id`, `label` (like "Home"), `formatted_address`, `latitude`, `longitude` (numbers).
- Line 2: `RideCategory`: `id`, `code`, `display_name`, `seat_count`, `base_fare_paise`, `estimated_arrival_minutes`, `icon_key`. **Paise** (1/100 of a rupee, stored as whole numbers so money has no decimal errors. *Example:* 5000 paise = Rs 50).
- Line 3: `RecentRide`: `id`, `pickup_address`, `destination_address`, `completed_at` (`string | null`, a date text or nothing), `final_duration_seconds` (`number | null`), `fare_paise`.
- Line 4: `PassengerHome`: `passenger_name` plus three lists: `saved_places`, `ride_categories`, `recent_rides`.

## 4. How data flows
```
backend JSON -> typed as PassengerHome -> screens read fields
```

## 5. Try it
Not runnable. Check types with `cd passenger-app && npx tsc --noEmit` (`tsc` is the TypeScript checker; `--noEmit` only checks and writes no files). Expected: no errors.

## 6. Can it be better?
- Good: precise, with nullable fields marked.
- Weak: all four types sit on single long lines. Types are written by hand and can drift from the backend schema. Dates are plain strings.
- Cleaner way: generate types from the backend OpenAPI schema (opinion).
- Security: none.

## 7. Check yourself
1. Why is `completed_at` typed `string | null`?
2. What unit is `base_fare_paise` in?
