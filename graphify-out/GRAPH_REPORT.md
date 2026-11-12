# Graph Report - CabSure-Ride-Booking-Application  (2026-10-26)

## Corpus Check
- 280 files · ~54,357 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 126 file(s) not represented in the graph (top: (none) 77, .ttf 12, .xml 8)

## Summary
- 1641 nodes · 4798 edges · 110 communities (47 shown, 63 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 334 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Driver Dashboard API
- Ride Matching and Driver Routes
- Passenger Auth Routes
- Passenger Auth UI
- Maps API
- Admin API
- Alembic Migrations
- Passenger Design System
- Passenger Booking Screens
- Passenger Foundation Components
- Driver Auth UI
- iOS Driver Shell
- Booking API Client
- Health and Settings
- Docs: Auth and Database Rules
- Driver Home Screen
- Passenger Navigation
- Driver Vehicle Verification
- Passenger Dependencies
- Dev Dependencies A
- Driver Brand Components
- Admin Web Console
- Driver Dependencies
- Dev Dependencies B
- Driver Session State
- Booking Routes
- Driver Config and Auth Service
- Driver Ride Map
- Passenger Login UI
- Passenger Profile
- Community 30: asyncio
- Community 31: alembic_config
- Community 32: get_home()
- Community 33: driver-app/metro.config.js
- Community 34: driver-app/package.json
- Community 35: passenger-app/package.json
- Community 36: require_admin_permission()
- Community 37: get_emergency_contacts()
- Community 38: driverapp/MainApplication.kt
- Community 39: App()
- Community 40: get_current_admin()
- Community 41: defaultreactactivitydelegate
- Community 42: BrandLogo.tsx
- Community 43: package.json
- Community 44: scripts
- Community 45: scripts
- Community 46: DriverDrawer
- Community 47: pnpm-workspace.yaml
- Community 49: .prettierrc.json
- Community 50: list_notifications()
- Community 51: driverRealtimeService
- Community 53: driver-app/tsconfig.json
- Community 55: passenger-app/tsconfig.json
- Community 60: @react-native-documents/picker@^12.0.2
- Community 61: react-native-gesture-handler@^2.29.1
- Community 62: react-native-maps@^1.26.19
- Community 63: @react-native-masked-view/masked-view@^0.3.2
- Community 64: @react-navigation/bottom-tabs@^7.8.12
- Community 65: @reduxjs/toolkit@^2.12.0
- Community 66: eslint@^9.39.1
- Community 67: eslint-plugin-react-hooks@^7.0.1
- Community 68: @react-native/babel-preset@0.86.2
- Community 69: @react-native-community/cli@20.1.0
- Community 70: @react-native/gradle-plugin@0.86.2
- Community 71: react-test-renderer@19.2.3
- Community 72: typescript@~6.0.3
- Community 73: driver-app/src/types/react-native-config.d.ts
- Community 74: driver-app/src/types/react-native-vector-icons.d.ts
- Community 75: react-native@0.86.2
- Community 76: react-native-gesture-handler@^2.29.1
- Community 77: react-native-maps@^1.26.19
- Community 78: react-native-svg@^15.15.5
- Community 79: @react-navigation/bottom-tabs@^7.8.12
- Community 80: react-redux@^9.2.0
- Community 81: @reduxjs/toolkit@^2.12.0
- Community 82: eslint-config-prettier@^10.1.8
- Community 83: eslint-plugin-react@^7.37.5
- Community 84: @react-native/babel-preset@0.86.2
- Community 85: @react-native-community/cli-platform-android@20.1.0
- Community 86: @react-native/jest-preset@0.86.2
- Community 87: @react-native/typescript-config@0.86.2
- Community 88: typescript@~6.0.3
- Community 89: assets.d.ts
- Community 90: passenger-app/src/types/react-native-config.d.ts
- Community 109: cabapp-api

## God Nodes (most connected - your core abstractions)
1. `Passenger` - 85 edges
2. `Driver` - 82 edges
3. `DsText()` - 80 edges
4. `DriverText()` - 58 edges
5. `Ride` - 44 edges
6. `RideMatchingService` - 44 edges
7. `Base` - 40 edges
8. `DsCard()` - 38 edges
9. `colors` - 37 edges
10. `OutstationService` - 34 edges

## Surprising Connections (you probably didn't know these)
- `Admin Bootstrap Account` --shares_data_with--> `FastAPI Backend`  [EXTRACTED]
  admin-app/README.md → README.md
- `Passenger Authentication API` --implements--> `FastAPI Backend`  [INFERRED]
  docs/authentication-api.md → README.md
- `Database Guide` --conceptually_related_to--> `FastAPI Backend`  [INFERRED]
  docs/database-guidelines.md → README.md
- `Android Emulator Setup (10.0.2.2:8000)` --shares_data_with--> `FastAPI Backend`  [EXTRACTED]
  passenger-app/README.md → README.md
- `get_current_admin()` --uses--> `AdminUser`  [INFERRED]
  backend/app/api/dependencies/admin_auth.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **CabSure platform components** — readme_passenger_app, readme_driver_app, readme_admin_console, readme_backend [EXTRACTED 1.00]
- **Firebase phone auth token exchange flow** — readme_firebase_auth, docs_authentication_api_firebase_exchange, docs_authentication_api_jwt_tokens [EXTRACTED 1.00]
- **Database data rules** — docs_database_guidelines_money_in_paise, docs_database_guidelines_no_secrets_stored, docs_database_guidelines_kyc_storage, docs_database_guidelines_integrity_records, docs_database_guidelines_alembic_migrations [EXTRACTED 1.00]

## Communities (110 total, 63 thin omitted)

### Community 0 - "Driver Dashboard API"
Cohesion: 0.06
Nodes (48): get_dashboard(), update_availability(), get_ride_request(), get_support(), get_trip_history(), Base, DeviceSession, Driver (+40 more)

### Community 1 - "Ride Matching and Driver Routes"
Cohesion: 0.06
Nodes (47): active_ride(), cancel_ride(), current_offer(), rate_passenger(), respond_to_offer(), ride_action(), ride_summary(), update_location() (+39 more)

### Community 2 - "Passenger Auth Routes"
Cohesion: 0.06
Nodes (36): firebase_login(), firebase_login_preflight(), firebase_signup(), login(), refresh(), request_otp(), signup(), verify_otp() (+28 more)

### Community 3 - "Passenger Auth UI"
Cohesion: 0.06
Nodes (60): AuthHeaderProps, styles, AuthInputProps, IconName, styles, AuthPromptProps, styles, RememberMeProps (+52 more)

### Community 4 - "Maps API"
Cohesion: 0.09
Nodes (25): map_config(), reverse_geocode(), search_places(), GeocodedPlaceResponse, MapConfigResponse, RouteResponse, AdminOutstationUpdate, DriverOutstationAssignmentResponse (+17 more)

### Community 5 - "Admin API"
Cohesion: 0.11
Nodes (21): change_password(), list_driver_documents(), list_drivers(), list_support_tickets(), login(), me(), review_driver_document(), update_support_ticket() (+13 more)

### Community 6 - "Alembic Migrations"
Cohesion: 0.08
Nodes (12): upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade() (+4 more)

### Community 7 - "Passenger Design System"
Cohesion: 0.09
Nodes (30): DsEmptyState(), DsLoading(), SavedAddressesScreen(), SavedAddressesScreenProps, styles, ImagePlaceholder(), ImagePlaceholderProps, styles (+22 more)

### Community 8 - "Passenger Booking Screens"
Cohesion: 0.13
Nodes (38): DsButton(), DsText(), DsCard(), DsTextField(), AppPageHeader(), BookingStatusScreen(), RouteLine(), FareEstimateScreen() (+30 more)

### Community 9 - "Passenger Foundation Components"
Cohesion: 0.07
Nodes (26): LoadingState(), LoadingStateProps, AppButton(), AppButtonProps, AppText(), AppTextProps, AppTextVariant, environment (+18 more)

### Community 10 - "Driver Auth UI"
Cohesion: 0.12
Nodes (26): DriverAuthHeaderProps, styles, DriverButtonProps, styles, styles, DriverTextProps, DriverTextFieldProps, styles (+18 more)

### Community 11 - "iOS Driver Shell"
Cohesion: 0.08
Nodes (8): AppDelegate, ReactNativeDelegate, AppDelegate, ReactNativeDelegate, React, React_RCTAppDelegate, ReactAppDependencyProvider, UIKit

### Community 12 - "Booking API Client"
Cohesion: 0.10
Nodes (26): bookingApi, FareEstimate, LocationOption, placePayload(), RideBooking, ridePayload(), RideStatus, RideSummary (+18 more)

### Community 13 - "Health and Settings"
Cohesion: 0.11
Nodes (8): health_check(), get_settings(), Settings, initialize_database(), create_app(), lifespan(), HealthResponse, initialize_firebase()

### Community 14 - "Docs: Auth and Database Rules"
Cohesion: 0.09
Nodes (30): Admin Bootstrap Account, Firebase ID Token Exchange, Access and Refresh JWT Tokens, OTP Signup and Verify Flow, Passenger Authentication API, Alembic Migrations Only, Database Guide, Idempotency Keys, Immutable Ride Events, Audit/Outbox (+22 more)

### Community 15 - "Driver Home Screen"
Cohesion: 0.15
Nodes (27): DriverText(), DriverHeader(), useDriverDashboard(), AvailabilityCard(), capitalize(), DashboardError(), DashboardLoading(), DetailSheet (+19 more)

### Community 16 - "Passenger Navigation"
Cohesion: 0.14
Nodes (30): LocationSelectionScreen(), HomeDrawer(), SplashScreen(), AddressesRoute(), AuthenticatedShell(), BookingDraftContext, BookingRoute(), DestinationRoute() (+22 more)

### Community 17 - "Driver Vehicle Verification"
Cohesion: 0.11
Nodes (25): DriverAuthHeader(), DriverTextField(), DriverPhoneAuthForm(), documents, DocumentType, DriverVehicleVerificationForm(), Props, seatsByVehicleType (+17 more)

### Community 18 - "Passenger Dependencies"
Cohesion: 0.07
Nodes (29): dependencies, axios@^1.13.2, react@^19.2.3, react-native@0.86.2, @react-native-async-storage/async-storage@^2.2.0, @react-native-community/netinfo@^11.4.1, react-native-config@^1.6.1, @react-native-firebase/app@25.1.0 (+21 more)

### Community 19 - "Dev Dependencies A"
Cohesion: 0.07
Nodes (29): devDependencies, @babel/core@7.25.2, eslint-config-prettier@^10.1.8, eslint-plugin-react@^7.37.5, jest@^30.2.0, prettier@^3.8.2, @react-native/codegen@0.86.2, @react-native-community/cli-platform-android@20.1.0 (+21 more)

### Community 20 - "Driver Brand Components"
Cohesion: 0.13
Nodes (22): DriverBrandLogo(), DriverBrandMark(), styles, DriverCard(), DriverPageHeader(), styles, driverMenuService, DriverRideRequest (+14 more)

### Community 21 - "Admin Web Console"
Cohesion: 0.19
Nodes (27): account(), api(), appView, badge(), changePassword(), clearSession(), content, documents() (+19 more)

### Community 22 - "Driver Dependencies"
Cohesion: 0.07
Nodes (27): dependencies, axios@^1.13.2, @babel/runtime@7.25.0, @maplibre/maplibre-react-native@11.0.0, react-hook-form@^7.71.2, @react-native-async-storage/async-storage@^2.2.0, @react-native-community/netinfo@^11.4.1, react-native-config@^1.6.1 (+19 more)

### Community 23 - "Dev Dependencies B"
Cohesion: 0.07
Nodes (27): devDependencies, @babel/core@7.25.2, eslint@^9.39.1, @eslint/js@^9.39.1, eslint-plugin-react-hooks@^7.0.1, jest@^30.2.0, @react-native/codegen@0.86.2, @react-native-community/cli@20.1.0 (+19 more)

### Community 24 - "Driver Session State"
Cohesion: 0.12
Nodes (20): DriverButton(), DriverOnboardingScreen(), DriverSession, DriverSessionContext, DriverSessionProvider(), RideRequestStatus, useDriverSession(), RideRequestScreen() (+12 more)

### Community 25 - "Booking Routes"
Cohesion: 0.19
Nodes (11): book_ride(), cancel_ride(), estimate_ride(), get_active_ride(), get_locations(), get_ride_status(), rate_driver(), ride_summary() (+3 more)

### Community 26 - "Driver Config and Auth Service"
Cohesion: 0.11
Nodes (14): environment, DriverAuthIntent, driverAuthService, DriverProfile, DriverRegistrationPayload, MapConfiguration, ConnectionListener, DriverRealtimeEvent (+6 more)

### Community 27 - "Driver Ride Map"
Cohesion: 0.14
Nodes (18): bounds(), Coordinate, DriverRideMap(), Props, RideMarker(), styles, useDriverLocationReporter(), getMapConfiguration() (+10 more)

### Community 28 - "Passenger Login UI"
Cohesion: 0.19
Nodes (17): AuthHeader(), AuthInput(), AuthPrompt(), RememberMe(), LoginScreen(), LoginScreenProps, styles, SignupScreen() (+9 more)

### Community 29 - "Passenger Profile"
Cohesion: 0.19
Nodes (5): get_profile(), update_profile(), PassengerProfileResponse, PassengerProfileUpdateRequest, PassengerProfileService

### Community 30 - "Community 30: asyncio"
Cohesion: 0.16
Nodes (4): RealtimeHub, schedule(), FakeWebSocket, test_realtime_hub_delivers_to_connected_channel_only()

### Community 32 - "Community 32: get_home()"
Cohesion: 0.23
Nodes (8): get_home(), HomeResponse, PlaceResponse, PlaceSuggestionResponse, RecentRideResponse, RideCategoryResponse, HomeSeedService, HomeService

### Community 33 - "Community 33: driver-app/metro.config.js"
Cohesion: 0.13
Nodes (10): babelRuntimeRoot, config, generatedCacheOutputs, realProjectRoot, workspaceNodeModules, workspaceRoot, babelRuntimeRoot, config (+2 more)

### Community 34 - "Community 34: driver-app/package.json"
Cohesion: 0.12
Nodes (15): @maplibre/maplibre-react-native@11.0.0, react-hook-form@^7.71.2, react-native-svg@15.15.5, @babel/runtime@7.25.0, @eslint/js@^9.39.1, @types/react-test-renderer@19.1.0, @babel/runtime, @eslint/js (+7 more)

### Community 35 - "Community 35: passenger-app/package.json"
Cohesion: 0.12
Nodes (15): react@^19.2.3, @react-native-masked-view/masked-view@^0.3.2, react-native-screens@^4.18.0, prettier@^3.8.2, @types/react@^19.1.1, typescript-eslint@^8.46.4, prettier, react (+7 more)

### Community 36 - "Community 36: require_admin_permission()"
Cohesion: 0.24
Nodes (9): require_admin_permission(), admin_bookings(), cancel_booking(), create_booking(), driver_assignments(), eligible_drivers(), estimate_booking(), passenger_bookings() (+1 more)

### Community 37 - "Community 37: get_emergency_contacts()"
Cohesion: 0.16
Nodes (4): get_emergency_contacts(), EmergencyContactResponse, NotificationResponse, EmergencyContactService

### Community 39 - "Community 39: App()"
Cohesion: 0.19
Nodes (8): App(), displayName, name, DriverNavigator(), App(), displayName, name, PassengerNavigator()

### Community 40 - "Community 40: get_current_admin()"
Cohesion: 0.25
Nodes (7): get_current_admin(), get_current_driver(), _bearer_token(), _decode(), driver_events(), _keep_alive(), passenger_ride_events()

### Community 42 - "Community 42: BrandLogo.tsx"
Cohesion: 0.19
Nodes (9): BrandLogo(), BrandLogoProps, BrandMark(), BrandMarkProps, styles, DrawerDestination, HomeDrawerProps, navigationItems (+1 more)

### Community 43 - "Community 43: package.json"
Cohesion: 0.18
Nodes (11): devDependencies, prettier@^3.8.2, prettier, name, packageManager, private, scripts, format (+3 more)

### Community 44 - "Community 44: scripts"
Cohesion: 0.20
Nodes (10): scripts, android, format, format:check, ios, lint, start, start:reset (+2 more)

### Community 45 - "Community 45: scripts"
Cohesion: 0.22
Nodes (9): scripts, android, format, format:check, ios, lint, start, test (+1 more)

### Community 47 - "Community 47: pnpm-workspace.yaml"
Cohesion: 0.29
Nodes (6): allowBuilds, @firebase/util, protobufjs, unrs-resolver, onlyBuiltDependencies, packages

### Community 49 - "Community 49: .prettierrc.json"
Cohesion: 0.33
Nodes (5): printWidth, semi, singleQuote, tabWidth, trailingComma

### Community 53 - "Community 53: driver-app/tsconfig.json"
Cohesion: 0.50
Nodes (3): extends, include, @react-native/typescript-config

### Community 55 - "Community 55: passenger-app/tsconfig.json"
Cohesion: 0.50
Nodes (3): extends, include, @react-native/typescript-config

## Knowledge Gaps
- **14 isolated node(s):** `cabapp-api`, `@react-native/typescript-config`, `@react-native/typescript-config`, `pnpm Workspaces`, `OTP Signup and Verify Flow` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 398 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **63 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Passenger` connect `Booking Routes` to `Community 32: get_home()`, `Driver Dashboard API`, `Passenger Auth Routes`, `Ride Matching and Driver Routes`, `Maps API`, `Community 37: get_emergency_contacts()`, `Community 36: require_admin_permission()`, `Admin API`, `Community 40: get_current_admin()`, `Health and Settings`, `Community 50: list_notifications()`, `Passenger Profile`, `Community 31: alembic_config`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `Passenger` (e.g. with `get_current_passenger()` and `book_ride()`) actually correct?**
  _`Passenger` has 33 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cabapp-api`, `@react-native/typescript-config`, `@react-native/typescript-config` to the rest of the system?**
  _14 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Driver Dashboard API` be split into smaller, more focused modules?**
  _Cohesion score 0.05573668684986803 - nodes in this community are weakly interconnected._
- **Why does `@react-native-documents/picker` connect `Community 60: @react-native-documents/picker@^12.0.2` to `Driver Vehicle Verification`, `Community 34: driver-app/package.json`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `Driver` (e.g. with `get_current_driver()` and `get_dashboard()`) actually correct?**
  _`Driver` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Should `Ride Matching and Driver Routes` be split into smaller, more focused modules?**
  _Cohesion score 0.06218144750254842 - nodes in this community are weakly interconnected._