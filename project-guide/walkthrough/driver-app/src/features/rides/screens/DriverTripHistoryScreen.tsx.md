# DriverTripHistoryScreen.tsx

## 1. Purpose
Shows the list of the driver's completed trips with fare. It loads once when opened. It calls `driverMenuService.getTripHistory()` from `features/dashboard/services/driverMenuService`.

## 2. Imports, one by one
- `import { useEffect, useState } from 'react';` (line 1). `useState` = memory for the screen; `useEffect` = run code after the screen shows.
- `import { ActivityIndicator, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` (line 2). Spinner, notch-safe box, scroll box, style helper, plain box.
- `MaterialCommunityIcons` (line 3): icon font (`history`, `map-marker-path`).
- `DriverPageHeader`, `DriverCard`, `DriverText` (lines 5-7): app components. `colors, spacing` (line 8): theme.
- `driverMenuService` and type `DriverTrip` (line 9): the service that fetches trips.

## 3. Walk through the code

**`DriverTripHistoryScreen({ onBack })`** (line 11).
- `trips` state (line 12): `null` = loading, `[]` = none, array = data.
- Effect (line 13): `driverMenuService.getTripHistory().then(setTrips).catch(() => setTrips([]))`. On success, trips are stored. On failure the list becomes empty, so the user sees "No completed trips yet" (the error is hidden; see section 6). `[]` means run once.
- Render (line 14): header; `ScrollView`; three cases using a nested ternary (`a ? x : b ? y : z`): spinner, empty card, or `trips.map(trip => <TripCard key={trip.id} trip={trip}/>)`.

**`TripCard({ trip })`** (line 16). Shows an icon, pickup, "to destination", category and date, and the fare. `new Date(trip.completed_at).toLocaleDateString('en-IN')` formats e.g. `26/10/2026`; if `completed_at` is missing it shows "Completed". Fare: `Math.round(trip.fare_paise / 100)`; paise are 1/100 rupee, so `12550` paise shows `₹126`.

**`styles`** (line 17).

## 4. How data flows
```
open -> useEffect -> driverMenuService.getTripHistory() -> backend -> DriverTrip[]
   -> setTrips -> map to TripCard rows
```

## 5. Try it
Not directly runnable alone. Open "Trip History" in the driver app. Expected: spinner, then cards or the empty message.

## 6. Can it be better?
- Good: short, three clear states.
- Weak: network errors look the same as "no trips" (line 13), which can mislead the driver. No refresh and no paging for a long history. No tests.
- Cleaner way:
```tsx
// before
.catch(() => setTrips([]))
// after
.catch(() => setError('Could not load trips. Pull down to retry.'))
```
- Security: none here beyond the token handled in `apiClient`.

## 7. Check yourself
1. What do `null`, `[]` and a filled array mean for `trips`?
2. How is 12550 paise shown on the card?
