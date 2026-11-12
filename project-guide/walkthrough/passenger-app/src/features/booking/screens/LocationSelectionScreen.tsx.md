# LocationSelectionScreen.tsx

File: `passenger-app/src/features/booking/screens/LocationSelectionScreen.tsx` (66 lines)

## 1. Purpose
The place picker. The passenger can type to search, tap the map to drop a pin, or use the current GPS position. Then they confirm one place. It is used for pickup and destination, and for local or outstation trips (`scope`). It calls `mapService` (search and reverse lookup) and reports the choice through `onSelected`. A parent (not read here) renders it. Note: line 1 starts with a hidden BOM character (byte order mark, an invisible character at file start); it is harmless but unneeded.

## 2. Imports, one by one
- `useEffect, useRef, useState` from `react`. `useRef` keeps a value that survives redraws without causing one (*Example:* `const r = useRef(0); r.current = 5`).
- `react-native`: `ActivityIndicator`, `Pressable` (tappable), `SafeAreaView`, `ScrollView`, `StyleSheet`, `TextInput` (typing field), `View`.
- `LocationManager` from `@maplibre/maplibre-react-native`: MapLibre is an open-source map library. `LocationManager` reads the phone's GPS (*Example:* `await LocationManager.getCurrentPosition()`).
- `MaterialCommunityIcons` icons.
- Project: `DsButton`, `DsCard`, `DsText`; `AppPageHeader`; `colors`, `radius`, `spacing`, `typography` (`theme`); `CabSureMap` (`features/maps/components`); `mapService` (`features/maps/services/mapService`, talks to the backend map endpoints); type `LocationOption` (`../data/bookingApi`).

## 3. Walk through the code, top to bottom

### Props (13)
`title`, `onBack`, `onMenuPress`, `onSelected(location)` (may be async), `scope` (`'local'` default or `'outstation'`).

### State (16-22)
`query` (text), `locations` (results), `selected`, `loading`, `submitting`, `message` (hint text, first text depends on scope), and `skipNextSearch` (a ref).

### `selectCoordinates` (24-33)
Given latitude and longitude, `mapService.reverse(lat, lon, scope)` finds the address (**reverse geocoding**: coordinates to place). It sets `skipNextSearch.current = true`, so that setting the query text does not trigger a new text search. Then it selects the place, fills the text box, shows only that place, and shows "Pin selected". On failure it shows a scope-specific message.

### Search effect (35-42)
Runs when `query` or `scope` changes. If the skip flag is set, clear it and stop. If the trimmed text is shorter than 2 characters, clear results. Otherwise **debounce**: wait 350 ms (`setTimeout`) and then call `mapService.search(text, scope)`. The returned cleanup `clearTimeout(timer)` cancels the pending search when the user types another letter. This avoids one request per key press.

### `useCurrentLocation` (44-60)
1. Ask GPS permission: `LocationManager.requestPermissions()`.
2. `getCurrentPosition()`. If empty, wait up to 10 s (`10_000`) for a position using `addListener`; a Promise resolves with the first position or `undefined` (45-55).
3. If still none, show a message.
4. Call `selectCoordinates` with the position.
`return` inside `try` still runs `finally`, which stops loading.

### `confirm` (61)
If something is selected, set `submitting`, `await onSelected(selected)`, show an error on failure.

### JSX (63)
Header; search box with a magnifier, `TextInput`, and a spinner or a clear button; "Use my current location" button; map (`onMapPress` triggers `selectCoordinates`); message text; result list: `locations.map(...)` builds a key from `place_id`, `id` or coordinates, marks the active one, and draws a tappable card; footer button "Use this location", disabled until something is selected.

### `styles` (66)
Styles in one line; `input` spreads `...typography.body` (copies the theme text style).

## 4. How data flows
```
type "Dhar" -> setQuery -> (350ms wait) -> mapService.search -> Backend -> setLocations -> list
tap map -> selectCoordinates -> mapService.reverse -> place -> setSelected
tap result -> setSelected
"Use this location" -> confirm -> onSelected(place) -> parent stores and goes to next step
```

## 5. Try it
Not directly runnable alone. Run the app and open the pickup screen. Type two letters. Expected: a spinner for about a moment and then matching places.

## 6. Can it be better?
- Good: debounce; the ref avoids a search loop; permission and timeout handling; accessibility labels on controls.
- Weak: the search request is not cancelled, so a slow old answer can overwrite a newer one (race condition); a huge JSX line (63) and style line; the `skipNextSearch` flag is fragile (if `setQuery` gets the same text, the effect will not run and the flag stays set); the Dharwad-Hubballi 150 km limit is hard-coded in text (21, 31, 58) and should come from config; `LocationManager.addListener` is used in a nested Promise that is hard to read; no tests.
- Cleaner way: move search and GPS into a `usePlaceSearch` hook, and ignore stale answers with a request counter:
```ts
const id = ++latest.current;
mapService.search(q, scope).then(r => { if (id === latest.current) setLocations(r); });
```
- Security: asks only for location permission when the user taps the button (good). Coordinates are sent to the backend map service.

## 7. Check yourself
1. Why does the screen wait 350 ms before searching?
2. What does `skipNextSearch` prevent?
