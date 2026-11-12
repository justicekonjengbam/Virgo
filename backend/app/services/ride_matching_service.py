from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from math import asin, cos, radians, sin, sqrt

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
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
from app.schemas.booking import (
    DriverRideOfferDecisionResponse,
    DriverRideOfferResponse,
    PassengerRideStatusResponse,
)
from app.services.document_management_service import DocumentManagementService
from app.services.driver_readiness_service import DriverReadinessService
from app.services.fare_calculation_service import FareCalculationService
from app.services.realtime_events import (
    publish_driver_location,
    publish_driver_offer,
    publish_driver_offer_cleared,
    publish_passenger_status,
)
from app.services.ride_lifecycle_service import RideLifecycleService

logger = logging.getLogger(__name__)


class RideMatchingService:
    """Core local dispatch engine with 45s driver offer timeout, 3-minute search timeout, and Imphal dispatch."""

    offer_ttl = timedelta(seconds=45)
    search_timeout = timedelta(minutes=3)
    maximum_pickup_distance_km = 40.0
    support_phone = '+91 6009060341'

    city_centres = {
        'imphal': (24.8170, 93.9368),
        'imphal west': (24.8170, 93.9368),
        'imphal east': (24.8210, 93.9540),
        'thangal bazar': (24.8105, 93.9372),
        'paona bazar': (24.8080, 93.9370),
        'lamphelpat': (24.8240, 93.9220),
        'porompat': (24.8260, 93.9620),
    }
    readiness_service = DriverReadinessService()
    document_service = DocumentManagementService()

    def dispatch(self, db: Session, ride: Ride) -> RideDispatchOffer | None:
        if ride.status != 'searching':
            return None

        # Check 3-minute search timeout
        now = datetime.now(UTC)
        requested_at = ride.requested_at.replace(tzinfo=UTC) if ride.requested_at.tzinfo is None else ride.requested_at
        if now - requested_at >= self.search_timeout:
            ride.status = 'cancelled'
            ride.cancelled_at = now
            ride.cancellation_reason = 'no_eligible_driver'
            db.add(
                RideEvent(
                    ride_id=ride.id,
                    actor_type='system',
                    actor_id=None,
                    event_type='matching_timeout',
                    payload={'reason': ride.cancellation_reason, 'timeout_seconds': (now - requested_at).total_seconds()},
                )
            )
            return None

        offered_driver_ids = set(
            db.scalars(select(RideDispatchOffer.driver_id).where(RideDispatchOffer.ride_id == ride.id))
        )
        candidate = self._nearest_candidate(db, ride, offered_driver_ids)
        if not candidate:
            ride.status = 'cancelled'
            ride.cancelled_at = now
            ride.cancellation_reason = 'no_eligible_driver'
            db.add(
                RideEvent(
                    ride_id=ride.id,
                    actor_type='system',
                    actor_id=None,
                    event_type='matching_failed',
                    payload={'reason': ride.cancellation_reason},
                )
            )
            return None

        offer = RideDispatchOffer(
            ride_id=ride.id,
            driver_id=candidate[0].id,
            expires_at=now + self.offer_ttl,
        )
        db.add(offer)
        db.add(
            RideEvent(
                ride_id=ride.id,
                actor_type='system',
                actor_id=None,
                event_type='ride_offered',
                payload={'driver_id': candidate[0].id, 'pickup_distance_km': candidate[1]},
            )
        )
        return offer

    def current_offer(self, db: Session, driver: Driver) -> DriverRideOfferResponse | None:
        now = datetime.now(UTC)
        offer = db.scalar(
            select(RideDispatchOffer)
            .where(
                RideDispatchOffer.driver_id == driver.id,
                RideDispatchOffer.status == 'pending',
            )
            .order_by(RideDispatchOffer.offered_at.desc())
        )
        if not offer:
            return None
        if self._is_expired(offer, now):
            next_offer = self._expire_and_retry(db, offer)
            db.commit()
            publish_driver_offer_cleared(driver.id, offer.ride_id)
            ride = db.get(Ride, offer.ride_id)
            if ride:
                publish_passenger_status(db, ride)
            if next_offer:
                publish_driver_offer(db, next_offer)
            return None
        ride = db.get(Ride, offer.ride_id)
        if not ride or ride.status != 'searching':
            return None
        quote = db.scalar(select(FareQuote).where(FareQuote.ride_id == ride.id).order_by(FareQuote.created_at.desc()))
        expires_at = (
            offer.expires_at.replace(tzinfo=UTC)
            if offer.expires_at.tzinfo is None
            else offer.expires_at
        )
        return DriverRideOfferResponse(
            offer_id=offer.id,
            ride_id=ride.id,
            pickup_address=ride.pickup_address,
            destination_address=ride.destination_address,
            estimated_distance_km=round((ride.estimated_distance_meters or 0) / 1000, 1),
            expected_fare_paise=quote.amount_paise if quote else 0,
            pickup_minutes_away=4,
            expires_at=expires_at,
            pickup_latitude=float(ride.pickup_latitude),
            pickup_longitude=float(ride.pickup_longitude),
            destination_latitude=float(ride.destination_latitude),
            destination_longitude=float(ride.destination_longitude),
        )

    def respond(self, db: Session, driver: Driver, offer_id: int, decision: str) -> DriverRideOfferDecisionResponse:
        offer = db.scalar(
            select(RideDispatchOffer).where(RideDispatchOffer.id == offer_id, RideDispatchOffer.driver_id == driver.id)
        )
        if not offer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ride offer was not found.')
        if offer.status != 'pending' or self._is_expired(offer, datetime.now(UTC)):
            if offer.status == 'pending':
                self._expire_and_retry(db, offer)
                db.commit()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='This ride offer has expired. We are finding the next Driver.',
            )
        ride = db.get(Ride, offer.ride_id)
        if not ride or ride.status != 'searching':
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='This ride is no longer available.')

        offer.status, offer.responded_at = decision, datetime.now(UTC)
        next_offer = None
        if decision == 'accepted':
            existing = db.scalar(
                select(Ride).where(
                    Ride.driver_id == driver.id,
                    Ride.status.in_(('driver_assigned', 'driver_arriving', 'driver_arrived', 'in_progress')),
                    Ride.id != ride.id,
                )
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'Finish active ride #{existing.id} before accepting another request.',
                )
            vehicle = self._active_vehicle(db, driver.id)
            if not vehicle or vehicle.verification_status != 'verified' or not driver.is_online:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail='Go online with a verified vehicle before accepting rides.',
                )
            ride.driver_id, ride.vehicle_id = driver.id, vehicle.id
            ride.status, ride.accepted_at = 'driver_arriving', datetime.now(UTC)
            db.add(
                RideEvent(
                    ride_id=ride.id,
                    actor_type='driver',
                    actor_id=driver.id,
                    event_type='ride_accepted',
                    payload={'offer_id': offer.id},
                )
            )
            message = 'Ride accepted. The passenger has been notified that you are on the way.'
        else:
            db.add(
                RideEvent(
                    ride_id=ride.id,
                    actor_type='driver',
                    actor_id=driver.id,
                    event_type='ride_declined',
                    payload={'offer_id': offer.id},
                )
            )
            next_offer = self.dispatch(db, ride)
            message = 'Ride declined. We are offering it to another eligible Driver.'

        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='You already have another active ride.') from exc

        db.refresh(ride)
        publish_driver_offer_cleared(driver.id, ride.id)
        publish_passenger_status(db, ride)
        if next_offer:
            publish_driver_offer(db, next_offer)
        return DriverRideOfferDecisionResponse(ride_id=ride.id, ride_status=ride.status, message=message)

    def passenger_status(self, db: Session, ride: Ride) -> PassengerRideStatusResponse:
        driver = db.get(Driver, ride.driver_id) if ride.driver_id else None
        vehicle = db.get(Vehicle, ride.vehicle_id) if ride.vehicle_id else None
        quote = db.scalar(select(FareQuote).where(FareQuote.ride_id == ride.id).order_by(FareQuote.created_at.desc()))
        if ride.status == 'driver_arriving':
            message = 'Your Driver is on the way.'
        elif ride.status == 'driver_arrived':
            message = 'Your Driver has arrived at the pickup location.'
        elif ride.status == 'in_progress':
            message = 'Your ride is in progress.'
        elif ride.status == 'completed':
            message = 'You have reached your destination.'
        elif ride.status == 'cancelled' and ride.cancelled_by:
            message = f'This ride was ended by the {ride.cancelled_by}.'
        elif ride.status == 'cancelled' and ride.cancellation_reason == 'no_eligible_driver':
            message = f'No nearby verified Driver is available right now. Please try again shortly or Call & Book at {self.support_phone}.'
        elif ride.status == 'searching':
            message = 'Finding a nearby Driver for you.'
        else:
            message = 'Your ride status has been updated.'
        location = db.get(DriverCurrentLocation, ride.driver_id) if ride.driver_id else None
        driver_coords = self._driver_coordinates(driver, location) if driver else (
            (float(location.latitude), float(location.longitude)) if location else None
        )
        arrival = None
        if driver_coords and ride.status in {'driver_arriving', 'driver_arrived'}:
            distance = self._distance_km(
                driver_coords[0], driver_coords[1], float(ride.pickup_latitude), float(ride.pickup_longitude)
            )
            arrival = 0 if ride.status == 'driver_arrived' else max(1, round(distance / 25 * 60))
        return PassengerRideStatusResponse(
            ride_id=ride.id,
            status=ride.status,
            message=message,
            pickup_address=ride.pickup_address,
            destination_address=ride.destination_address,
            fare_paise=quote.amount_paise if quote else 0,
            driver_name=driver.full_name if driver else None,
            vehicle_name=f'{vehicle.make} {vehicle.model}' if vehicle else None,
            vehicle_registration_number=vehicle.registration_number if vehicle else None,
            driver_arrival_minutes=arrival,
            pickup_latitude=float(ride.pickup_latitude),
            pickup_longitude=float(ride.pickup_longitude),
            destination_latitude=float(ride.destination_latitude),
            destination_longitude=float(ride.destination_longitude),
            driver_latitude=driver_coords[0] if driver_coords else (float(location.latitude) if location else None),
            driver_longitude=driver_coords[1] if driver_coords else (float(location.longitude) if location else None),
            driver_heading_degrees=location.heading_degrees if location else None,
            route_geojson=ride.route_geojson,
            can_cancel=ride.status in {'requested', 'searching', 'driver_assigned', 'driver_arriving', 'driver_arrived'},
            can_end=ride.status == 'in_progress',
            ride_start_otp=(
                RideLifecycleService.get_passenger_ride_otp(db, ride)
                if ride.status in {'driver_assigned', 'driver_arriving', 'driver_arrived'}
                else None
            ),
            cancellation_reason=ride.cancellation_reason if ride.status == 'cancelled' else None,
        )

    def update_driver_location(
        self,
        db: Session,
        driver: Driver,
        latitude: float,
        longitude: float,
        heading_degrees: int | None,
        accuracy_meters: float | None = None,
        speed_mps: float | None = None,
        recorded_at: datetime | None = None,
    ) -> None:
        ride = db.scalar(
            select(Ride).where(
                Ride.driver_id == driver.id,
                Ride.status.in_(('driver_arriving', 'driver_arrived', 'in_progress')),
            )
        )
        if not driver.is_online and not ride:
            raise HTTPException(status_code=409, detail='Go online before sharing your Driver location.')
        now = datetime.now(UTC)
        captured_at = recorded_at or now
        if captured_at.tzinfo is None:
            captured_at = captured_at.replace(tzinfo=UTC)
        if abs((now - captured_at).total_seconds()) > 120:
            raise HTTPException(status_code=422, detail='Location reading is stale. Wait for a fresh GPS signal.')
        if accuracy_meters is not None and accuracy_meters > 150:
            raise HTTPException(status_code=422, detail='Location accuracy is too low. Move to an open area and try again.')
        location = db.get(DriverCurrentLocation, driver.id)
        if location:
            previous_at = (
                location.recorded_at.replace(tzinfo=UTC) if location.recorded_at.tzinfo is None else location.recorded_at
            )
            elapsed = max(1, (captured_at - previous_at).total_seconds())
            implied_speed = (
                self._distance_km(float(location.latitude), float(location.longitude), latitude, longitude) * 1000 / elapsed
            )
            if elapsed < 120 and implied_speed > 55:
                raise HTTPException(status_code=422, detail='Location jump was rejected. Wait for GPS to stabilize.')
            location.latitude, location.longitude = latitude, longitude
            location.heading_degrees, location.recorded_at = heading_degrees, captured_at
            location.accuracy_meters, location.speed_mps = accuracy_meters, speed_mps
        else:
            location = DriverCurrentLocation(
                driver_id=driver.id,
                latitude=latitude,
                longitude=longitude,
                heading_degrees=heading_degrees,
                accuracy_meters=accuracy_meters,
                speed_mps=speed_mps,
                recorded_at=captured_at,
            )
            db.add(location)
        db.commit()
        if ride:
            driver_coords = self._driver_coordinates(driver, location)
            pub_lat = driver_coords[0] if driver_coords else latitude
            pub_lon = driver_coords[1] if driver_coords else longitude
            publish_driver_location(
                ride.passenger_id,
                ride.id,
                {
                    'ride_id': ride.id,
                    'latitude': pub_lat,
                    'longitude': pub_lon,
                    'heading_degrees': heading_degrees,
                    'accuracy_meters': accuracy_meters,
                    'recorded_at': captured_at.isoformat(),
                },
            )

    def expire_offer(self, db: Session, offer_id: int) -> tuple[RideDispatchOffer, Ride, RideDispatchOffer | None] | None:
        offer = db.get(RideDispatchOffer, offer_id)
        if not offer or offer.status != 'pending' or not self._is_expired(offer, datetime.now(UTC)):
            return None
        ride = db.get(Ride, offer.ride_id)
        next_offer = self._expire_and_retry(db, offer)
        db.commit()
        if not ride:
            return None
        db.refresh(ride)
        return offer, ride, next_offer

    def invalidate_driver_offers(self, db: Session, driver_id: int) -> list[RideDispatchOffer]:
        """Invalidates pending offers when a driver goes offline and attempts redispatch."""
        now = datetime.now(UTC)
        pending_offers = db.scalars(
            select(RideDispatchOffer).where(
                RideDispatchOffer.driver_id == driver_id,
                RideDispatchOffer.status == 'pending',
            )
        ).all()
        new_offers = []
        for offer in pending_offers:
            offer.status = 'cancelled'
            offer.responded_at = now
            ride = db.get(Ride, offer.ride_id)
            if ride and ride.status == 'searching':
                db.add(
                    RideEvent(
                        ride_id=ride.id,
                        actor_type='system',
                        actor_id=None,
                        event_type='driver_offline_cancelled_offer',
                        payload={'driver_id': driver_id, 'offer_id': offer.id},
                    )
                )
                next_offer = self.dispatch(db, ride)
                if next_offer:
                    new_offers.append(next_offer)
        return new_offers

    def _expire_and_retry(self, db: Session, offer: RideDispatchOffer) -> RideDispatchOffer | None:
        offer.status, offer.responded_at = 'expired', datetime.now(UTC)
        ride = db.get(Ride, offer.ride_id)
        if ride and ride.status == 'searching':
            db.add(
                RideEvent(
                    ride_id=ride.id,
                    actor_type='system',
                    actor_id=None,
                    event_type='ride_offer_expired',
                    payload={'offer_id': offer.id},
                )
            )
            return self.dispatch(db, ride)
        return None

    def _nearest_candidate(self, db: Session, ride: Ride, excluded_driver_ids: set[int]) -> tuple[Driver, float] | None:
        category = db.get(RideCategory, ride.category_id)
        if not category:
            return None

        normalized_category_code = FareCalculationService.normalize_code(category.code)

        # Reconcile pending online accounts before matching
        pending_online = db.scalars(
            select(Driver).where(
                Driver.is_online.is_(True),
                Driver.status == 'pending',
            )
        ).all()
        for pending_driver in pending_online:
            self.readiness_service.reconcile(db, pending_driver)

        rows = db.execute(
            select(Driver, DriverCurrentLocation, Vehicle)
            .outerjoin(
                DriverCurrentLocation,
                DriverCurrentLocation.driver_id == Driver.id,
            )
            .join(
                DriverVehicleAssignment,
                (DriverVehicleAssignment.driver_id == Driver.id) & DriverVehicleAssignment.ended_at.is_(None),
            )
            .join(
                Vehicle,
                Vehicle.id == DriverVehicleAssignment.vehicle_id,
            )
            .where(
                Driver.is_online.is_(True),
                Driver.status == 'active',
                Vehicle.verification_status == 'verified',
            )
        ).all()

        candidates: list[tuple[Driver, float]] = []
        now = datetime.now(UTC)

        for driver, location, vehicle in rows:
            if driver.id in excluded_driver_ids:
                continue

            # Vehicle category compatibility check
            veh_cat = FareCalculationService.normalize_code(vehicle.category_code)
            if veh_cat != normalized_category_code and vehicle.category_code != category.code:
                continue

            # Check expired or invalid mandatory documents
            expired_docs = self.document_service.check_expired_mandatory_documents(db, driver.id)
            if expired_docs:
                continue

            # Check if driver is already on an active ride
            active_ride = db.scalar(
                select(Ride.id)
                .where(
                    Ride.driver_id == driver.id,
                    Ride.status.in_(('driver_assigned', 'driver_arriving', 'driver_arrived', 'in_progress')),
                )
                .limit(1)
            )
            if active_ride:
                continue

            # Check if driver has an existing pending offer that is not expired
            has_pending = db.scalar(
                select(RideDispatchOffer.id)
                .where(
                    RideDispatchOffer.driver_id == driver.id,
                    RideDispatchOffer.status == 'pending',
                    RideDispatchOffer.expires_at > now,
                )
                .limit(1)
            )
            if has_pending:
                continue

            if location:
                rec_at = (
                    location.recorded_at.replace(tzinfo=UTC)
                    if location.recorded_at.tzinfo is None
                    else location.recorded_at
                )
                if now - rec_at > timedelta(minutes=5):
                    location = None

            coordinates = self._driver_coordinates(driver, location)
            if not coordinates:
                continue

            distance = self._distance_km(
                coordinates[0], coordinates[1], float(ride.pickup_latitude), float(ride.pickup_longitude)
            )
            if distance <= self.maximum_pickup_distance_km:
                candidates.append((driver, distance))

        return min(candidates, key=lambda item: item[1]) if candidates else None

    def _driver_coordinates(self, driver: Driver, location: DriverCurrentLocation | None) -> tuple[float, float] | None:
        settings = get_settings()
        # Development-only test location simulation for seeded test driver
        if (
            settings.environment == 'development'
            and settings.dev_simulate_test_driver_imphal
            and driver.phone_number == settings.dev_test_driver_phone
        ):
            actual_coords = (float(location.latitude), float(location.longitude)) if location else None
            if actual_coords:
                dist = self._distance_km(
                    actual_coords[0], actual_coords[1],
                    settings.service_center_latitude, settings.service_center_longitude
                )
                if dist > settings.service_radius_km:
                    logger.info(
                        "DEV_SIMULATION: Test driver %s (phone %s) actual GPS (%s, %s) is %0.1f km from Imphal. "
                        "Using configured Imphal test coordinates (%s, %s) for matching.",
                        driver.id, driver.phone_number, actual_coords[0], actual_coords[1],
                        dist, settings.dev_test_driver_latitude, settings.dev_test_driver_longitude
                    )
                    return settings.dev_test_driver_latitude, settings.dev_test_driver_longitude
            else:
                logger.info(
                    "DEV_SIMULATION: Test driver %s has no GPS reading. Using configured Imphal test coordinates (%s, %s).",
                    driver.id, settings.dev_test_driver_latitude, settings.dev_test_driver_longitude
                )
                return settings.dev_test_driver_latitude, settings.dev_test_driver_longitude

        if location:
            return float(location.latitude), float(location.longitude)
        city = (driver.operating_city or '').strip().casefold()
        return self.city_centres.get(city)

    @staticmethod
    def _active_vehicle(db: Session, driver_id: int) -> Vehicle | None:
        return db.scalar(
            select(Vehicle)
            .join(DriverVehicleAssignment, DriverVehicleAssignment.vehicle_id == Vehicle.id)
            .where(DriverVehicleAssignment.driver_id == driver_id, DriverVehicleAssignment.ended_at.is_(None))
            .order_by(DriverVehicleAssignment.started_at.desc())
        )

    @staticmethod
    def _distance_km(latitude_a: float, longitude_a: float, latitude_b: float, longitude_b: float) -> float:
        lat_a, lon_a, lat_b, lon_b = map(radians, (latitude_a, longitude_a, latitude_b, longitude_b))
        value = sin((lat_b - lat_a) / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin((lon_b - lon_a) / 2) ** 2
        return 6371 * 2 * asin(sqrt(value))

    @staticmethod
    def _is_expired(offer: RideDispatchOffer, now: datetime) -> bool:
        expires_at = offer.expires_at.replace(tzinfo=UTC) if offer.expires_at.tzinfo is None else offer.expires_at
        return expires_at <= now
