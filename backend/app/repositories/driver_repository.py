from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.phone import phone_variants
from app.models.ride_hailing import Driver, DriverDocument, DriverVehicleAssignment, Vehicle


class DriverRepository:
    """Persistence boundary for Driver identity and the active assigned vehicle."""

    def get_by_firebase_uid(self, db: Session, firebase_uid: str) -> Driver | None:
        return db.scalar(select(Driver).where(Driver.firebase_uid == firebase_uid))

    def get_by_phone(self, db: Session, phone_number: str) -> Driver | None:
        variants = phone_variants(phone_number)
        return db.scalar(select(Driver).where(Driver.phone_number.in_(variants)))

    def create(self, db: Session, driver: Driver) -> Driver:
        db.add(driver)
        db.commit()
        db.refresh(driver)
        return driver

    def save(self, db: Session, driver: Driver) -> Driver:
        db.add(driver)
        db.commit()
        db.refresh(driver)
        return driver

    def get_active_assignment(self, db: Session, driver_id: int) -> DriverVehicleAssignment | None:
        return db.scalar(
            select(DriverVehicleAssignment)
            .where(DriverVehicleAssignment.driver_id == driver_id, DriverVehicleAssignment.ended_at.is_(None))
            .order_by(DriverVehicleAssignment.started_at.desc())
        )

    def get_document(self, db: Session, driver_id: int, document_type: str) -> DriverDocument | None:
        return db.scalar(select(DriverDocument).where(
            DriverDocument.driver_id == driver_id,
            DriverDocument.document_type == document_type,
        ))

    def get_documents(self, db: Session, driver_id: int) -> list[DriverDocument]:
        return list(db.scalars(select(DriverDocument).where(DriverDocument.driver_id == driver_id)))

    def get_active_vehicle(self, db: Session, driver_id: int) -> Vehicle | None:
        assignment = self.get_active_assignment(db, driver_id)
        return db.get(Vehicle, assignment.vehicle_id) if assignment else None

    def create_vehicle_and_assignment(self, db: Session, driver: Driver, vehicle: Vehicle) -> DriverVehicleAssignment:
        db.add(vehicle)
        db.flush()
        assignment = DriverVehicleAssignment(driver_id=driver.id, vehicle_id=vehicle.id)
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    def create_complete_registration(self, db: Session, driver: Driver, vehicle: Vehicle, documents: list[DriverDocument]) -> Driver:
        try:
            db.add(driver)
            db.flush()
            db.add(vehicle)
            db.flush()
            db.add(DriverVehicleAssignment(driver_id=driver.id, vehicle_id=vehicle.id))
            for document in documents:
                document.driver_id = driver.id
                db.add(document)
            db.commit()
            db.refresh(driver)
            return driver
        except Exception:
            db.rollback()
            raise
