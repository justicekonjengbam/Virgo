from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.db import Base
from app.models.ride_hailing import Driver, DriverVehicleAssignment, Notification, Vehicle
from app.models.user import Passenger
from app.schemas.maps import RouteResponse
from app.schemas.outstation import AdminOutstationUpdate, OutstationBookingCreate, OutstationLocation
from app.services.outstation_service import OutstationService


def _session():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def _passenger(session):
    passenger = Passenger(full_name='Outstation Passenger', phone_number='919876543210', password_hash='hashed', is_phone_verified=True)
    session.add(passenger); session.commit()
    return passenger


class _MapProvider:
    def route(self, origin, destination):
        return RouteResponse(distance_meters=430_000, duration_seconds=25_200, geometry={'type': 'LineString', 'coordinates': [[75.0, 15.4], [77.6, 12.9]]})


def _request(hours: int = 48, preference: str | None = 'sedan') -> OutstationBookingCreate:
    return OutstationBookingCreate(
        scheduled_at=datetime.now(UTC) + timedelta(hours=hours),
        pickup=OutstationLocation(place_id='imphal_airport', name='Bir Tikendrajit Airport', formatted_address='Airport Road, Imphal, Manipur, India', latitude=24.7600, longitude=93.8967),
        destination=OutstationLocation(place_id='guwahati', name='Guwahati Railway Station', formatted_address='Paltan Bazaar, Guwahati, Assam, India', latitude=26.1824, longitude=91.7505),
        preferred_vehicle_type=preference,
    )


def test_request_is_stored_and_notified() -> None:
    session, service = _session(), OutstationService(_MapProvider()); passenger = _passenger(session)
    response = service.create(session, passenger, _request())
    assert response.status == 'requested'
    assert session.query(Notification).filter_by(passenger_id=passenger.id, notification_type='outstation_requested').count() == 1


def test_request_rejects_short_notice() -> None:
    session, service = _session(), OutstationService(_MapProvider()); passenger = _passenger(session)
    with pytest.raises(HTTPException) as error:
        service.create(session, passenger, _request(hours=2))
    assert error.value.status_code == 422


def test_support_confirms_fare_and_assigns_verified_driver() -> None:
    session, service = _session(), OutstationService(_MapProvider()); passenger = _passenger(session)
    booking = service.create(session, passenger, _request(hours=72, preference='suv'))
    confirmed = service.admin_update(session, booking.id, AdminOutstationUpdate(status='confirmed'), 1)
    assert confirmed.estimated_fare_paise and confirmed.estimated_fare_paise > 330000
    driver = Driver(firebase_uid='outstation-driver', full_name='Verified Driver', phone_number='919876543211', status='active')
    vehicle = Vehicle(registration_number='KA25OS1234', make='Test', model='SUV', year=2025, category_code='car', seat_count=6, verification_status='verified')
    session.add_all([driver, vehicle]); session.flush(); session.add(DriverVehicleAssignment(driver_id=driver.id, vehicle_id=vehicle.id)); session.commit()
    eligible = service.eligible_drivers(session, booking.id)
    assert len(eligible) == 1
    assert eligible[0].phone_number == '9876543211'
    assigned = service.admin_update(session, booking.id, AdminOutstationUpdate(status='driver_assigned', driver_phone_number='9876543211'), 1)
    assert assigned.status == 'driver_assigned'
    assert assigned.driver_name == 'Verified Driver'
    assert assigned.driver_phone_number == '9876543211'
    assert session.query(Notification).filter_by(passenger_id=passenger.id, notification_type='outstation_driver_assigned').count() == 1
    completed = service.admin_update(session, booking.id, AdminOutstationUpdate(status='completed'), 1)
    assert completed.status == 'completed'
    history = service.driver_assignments(session, driver)
    assert len(history) == 1
    assert history[0].status == 'completed'
