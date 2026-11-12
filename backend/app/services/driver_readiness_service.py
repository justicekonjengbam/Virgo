from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ride_hailing import Driver, DriverDocument, DriverVehicleAssignment, Vehicle


class DriverReadinessService:
    """Maintains the invariant between approved documents, vehicle, and Driver status."""

    required_document_types = {
        'driving_licence', 'vehicle_registration', 'aadhaar', 'vehicle_insurance',
    }

    def reconcile(self, db: Session, driver: Driver) -> bool:
        if driver.status != 'pending':
            return driver.status == 'active'
        vehicle = db.scalar(select(Vehicle).join(
            DriverVehicleAssignment, DriverVehicleAssignment.vehicle_id == Vehicle.id,
        ).where(
            DriverVehicleAssignment.driver_id == driver.id,
            DriverVehicleAssignment.ended_at.is_(None),
        ).order_by(DriverVehicleAssignment.started_at.desc()))
        if not vehicle or vehicle.verification_status != 'verified':
            return False
        statuses = dict(db.execute(select(
            DriverDocument.document_type, DriverDocument.verification_status,
        ).where(DriverDocument.driver_id == driver.id)).all())
        if not (
            self.required_document_types <= statuses.keys()
            and all(statuses[name] == 'verified' for name in self.required_document_types)
        ):
            return False
        driver.status = 'active'
        db.add(driver)
        db.flush()
        return True
