from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ride_hailing import EmergencyContact
from app.models.user import Passenger
from app.schemas.emergency import EmergencyContactResponse


class EmergencyContactService:
    """Read-only development contact directory; CRUD is intentionally deferred."""

    demo_contacts = (
        ('Mom', '9899654500', 'Family'),
        ('Dad', '8787623452', 'Family'),
        ('Virgo Support', '+91 6009060341', 'Support'),
    )
    legacy_demo_names = {'Ananya Sharma', 'Rahul Patil', 'Cab Sure Safety Desk', 'CabSure Support'}

    def list_for_passenger(self, db: Session, passenger: Passenger) -> list[EmergencyContactResponse]:
        contacts = db.scalars(select(EmergencyContact).where(EmergencyContact.passenger_id == passenger.id).order_by(EmergencyContact.id)).all()
        if not contacts or {item.name for item in contacts} == self.legacy_demo_names:
            if contacts:
                for contact, (name, phone, relationship) in zip(contacts, self.demo_contacts, strict=True):
                    contact.name = name
                    contact.phone_number = phone
                    contact.relationship = relationship
            else:
                db.add_all(EmergencyContact(passenger_id=passenger.id, name=name, phone_number=phone, relationship=relationship) for name, phone, relationship in self.demo_contacts)
            db.commit()
            contacts = db.scalars(select(EmergencyContact).where(EmergencyContact.passenger_id == passenger.id).order_by(EmergencyContact.id)).all()
        return [EmergencyContactResponse(id=item.id, name=item.name, phone_number=item.phone_number, relationship=item.relationship) for item in contacts]
