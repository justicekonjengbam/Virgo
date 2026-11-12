# FareEstimateScreen.tsx

File: `passenger-app/src/features/booking/screens/FareEstimateScreen.tsx` (18 lines)

## 1. Purpose
Shows the price for the chosen pickup, destination and vehicle category, and a "Confirm ride" button that books the ride. A parent navigator (not read here) renders it. It calls `bookingApi.estimate` and `bookingApi.book`, and the shared `CabSureMap`.

## 2. Imports, one by one
- `import { useEffect, useState } from 'react';` `useState` gives a component memory (*Example:* `const [n,setN]=useState(0)`). `useEffect` runs code after the screen draws, and again when listed values change (*Example:* load data once on open).
- `from 'react-native'`: `SafeAreaView` (avoid notches), `ScrollView`, `StyleSheet`, `View`.
- Project: `AppPageHeader` (`components/navigation`, a top bar with back and menu); `DsButton`, `DsCard`, `DsEmptyState`, `DsLoading`, `DsText` (`components/design-system`: button, card, empty message, spinner, text); `colors`, `spacing` (`theme`); `bookingApi` and types (`../data/bookingApi`); `CabSureMap` (`features/maps/components/CabSureMap`, draws the map).

## 3. Walk through the code, top to bottom

### Props (9)
`pickup`, `destination` (LocationOption), `categoryId`, and callbacks `onBack`, `onMenuPress`, `onBooked(ride)`.

### State (11)
`estimate` (result or `null`), `error` (text or `null`), `booking` (true while booking).

### Effect (12)
`useEffect(() => { bookingApi.estimate(...).then(setEstimate).catch(() => setError('Unable to calculate your fare.')); }, [pickup, destination, categoryId]);`
On open, and whenever any of the three listed values changes, ask the backend for the estimate. `.then(setEstimate)` stores the answer. `.catch` stores a message. `void` before the call tells the linter the promise is left on purpose.

### Early returns (13-14)
If `error`, show an empty-state with a Back button. If no `estimate` yet, show a loading spinner "Calculating fare…". **Early return** means the function stops and draws only that.

### `book` (15)
Sets `booking`, calls `bookingApi.book(...)`, and passes the result to `onBooked`. On error it shows the error text (the error replaces the whole screen via line 13). `finally` turns `booking` off.

### JSX (16)
Header, map with route (`estimate.route_geojson`), a card with pickup and destination names, a card with category, distance, time, each fare item, and the total, then the confirm button. `₹ {item.amount_paise / 100}` converts paise to rupees. `estimate.fare_items.map(item => <View key=...>)` draws one row per fare item; `key` helps React track list rows.

### `styles` (18)
Layout rules: `gap`, `flexDirection: 'row'`, `justifyContent: 'space-between'` (label left, price right).

## 4. How data flows
```
open screen -> useEffect -> bookingApi.estimate -> Backend -> estimate -> setEstimate -> redraw
tap Confirm -> book() -> bookingApi.book -> Backend -> RideBooking -> onBooked(ride) -> parent shows BookingStatusScreen
```

## 5. Try it
Not directly runnable alone. Run the app, pick two places, pick a category. Expected: "Calculating fare…" then the price card.

## 6. Can it be better?
- Good: handles loading, error and success; busy flag on the button.
- Weak: `error` set during booking hides the whole screen, so the user must go Back and lose the estimate; `pickup`/`destination` objects as effect dependencies re-run the effect if the parent makes new objects each render; no cancel of the request if the screen closes (can set state on an unmounted screen); `amount_paise / 100` can print `12.5` instead of `12.50`; the code is dense on single lines.
- Cleaner way:
```ts
const rupees = (paise: number) => (paise / 100).toFixed(2);
```
- Security: money is only displayed here; the backend must recompute the fare when booking.

## 7. Check yourself
1. When does the estimate request run again?
2. Why does the screen return early before the main JSX?
