# DriverHelpScreen.tsx

## 1. Purpose
"Help & Support" page: loads support articles from the backend and shows each as a question row that opens to show the answer (an accordion). It calls `driverMenuService.getSupport()` from `features/dashboard/services/driverMenuService`.

## 2. Imports, one by one
- `import { useEffect, useState } from 'react';` (line 1). `useState` = screen memory. `useEffect` = code that runs after the screen shows.
- `import { ActivityIndicator, Pressable, SafeAreaView, ScrollView, StyleSheet } from 'react-native';` (line 2). Spinner; `Pressable` (tappable area); notch-safe box; scroll box; style helper.
- `MaterialCommunityIcons` (line 3): icon font (`chevron-up`, `chevron-down`).
- `DriverPageHeader`, `DriverCard`, `DriverText` (lines 5-7); `colors, spacing` (line 8).
- `driverMenuService`, type `DriverSupportArticle` (line 9).

## 3. Walk through the code
**`DriverHelpScreen({ onBack })`** (line 11).
- `articles` state (line 12): `null` = loading, array = loaded.
- Effect (line 13): `driverMenuService.getSupport().then(setArticles).catch(() => setArticles([]))`. `[]` as second argument = run once. On error the list is empty (the screen then shows only the title).
- Render (line 14): header, title "How can we help?", subtitle, and either a spinner or `articles.map(article => <HelpItem article={article} key={article.id}/>)`. `map` turns each article into a row; `key` lets React track rows.

**`HelpItem({ article })`** (line 17). Local state `open` (starts false). The `Pressable` has `accessibilityRole="button"` (screen readers say "button") and `onPress={() => setOpen(value => !value)}`, which flips the value (using the previous value `value`). The icon is `chevron-up` when open, else `chevron-down`. If `open`, the body text is shown.

**`styles`** (line 18).

## 4. How data flows
```
open -> useEffect -> getSupport() -> backend -> DriverSupportArticle[] -> setArticles -> rows
tap row -> setOpen(!open) -> body text appears
```

## 5. Try it
Not directly runnable alone. Open Help in the driver app and tap a question. Expected: the answer expands.

## 6. Can it be better?
- Good: simple; accessible button role; collapsed by default.
- Weak: a load failure shows an empty page with no message; no retry; no contact option (phone, email); `accessibilityState={{ expanded: open }}` is missing.
- Cleaner way:
```tsx
<Pressable accessibilityRole="button" accessibilityState={{ expanded: open }} ...>
```
and show "Could not load help. Try again." on error.
- Security: article text comes from the backend; React Native `Text` does not run HTML, so it is safe.

## 7. Check yourself
1. What does `setOpen(value => !value)` do?
2. What does the user see if the support request fails?
