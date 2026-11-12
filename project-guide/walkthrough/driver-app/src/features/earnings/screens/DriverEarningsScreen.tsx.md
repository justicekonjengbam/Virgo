# DriverEarningsScreen.tsx

## 1. Purpose
A screen that shows the driver's month total and a breakdown (today, rides today, month). `DriverHomeScreen` gives it an `onBack` function through the app's navigation (opened by `onOpenEarnings`). It uses `useDriverDashboard` for data.

## 2. Imports, one by one
- `import { ActivityIndicator, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';` (`driver-app/src/features/earnings/screens/DriverEarningsScreen.tsx:1`): `ActivityIndicator` is a spinner; `SafeAreaView` keeps content away from notches; `ScrollView` scrolls; `View` is a box.
- `MaterialCommunityIcons` (line 2): icons.
- `DriverPageHeader` (line 4): shared header with a back button and a title.
- `DriverCard` (line 5), `DriverText` (line 6): shared card box and text.
- `colors, spacing` (line 7): theme values.
- `useDriverDashboard` (line 8) from `dashboard/hooks/useDriverDashboard.ts`.

## 3. Walk through the code
- **`DriverEarningsScreen({ onBack })`** (line 10).
  - Line 11: the hook returns `dashboard` and `isLoading`. This starts its own fetch of `/api/v1/drivers/dashboard`.
  - Line 12: the layout. Header with title "Earnings". In the scroll area: if loading or no data, show a spinner. Else show a fragment (`<> </>`, a wrapper with no box) holding: a blue total card (month earnings and ride count), the heading "Earnings breakdown", a card with three `Metric` rows, and an info notice.
- **`Metric({ icon, label, value })`** (line 14): icon on the left, label and bold value on the right.
- **`rupees(paise)`** (line 15): `Math.round(paise / 100)` converts paise to rupees; `toLocaleString('en-IN')` adds Indian digit grouping. *Example:* `rupees(1234500)` gives `₹12,345`. Beware: it rounds, so 99 paise shows `₹1`.
- `styles` (line 16).
- Errors: the hook's `error` is not read. If loading fails, `dashboard` stays `null` and the spinner shows forever.

## 4. How data flows
```
Screen -> useDriverDashboard -> service GET dashboard -> {month_earnings_paise,...} -> rupees() -> text
```

## 5. Try it
Not directly runnable. In the driver app tap Earnings on the home screen.

## 6. Can it be better?
- Good: short, reuses the dashboard data and shared components.
- Weak: no error view (infinite spinner on failure). `rupees` is duplicated in `DriverHomeScreen.tsx:123` (`formatRupees`). Fetches the dashboard again instead of sharing. Does not show a daily or weekly list, only three numbers.
- Cleaner way: move one `formatRupees` into a shared utils file and show `error` with a retry button.
- Security: none.

## 7. Check yourself
1. What does the screen show if the request fails?
2. What does `rupees(250)` return?
