# OutstationBookingScreen.tsx

## 1. Purpose
The screen where a passenger plans a long-distance ride (over 150 km). Steps: pick a route, pick date and time, pick an optional car type, get an estimate, then send the request to support. It also lists past requests and lets the user cancel. It lives in `features/outstation/screens/`. The navigator renders it with pickup/destination from shared state. It calls `outstationService`, and uses `CabSureMap` and `AppPageHeader`.

## 2. Imports, one by one
- `import { useEffect, useMemo, useState } from 'react';` State, run-after-draw, and remember-a-calculation hooks.
- `import { ActivityIndicator, Alert, Modal, Pressable, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` `Alert` shows a native popup (`Alert.alert('Title','Text')`). `Modal` shows a layer above the screen. `ActivityIndicator` is a spinner. Others as in other screens.
- `MaterialCommunityIcons` icon font.
- `DsButton, DsCard, DsText` from `../../../components/design-system`.
- `AppPageHeader` from `../../../components/navigation/AppPageHeader`.
- `colors, radius, spacing` from `../../../theme`.
- `type LocationOption` from `../../booking/data/bookingApi`.
- `CabSureMap` from `../../maps/components/CabSureMap`.
- `outstationService`, types `OutstationBooking`, `OutstationEstimate` from `../services/outstationService`.

## 3. Walk through the code, top to bottom
**Types** `Props`, `Picker` (lines 12-13). `Picker` is `'date' | 'time' | null` (which sheet is open).

**`OutstationBookingScreen`** (lines 15-26).
- Lines 16-17: state: `date`, `hour` (9), `minute` (0), `period` AM/PM, `picker`, `preference` (sedan/suv/muv/null), `estimate`, `bookings` (null = loading), `busy`, `error`.
- Line 18 `scheduled`: with `useMemo`, builds a `Date` from date + 12-hour clock. `(hour % 12) + (PM ? 12 : 0)` converts to 24-hour. *Example:* 12 AM -> 0; 12 PM -> 12; 3 PM -> 15.
- Line 19 `load`: fetches the list and stores it, or sets an error.
- Line 20: first effect runs `load` once. Second effect clears the estimate whenever pickup, destination, time or preference changes (an old estimate must not be sent for a new route). Note: `useEffect(load, [])` passes `load`, which returns nothing useful (it returns `void`), so it is fine.
- Line 21 `input`: returns the request body, or null if something is missing. `toISOString()` makes a UTC time text like `2026-03-05T09:00:00.000Z`.
- Line 22 `calculate`: calls `estimate`, stores it. `finally` ends busy.
- Line 23 `submit`: calls `create`, reloads the list, resets the form, calls `onClearLocations()`, and shows an Alert that support will confirm.
- Line 24 `cancel`: an Alert with two buttons. "Cancel request" calls `outstationService.cancel(id, 'Passenger changed travel plans')`, then `load`, or shows an error Alert. The reason is a fixed text.
- Line 25: the UI. Sections: hero card; "1. Choose your route" with two `LocationSelector`s and a map when both are set (the route line comes from `estimate?.route_geojson`); "2. Choose departure" with two `PickerButton`s; car options (tapping the chosen one again clears it); `EstimateCard` or an info note; error text; a button that is either "Send request" (after estimate) or "Calculate" (disabled until route and time exist); the "Your requests" list; and the `SchedulePicker` modal.

**`LocationSelector`** (28), **`PickerButton`** (29): tappable rows.

**`EstimateCard`** (30): shows distance, time as `Math.floor(min/60)` hours and `min%60` minutes, and the fare `Math.round(paise/100).toLocaleString('en-IN')` (*example:* 1234567 paise -> `₹12,346`). Shows a disclaimer.

**`SchedulePicker`** (31): returns `null` when `type` is null. Otherwise a bottom-sheet `Modal` with `Calendar` or `TimePicker`. It keeps its own `month` state. Hook rule note: the `useState` is called before the early `return null`, which is correct.

**`Calendar`** (32): the minimum date is now plus 4 hours; the maximum is 180 days ahead. Previous month is disabled when already in the minimum month; next is disabled at the maximum. Day cells outside the range are disabled and grey. Weekday header letters use `index` in the key because letters repeat (S, T).

**`TimePicker`** (33): hours 1-12 (`Array.from({length:12}, (_, i) => i + 1)`), minutes 0/15/30/45, and AM/PM, via `Choice` buttons.

**`Choice`** (34): a toggle chip. **`BookingCard`** (35): shows booking id, date/time, status (underscores replaced by spaces), addresses, estimate, driver info or a "support is handling" text, and a cancel button if `can_cancel`.

**Date helpers** (36): `startDay` (midnight), `startMonth` (first day), `addMonths`, `sameMonth`, `sameDay`, `calendarCells` (leading `null`s for the weekday offset, then each date). *Example:* if the month starts on Wednesday (`getDay()` = 3), there are 3 `null` blanks first.

**`styles`** (37): one-line style table. `'14.28%'` is 1/7 of the width for a 7-day week.

## 4. How data flows
```
user picks pickup/destination (parent state) + date/time + car
 -> calculate() -> outstationService.estimate -> POST /outstation-estimates -> backend
 <- estimate (fare, route) -> EstimateCard + route on CabSureMap
 -> submit() -> POST /outstation-bookings -> backend -> support team
 -> list refreshed -> Alert "Request sent to support"
```

## 5. Try it
Not directly runnable alone. Run the app, open Outstation, choose two places far apart, pick a date at least 4 hours ahead, tap Calculate. Expected: distance, time and fare appear, then "Send request" is shown.

## 6. Can it be better?
- Good: clear step flow; estimate resets when inputs change; date limits; safe handling of busy and error.
- Weak:
  - A 2,000-character component in a few dozen very long lines; split into files (`Calendar.tsx`, `TimePicker.tsx`, `BookingCard.tsx`) and format.
  - `useEffect(load, [])` and the effect using `scheduled?.getTime()` may trigger lint warnings.
  - The 4-hour and 180-day limits are magic numbers, and the 150 km rule is only in text; the backend must enforce them.
  - The cancel reason is hard-coded.
  - Time zone: `toISOString` sends UTC; the backend should show local time back.
  - Selecting a date in the same day with a time less than 4 hours ahead is not blocked (the time picker does not check).
  - `hour % 12` with `hour = 12` works, but the display shows what the user picked, so that is fine.
  - No tests.
- Security: the backend must verify ownership on cancel and recheck distance/time rules. Fare shown is only an estimate (the text says so).

## 7. Check yourself
1. How does the code turn "3:00 PM" into a 24-hour `Date`?
2. Why is the estimate cleared in the effect on line 20?
