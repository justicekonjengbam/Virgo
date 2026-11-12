from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models.ride_hailing import Driver, DriverDocument, DriverVehicleAssignment, Vehicle
from app.schemas.admin_review import DriverDocumentReviewRequest
from app.services.driver_document_review_service import DriverDocumentReviewService
import app.models  # noqa: F401


def test_vehicle_is_approved_only_after_every_required_document_is_verified() -> None:
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    driver = Driver(firebase_uid='firebase-driver', full_name='Test Driver', phone_number='919876543210')
    vehicle = Vehicle(registration_number='KA01AB1234', make='Test', model='Car', year=2024, category_code='car', seat_count=4)
    session.add_all([driver, vehicle])
    session.flush()
    session.add(DriverVehicleAssignment(driver_id=driver.id, vehicle_id=vehicle.id))
    for document_type in DriverDocumentReviewService.required_document_types:
        session.add(DriverDocument(driver_id=driver.id, document_type=document_type, document_number=f'{document_type}-1234', storage_key=f'uploads/{document_type}.png'))
    session.commit()

    service = DriverDocumentReviewService()
    for document_type in DriverDocumentReviewService.required_document_types:
        result = service.review(session, driver.id, document_type, DriverDocumentReviewRequest(status='verified'), 'test-admin')

    assert result.document_status == 'verified'
    assert result.vehicle_verification_status == 'verified'
    assert session.get(Vehicle, vehicle.id).verification_status == 'verified'
