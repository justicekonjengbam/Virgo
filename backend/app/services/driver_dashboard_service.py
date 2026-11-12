from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ride_hailing import (
    Driver,
    DriverVehicleAssignment,
    FareQuote,
    Rating,
    Ride,
    Vehicle,
)
from app.schemas.driver_dashboard import DriverDashboardResponse, DriverVehicleStatusResponse
from app.services.document_management_service import DocumentManagementService
from app.services.driver_readiness_service import DriverReadinessService


class DriverDashboardService:
    """Read model for the Driver dashboard. All monetary values remain in paise."""

    readiness_service = DriverReadinessService()

    def dashboard(self, db: Session, driver: Driver) -> DriverDashboardResponse:
        self.readiness_service.reconcile(db, driver)
        now = datetime.now(UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = today_start.replace(day=1)

        return DriverDashboardResponse(
            full_name=driver.full_name,
            is_online=driver.is_online,
            online_minutes=self._online_minutes(driver, now),
            safety_score=self._safety_score(db, driver.id),
            rating=self._rating(db, driver.id),
            today_earnings_paise=self._earnings(db, driver.id, today_start),
            month_earnings_paise=self._earnings(db, driver.id, month_start),
            today_completed_rides=self._completed_rides(db, driver.id, today_start),
            month_completed_rides=self._completed_rides(db, driver.id, month_start),
            vehicle=self._vehicle(db, driver.id),
        )

    def set_availability(self, db: Session, driver: Driver, is_online: bool) -> DriverDashboardResponse:
        self.readiness_service.reconcile(db, driver)
        if is_online:
            expired_docs = DocumentManagementService().check_expired_mandatory_documents(db, driver.id)
            if expired_docs:
                detail = f"Cannot go online: {', '.join(expired_docs)}. Please submit renewed documents to Virgo operations."
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
            if driver.status != 'active':
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Your Driver account is pending verification. All mandatory documents must be approved before going online.")
        driver.is_online = is_online
        if is_online:
            driver.last_online_at = datetime.now(UTC)
        else:
            from app.services.ride_matching_service import RideMatchingService
            RideMatchingService().invalidate_driver_offers(db, driver.id)
        db.add(driver)
        db.commit()
        db.refresh(driver)
        return self.dashboard(db, driver)

    def _completed_rides(self, db: Session, driver_id: int, since: datetime) -> int:
        return int(db.scalar(select(func.count(Ride.id)).where(
            Ride.driver_id == driver_id, Ride.status == "completed", Ride.completed_at >= since,
        )) or 0)

    def _earnings(self, db: Session, driver_id: int, since: datetime) -> int:
        total = db.scalar(select(func.coalesce(func.sum(FareQuote.amount_paise), 0)).join(
            Ride, FareQuote.ride_id == Ride.id,
        ).where(
            Ride.driver_id == driver_id,
            Ride.status == "completed",
            Ride.completed_at >= since,
            FareQuote.is_final.is_(True),
        ))
        return int(total or 0)

    def _rating(self, db: Session, driver_id: int) -> float | None:
        value = db.scalar(select(func.avg(Rating.score)).join(Ride, Rating.ride_id == Ride.id).where(
            Ride.driver_id == driver_id, Rating.rater_type == "passenger",
        ))
        return round(float(value), 1) if value is not None else None

    def _safety_score(self, db: Session, driver_id: int) -> int | None:
        completed = int(db.scalar(select(func.count(Ride.id)).where(
            Ride.driver_id == driver_id, Ride.status == "completed",
        )) or 0)
        cancelled = int(db.scalar(select(func.count(Ride.id)).where(
            Ride.driver_id == driver_id, Ride.status == "cancelled",
        )) or 0)
        total = completed + cancelled
        return round(completed / total * 100) if total else None

    def _online_minutes(self, driver: Driver, now: datetime) -> int:
        if not driver.is_online or not driver.last_online_at:
            return 0
        started_at = driver.last_online_at
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=UTC)
        elapsed_minutes = max(0, int((now - started_at).total_seconds() // 60))
        # The compact dashboard metric is a current-cycle value rather than a
        # lifetime counter, so it restarts after every complete 24-hour cycle.
        return elapsed_minutes % (24 * 60)

    def _vehicle(self, db: Session, driver_id: int) -> DriverVehicleStatusResponse | None:
        vehicle = db.scalar(select(Vehicle).join(
            DriverVehicleAssignment, DriverVehicleAssignment.vehicle_id == Vehicle.id,
        ).where(
            DriverVehicleAssignment.driver_id == driver_id,
            DriverVehicleAssignment.ended_at.is_(None),
        ).order_by(DriverVehicleAssignment.started_at.desc()))
        if not vehicle:
            return None
        return DriverVehicleStatusResponse(
            category=vehicle.category_code,
            make=vehicle.make,
            model=vehicle.model,
            registration_number=vehicle.registration_number,
            seat_count=vehicle.seat_count,
            color=vehicle.color,
            verification_status=vehicle.verification_status,
        )
