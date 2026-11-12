# 07. Reading order

Read the source in this order. Each line links to the explained page for that file. Tick them off as you go.

## First, set up (do these once)

1. Follow `03-setup-and-run.md` to make the virtual environment, install packages, create `backend/.env`, and start the server.
2. Open `http://127.0.0.1:8000/docs` and look at the routes.
3. From `backend/` run `pytest` to see that tests pass.

## Part A. Backend, in dependency order

The numbers follow the path of one request: settings → database → tables → routes → rules.

1. [ ] [`backend/app/main.py`](walkthrough/backend/app/main.py.md): The entry point. Builds the app, runs migrations, mounts routes and `/admin`.
2. [ ] [`backend/app/core/config.py`](walkthrough/backend/app/core/config.py.md): Every setting and its default. You need this to understand any other file.
3. [ ] [`backend/app/db.py`](walkthrough/backend/app/db.py.md): Database engine, session, `get_db`, and the migration runner.
4. [ ] [`backend/app/models/user.py`](walkthrough/backend/app/models/user.py.md): Passenger and AdminUser tables.
5. [ ] [`backend/app/models/ride_hailing.py`](walkthrough/backend/app/models/ride_hailing.py.md): All other tables. The data model of the whole product.
6. [ ] [`backend/app/schemas/auth.py`](walkthrough/backend/app/schemas/auth.py.md): Shapes of login and registration requests and replies.
7. [ ] [`backend/app/api/v1/router.py`](walkthrough/backend/app/api/v1/router.py.md): The list of every route group.
8. [ ] [`backend/app/api/dependencies/auth.py`](walkthrough/backend/app/api/dependencies/auth.py.md): How a passenger token becomes a `Passenger` object.
9. [ ] [`backend/app/api/v1/routes/auth.py`](walkthrough/backend/app/api/v1/routes/auth.py.md): Passenger login routes.
10. [ ] [`backend/app/services/auth_service.py`](walkthrough/backend/app/services/auth_service.py.md): Passenger login rules and tokens.
11. [ ] [`backend/app/services/firebase_service.py`](walkthrough/backend/app/services/firebase_service.py.md): Starts Firebase Admin.
12. [ ] [`backend/app/repositories/passenger_repository.py`](walkthrough/backend/app/repositories/passenger_repository.py.md): The simplest repository, a good pattern example.
13. [ ] [`backend/app/services/driver_auth_service.py`](walkthrough/backend/app/services/driver_auth_service.py.md): Driver login and registration.
14. [ ] [`backend/app/services/driver_readiness_service.py`](walkthrough/backend/app/services/driver_readiness_service.py.md): When a driver becomes active.
15. [ ] [`backend/app/schemas/booking.py`](walkthrough/backend/app/schemas/booking.py.md): Booking request and reply shapes.
16. [ ] [`backend/app/api/v1/routes/booking.py`](walkthrough/backend/app/api/v1/routes/booking.py.md): Passenger booking routes.
17. [ ] [`backend/app/services/booking_service.py`](walkthrough/backend/app/services/booking_service.py.md): Fare estimate and booking.
18. [ ] [`backend/app/services/map_provider_service.py`](walkthrough/backend/app/services/map_provider_service.py.md): Geoapify calls and the 150 km area.
19. [ ] [`backend/app/services/ride_matching_service.py`](walkthrough/backend/app/services/ride_matching_service.py.md): Dispatch and offers. The heart of the product.
20. [ ] [`backend/app/services/ride_lifecycle_service.py`](walkthrough/backend/app/services/ride_lifecycle_service.py.md): Ride status changes, cancel, rating, start OTP.
21. [ ] [`backend/app/api/v1/routes/driver_matching.py`](walkthrough/backend/app/api/v1/routes/driver_matching.py.md): Driver routes: online, offers, trip steps.
22. [ ] [`backend/app/services/realtime_service.py`](walkthrough/backend/app/services/realtime_service.py.md): The WebSocket hub.
23. [ ] [`backend/app/services/realtime_events.py`](walkthrough/backend/app/services/realtime_events.py.md): Helpers that publish events to the hub.
24. [ ] [`backend/app/api/v1/routes/realtime.py`](walkthrough/backend/app/api/v1/routes/realtime.py.md): WebSocket endpoints.
25. [ ] [`backend/app/services/outstation_service.py`](walkthrough/backend/app/services/outstation_service.py.md): Long-trip flow.
26. [ ] [`backend/app/services/admin_auth_service.py`](walkthrough/backend/app/services/admin_auth_service.py.md): Admin login, roles, permissions.
27. [ ] [`backend/app/api/v1/routes/admin.py`](walkthrough/backend/app/api/v1/routes/admin.py.md): Admin routes.
28. [ ] [`backend/app/services/driver_document_review_service.py`](walkthrough/backend/app/services/driver_document_review_service.py.md): Approve or reject documents.
29. [ ] [`backend/tests/test_ride_matching.py`](walkthrough/backend/tests/test_ride_matching.py.md): See the matching rules as tests.
30. [ ] [`backend/tests/test_booking_policy.py`](walkthrough/backend/tests/test_booking_policy.py.md): See booking rules as tests.

## Part B. Everything else

Mobile apps: start at `index.js` → `App.tsx` → `src/navigation/*Navigator.tsx`, then follow the screens. Inside each feature folder read in this order: `data/` (API calls), `services/`, `domain/`, `screens/`.

### Backend: remaining files

- [ ] [`backend/app/api/dependencies/admin_auth.py`](walkthrough/backend/app/api/dependencies/admin_auth.py.md)
- [ ] [`backend/app/api/dependencies/driver_auth.py`](walkthrough/backend/app/api/dependencies/driver_auth.py.md)
- [ ] [`backend/app/api/__init__.py`](walkthrough/backend/app/api/__init__.py.md)
- [ ] [`backend/app/api/v1/__init__.py`](walkthrough/backend/app/api/v1/__init__.py.md)
- [ ] [`backend/app/api/v1/routes/driver_dashboard.py`](walkthrough/backend/app/api/v1/routes/driver_dashboard.py.md)
- [ ] [`backend/app/api/v1/routes/driver_menu.py`](walkthrough/backend/app/api/v1/routes/driver_menu.py.md)
- [ ] [`backend/app/api/v1/routes/drivers_auth.py`](walkthrough/backend/app/api/v1/routes/drivers_auth.py.md)
- [ ] [`backend/app/api/v1/routes/emergency_contacts.py`](walkthrough/backend/app/api/v1/routes/emergency_contacts.py.md)
- [ ] [`backend/app/api/v1/routes/health.py`](walkthrough/backend/app/api/v1/routes/health.py.md)
- [ ] [`backend/app/api/v1/routes/home.py`](walkthrough/backend/app/api/v1/routes/home.py.md)
- [ ] [`backend/app/api/v1/routes/__init__.py`](walkthrough/backend/app/api/v1/routes/__init__.py.md)
- [ ] [`backend/app/api/v1/routes/maps.py`](walkthrough/backend/app/api/v1/routes/maps.py.md)
- [ ] [`backend/app/api/v1/routes/notifications.py`](walkthrough/backend/app/api/v1/routes/notifications.py.md)
- [ ] [`backend/app/api/v1/routes/outstation.py`](walkthrough/backend/app/api/v1/routes/outstation.py.md)
- [ ] [`backend/app/api/v1/routes/passenger_profile.py`](walkthrough/backend/app/api/v1/routes/passenger_profile.py.md)
- [ ] [`backend/app/core/__init__.py`](walkthrough/backend/app/core/__init__.py.md)
- [ ] [`backend/app/__init__.py`](walkthrough/backend/app/__init__.py.md)
- [ ] [`backend/app/models/__init__.py`](walkthrough/backend/app/models/__init__.py.md)
- [ ] [`backend/app/repositories/driver_repository.py`](walkthrough/backend/app/repositories/driver_repository.py.md)
- [ ] [`backend/app/schemas/admin.py`](walkthrough/backend/app/schemas/admin.py.md)
- [ ] [`backend/app/schemas/admin_review.py`](walkthrough/backend/app/schemas/admin_review.py.md)
- [ ] [`backend/app/schemas/driver_dashboard.py`](walkthrough/backend/app/schemas/driver_dashboard.py.md)
- [ ] [`backend/app/schemas/driver_menu.py`](walkthrough/backend/app/schemas/driver_menu.py.md)
- [ ] [`backend/app/schemas/emergency.py`](walkthrough/backend/app/schemas/emergency.py.md)
- [ ] [`backend/app/schemas/health.py`](walkthrough/backend/app/schemas/health.py.md)
- [ ] [`backend/app/schemas/home.py`](walkthrough/backend/app/schemas/home.py.md)
- [ ] [`backend/app/schemas/maps.py`](walkthrough/backend/app/schemas/maps.py.md)
- [ ] [`backend/app/schemas/notification.py`](walkthrough/backend/app/schemas/notification.py.md)
- [ ] [`backend/app/schemas/outstation.py`](walkthrough/backend/app/schemas/outstation.py.md)
- [ ] [`backend/app/schemas/profile.py`](walkthrough/backend/app/schemas/profile.py.md)
- [ ] [`backend/app/services/admin_operations_service.py`](walkthrough/backend/app/services/admin_operations_service.py.md)
- [ ] [`backend/app/services/driver_dashboard_service.py`](walkthrough/backend/app/services/driver_dashboard_service.py.md)
- [ ] [`backend/app/services/driver_menu_service.py`](walkthrough/backend/app/services/driver_menu_service.py.md)
- [ ] [`backend/app/services/emergency_contact_service.py`](walkthrough/backend/app/services/emergency_contact_service.py.md)
- [ ] [`backend/app/services/home_seed_service.py`](walkthrough/backend/app/services/home_seed_service.py.md)
- [ ] [`backend/app/services/home_service.py`](walkthrough/backend/app/services/home_service.py.md)
- [ ] [`backend/app/services/passenger_profile_service.py`](walkthrough/backend/app/services/passenger_profile_service.py.md)

### Backend: database migrations (read in file-date order)

- [ ] [`backend/app/database/migrations/env.py`](walkthrough/backend/app/database/migrations/env.py.md)
- [ ] [`backend/app/database/migrations/versions/28bc77a50115_add_home_category_metadata.py`](walkthrough/backend/app/database/migrations/versions/28bc77a50115_add_home_category_metadata.py.md)
- [ ] [`backend/app/database/migrations/versions/841c1f195299_add_static_location_catalog.py`](walkthrough/backend/app/database/migrations/versions/841c1f195299_add_static_location_catalog.py.md)
- [ ] [`backend/app/database/migrations/versions/b7d9d0e0f001_add_driver_document_number.py`](walkthrough/backend/app/database/migrations/versions/b7d9d0e0f001_add_driver_document_number.py.md)
- [ ] [`backend/app/database/migrations/versions/c1d6e1b40001_add_driver_online_status.py`](walkthrough/backend/app/database/migrations/versions/c1d6e1b40001_add_driver_online_status.py.md)
- [ ] [`backend/app/database/migrations/versions/d2f7e1a50001_add_driver_document_review_metadata.py`](walkthrough/backend/app/database/migrations/versions/d2f7e1a50001_add_driver_document_review_metadata.py.md)
- [ ] [`backend/app/database/migrations/versions/e3f8a2b60001_add_admin_operations_schema.py`](walkthrough/backend/app/database/migrations/versions/e3f8a2b60001_add_admin_operations_schema.py.md)
- [ ] [`backend/app/database/migrations/versions/e4ffba93f4c4_initial_ride_hailing_schema.py`](walkthrough/backend/app/database/migrations/versions/e4ffba93f4c4_initial_ride_hailing_schema.py.md)
- [ ] [`backend/app/database/migrations/versions/f4a9c3d70001_add_ride_dispatch_offers.py`](walkthrough/backend/app/database/migrations/versions/f4a9c3d70001_add_ride_dispatch_offers.py.md)
- [ ] [`backend/app/database/migrations/versions/g5b0d4e80001_add_live_ride_tracking.py`](walkthrough/backend/app/database/migrations/versions/g5b0d4e80001_add_live_ride_tracking.py.md)
- [ ] [`backend/app/database/migrations/versions/h6c1e5f90001_harden_admin_accounts.py`](walkthrough/backend/app/database/migrations/versions/h6c1e5f90001_harden_admin_accounts.py.md)
- [ ] [`backend/app/database/migrations/versions/i7d2f6a00001_add_outstation_bookings.py`](walkthrough/backend/app/database/migrations/versions/i7d2f6a00001_add_outstation_bookings.py.md)
- [ ] [`backend/app/database/migrations/versions/j8e3a7b10001_add_outstation_route.py`](walkthrough/backend/app/database/migrations/versions/j8e3a7b10001_add_outstation_route.py.md)

### Backend: tests and tools

- [ ] [`backend/alembic.ini`](walkthrough/backend/alembic.ini.md)
- [ ] [`backend/.env.example`](walkthrough/backend/.env.example.md)
- [ ] [`backend/pyproject.toml`](walkthrough/backend/pyproject.toml.md)
- [ ] [`backend/scripts/format.ps1`](walkthrough/backend/scripts/format.ps1.md)
- [ ] [`backend/scripts/lint.ps1`](walkthrough/backend/scripts/lint.ps1.md)
- [ ] [`backend/scripts/start-dev.ps1`](walkthrough/backend/scripts/start-dev.ps1.md)
- [ ] [`backend/scripts/test.ps1`](walkthrough/backend/scripts/test.ps1.md)
- [ ] [`backend/tests/test_database_schema.py`](walkthrough/backend/tests/test_database_schema.py.md)
- [ ] [`backend/tests/test_driver_auth_contract.py`](walkthrough/backend/tests/test_driver_auth_contract.py.md)
- [ ] [`backend/tests/test_driver_document_review.py`](walkthrough/backend/tests/test_driver_document_review.py.md)
- [ ] [`backend/tests/test_outstation_booking.py`](walkthrough/backend/tests/test_outstation_booking.py.md)
- [ ] [`backend/tests/test_phone_normalization.py`](walkthrough/backend/tests/test_phone_normalization.py.md)
- [ ] [`backend/tests/unit/test_health.py`](walkthrough/backend/tests/unit/test_health.py.md)
- [ ] [`backend/tests/unit/test_realtime_service.py`](walkthrough/backend/tests/unit/test_realtime_service.py.md)

### Admin site

- [ ] [`admin-app/app.js`](walkthrough/admin-app/app.js.md)
- [ ] [`admin-app/index.html`](walkthrough/admin-app/index.html.md)
- [ ] [`admin-app/README.md`](walkthrough/admin-app/README.md.md)
- [ ] [`admin-app/styles.css`](walkthrough/admin-app/styles.css.md)

### Passenger app source

- [ ] [`passenger-app/src/components/auth/AuthHeader.tsx`](walkthrough/passenger-app/src/components/auth/AuthHeader.tsx.md)
- [ ] [`passenger-app/src/components/auth/AuthInput.tsx`](walkthrough/passenger-app/src/components/auth/AuthInput.tsx.md)
- [ ] [`passenger-app/src/components/auth/AuthPrompt.tsx`](walkthrough/passenger-app/src/components/auth/AuthPrompt.tsx.md)
- [ ] [`passenger-app/src/components/auth/BrandLogo.tsx`](walkthrough/passenger-app/src/components/auth/BrandLogo.tsx.md)
- [ ] [`passenger-app/src/components/auth/BrandMark.tsx`](walkthrough/passenger-app/src/components/auth/BrandMark.tsx.md)
- [ ] [`passenger-app/src/components/auth/RememberMe.tsx`](walkthrough/passenger-app/src/components/auth/RememberMe.tsx.md)
- [ ] [`passenger-app/src/components/design-system/atoms/DsButton.tsx`](walkthrough/passenger-app/src/components/design-system/atoms/DsButton.tsx.md)
- [ ] [`passenger-app/src/components/design-system/atoms/DsIcon.tsx`](walkthrough/passenger-app/src/components/design-system/atoms/DsIcon.tsx.md)
- [ ] [`passenger-app/src/components/design-system/atoms/DsText.tsx`](walkthrough/passenger-app/src/components/design-system/atoms/DsText.tsx.md)
- [ ] [`passenger-app/src/components/design-system/index.ts`](walkthrough/passenger-app/src/components/design-system/index.ts.md)
- [ ] [`passenger-app/src/components/design-system/molecules/DsCard.tsx`](walkthrough/passenger-app/src/components/design-system/molecules/DsCard.tsx.md)
- [ ] [`passenger-app/src/components/design-system/molecules/DsChip.tsx`](walkthrough/passenger-app/src/components/design-system/molecules/DsChip.tsx.md)
- [ ] [`passenger-app/src/components/design-system/molecules/DsTextField.tsx`](walkthrough/passenger-app/src/components/design-system/molecules/DsTextField.tsx.md)
- [ ] [`passenger-app/src/components/design-system/organisms/DsEmptyState.tsx`](walkthrough/passenger-app/src/components/design-system/organisms/DsEmptyState.tsx.md)
- [ ] [`passenger-app/src/components/design-system/organisms/DsLoading.tsx`](walkthrough/passenger-app/src/components/design-system/organisms/DsLoading.tsx.md)
- [ ] [`passenger-app/src/components/feedback/LoadingState.tsx`](walkthrough/passenger-app/src/components/feedback/LoadingState.tsx.md)
- [ ] [`passenger-app/src/components/foundation/AppButton.tsx`](walkthrough/passenger-app/src/components/foundation/AppButton.tsx.md)
- [ ] [`passenger-app/src/components/foundation/AppText.tsx`](walkthrough/passenger-app/src/components/foundation/AppText.tsx.md)
- [ ] [`passenger-app/src/components/navigation/AppPageHeader.tsx`](walkthrough/passenger-app/src/components/navigation/AppPageHeader.tsx.md)
- [ ] [`passenger-app/src/config/environment.ts`](walkthrough/passenger-app/src/config/environment.ts.md)
- [ ] [`passenger-app/src/features/addresses/screens/SavedAddressesScreen.tsx`](walkthrough/passenger-app/src/features/addresses/screens/SavedAddressesScreen.tsx.md)
- [ ] [`passenger-app/src/features/app/screens/PostLoginPlaceholderScreen.tsx`](walkthrough/passenger-app/src/features/app/screens/PostLoginPlaceholderScreen.tsx.md)
- [ ] [`passenger-app/src/features/auth/screens/LoginScreen.tsx`](walkthrough/passenger-app/src/features/auth/screens/LoginScreen.tsx.md)
- [ ] [`passenger-app/src/features/auth/screens/SignupScreen.tsx`](walkthrough/passenger-app/src/features/auth/screens/SignupScreen.tsx.md)
- [ ] [`passenger-app/src/features/auth/services/authService.ts`](walkthrough/passenger-app/src/features/auth/services/authService.ts.md)
- [ ] [`passenger-app/src/features/auth/utils/authErrorMessage.ts`](walkthrough/passenger-app/src/features/auth/utils/authErrorMessage.ts.md)
- [ ] [`passenger-app/src/features/auth/validation/authValidation.ts`](walkthrough/passenger-app/src/features/auth/validation/authValidation.ts.md)
- [ ] [`passenger-app/src/features/booking/data/bookingApi.ts`](walkthrough/passenger-app/src/features/booking/data/bookingApi.ts.md)
- [ ] [`passenger-app/src/features/booking/screens/BookingStatusScreen.tsx`](walkthrough/passenger-app/src/features/booking/screens/BookingStatusScreen.tsx.md)
- [ ] [`passenger-app/src/features/booking/screens/FareEstimateScreen.tsx`](walkthrough/passenger-app/src/features/booking/screens/FareEstimateScreen.tsx.md)
- [ ] [`passenger-app/src/features/booking/screens/LocationSelectionScreen.tsx`](walkthrough/passenger-app/src/features/booking/screens/LocationSelectionScreen.tsx.md)
- [ ] [`passenger-app/src/features/booking/services/passengerRealtimeService.ts`](walkthrough/passenger-app/src/features/booking/services/passengerRealtimeService.ts.md)
- [ ] [`passenger-app/src/features/emergency/data/emergencyContactsApi.ts`](walkthrough/passenger-app/src/features/emergency/data/emergencyContactsApi.ts.md)
- [ ] [`passenger-app/src/features/emergency/screens/EmergencyContactsScreen.tsx`](walkthrough/passenger-app/src/features/emergency/screens/EmergencyContactsScreen.tsx.md)
- [ ] [`passenger-app/src/features/health/screens/HealthCheckScreen.tsx`](walkthrough/passenger-app/src/features/health/screens/HealthCheckScreen.tsx.md)
- [ ] [`passenger-app/src/features/health/services/healthService.ts`](walkthrough/passenger-app/src/features/health/services/healthService.ts.md)
- [ ] [`passenger-app/src/features/home/components/HomeDrawer.tsx`](walkthrough/passenger-app/src/features/home/components/HomeDrawer.tsx.md)
- [ ] [`passenger-app/src/features/home/components/ImagePlaceholder.tsx`](walkthrough/passenger-app/src/features/home/components/ImagePlaceholder.tsx.md)
- [ ] [`passenger-app/src/features/home/components/LocationCard.tsx`](walkthrough/passenger-app/src/features/home/components/LocationCard.tsx.md)
- [ ] [`passenger-app/src/features/home/components/RideOptionCard.tsx`](walkthrough/passenger-app/src/features/home/components/RideOptionCard.tsx.md)
- [ ] [`passenger-app/src/features/home/data/homeApi.ts`](walkthrough/passenger-app/src/features/home/data/homeApi.ts.md)
- [ ] [`passenger-app/src/features/home/domain/homeTypes.ts`](walkthrough/passenger-app/src/features/home/domain/homeTypes.ts.md)
- [ ] [`passenger-app/src/features/home/screens/PassengerHomeScreen.tsx`](walkthrough/passenger-app/src/features/home/screens/PassengerHomeScreen.tsx.md)
- [ ] [`passenger-app/src/features/home/state/usePassengerHome.ts`](walkthrough/passenger-app/src/features/home/state/usePassengerHome.ts.md)
- [ ] [`passenger-app/src/features/maps/components/CabSureMap.tsx`](walkthrough/passenger-app/src/features/maps/components/CabSureMap.tsx.md)
- [ ] [`passenger-app/src/features/maps/services/mapService.ts`](walkthrough/passenger-app/src/features/maps/services/mapService.ts.md)
- [ ] [`passenger-app/src/features/navigation/screens/MenuPlaceholderScreen.tsx`](walkthrough/passenger-app/src/features/navigation/screens/MenuPlaceholderScreen.tsx.md)
- [ ] [`passenger-app/src/features/notifications/screens/NotificationsScreen.tsx`](walkthrough/passenger-app/src/features/notifications/screens/NotificationsScreen.tsx.md)
- [ ] [`passenger-app/src/features/outstation/screens/OutstationBookingScreen.tsx`](walkthrough/passenger-app/src/features/outstation/screens/OutstationBookingScreen.tsx.md)
- [ ] [`passenger-app/src/features/outstation/services/outstationService.ts`](walkthrough/passenger-app/src/features/outstation/services/outstationService.ts.md)
- [ ] [`passenger-app/src/features/profile/data/passengerProfileApi.ts`](walkthrough/passenger-app/src/features/profile/data/passengerProfileApi.ts.md)
- [ ] [`passenger-app/src/features/profile/screens/PassengerSettingsScreen.tsx`](walkthrough/passenger-app/src/features/profile/screens/PassengerSettingsScreen.tsx.md)
- [ ] [`passenger-app/src/features/rides/screens/MyRidesScreen.tsx`](walkthrough/passenger-app/src/features/rides/screens/MyRidesScreen.tsx.md)
- [ ] [`passenger-app/src/features/splash/screens/SplashScreen.tsx`](walkthrough/passenger-app/src/features/splash/screens/SplashScreen.tsx.md)
- [ ] [`passenger-app/src/features/support/screens/FaqScreen.tsx`](walkthrough/passenger-app/src/features/support/screens/FaqScreen.tsx.md)
- [ ] [`passenger-app/src/features/support/screens/InstantRideScreen.tsx`](walkthrough/passenger-app/src/features/support/screens/InstantRideScreen.tsx.md)
- [ ] [`passenger-app/src/features/support/screens/PassengerSupportScreen.tsx`](walkthrough/passenger-app/src/features/support/screens/PassengerSupportScreen.tsx.md)
- [ ] [`passenger-app/src/navigation/PassengerNavigator.tsx`](walkthrough/passenger-app/src/navigation/PassengerNavigator.tsx.md)
- [ ] [`passenger-app/src/navigation/types.ts`](walkthrough/passenger-app/src/navigation/types.ts.md)
- [ ] [`passenger-app/src/services/apiClient.ts`](walkthrough/passenger-app/src/services/apiClient.ts.md)
- [ ] [`passenger-app/src/theme/index.ts`](walkthrough/passenger-app/src/theme/index.ts.md)
- [ ] [`passenger-app/src/theme/tokens.ts`](walkthrough/passenger-app/src/theme/tokens.ts.md)
- [ ] [`passenger-app/src/types/assets.d.ts`](walkthrough/passenger-app/src/types/assets.d.ts.md)
- [ ] [`passenger-app/src/types/react-native-config.d.ts`](walkthrough/passenger-app/src/types/react-native-config.d.ts.md)
- [ ] [`passenger-app/src/types/react-native-vector-icons.d.ts`](walkthrough/passenger-app/src/types/react-native-vector-icons.d.ts.md)

### Driver app source

- [ ] [`driver-app/src/components/auth/DriverAuthHeader.tsx`](walkthrough/driver-app/src/components/auth/DriverAuthHeader.tsx.md)
- [ ] [`driver-app/src/components/brand/DriverBrandLogo.tsx`](walkthrough/driver-app/src/components/brand/DriverBrandLogo.tsx.md)
- [ ] [`driver-app/src/components/brand/DriverBrandMark.tsx`](walkthrough/driver-app/src/components/brand/DriverBrandMark.tsx.md)
- [ ] [`driver-app/src/components/DriverButton.tsx`](walkthrough/driver-app/src/components/DriverButton.tsx.md)
- [ ] [`driver-app/src/components/DriverCard.tsx`](walkthrough/driver-app/src/components/DriverCard.tsx.md)
- [ ] [`driver-app/src/components/DriverPageHeader.tsx`](walkthrough/driver-app/src/components/DriverPageHeader.tsx.md)
- [ ] [`driver-app/src/components/DriverTextField.tsx`](walkthrough/driver-app/src/components/DriverTextField.tsx.md)
- [ ] [`driver-app/src/components/DriverText.tsx`](walkthrough/driver-app/src/components/DriverText.tsx.md)
- [ ] [`driver-app/src/config/environment.ts`](walkthrough/driver-app/src/config/environment.ts.md)
- [ ] [`driver-app/src/features/auth/components/DriverPhoneAuthForm.tsx`](walkthrough/driver-app/src/features/auth/components/DriverPhoneAuthForm.tsx.md)
- [ ] [`driver-app/src/features/auth/components/DriverVehicleVerificationForm.tsx`](walkthrough/driver-app/src/features/auth/components/DriverVehicleVerificationForm.tsx.md)
- [ ] [`driver-app/src/features/auth/screens/DriverLoginScreen.tsx`](walkthrough/driver-app/src/features/auth/screens/DriverLoginScreen.tsx.md)
- [ ] [`driver-app/src/features/auth/screens/DriverOnboardingScreen.tsx`](walkthrough/driver-app/src/features/auth/screens/DriverOnboardingScreen.tsx.md)
- [ ] [`driver-app/src/features/auth/screens/DriverSignupScreen.tsx`](walkthrough/driver-app/src/features/auth/screens/DriverSignupScreen.tsx.md)
- [ ] [`driver-app/src/features/auth/services/driverAuthService.ts`](walkthrough/driver-app/src/features/auth/services/driverAuthService.ts.md)
- [ ] [`driver-app/src/features/auth/utils/driverAuthError.ts`](walkthrough/driver-app/src/features/auth/utils/driverAuthError.ts.md)
- [ ] [`driver-app/src/features/dashboard/components/DriverDrawer.tsx`](walkthrough/driver-app/src/features/dashboard/components/DriverDrawer.tsx.md)
- [ ] [`driver-app/src/features/dashboard/components/DriverHeader.tsx`](walkthrough/driver-app/src/features/dashboard/components/DriverHeader.tsx.md)
- [ ] [`driver-app/src/features/dashboard/hooks/useDriverDashboard.ts`](walkthrough/driver-app/src/features/dashboard/hooks/useDriverDashboard.ts.md)
- [ ] [`driver-app/src/features/dashboard/screens/DriverHomeScreen.tsx`](walkthrough/driver-app/src/features/dashboard/screens/DriverHomeScreen.tsx.md)
- [ ] [`driver-app/src/features/dashboard/services/driverDashboardService.ts`](walkthrough/driver-app/src/features/dashboard/services/driverDashboardService.ts.md)
- [ ] [`driver-app/src/features/dashboard/services/driverMenuService.ts`](walkthrough/driver-app/src/features/dashboard/services/driverMenuService.ts.md)
- [ ] [`driver-app/src/features/dashboard/state/DriverSessionContext.tsx`](walkthrough/driver-app/src/features/dashboard/state/DriverSessionContext.tsx.md)
- [ ] [`driver-app/src/features/earnings/screens/DriverEarningsScreen.tsx`](walkthrough/driver-app/src/features/earnings/screens/DriverEarningsScreen.tsx.md)
- [ ] [`driver-app/src/features/maps/components/DriverRideMap.tsx`](walkthrough/driver-app/src/features/maps/components/DriverRideMap.tsx.md)
- [ ] [`driver-app/src/features/maps/hooks/useDriverLocationReporter.ts`](walkthrough/driver-app/src/features/maps/hooks/useDriverLocationReporter.ts.md)
- [ ] [`driver-app/src/features/maps/services/driverMapService.ts`](walkthrough/driver-app/src/features/maps/services/driverMapService.ts.md)
- [ ] [`driver-app/src/features/profile/screens/DriverSettingsScreen.tsx`](walkthrough/driver-app/src/features/profile/screens/DriverSettingsScreen.tsx.md)
- [ ] [`driver-app/src/features/profile/services/driverProfileService.ts`](walkthrough/driver-app/src/features/profile/services/driverProfileService.ts.md)
- [ ] [`driver-app/src/features/rides/screens/DriverActiveRideScreen.tsx`](walkthrough/driver-app/src/features/rides/screens/DriverActiveRideScreen.tsx.md)
- [ ] [`driver-app/src/features/rides/screens/DriverOutstationScreen.tsx`](walkthrough/driver-app/src/features/rides/screens/DriverOutstationScreen.tsx.md)
- [ ] [`driver-app/src/features/rides/screens/DriverTripHistoryScreen.tsx`](walkthrough/driver-app/src/features/rides/screens/DriverTripHistoryScreen.tsx.md)
- [ ] [`driver-app/src/features/rides/screens/RideRequestScreen.tsx`](walkthrough/driver-app/src/features/rides/screens/RideRequestScreen.tsx.md)
- [ ] [`driver-app/src/features/rides/services/driverRealtimeService.ts`](walkthrough/driver-app/src/features/rides/services/driverRealtimeService.ts.md)
- [ ] [`driver-app/src/features/rides/services/rideMatchingService.ts`](walkthrough/driver-app/src/features/rides/services/rideMatchingService.ts.md)
- [ ] [`driver-app/src/features/splash/screens/DriverSplashScreen.tsx`](walkthrough/driver-app/src/features/splash/screens/DriverSplashScreen.tsx.md)
- [ ] [`driver-app/src/features/support/screens/DriverHelpScreen.tsx`](walkthrough/driver-app/src/features/support/screens/DriverHelpScreen.tsx.md)
- [ ] [`driver-app/src/navigation/DriverNavigator.tsx`](walkthrough/driver-app/src/navigation/DriverNavigator.tsx.md)
- [ ] [`driver-app/src/navigation/types.ts`](walkthrough/driver-app/src/navigation/types.ts.md)
- [ ] [`driver-app/src/services/apiClient.ts`](walkthrough/driver-app/src/services/apiClient.ts.md)
- [ ] [`driver-app/src/theme/index.ts`](walkthrough/driver-app/src/theme/index.ts.md)
- [ ] [`driver-app/src/theme/tokens.ts`](walkthrough/driver-app/src/theme/tokens.ts.md)
- [ ] [`driver-app/src/types/react-native-config.d.ts`](walkthrough/driver-app/src/types/react-native-config.d.ts.md)
- [ ] [`driver-app/src/types/react-native-vector-icons.d.ts`](walkthrough/driver-app/src/types/react-native-vector-icons.d.ts.md)

### Passenger app config and native files

- [ ] [`passenger-app/android/app/build.gradle`](walkthrough/passenger-app/android/app/build.gradle.md)
- [ ] [`passenger-app/android/app/src/main/AndroidManifest.xml`](walkthrough/passenger-app/android/app/src/main/AndroidManifest.xml.md)
- [ ] [`passenger-app/android/app/src/main/java/com/passengerapp/MainActivity.kt`](walkthrough/passenger-app/android/app/src/main/java/com/passengerapp/MainActivity.kt.md)
- [ ] [`passenger-app/android/app/src/main/java/com/passengerapp/MainApplication.kt`](walkthrough/passenger-app/android/app/src/main/java/com/passengerapp/MainApplication.kt.md)
- [ ] [`passenger-app/android/app/src/main/res/values/strings.xml`](walkthrough/passenger-app/android/app/src/main/res/values/strings.xml.md)
- [ ] [`passenger-app/android/app/src/main/res/values/styles.xml`](walkthrough/passenger-app/android/app/src/main/res/values/styles.xml.md)
- [ ] [`passenger-app/android/build.gradle`](walkthrough/passenger-app/android/build.gradle.md)
- [ ] [`passenger-app/android/settings.gradle`](walkthrough/passenger-app/android/settings.gradle.md)
- [ ] [`passenger-app/app.json`](walkthrough/passenger-app/app.json.md)
- [ ] [`passenger-app/App.tsx`](walkthrough/passenger-app/App.tsx.md)
- [ ] [`passenger-app/babel.config.js`](walkthrough/passenger-app/babel.config.js.md)
- [ ] [`passenger-app/.env.example`](walkthrough/passenger-app/.env.example.md)
- [ ] [`passenger-app/eslint.config.mjs`](walkthrough/passenger-app/eslint.config.mjs.md)
- [ ] [`passenger-app/index.js`](walkthrough/passenger-app/index.js.md)
- [ ] [`passenger-app/ios/PassengerApp/AppDelegate.swift`](walkthrough/passenger-app/ios/PassengerApp/AppDelegate.swift.md)
- [ ] [`passenger-app/ios/.xcode.env`](walkthrough/passenger-app/ios/.xcode.env.md)
- [ ] [`passenger-app/jest.config.js`](walkthrough/passenger-app/jest.config.js.md)
- [ ] [`passenger-app/metro.config.js`](walkthrough/passenger-app/metro.config.js.md)
- [ ] [`passenger-app/package.json`](walkthrough/passenger-app/package.json.md)
- [ ] [`passenger-app/react-native.config.js`](walkthrough/passenger-app/react-native.config.js.md)
- [ ] [`passenger-app/README.md`](walkthrough/passenger-app/README.md.md)
- [ ] [`passenger-app/tsconfig.json`](walkthrough/passenger-app/tsconfig.json.md)

### Driver app config and native files

- [ ] [`driver-app/android/app/build.gradle`](walkthrough/driver-app/android/app/build.gradle.md)
- [ ] [`driver-app/android/app/src/main/AndroidManifest.xml`](walkthrough/driver-app/android/app/src/main/AndroidManifest.xml.md)
- [ ] [`driver-app/android/app/src/main/java/com/driverapp/MainActivity.kt`](walkthrough/driver-app/android/app/src/main/java/com/driverapp/MainActivity.kt.md)
- [ ] [`driver-app/android/app/src/main/java/com/driverapp/MainApplication.kt`](walkthrough/driver-app/android/app/src/main/java/com/driverapp/MainApplication.kt.md)
- [ ] [`driver-app/android/app/src/main/res/values/strings.xml`](walkthrough/driver-app/android/app/src/main/res/values/strings.xml.md)
- [ ] [`driver-app/android/app/src/main/res/values/styles.xml`](walkthrough/driver-app/android/app/src/main/res/values/styles.xml.md)
- [ ] [`driver-app/android/build.gradle`](walkthrough/driver-app/android/build.gradle.md)
- [ ] [`driver-app/android/settings.gradle`](walkthrough/driver-app/android/settings.gradle.md)
- [ ] [`driver-app/app.json`](walkthrough/driver-app/app.json.md)
- [ ] [`driver-app/App.tsx`](walkthrough/driver-app/App.tsx.md)
- [ ] [`driver-app/babel.config.js`](walkthrough/driver-app/babel.config.js.md)
- [ ] [`driver-app/.env.example`](walkthrough/driver-app/.env.example.md)
- [ ] [`driver-app/eslint.config.mjs`](walkthrough/driver-app/eslint.config.mjs.md)
- [ ] [`driver-app/index.js`](walkthrough/driver-app/index.js.md)
- [ ] [`driver-app/ios/DriverApp/AppDelegate.swift`](walkthrough/driver-app/ios/DriverApp/AppDelegate.swift.md)
- [ ] [`driver-app/ios/.xcode.env`](walkthrough/driver-app/ios/.xcode.env.md)
- [ ] [`driver-app/jest.config.js`](walkthrough/driver-app/jest.config.js.md)
- [ ] [`driver-app/metro.config.js`](walkthrough/driver-app/metro.config.js.md)
- [ ] [`driver-app/package.json`](walkthrough/driver-app/package.json.md)
- [ ] [`driver-app/react-native.config.js`](walkthrough/driver-app/react-native.config.js.md)
- [ ] [`driver-app/tsconfig.json`](walkthrough/driver-app/tsconfig.json.md)

### Root and docs

- [ ] [`docs/authentication-api.md`](walkthrough/docs/authentication-api.md.md)
- [ ] [`docs/database-guidelines.md`](walkthrough/docs/database-guidelines.md.md)
- [ ] [`docs/driver-app-foundation.md`](walkthrough/docs/driver-app-foundation.md.md)
- [ ] [`.env.example`](walkthrough/.env.example.md)
- [ ] [`package.json`](walkthrough/package.json.md)
- [ ] [`pnpm-workspace.yaml`](walkthrough/pnpm-workspace.yaml.md)
- [ ] [`.prettierrc.json`](walkthrough/.prettierrc.json.md)
- [ ] [`README.md`](walkthrough/README.md.md)


Back to `00-start-here.md`.
