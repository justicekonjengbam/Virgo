# driver-app/src/navigation/types.ts

## 1. Purpose
It lists the names of all Driver screens in one TypeScript type. `DriverNavigator.tsx` imports it so a wrong screen name fails at compile time. Nothing here runs; types disappear when the app is built.

## 2. Imports, one by one
None. The file only has an `export type`.

## 3. Walk through the code
`export type DriverStackParamList = { Splash: undefined; ... Settings: undefined; };` (`types.ts:1-14`).
- A **type alias** (a name for a shape. *Example:* `type Age = number`).
- Each key is a screen name: Splash, Login, Signup, Help, Onboarding, Home, RideRequest, ActiveRide, Earnings, TripHistory, Outstation, Settings (lines 2-13).
- The value is the **params** (data passed when you navigate. *Example:* `navigate('Ride', { id: 5 })` would need `Ride: { id: number }`). `undefined` means "this screen takes no data". All 12 screens take none.

## 4. How data flows
```
types.ts --(type only)--> DriverNavigator.tsx
 navigation.navigate('Hom')  -> compile error (no such key)
```

## 5. Try it
`cd driver-app && pnpm typecheck` (runs the TypeScript checker, as the root README says). Change `navigate('Home')` to `navigate('Hom')` somewhere and you will see an error.

## 6. Can it be better?
- Good: simple and complete.
- Weak: every screen gets data from shared context/services, not params, so deep links cannot say "open ride 5". Fine for now (opinion).
- Security: none.

## 7. Check yourself
1. What does `undefined` mean as a value here?
2. Does this file exist in the final app bundle at run time?
