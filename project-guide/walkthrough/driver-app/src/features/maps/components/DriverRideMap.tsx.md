# DriverRideMap.tsx

## 1. Purpose
A map component for the driver. It shows pickup and destination markers, an optional route line, the driver's own dot, and a credit line. Ride screens in `driver-app/src/features/rides` use it (I did not list them; run `rg DriverRideMap driver-app/src`). It calls `driverMapService.ts` for the style URL.

## 2. Imports, one by one
- `import { useEffect, useMemo, useState } from 'react';` (`driver-app/src/features/maps/components/DriverRideMap.tsx:1`): `useMemo` remembers a calculated value until inputs change.
- `import { StyleSheet, View } from 'react-native';` (line 2): box and style helper.
- `import { Camera, GeoJSONSource, Layer, Map, Marker, UserLocation } from '@maplibre/maplibre-react-native';` (line 3): MapLibre pieces. `Map` draws the map. `Camera` sets what part is visible. `UserLocation` shows the blue dot. `Marker` puts a view at a coordinate. `GeoJSONSource` feeds shape data (**GeoJSON** is a JSON format for shapes; *example:* a `LineString` with coordinate pairs). `Layer` says how to paint that data (here, a line).
- `MaterialCommunityIcons` (line 4): icon set.
- `DriverText` (line 6), `colors, radius, spacing` (line 7): shared UI parts.
- `getMapConfiguration` (line 8) from `../services/driverMapService`.

## 3. Walk through the code
- Types (lines 10-11): `Coordinate` is `{ latitude, longitude }`. `Props` has `pickup`, `destination`, optional `driver`, optional `route` (GeoJSON geometry) and `height`.
- **`DriverRideMap({ pickup, destination, driver, route, height = 300 })`** (line 13).
  - State `styleUrl` (null until loaded) and `failed` (lines 14-15).
  - Line 16: on first draw, load the config; on success keep `style_url`, on error set `failed`.
  - Line 17: `points` = pickup, destination and the driver if present. `...(driver ? [driver] : [])` adds the driver only when set.
  - Line 18: `mapBounds` = box that contains all points.
  - Line 19: while loading or on failure, show a placeholder box with "Loading map…" or "Map is unavailable".
  - Line 20: the real map. `mapStyle={styleUrl}` picks the look. `onDidFailLoadingMap` flips to the failure view. `Camera initialViewState={{ bounds, padding }}` zooms to fit all points with 48 px padding. `UserLocation accuracy animated heading` shows the driver dot, accuracy circle and direction. If `route` exists, a line layer is drawn with `colors.primary` and width 5. Two `RideMarker`s are placed. A small credit text "© OpenStreetMap · Geoapify" is overlaid (required by the data licenses).
- **`RideMarker`** (line 23): a `Marker` anchored at its bottom, at `lngLat={[longitude, latitude]}`. Note the order: longitude first, as in GeoJSON.
- **`bounds(points)`** (line 24): returns `[minLng, minLat, maxLng, maxLat]`. *Example:* points (77,12) and (78,13) give `[77,12,78,13]`.
- `styles` (line 25): container clipped with `overflow: 'hidden'` so rounded corners cut the map; the credit box is `position: 'absolute'` at the bottom right.

## 4. How data flows
```
Screen --(pickup, destination, driver, route)--> DriverRideMap
DriverRideMap -> getMapConfiguration() -> backend /maps/config -> style_url -> <Map>
```

## 5. Try it
Not directly runnable. Open an active ride in the driver app; the map shows two markers and the route.

## 6. Can it be better?
- Good: graceful fallback, bounds fit, credit shown.
- Weak: `bounds` with zero-size box (pickup equals destination) may zoom in extremely. The hard-coded attribution text ignores the `attribution` field from the config. No retry button after failure. The Camera only uses initial bounds, so it does not follow later driver movement.
- Cleaner way: use `config.attribution` and store it in state.
- Security: the style URL may hold a provider key (not checked).

## 7. Check yourself
1. In `lngLat`, which value comes first?
2. What does the user see if the config request fails?
