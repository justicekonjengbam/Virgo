from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ride_hailing import FareQuote, Ride, RideCategory, SavedPlace
from app.models.user import Passenger
from app.schemas.home import HomeResponse, PlaceResponse, RecentRideResponse, RideCategoryResponse
from app.services.home_seed_service import HomeSeedService


class HomeService:
    def __init__(self) -> None:
        self.seed_service = HomeSeedService()

    def get_home(self, db: Session, passenger: Passenger) -> HomeResponse:
        self.seed_service.ensure(db, passenger)
        places = db.scalars(select(SavedPlace).where(SavedPlace.passenger_id == passenger.id).order_by(SavedPlace.label)).all()
        categories = db.scalars(select(RideCategory).where(RideCategory.is_active.is_(True)).order_by(RideCategory.id)).all()
        rides = db.scalars(
            select(Ride).where(Ride.passenger_id == passenger.id, Ride.status == 'completed').order_by(Ride.completed_at.desc()).limit(3)
        ).all()
        return HomeResponse(
            passenger_name=passenger.full_name,
            saved_places=[PlaceResponse(id=item.id, label=item.label, formatted_address=item.formatted_address, latitude=float(item.latitude), longitude=float(item.longitude)) for item in places],
            ride_categories=[RideCategoryResponse(id=item.id, code=item.code, display_name=item.display_name, seat_count=item.seat_count, base_fare_paise=item.base_fare_paise, estimated_arrival_minutes=item.estimated_arrival_minutes, icon_key=item.icon_key) for item in categories],
            recent_rides=[self._recent_ride(db, item) for item in rides],
        )

    def _recent_ride(self, db: Session, ride: Ride) -> RecentRideResponse:
        fare = db.scalar(select(FareQuote.amount_paise).where(FareQuote.ride_id == ride.id, FareQuote.is_final.is_(True))) or 0
        return RecentRideResponse(id=ride.id, pickup_address=ride.pickup_address, destination_address=ride.destination_address, completed_at=ride.completed_at, final_duration_seconds=ride.final_duration_seconds, fare_paise=fare)
