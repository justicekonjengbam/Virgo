from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ride_hailing import FareQuote, Ride, RideCategory
from app.schemas.driver_menu import DriverRideRequestResponse, DriverSupportArticleResponse, DriverTripHistoryItemResponse


class DriverMenuService:
    """Backend-owned content for the Driver menu until live dispatch is introduced."""

    support_articles = (
        ('ride-requests', 'Receiving ride requests', 'Go online after completing your Driver profile. Eligible rides will appear on your dashboard.'),
        ('documents', 'Document verification', 'Your vehicle becomes verified when Virgo approves your driving licence, RC, Aadhaar, and insurance documents.'),
        ('earnings', 'Earnings and payouts', 'Completed rides with a final fare are added to your earnings summary.'),
        ('safety', 'Safety support', 'Use in-app support for ride, safety, and onboarding help in Tier 2 and Tier 3 service areas.'),
    )

    def current_ride_request(self) -> DriverRideRequestResponse:
        # Temporary dispatch fixture. It stays server-owned so the mobile screen
        # can move to a real matching service without changing its UI contract.
        return DriverRideRequestResponse(
            pickup_address='Thangal Bazar, Imphal',
            destination_address='Bir Tikendrajit Airport, Imphal',
            estimated_distance_km=3.5,
            expected_fare_paise=18000,
            pickup_minutes_away=4,
        )

    def trip_history(self, db: Session, driver_id: int) -> list[DriverTripHistoryItemResponse]:
        rows = db.execute(select(Ride, RideCategory, FareQuote).join(
            RideCategory, Ride.category_id == RideCategory.id,
        ).outerjoin(
            FareQuote, (FareQuote.ride_id == Ride.id) & FareQuote.is_final.is_(True),
        ).where(
            Ride.driver_id == driver_id, Ride.status == 'completed',
        ).order_by(Ride.completed_at.desc()).limit(30)).all()
        return [DriverTripHistoryItemResponse(
            id=ride.id,
            pickup_address=ride.pickup_address,
            destination_address=ride.destination_address,
            category=category.display_name,
            completed_at=ride.completed_at,
            fare_paise=fare.amount_paise if fare else 0,
        ) for ride, category, fare in rows]

    def support(self) -> list[DriverSupportArticleResponse]:
        return [DriverSupportArticleResponse(id=item[0], title=item[1], body=item[2]) for item in self.support_articles]
