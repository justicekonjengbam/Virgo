# NotificationsScreen.tsx

## 1. Purpose
Shows the passenger's notifications. Unread ones are highlighted with a dot. Tapping one marks it read. It lives in `features/notifications/screens/`. The navigator opens it from the bell on Home. It calls the backend directly through `apiClient` (no separate data layer).

## 2. Imports, one by one
- `import { useEffect, useState } from 'react';` `useState` stores values; `useEffect` runs code after the first draw.
- `import { ActivityIndicator, Pressable, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` `ActivityIndicator` is a native spinner. Others are as in the other screens: touch box, safe box, scroll box, styles, box.
- `MaterialCommunityIcons` icon font.
- `DsCard, DsText` from `../../../components/design-system`.
- `AppPageHeader` from `../../../components/navigation/AppPageHeader`.
- `apiClient` from `../../../services/apiClient`: HTTP client.
- `colors, radius, spacing` from `../../../theme`.

## 3. Walk through the code, top to bottom
**`NotificationItem`** (line 10): `id`, `notification_type`, `title`, `body`, `read_at` (a time string or null), `created_at`.

**`NotificationsScreen({ onBack, onMenuPress })`** (lines 12-17).
- Line 13: `items` is `null` while loading, then a list. `error` is a string.
- Line 14: `useEffect` with `[]` runs once: `apiClient.get('/api/v1/passengers/me/notifications')` returns the list; `.then(response => setItems(response.data))`; `.catch(...)` sets an error text, using the error's own message if it is an `Error`. `void` ignores the promise.
- Line 15 `read(item)`: if already read, stop. Otherwise PATCH `/api/v1/passengers/me/notifications/{id}/read` (PATCH = change part of a resource) and take the updated item. Then `setItems(current => current?.map(...) ?? null)` replaces the matching item in the list with the updated one. `current?.map` is safe when `current` is null. This function has no try/catch (see section 6).
- Line 16, the UI, in one long line: error text if any; a spinner if `items === null`; the list if it has items; otherwise an "No notifications yet." card. For each item, an icon is chosen by the type string: contains `driver_assigned` -> `account-check`; contains `confirmed` -> `check-decagram`; else `bell-outline`. It shows title, body, and the time via `toLocaleString('en-IN')`. A dot appears when `read_at` is empty. Unread cards are elevated and tinted.
- Line 18: the styles, minified onto one line.

## 4. How data flows
```
Screen mounts -> GET /api/v1/passengers/me/notifications -> backend
   <- [items] -> setItems -> list drawn
tap unread item -> PATCH .../{id}/read -> backend sets read_at
   <- updated item -> replace in items -> dot disappears
```

## 5. Try it
Not directly runnable alone. Run the app, trigger a notification (for example assign a driver from the admin app), and open the bell. Expected: a new row with a dot; after tapping, the dot goes.

## 6. Can it be better?
- Good: optimistic-free but correct update; handles empty and loading states.
- Weak: `read` has no error handling, so a failed PATCH becomes an unhandled promise error. Lines 13-18 are dense and hard to read; format them. The icon logic uses `includes` on free text; a lookup table is safer. Notification type strings are magic. No pull-to-refresh. It bypasses the feature "data" layer used elsewhere.
- Cleaner way: `const ICONS = { driver_assigned: 'account-check', ... }` and `ICONS[type] ?? 'bell-outline'`.
- Security: it relies on the backend to return only this passenger's items (`/me/` path). Not verifiable here.

## 7. Check yourself
1. When is `items` `null` and what does the screen show then?
2. What would happen if the PATCH in `read` fails?
