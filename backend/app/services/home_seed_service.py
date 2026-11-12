from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.ride_hailing import FareQuote, RateCard, Ride, RideCategory, SavedPlace
from app.models.user import Passenger
from app.services.fare_calculation_service import FareCalculationService


class HomeSeedService:
    """Creates idempotent demo content for authenticated development accounts."""

    categories = (
        ('hatchback', 'Hatchback', 4, 8000, 4, 'car'),
        ('sedan', 'Sedan', 4, 9000, 5, 'car'),
        ('suv', 'SUV', 6, 12000, 6, 'car'),
        ('e_auto', 'E-Auto', 3, 3500, 3, 'rickshaw'),
        ('e_rickshaw', 'E-Rickshaw', 4, 3500, 3, 'rickshaw'),
        ('bike', 'Bike', 1, 1500, 2, 'motorbike'),
    )
    places = (
        ('Home', 'Paona Bazar, Imphal, Manipur', 24.8080, 93.9370),
        ('Work', 'RIMS, Lamphelpat, Imphal, Manipur', 24.8236, 93.9214),
    )

    def ensure(self, db: Session, passenger: Passenger) -> None:
        categories = self._ensure_categories(db)
        self._ensure_rate_cards(db)
        # Shop was a temporary third shortcut. Keep only the intentional Home/Work pair.
        db.execute(delete(SavedPlace).where(SavedPlace.passenger_id == passenger.id, SavedPlace.label == 'Shop'))
        existing_places = {item.label for item in db.scalars(select(SavedPlace).where(SavedPlace.passenger_id == passenger.id)).all()}
        db.add_all(
            SavedPlace(
                passenger_id=passenger.id,
                label=label,
                formatted_address=address,
                latitude=latitude,
                longitude=longitude,
            )
            for label, address, latitude, longitude in self.places
            if label not in existing_places
        )
        if not db.scalar(select(Ride.id).where(Ride.passenger_id == passenger.id).limit(1)):
            self._add_recent_rides(db, passenger.id, categories)
        db.commit()

    def _ensure_categories(self, db: Session) -> dict[str, RideCategory]:
        existing = {item.code: item for item in db.scalars(select(RideCategory)).all()}
        for code, name, seats, fare, eta, icon in self.categories:
            if code not in existing:
                item = RideCategory(
                    code=code,
                    display_name=name,
                    seat_count=seats,
                    base_fare_paise=fare,
                    estimated_arrival_minutes=eta,
                    icon_key=icon,
                    is_active=True,
                )
                db.add(item)
                db.flush()
                existing[code] = item
            else:
                item = existing[code]
                item.display_name = name
                item.seat_count = seats
                item.base_fare_paise = fare
                item.estimated_arrival_minutes = eta
                item.icon_key = icon
                item.is_active = True
                db.add(item)
                db.flush()
        return existing

    def _ensure_rate_cards(self, db: Session) -> None:
        for code, defaults in FareCalculationService.DEFAULT_RATE_CARDS.items():
            card = db.scalar(select(RateCard).where(RateCard.category_code == code).limit(1))
            if not card:
                card = RateCard(
                    category_code=code,
                    version=1,
                    is_active=True,
                    base_fare_paise=defaults['base_fare_paise'],
                    first_tier_km=defaults['first_tier_km'],
                    first_tier_rate_paise=defaults['first_tier_rate_paise'],
                    second_tier_rate_paise=defaults['second_tier_rate_paise'],
                    waiting_charge_per_minute_paise=defaults['waiting_charge_per_minute_paise'],
                    waiting_grace_period_minutes=defaults['waiting_grace_period_minutes'],
                    surcharge_distance_threshold_km=defaults['surcharge_distance_threshold_km'],
                    surcharge_percentage=defaults['surcharge_percentage'],
                    cancellation_fee_paise=defaults['cancellation_fee_paise'],
                    gst_rate=defaults['gst_rate'],
                    commission_rate=defaults['commission_rate'],
                )
                db.add(card)
        db.flush()

    def _add_recent_rides(self, db: Session, passenger_id: int, categories: dict[str, RideCategory]) -> None:
        now = datetime.now(UTC)
        rides = (
            ('Imphal', 'Thoubal', 40 * 60, 20000, now - timedelta(days=2)),
            ('Bishnupur', 'Imphal', 55 * 60, 80000, now - timedelta(days=14)),
            ('Imphal', 'Churachandpur', 120 * 60, 500000, now - timedelta(days=30)),
        )
        cat = categories.get('hatchback') or categories.get('car') or list(categories.values())[0]
        for pickup, destination, duration, fare, completed_at in rides:
            ride = Ride(
                passenger_id=passenger_id,
                category_id=cat.id,
                status='completed',
                pickup_address=pickup,
                pickup_latitude=24.8170,
                pickup_longitude=93.9368,
                destination_address=destination,
                destination_latitude=24.6300,
                destination_longitude=93.9700,
                requested_at=completed_at - timedelta(minutes=duration // 60),
                completed_at=completed_at,
                final_duration_seconds=duration,
            )
            db.add(ride)
            db.flush()
            db.add(FareQuote(ride_id=ride.id, amount_paise=fare, is_final=True))
