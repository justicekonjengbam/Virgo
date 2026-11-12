from datetime import UTC, datetime, timedelta

from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.db import Base
from app.models.ride_hailing import Driver, DriverCurrentLocation, DriverVehicleAssignment, FareQuote, Ride, RideCategory, Vehicle
from app.models.user import Passenger
from app.services.ride_matching_service import RideMatchingService


def _session():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def _ride(session, driver_ready: bool = True):
    passenger = Passenger(full_name='Passenger', phone_number='919876543210', password_hash='hashed', is_phone_verified=True)
    category = RideCategory(code='car', display_name='Car', seat_count=4, base_fare_paise=18000, estimated_arrival_minutes=4, icon_key='car')
    session.add_all([passenger, category]); session.flush()
    if driver_ready:
        driver = Driver(firebase_uid='driver-firebase', full_name='Driver', phone_number='919876543211', status='active', is_online=True)
        vehicle = Vehicle(registration_number='MN01AB1234', make='Test', model='Car', year=2024, category_code='car', seat_count=4, verification_status='verified')
        session.add_all([driver, vehicle]); session.flush()
        session.add_all([DriverVehicleAssignment(driver_id=driver.id, vehicle_id=vehicle.id), DriverCurrentLocation(driver_id=driver.id, latitude=24.8115, longitude=93.9422)])
    ride = Ride(passenger_id=passenger.id, category_id=category.id, status='searching', pickup_address='Kangla Fort, Imphal', pickup_latitude=24.8115, pickup_longitude=93.9422, destination_address='Bir Tikendrajit Airport, Imphal', destination_latitude=24.7600, destination_longitude=93.8967, requested_at=datetime.now(UTC), estimated_distance_meters=3500)
    session.add(ride); session.flush(); session.add(FareQuote(ride_id=ride.id, amount_paise=18000, expires_at=datetime.now(UTC) + timedelta(minutes=5))); session.commit()
    return ride, driver if driver_ready else None


def test_matching_assigns_nearby_verified_online_driver_after_acceptance() -> None:
    session = _session(); ride, driver = _ride(session)
    service = RideMatchingService()
    offer = service.dispatch(session, ride); session.commit()
    assert offer is not None
    current = service.current_offer(session, driver)
    assert current and current.ride_id == ride.id
    result = service.respond(session, driver, current.offer_id, 'accepted')
    session.refresh(ride)
    assert result.ride_status == 'driver_arriving'
    assert ride.driver_id == driver.id
    assert service.passenger_status(session, ride).driver_name == 'Driver'


def test_matching_cancels_when_no_eligible_driver_exists() -> None:
    session = _session(); ride, _ = _ride(session, driver_ready=False)
    service = RideMatchingService()
    assert service.dispatch(session, ride) is None
    assert ride.status == 'cancelled'
    assert ride.cancellation_reason == 'no_eligible_driver'


def test_matching_uses_imphal_city_when_driver_has_no_gps_fix() -> None:
    session = _session(); ride, driver = _ride(session)
    driver.operating_city = 'Imphal'
    location = session.get(DriverCurrentLocation, driver.id)
    session.delete(location)
    ride.pickup_latitude = 24.8170
    ride.pickup_longitude = 93.9368
    session.commit()

    offer = RideMatchingService().dispatch(session, ride)

    assert offer is not None
    assert offer.driver_id == driver.id


def test_matching_uses_operating_city_when_gps_fix_is_stale() -> None:
    session = _session(); ride, driver = _ride(session)
    driver.operating_city = 'Imphal West'
    location = session.get(DriverCurrentLocation, driver.id)
    location.recorded_at = datetime.now(UTC) - timedelta(minutes=6)
    session.commit()

    offer = RideMatchingService().dispatch(session, ride)

    assert offer is not None
    assert offer.driver_id == driver.id


def test_current_offer_serializes_naive_utc_datetime_with_z() -> None:
    session = _session(); ride, driver = _ride(session)
    service = RideMatchingService()
    offer = service.dispatch(session, ride)
    assert offer is not None

    # Simulate SQLite storing and returning naive datetime
    offer.expires_at = offer.expires_at.replace(tzinfo=None)
    session.commit()

    current = service.current_offer(session, driver)
    assert current is not None
    assert current.expires_at.tzinfo == UTC

    encoded = jsonable_encoder(current)
    assert isinstance(encoded['expires_at'], str)
    assert encoded['expires_at'].endswith('Z')


def test_current_offer_preserves_already_aware_datetime() -> None:
    session = _session(); ride, driver = _ride(session)
    service = RideMatchingService()
    offer = service.dispatch(session, ride)
    assert offer is not None

    # Explicitly ensure aware datetime
    offer.expires_at = datetime.now(UTC) + timedelta(seconds=45)
    session.commit()

    current = service.current_offer(session, driver)
    assert current is not None
    assert current.expires_at.tzinfo == UTC

    encoded = jsonable_encoder(current)
    assert isinstance(encoded['expires_at'], str)
    assert encoded['expires_at'].endswith('Z')


def test_valid_offer_remains_visible_throughout_45_second_lifetime() -> None:
    session = _session(); ride, driver = _ride(session)
    service = RideMatchingService()
    offer = service.dispatch(session, ride)
    assert offer is not None
    session.commit()

    # Immediately visible
    current = service.current_offer(session, driver)
    assert current is not None
    assert current.offer_id == offer.id

    # Simulate 40 seconds elapsed (5s before expiry)
    offer.expires_at = datetime.now(UTC) + timedelta(seconds=5)
    session.commit()
    current_near_expiry = service.current_offer(session, driver)
    assert current_near_expiry is not None
    assert current_near_expiry.offer_id == offer.id


def test_actually_expired_offer_is_cleared_correctly() -> None:
    session = _session(); ride, driver = _ride(session)
    service = RideMatchingService()
    offer = service.dispatch(session, ride)
    assert offer is not None
    session.commit()

    # Simulate offer past expiry
    offer.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    session.commit()

    current = service.current_offer(session, driver)
    assert current is None

    session.refresh(offer)
    assert offer.status == 'expired'



