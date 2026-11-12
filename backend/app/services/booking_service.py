from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, timezone
try:
    from zoneinfo import ZoneInfo
    INDIA_TZ = ZoneInfo('Asia/Kolkata')
except Exception:
    INDIA_TZ = timezone(timedelta(hours=5, minutes=30))

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.ride_hailing import FareLineItem, FareQuote, LocationCatalog, Ride, RideCategory, RideEvent, SavedPlace
from app.models.user import Passenger
from app.schemas.booking import FareItemResponse, LocationOptionResponse, RideBookingResponse, RideEstimateRequest, RideEstimateResponse, SelectedPlaceRequest
from app.schemas.home import PlaceResponse
from app.services.fare_calculation_service import FareCalculationService
from app.services.map_provider_service import MapProviderService
from app.services.realtime_events import publish_driver_offer, publish_passenger_status
from app.services.ride_lifecycle_service import RideLifecycleService
from app.services.ride_matching_service import RideMatchingService


@dataclass(frozen=True)
class BookingLocation:
    id: int | None
    place_id: str | None
    name: str
    formatted_address: str
    latitude: float
    longitude: float


class BookingService:
    matching_service = RideMatchingService()
    map_service = MapProviderService()
    active_statuses = ('requested', 'searching', 'driver_assigned', 'driver_arriving', 'driver_arrived', 'in_progress')
    catalog = (
        ('Kangla Fort', 'Kangla, Imphal, Manipur', 24.8115, 93.9422),
        ('Bir Tikendrajit Airport', 'Airport Road, Imphal, Manipur', 24.7600, 93.8967),
        ("Ema Keithel (Mother's Market)", 'Thangal Bazar, Imphal, Manipur', 24.8085, 93.9365),
        ('Regional Institute of Medical Sciences (RIMS)', 'Lamphelpat, Imphal, Manipur', 24.8236, 93.9214),
        ('Manipur University', 'Canchipur, Imphal, Manipur', 24.7533, 93.9280),
        ('JNIMS Porompat', 'Porompat, Imphal East, Manipur', 24.8258, 93.9625),
    )
    india_timezone = INDIA_TZ

    def locations(self, db: Session) -> list[LocationOptionResponse]:
        if not db.scalar(select(LocationCatalog.id).limit(1)):
            db.add_all(
                LocationCatalog(name=name, formatted_address=address, latitude=latitude, longitude=longitude)
                for name, address, latitude, longitude in self.catalog
            )
            db.commit()
        return [self._location(item) for item in db.scalars(select(LocationCatalog).order_by(LocationCatalog.name)).all()]

    def estimate(self, db: Session, request: RideEstimateRequest) -> RideEstimateResponse:
        pickup, destination = self._locations_for_request(db, request)
        category = db.get(RideCategory, request.category_id)
        if not category or not category.is_active:
            raise HTTPException(status_code=404, detail='Ride category is not available.')

        route = self.map_service.route(
            (pickup.latitude, pickup.longitude),
            (destination.latitude, destination.longitude),
        )
        distance_km = round(max(1.0, route.distance_meters / 1000), 1)
        duration = max(1, round(route.duration_seconds / 60))

        rate_card = FareCalculationService.get_active_rate_card(db, category.code)
        breakdown = FareCalculationService.calculate_fare(
            category_code=category.code,
            distance_km=distance_km,
            waiting_minutes=0.0,
            rate_card=rate_card,
            pickup_coords=(pickup.latitude, pickup.longitude),
            dest_coords=(destination.latitude, destination.longitude),
        )

        items = [
            FareItemResponse(label='Base fare', amount_paise=breakdown.base_fare_paise),
            FareItemResponse(
                label=f'Distance fare ({distance_km:.1f} km)',
                amount_paise=breakdown.distance_fare_paise,
            ),
        ]
        if breakdown.surcharge_paise > 0:
            items.append(
                FareItemResponse(
                    label=f'Extended area surcharge ({int(breakdown.surcharge_percentage * 100)}%)',
                    amount_paise=breakdown.surcharge_paise,
                )
            )
        if breakdown.discount_paise > 0:
            items.append(FareItemResponse(label='Promo discount', amount_paise=-breakdown.discount_paise))

        items.append(FareItemResponse(label=f'GST ({int(breakdown.gst_rate * 100)}%)', amount_paise=breakdown.gst_paise))

        rounding_diff = breakdown.customer_pays_paise - breakdown.total_exact_paise
        if rounding_diff != 0:
            items.append(FareItemResponse(label='Rounding', amount_paise=rounding_diff))

        return RideEstimateResponse(
            pickup=self._location(pickup),
            destination=self._location(destination),
            category_name=category.display_name,
            distance_km=distance_km,
            duration_minutes=duration,
            fare_paise=breakdown.customer_pays_paise,
            fare_items=items,
            route_geojson=route.geometry,
        )

    def book(self, db: Session, passenger: Passenger, request: RideEstimateRequest) -> RideBookingResponse:
        active = db.scalar(
            select(Ride)
            .where(
                Ride.passenger_id == passenger.id,
                Ride.status.in_(self.active_statuses),
            )
            .order_by(Ride.requested_at.desc())
        )
        if active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'You already have an active ride (#{active.id}). End or cancel it before requesting another.',
            )

        estimate = self.estimate(db, request)
        category = db.get(RideCategory, request.category_id)
        if not category:
            raise HTTPException(status_code=404, detail='Ride category not found.')

        rate_card = FareCalculationService.get_active_rate_card(db, category.code)
        breakdown = FareCalculationService.calculate_fare(
            category_code=category.code,
            distance_km=estimate.distance_km,
            waiting_minutes=0.0,
            rate_card=rate_card,
            pickup_coords=(estimate.pickup.latitude, estimate.pickup.longitude),
            dest_coords=(estimate.destination.latitude, estimate.destination.longitude),
        )

        ride = Ride(
            passenger_id=passenger.id,
            category_id=category.id,
            status='searching',
            pickup_address=estimate.pickup.formatted_address,
            pickup_place_id=estimate.pickup.place_id,
            pickup_latitude=estimate.pickup.latitude,
            pickup_longitude=estimate.pickup.longitude,
            destination_address=estimate.destination.formatted_address,
            destination_place_id=estimate.destination.place_id,
            destination_latitude=estimate.destination.latitude,
            destination_longitude=estimate.destination.longitude,
            requested_at=datetime.now(UTC),
            estimated_distance_meters=round(estimate.distance_km * 1000),
            estimated_duration_seconds=estimate.duration_minutes * 60,
            route_geojson=estimate.route_geojson,
            rate_card_version=breakdown.rate_card_version,
        )
        db.add(ride)
        try:
            db.flush()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='You already have an active ride. Return to its tracking screen.',
            ) from exc

        salt, otp_hash = RideLifecycleService.create_ride_otp_credentials(
            get_settings().jwt_secret_key,
            ride.id,
            passenger.id,
        )
        ride.otp_salt = salt
        ride.start_otp_hash = otp_hash
        ride.otp_attempts = 0

        quote = FareQuote(
            ride_id=ride.id,
            amount_paise=breakdown.customer_pays_paise,
            is_final=False,
            rate_card_version=breakdown.rate_card_version,
            base_fare_paise=breakdown.base_fare_paise,
            distance_fare_paise=breakdown.distance_fare_paise,
            waiting_charge_paise=breakdown.waiting_charge_paise,
            surcharge_paise=breakdown.surcharge_paise,
            subtotal_paise=breakdown.gross_fare_paise,
            discount_paise=breakdown.discount_paise,
            gst_paise=breakdown.gst_paise,
            commission_paise=breakdown.commission_paise,
            driver_net_paise=breakdown.driver_net_paise,
        )
        db.add(quote)
        db.flush()

        db.add_all(
            FareLineItem(
                fare_quote_id=quote.id,
                item_type=item.label.lower().replace(' ', '_'),
                amount_paise=item.amount_paise,
            )
            for item in estimate.fare_items
        )
        db.add(
            RideEvent(
                ride_id=ride.id,
                actor_type='passenger',
                actor_id=passenger.id,
                event_type='ride_requested',
                payload={'fare_paise': breakdown.customer_pays_paise, 'category': category.code},
            )
        )

        offer = self.matching_service.dispatch(db, ride)
        db.commit()
        db.refresh(ride)

        publish_passenger_status(db, ride)
        if offer:
            publish_driver_offer(db, offer)

        message = (
            'Finding a nearby Driver for you.'
            if ride.status == 'searching'
            else 'No nearby verified Driver is available right now. Please try again shortly or Call & Book at +91 6009060341.'
        )
        return RideBookingResponse(
            ride_id=ride.id,
            status=ride.status,
            pickup_address=ride.pickup_address,
            destination_address=ride.destination_address,
            fare_paise=breakdown.customer_pays_paise,
            requested_at=ride.requested_at,
            message=message,
        )

    def update_saved_place(self, db: Session, passenger: Passenger, saved_place_id: int, request) -> PlaceResponse:
        saved_place = db.scalar(
            select(SavedPlace).where(SavedPlace.id == saved_place_id, SavedPlace.passenger_id == passenger.id)
        )
        if not saved_place:
            raise HTTPException(status_code=404, detail='Saved place was not found.')
        if request.location:
            location = self._selected_location(request.location)
        else:
            row = db.get(LocationCatalog, request.location_id)
            if not row:
                raise HTTPException(status_code=404, detail='Selected location is unavailable.')
            location = self._catalog_location(row)
        saved_place.formatted_address = location.formatted_address
        saved_place.latitude = location.latitude
        saved_place.longitude = location.longitude
        saved_place.google_place_id = location.place_id
        db.commit()
        db.refresh(saved_place)
        return PlaceResponse(
            id=saved_place.id,
            label=saved_place.label,
            formatted_address=saved_place.formatted_address,
            latitude=float(saved_place.latitude),
            longitude=float(saved_place.longitude),
        )

    def _locations_for_request(self, db: Session, request: RideEstimateRequest) -> tuple[BookingLocation, BookingLocation]:
        if request.pickup and request.destination:
            pickup = self._selected_location(request.pickup)
            destination = self._selected_location(request.destination)
        else:
            pickup_row = db.get(LocationCatalog, request.pickup_location_id)
            destination_row = db.get(LocationCatalog, request.destination_location_id)
            if not pickup_row or not destination_row:
                raise HTTPException(status_code=404, detail='Selected location is unavailable.')
            pickup, destination = self._catalog_location(pickup_row), self._catalog_location(destination_row)
        if pickup.place_id == destination.place_id or (
            abs(pickup.latitude - destination.latitude) < 0.0001
            and abs(pickup.longitude - destination.longitude) < 0.0001
        ):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Pickup and destination must be different.')
        self.map_service.ensure_in_service_area(pickup.latitude, pickup.longitude)
        self.map_service.ensure_in_service_area(destination.latitude, destination.longitude)
        return pickup, destination

    @staticmethod
    def _is_night(moment: datetime) -> bool:
        return moment.hour >= 22 or moment.hour < 5

    @staticmethod
    def _location(item: LocationCatalog | BookingLocation) -> LocationOptionResponse:
        return LocationOptionResponse(
            id=item.id,
            place_id=getattr(item, 'place_id', None),
            name=item.name,
            formatted_address=item.formatted_address,
            latitude=float(item.latitude),
            longitude=float(item.longitude),
        )

    @staticmethod
    def _catalog_location(item: LocationCatalog) -> BookingLocation:
        return BookingLocation(
            item.id,
            f'catalog:{item.id}',
            item.name,
            item.formatted_address,
            float(item.latitude),
            float(item.longitude),
        )

    @staticmethod
    def _selected_location(item: SelectedPlaceRequest) -> BookingLocation:
        return BookingLocation(None, item.place_id, item.name, item.formatted_address, item.latitude, item.longitude)
