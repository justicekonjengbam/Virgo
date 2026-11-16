from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.db import Base
from app.models.ride_hailing import (
    Driver,
    DriverCurrentLocation,
    DriverVehicleAssignment,
    FareQuote,
    Ride,
    RideCategory,
    RideDispatchOffer,
    RideEvent,
    Vehicle,
)
from app.models.user import Passenger
from app.services.ride_matching_service import RideMatchingService
from app.services.spatial_grid import HexSpatialGrid, UberStyleDispatchSelector


def _session():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_hex_spatial_grid_geometry_and_k_ring_symmetry():
    grid = HexSpatialGrid(cell_radius_meters=600.0, origin_lat=24.8170, origin_lon=93.9368)

    # Center cell
    center_cell, center_cube = grid.get_cell(24.8170, 93.9368)
    assert center_cube == (0, 0, 0)
    assert center_cell == 'hex:0:0'

    # Same location has hex distance 0
    assert grid.hex_distance(center_cube, center_cube) == 0

    # Slight move (< 400m) stays in same cell
    _, near_cube = grid.get_cell(24.8180, 93.9372)
    assert grid.hex_distance(center_cube, near_cube) == 0

    # ~1.2 km move is in Ring 1 or 2
    _, ring1_cube = grid.get_cell(24.8250, 93.9368)
    d = grid.hex_distance(center_cube, ring1_cube)
    assert d in (1, 2)


def test_bearing_and_heading_alignment():
    grid = HexSpatialGrid()

    # Point directly North: lat increases, lon stays same
    bearing_north = grid.calculate_bearing(24.8000, 93.9300, 24.8200, 93.9300)
    assert round(bearing_north) == 0 or round(bearing_north) == 360

    # Point directly East: lon increases
    bearing_east = grid.calculate_bearing(24.8000, 93.9300, 24.8000, 93.9500)
    assert 85 <= bearing_east <= 95


def test_expanding_ring_prefers_closer_ring_tier():
    selector = UberStyleDispatchSelector()
    pickup_lat, pickup_lon = 24.8170, 93.9368  # Imphal center

    class DummyDriver:
        def __init__(self, driver_id: int):
            self.id = driver_id

    # Driver 1: 1.0 km away (Tier 0: Hyper-Local)
    driver_1 = {
        'driver': DummyDriver(1),
        'latitude': 24.8250,
        'longitude': 93.9368,
        'heading_degrees': 180,
        'idle_minutes': 5.0,
        'rating': 4.5,
    }

    # Driver 2: 7.0 km away (Tier 2: District), but has 5.0 rating and 60 min idle
    driver_2 = {
        'driver': DummyDriver(2),
        'latitude': 24.7600,
        'longitude': 93.9000,
        'heading_degrees': 40,
        'idle_minutes': 60.0,
        'rating': 5.0,
    }

    # When both are available, Driver 1 in Tier 0 MUST win over Driver 2 in Tier 2
    match = selector.select_best_candidate(pickup_lat, pickup_lon, [driver_1, driver_2], set())
    assert match is not None
    assert match.driver.id == 1
    assert match.tier == 0
    assert 'Hyper-Local' in match.tier_name

    # When Driver 1 is excluded (declined/expired), ring expands to Tier 2!
    match_expanded = selector.select_best_candidate(pickup_lat, pickup_lon, [driver_1, driver_2], {1})
    assert match_expanded is not None
    assert match_expanded.driver.id == 2
    assert match_expanded.tier == 2
    assert 'District' in match_expanded.tier_name


def test_multi_factor_scoring_heading_and_idle_time_advantage():
    selector = UberStyleDispatchSelector()
    pickup_lat, pickup_lon = 24.8170, 93.9368

    class DummyDriver:
        def __init__(self, driver_id: int):
            self.id = driver_id

    # Both drivers at the exact same location (same tier, same distance ~1.0 km North)
    # Pickup is South (bearing ~180)
    # Driver 3 is driving AWAY (heading 0 / North)
    driver_away = {
        'driver': DummyDriver(3),
        'latitude': 24.8250,
        'longitude': 93.9368,
        'heading_degrees': 0,
        'idle_minutes': 2.0,
        'rating': 4.5,
    }

    # Driver 4 is driving TOWARDS pickup (heading 180 / South) with longer idle time
    driver_towards = {
        'driver': DummyDriver(4),
        'latitude': 24.8250,
        'longitude': 93.9368,
        'heading_degrees': 180,
        'idle_minutes': 25.0,
        'rating': 4.9,
    }

    match = selector.select_best_candidate(pickup_lat, pickup_lon, [driver_away, driver_towards], set())
    assert match is not None
    assert match.driver.id == 4, "Driver heading towards pickup with higher idle time must win"
    assert match.score > 0.6


def test_dispatch_lifecycle_ring_expansion_events_and_status_message():
    session = _session()
    passenger = Passenger(full_name='Rider', phone_number='919999999991', password_hash='hash', is_phone_verified=True)
    category = RideCategory(code='car', display_name='Car', seat_count=4, base_fare_paise=18000, estimated_arrival_minutes=4, icon_key='car')
    session.add_all([passenger, category])
    session.flush()

    # Driver 10: 1.2 km away (Tier 0: Hyper-Local)
    d1 = Driver(firebase_uid='uid-10', full_name='Driver Near', phone_number='919876543210', status='active', is_online=True)
    v1 = Vehicle(registration_number='MN01A1111', make='Car', model='One', year=2024, category_code='car', seat_count=4, verification_status='verified')
    session.add_all([d1, v1])
    session.flush()
    session.add_all([
        DriverVehicleAssignment(driver_id=d1.id, vehicle_id=v1.id),
        DriverCurrentLocation(driver_id=d1.id, latitude=24.8250, longitude=93.9368, heading_degrees=180),
    ])

    # Driver 20: 7.5 km away (Tier 2: District)
    d2 = Driver(firebase_uid='uid-20', full_name='Driver Far', phone_number='919876543220', status='active', is_online=True)
    v2 = Vehicle(registration_number='MN01A2222', make='Car', model='Two', year=2024, category_code='car', seat_count=4, verification_status='verified')
    session.add_all([d2, v2])
    session.flush()
    session.add_all([
        DriverVehicleAssignment(driver_id=d2.id, vehicle_id=v2.id),
        DriverCurrentLocation(driver_id=d2.id, latitude=24.7550, longitude=93.9100, heading_degrees=30),
    ])

    # Ride requested at Imphal Center
    ride = Ride(
        passenger_id=passenger.id,
        category_id=category.id,
        status='searching',
        pickup_address='Kangla Fort, Imphal',
        pickup_latitude=24.8170,
        pickup_longitude=93.9368,
        destination_address='Airport, Imphal',
        destination_latitude=24.7600,
        destination_longitude=93.8967,
        requested_at=datetime.now(UTC),
        estimated_distance_meters=4000,
    )
    session.add(ride)
    session.flush()
    session.add(FareQuote(ride_id=ride.id, amount_paise=18000, expires_at=datetime.now(UTC) + timedelta(minutes=5)))
    session.commit()

    service = RideMatchingService()

    # First dispatch attempt: Must match Near Driver (Tier 0)
    offer_1 = service.dispatch(session, ride)
    session.commit()
    assert offer_1 is not None
    assert offer_1.driver_id == d1.id

    # Check RideEvent has cell_id and ring_tier
    events = session.scalars(select(RideEvent).where(RideEvent.ride_id == ride.id)).all()
    offered_event = next(e for e in events if e.event_type == 'ride_offered')
    assert offered_event.payload['ring_tier'] == 0
    assert offered_event.payload['cell_id'].startswith('hex:')

    # Passenger status while searching in Tier 0
    p_status_1 = service.passenger_status(session, ride)
    assert 'closest' in p_status_1.message.lower() or 'near' in p_status_1.message.lower()

    # Near Driver declines the ride
    service.respond(session, d1, offer_1.id, 'declined')
    session.commit()

    # Second dispatch attempt: System automatically expands ring to Tier 2 (Driver Far)!
    session.refresh(ride)
    assert ride.status == 'searching'
    current_offer_d2 = service.current_offer(session, d2)
    assert current_offer_d2 is not None
    assert current_offer_d2.ride_id == ride.id

    # Verify ring expansion event was logged
    all_events = session.scalars(select(RideEvent).where(RideEvent.ride_id == ride.id)).all()
    expansion_events = [e for e in all_events if e.event_type == 'ride_search_ring_expanded']
    assert len(expansion_events) >= 1
    assert expansion_events[0].payload['from_tier'] == 0
    assert expansion_events[0].payload['to_tier'] == 2

    # Verify passenger status message updated to district expansion message
    p_status_2 = service.passenger_status(session, ride)
    assert 'district' in p_status_2.message.lower() or 'expanding' in p_status_2.message.lower()
