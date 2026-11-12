from datetime import UTC, datetime, timedelta
from unittest.mock import patch
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.core.config import Settings
from app.db import Base
from app.models.ride_hailing import Driver, DriverCurrentLocation, DriverVehicleAssignment, FareQuote, RateCard, Ride, RideCategory, Vehicle
from app.models.user import Passenger
from app.repositories.passenger_repository import PassengerRepository
from app.services.auth_service import AuthService
from app.services.map_provider_service import MapProviderService
from app.services.ride_lifecycle_service import RideLifecycleService
from app.services.ride_matching_service import RideMatchingService


def _session():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_map_provider_offline_fallback_in_development():
    dev_settings = Settings(environment='development', geoapify_api_key=None)
    with patch('app.services.map_provider_service.get_settings', return_value=dev_settings):
        service = MapProviderService()

        # Config
        config = service.config()
        assert config.offline_mode is True
        assert 'style.json' in config.style_url

        # Search
        results = service.search('Kangla')
        assert len(results) > 0
        assert 'Kangla' in results[0].name

        # Reverse
        place = service.reverse(24.8170, 93.9368)
        assert place.name == 'Kangla Fort'
        assert 'Imphal' in place.formatted_address

        # Route
        route = service.route((24.8170, 93.9368), (24.7600, 93.8967))
        assert route.is_estimated is True
        assert route.route_type == 'straight_line_estimate'
        assert route.distance_meters > 0
        assert route.duration_seconds > 0


def test_map_provider_raises_503_in_production_without_key():
    prod_settings = Settings(
        environment='production',
        jwt_secret_key='a' * 32,
        geoapify_api_key=None,
    )
    with patch('app.services.map_provider_service.get_settings', return_value=prod_settings):
        service = MapProviderService()
        with pytest.raises(HTTPException) as exc:
            service.config()
        assert exc.value.status_code == 503

        with pytest.raises(HTTPException) as exc:
            service.search('Kangla')
        assert exc.value.status_code == 503

        with pytest.raises(HTTPException) as exc:
            service.reverse(24.8170, 93.9368)
        assert exc.value.status_code == 503

        with pytest.raises(HTTPException) as exc:
            service.route((24.8170, 93.9368), (24.7600, 93.8967))
        assert exc.value.status_code == 503


def test_ride_matching_dev_simulation_matches_karnataka_test_driver():
    session = _session()
    passenger = Passenger(full_name='Passenger Dishant', phone_number='919876543210', password_hash='hashed', is_phone_verified=True)
    category = RideCategory(code='hatchback', display_name='Hatchback', seat_count=4, base_fare_paise=18000, estimated_arrival_minutes=4, icon_key='car')
    session.add_all([passenger, category])
    session.flush()

    # Seeded test driver with phone +919876543220 physically in Karnataka (15.4848, 74.9365)
    driver = Driver(
        firebase_uid='driver-test-uid',
        full_name='Test Driver',
        phone_number='+919876543220',
        status='active',
        is_online=True,
    )
    vehicle = Vehicle(
        registration_number='MN01AB1234',
        make='Maruti',
        model='WagonR',
        year=2024,
        category_code='hatchback',
        seat_count=4,
        verification_status='verified',
    )
    session.add_all([driver, vehicle])
    session.flush()

    session.add(DriverVehicleAssignment(driver_id=driver.id, vehicle_id=vehicle.id))
    # Driver actual location in Karnataka
    karnataka_lat, karnataka_lon = 15.4848, 74.9365
    session.add(DriverCurrentLocation(driver_id=driver.id, latitude=karnataka_lat, longitude=karnataka_lon))

    # Ride requested in Imphal
    ride = Ride(
        passenger_id=passenger.id,
        category_id=category.id,
        status='searching',
        pickup_address='Kangla Fort, Imphal',
        pickup_latitude=24.8170,
        pickup_longitude=93.9368,
        destination_address='Bir Tikendrajit Airport, Imphal',
        destination_latitude=24.7600,
        destination_longitude=93.8967,
        requested_at=datetime.now(UTC),
        estimated_distance_meters=9500,
    )
    session.add(ride)
    session.flush()
    session.add(FareQuote(ride_id=ride.id, amount_paise=24000, expires_at=datetime.now(UTC) + timedelta(minutes=5)))
    session.commit()

    dev_settings = Settings(
        environment='development',
        dev_simulate_test_driver_imphal=True,
        dev_test_driver_phone='+919876543220',
        dev_test_driver_latitude=24.8170,
        dev_test_driver_longitude=93.9368,
    )
    with patch('app.services.ride_matching_service.get_settings', return_value=dev_settings):
        service = RideMatchingService()
        offer = service.dispatch(session, ride)
        session.commit()

        # Offer should be created and assigned to test driver
        assert offer is not None
        assert offer.driver_id == driver.id

        # Driver responds and accepts offer
        res = service.respond(session, driver, offer.id, 'accepted')
        session.commit()
        assert res.ride_status == 'driver_arriving'

        # Crucial: verify that the actual GPS location record in the database was NOT overwritten
        loc = session.get(DriverCurrentLocation, driver.id)
        assert round(float(loc.latitude), 4) == round(karnataka_lat, 4)
        assert round(float(loc.longitude), 4) == round(karnataka_lon, 4)

        # Verify passenger_status reports simulated Imphal coordinates for map tracking
        session.refresh(ride)
        status = service.passenger_status(session, ride)
        assert status.driver_latitude == 24.8170
        assert status.driver_longitude == 93.9368
        assert status.driver_name == 'Test Driver'
        assert status.vehicle_registration_number == 'MN01AB1234'


def test_ride_matching_production_rejects_driver_outside_radius():
    session = _session()
    passenger = Passenger(full_name='Passenger Dishant', phone_number='919876543210', password_hash='hashed', is_phone_verified=True)
    category = RideCategory(code='hatchback', display_name='Hatchback', seat_count=4, base_fare_paise=18000, estimated_arrival_minutes=4, icon_key='car')
    session.add_all([passenger, category])
    session.flush()

    driver = Driver(
        firebase_uid='driver-test-uid',
        full_name='Test Driver',
        phone_number='+919876543220',
        status='active',
        is_online=True,
    )
    vehicle = Vehicle(
        registration_number='MN01AB1234',
        make='Maruti',
        model='WagonR',
        year=2024,
        category_code='hatchback',
        seat_count=4,
        verification_status='verified',
    )
    session.add_all([driver, vehicle])
    session.flush()

    session.add(DriverVehicleAssignment(driver_id=driver.id, vehicle_id=vehicle.id))
    # Driver in Karnataka
    session.add(DriverCurrentLocation(driver_id=driver.id, latitude=15.4848, longitude=74.9365))

    ride = Ride(
        passenger_id=passenger.id,
        category_id=category.id,
        status='searching',
        pickup_address='Kangla Fort, Imphal',
        pickup_latitude=24.8170,
        pickup_longitude=93.9368,
        destination_address='Bir Tikendrajit Airport, Imphal',
        destination_latitude=24.7600,
        destination_longitude=93.8967,
        requested_at=datetime.now(UTC),
        estimated_distance_meters=9500,
    )
    session.add(ride)
    session.flush()
    session.add(FareQuote(ride_id=ride.id, amount_paise=24000, expires_at=datetime.now(UTC) + timedelta(minutes=5)))
    session.commit()

    prod_settings = Settings(
        environment='production',
        jwt_secret_key='a' * 32,
        dev_simulate_test_driver_imphal=True,
        dev_test_driver_phone='+919876543220',
    )
    with patch('app.services.ride_matching_service.get_settings', return_value=prod_settings):
        service = RideMatchingService()
        offer = service.dispatch(session, ride)
        # In production, dev simulation is disabled because environment != 'development'
        assert offer is None
        assert ride.status == 'cancelled'
        assert ride.cancellation_reason == 'no_eligible_driver'


def test_complete_passenger_to_driver_booking_flow_with_simulation():
    session = _session()
    passenger = Passenger(full_name='Dishant Passenger', phone_number='+919876543210', password_hash='hashed', is_phone_verified=True)
    category = RideCategory(code='hatchback', display_name='Hatchback', seat_count=4, base_fare_paise=8000, estimated_arrival_minutes=4, icon_key='car')
    rate_card = RateCard(
        category_code='hatchback',
        version=1,
        base_fare_paise=8000,
        first_tier_km=10.0,
        first_tier_rate_paise=2800,
        second_tier_rate_paise=2800,
        waiting_charge_per_minute_paise=200,
        waiting_grace_period_minutes=3.0,
        surcharge_distance_threshold_km=15.0,
        surcharge_percentage=15.0,
        cancellation_fee_paise=5000,
        gst_rate=0.05,
        commission_rate=0.0,
        is_active=True,
    )
    session.add_all([passenger, category, rate_card])
    session.flush()

    # Seeded Test Driver in Karnataka (15.4848, 74.9365)
    driver = Driver(
        firebase_uid='driver-sim-uid',
        full_name='Test Driver',
        phone_number='+919876543220',
        status='active',
        is_online=True,
    )
    vehicle = Vehicle(
        registration_number='MN01AB1234',
        make='Maruti',
        model='WagonR',
        year=2024,
        category_code='hatchback',
        seat_count=4,
        verification_status='verified',
    )
    session.add_all([driver, vehicle])
    session.flush()

    session.add(DriverVehicleAssignment(driver_id=driver.id, vehicle_id=vehicle.id))
    karnataka_lat, karnataka_lon = 15.484867, 74.936546
    session.add(DriverCurrentLocation(driver_id=driver.id, latitude=karnataka_lat, longitude=karnataka_lon))

    # Passenger creates ride in Imphal
    ride = Ride(
        passenger_id=passenger.id,
        category_id=category.id,
        status='searching',
        pickup_address='Kangla Fort, Imphal',
        pickup_latitude=24.8170,
        pickup_longitude=93.9368,
        destination_address='Bir Tikendrajit Airport, Imphal',
        destination_latitude=24.7600,
        destination_longitude=93.8967,
        requested_at=datetime.now(UTC),
        estimated_distance_meters=8700,
    )
    session.add(ride)
    session.flush()
    session.add(FareQuote(ride_id=ride.id, amount_paise=34300, expires_at=datetime.now(UTC) + timedelta(minutes=5)))
    session.commit()

    dev_settings = Settings(
        environment='development',
        dev_simulate_test_driver_imphal=True,
        dev_test_driver_phone='+919876543220',
        dev_test_driver_latitude=24.8170,
        dev_test_driver_longitude=93.9368,
    )

    with patch('app.services.ride_matching_service.get_settings', return_value=dev_settings), \
         patch('app.services.ride_lifecycle_service.get_settings', return_value=dev_settings):

        matching_service = RideMatchingService()
        lifecycle_service = RideLifecycleService()

        # Step 1: Matching dispatches offer to simulated driver
        offer = matching_service.dispatch(session, ride)
        session.commit()
        assert offer is not None
        assert offer.driver_id == driver.id
        assert offer.status == 'pending'

        # Step 2: Driver accepts offer
        decision = matching_service.respond(session, driver, offer.id, 'accepted')
        session.commit()
        session.refresh(ride)
        assert decision.ride_status == 'driver_arriving'
        assert ride.status == 'driver_arriving'
        assert ride.driver_id == driver.id

        # Step 3: Passenger checks status, sees simulated driver coordinates in Imphal
        pass_status = matching_service.passenger_status(session, ride)
        assert pass_status.driver_name == 'Test Driver'
        assert pass_status.vehicle_registration_number == 'MN01AB1234'
        assert pass_status.driver_latitude == 24.8170
        assert pass_status.driver_longitude == 93.9368

        # Step 4: Driver marks arrived
        arrived_res = lifecycle_service.action(session, driver, ride.id, 'arrived')
        session.commit()
        session.refresh(ride)
        assert ride.status == 'driver_arrived'

        # Step 5: Passenger retrieves 4-digit ride start OTP
        start_otp = RideLifecycleService.get_passenger_ride_otp(session, ride)
        assert start_otp is not None
        assert len(start_otp) == 4

        # Step 6: Driver starts trip with OTP
        start_res = lifecycle_service.action(session, driver, ride.id, 'start', start_otp=start_otp)
        session.commit()
        session.refresh(ride)
        assert ride.status == 'in_progress'

        # Step 7: Driver completes trip
        complete_res = lifecycle_service.action(session, driver, ride.id, 'complete')
        session.commit()
        session.refresh(ride)
        assert ride.status == 'completed'
        assert ride.final_distance_meters > 0

        # Step 8: Driver confirms cash payment collection
        pay_res = lifecycle_service.action(session, driver, ride.id, 'confirm_payment', payment_method='cash')
        session.commit()
        assert 'confirmed' in pay_res.message.lower()

        # Step 9: Verify driver's actual physical location in database was never altered
        db_loc = session.get(DriverCurrentLocation, driver.id)
        assert round(float(db_loc.latitude), 4) == round(karnataka_lat, 4)
        assert round(float(db_loc.longitude), 4) == round(karnataka_lon, 4)


def test_passenger_token_refresh_flow():
    session = _session()
    auth_service = AuthService()

    # 1. Create a verified passenger
    passenger = Passenger(
        full_name='Test Passenger',
        phone_number='+919876543210',
        password_hash='test-hash',
        is_phone_verified=True,
        status='active',
    )
    session.add(passenger)
    session.commit()
    session.refresh(passenger)

    # 2. Issue initial tokens
    tokens = auth_service._tokens(passenger)
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None

    # 3. Test PassengerRepository.get()
    repo = PassengerRepository()
    fetched = repo.get(session, passenger.id)
    assert fetched is not None
    assert fetched.id == passenger.id
    assert fetched.phone_number == '+919876543210'

    # 4. Refresh tokens using the refresh token
    new_tokens = auth_service.refresh(session, tokens.refresh_token)
    assert new_tokens.access_token is not None
    assert new_tokens.refresh_token is not None

    # Verify decoded access token belongs to passenger
    decoded = auth_service._decode(new_tokens.access_token, 'access')
    assert int(decoded['sub']) == passenger.id
    assert decoded['actor'] == 'passenger'

    # 5. Invalid refresh token raises 401
    with pytest.raises(HTTPException) as exc:
        auth_service.refresh(session, 'invalid.token.here')
    assert exc.value.status_code == 401

    # 6. Deactivated passenger cannot refresh
    passenger.status = 'suspended'
    session.commit()
    with pytest.raises(HTTPException) as exc:
        auth_service.refresh(session, new_tokens.refresh_token)
    assert exc.value.status_code == 401


