# Driver app foundation

## Phase 0 baseline

- React Native 0.86, TypeScript, React Navigation, and pnpm workspace dependencies mirror the Passenger app.
- Driver UI uses the shared Virgo visual language: Poppins, primary purple `#952B7D`, bold primary actions, high-contrast outlined fields, consistent spacing, and accessible 44px-or-larger targets.
- Firebase configuration and the Driver API client are present. Authentication work is intentionally performed in Phase 1.
- The legacy `DriverAuthScreen` was removed. The supported entry route is `Splash → Login → Sign Up → Help`.
- Metro resolves dependencies through the physical workspace location so the app remains stable when launched through a Windows mapped drive.

## Development checks

Run from `driver-app`:

```cmd
pnpm typecheck
pnpm lint
pnpm start:reset --port 8082
```

In a second CMD window:

```cmd
pnpm android --port 8082
```

## Next phase boundary

Phase 1 owns the Firebase OTP and Driver token contract. Phase 2 owns the atomic two-step Driver registration transaction and document-storage integration.
