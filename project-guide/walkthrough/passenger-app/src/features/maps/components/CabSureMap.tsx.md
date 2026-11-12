# CabSureMap.tsx

## 1. Purpose
A reusable map widget. It shows pickup, destination and driver markers, an optional route line, and the user's own location. It fetches the map style URL from the backend through `mapService`. It is used by screens such as `OutstationBookingScreen.tsx` (line 25 there) and other booking screens. It calls `mapService.configuration()` in `../services/mapService`.

## 2. Imports, one by one
- `import { useEffect, useMemo, useState } from 'react';` `useState` keeps memory, `useEffect` runs code after drawing, `useMemo` remembers a calculated value until its inputs change. *Example:* `useMemo(() => a + b, [a, b])`.
- `import { StyleSheet, View } from 'react-native';` Style table builder and box.
- `import { Camera, GeoJSONSource, Layer, Map, Marker, UserLocation } from '@maplibre/maplibre-react-native';` **MapLibre** is an open source map engine. `Map` draws the map. `Camera` sets where the view looks. `Marker` puts a view at a coordinate. `GeoJSONSource` feeds shape data (**GeoJSON** is a JSON format for shapes, such as a line made of points). `Layer` says how to draw a source (here a line). `UserLocation` shows the blue dot. *Example:* `<Map mapStyle={url}/>`.
- `MaterialCommunityIcons` icon font (line 4).
- `DsLoading, DsText` from `../../../components/design-system`; `colors, radius, spacing` from `../../../theme`; `mapService` from `../services/mapService`.

## 3. Walk through the code, top to bottom
**`Coordinate`, `Props`** (lines 10-11): types. All props are optional. `route` is a GeoJSON geometry; `GeoJSON.Geometry` comes from a global type package (I am not sure which one provides it; check `@types/geojson` in `package.json`). `onMapPress` gets a coordinate when the user taps the map.

**`CabSureMap`** (lines 13-22). Defaults: `showUserLocation=false`, `height=240`.
- Lines 14-15: `styleUrl` (string or null) and `error` state.
- Line 16: on first draw (`[]`), calls `mapService.configuration()`, which returns the config; `.then(value => setStyleUrl(value.style_url))` stores the style URL; `.catch(() => setError(true))` flags failure.
- Line 17: `points` = the three coordinates with empty ones removed. `.filter(Boolean)` drops null/undefined; `as Coordinate[]` tells TypeScript the result type.
- Line 18: `initialViewState` computed with `useMemo`. If there are 2 or more points, fit a box: `bounds(points)` with 48 padding. Otherwise center on the one point at zoom 14, or on a default center `[75.0833, 15.3926]` at zoom 10 (longitude first; this is near Dharwad in Karnataka, India, I believe; it is simplified guess). The dependency list names every latitude and longitude so the view updates only when numbers change.
- Line 19: if `error`, show "Map is unavailable" box.
- Line 20: if no `styleUrl` yet, show a loading box.
- Line 21: the real map. `onDidFailLoadingMap` sets error. `onPress` reads `event.nativeEvent.lngLat` (MapLibre gives longitude then latitude), and calls `onMapPress` with `?.()` (call only if defined). `Camera` receives `initialViewState`. `UserLocation` is shown when allowed. If `route` exists, a `GeoJSONSource` with id `ride-route` wraps a `Feature` and a `Layer` of type `line` painted with the primary colour, width 5. Then three `MapMarker`s. A hint "Tap map to place pin" shows only if `onMapPress` was passed. An attribution text "© OpenStreetMap · Geoapify" is always shown (map data licence needs this). `pointerEvents="none"` lets touches pass through those overlays.

**`MapMarker`** (line 24): a round coloured badge with an icon, anchored at its bottom, at `[longitude, latitude]`.

**`bounds`** (line 25): finds min and max longitude and latitude. *Example:* points (77,12) and (78,13) give `[77,12,78,13]`. `Math.min(...arr)` spreads the array as arguments.

**`styles`** (line 26): all on one line. `overflow: 'hidden'` clips the map to rounded corners. `position: 'absolute'` pins overlays.

## 4. How data flows
```
CabSureMap mounts -> mapService.configuration() -> GET /api/v1/maps/config -> backend
   <- {style_url,...} -> setStyleUrl -> redraw -> <Map mapStyle=style_url>
tap on map -> event.nativeEvent.lngLat -> onMapPress({latitude, longitude}) -> parent screen
```

## 5. Try it
Not directly runnable alone. Render it in a screen:
```tsx
<CabSureMap pickup={{latitude:15.39,longitude:75.08}} height={200} />
```
Expected: a loading box, then a map centred on that point with one marker.

## 6. Can it be better?
- Good: handles loading and failure; shows map credit; avoids rebuilding the camera needlessly.
- Weak: the style URL fetch has no cancel if the component unmounts. Lines 18, 21 and 26 are huge single lines; split them. Default centre is a magic number; name it `DEFAULT_CENTER`. `initialViewState` is initial only, so the camera will not follow a moving driver; I am not sure if `Camera` re-reads it after first draw, so test it. `points` is rebuilt every draw while the memo watches the raw numbers (the lint rule for hooks may complain). Marker colours and the attribution text are hard-coded, while the backend also sends `attribution`.
- Cleaner way: use `value.attribution` from `MapConfiguration` for the credit text.
- Security: the style URL may contain a map API key from the backend; do not log it. The keys are not in this file.

## 7. Check yourself
1. Why must `points.length > 1` use `bounds` and not a single centre?
2. In which order does MapLibre want coordinates, and where does the file apply that?
