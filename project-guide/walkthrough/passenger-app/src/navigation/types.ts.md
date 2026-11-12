# passenger-app/src/navigation/types.ts

## 1. Purpose
This file holds TypeScript types only. It lists every screen name of the passenger app and the data each screen needs when opened. `PassengerNavigator.tsx` imports it (line 26). It has no runtime code.

## 2. Imports, one by one
- `import type { RideBooking, LocationOption } from '../features/booking/data/bookingApi';` (line 1). `import type` brings in only a **type** (a description of data shape; *Example:* `type P = {x: number}`). It is erased at build time. `RideBooking` is the ride data after booking. `LocationOption` is a place the user picked.
- `import type { SavedPlace } from '../features/home/domain/homeTypes';` (line 2). A saved place such as Home or Work.

## 3. Walk through the code
- `export type PassengerStackParamList = {...}` (lines 4-25). **Stack navigator** (screens piled like cards; opening one puts it on top, going back removes it). This map gives each screen name its **params** (data passed when opening it).
  - `Splash: undefined;` means "no params".
  - `SavedPlace: { place: SavedPlace };` (line 12) means you must pass `{ place }`. *Example:* `navigation.navigate('SavedPlace', { place })`.
  - `Booking: { ride: RideBooking };` (line 14) needs the ride.
  - 20 screens in total: Splash, Login, Signup, Faq, Home, Pickup, Destination, SavedPlace, Fare, Booking, Rides, Addresses, Emergency, Support, InstantRide, Outstation, OutstationPickup, OutstationDestination, Notifications, Settings.
  - Benefit: `navigation.navigate('Bookng')` (typo) is a compile error.
- `export type BookingDraft = {...}` (line 27). The half-finished booking: `pickup`, `destination`, `categoryId` (vehicle type id), and outstation (long-distance) `outstationPickup`, `outstationDestination`. Each may be `null` before the user picks.

## 4. How data flows
```
types.ts --types--> PassengerNavigator.tsx
  createNativeStackNavigator<PassengerStackParamList>()
  NativeStackScreenProps<PassengerStackParamList,'Booking'> -> route.params.ride
```

## 5. Try it
Not directly runnable. Check types: `cd passenger-app && npx tsc --noEmit`. Add a typo like `navigation.navigate('Hom')` in the navigator and the check fails.

## 6. Can it be better?
- Good: strong route safety, one place for all screen names.
- Weak: `BookingDraft` is a data type, not a route type, so it fits better in a booking folder. The long single line on line 27 is hard to read. `navigation/types.ts` imports from features, and features import from navigation, so there is a risk of import loops (types only, so safe now).
- Cleaner way: split `BookingDraft` into `features/booking/domain/`. (Opinion.)
- Security: none.

## 7. Check yourself
1. What does `undefined` mean next to a screen name?
2. Which screen needs data when opened, and what data?
