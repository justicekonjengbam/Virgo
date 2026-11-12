from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ride_hailing import PassengerProfile
from app.models.user import Passenger
from app.schemas.profile import PassengerProfileResponse, PassengerProfileUpdateRequest


class PassengerProfileService:
    def get(self, db: Session, passenger: Passenger) -> PassengerProfileResponse:
        profile = self._profile(db, passenger)
        return self._response(passenger, profile)

    def update(self, db: Session, passenger: Passenger, request: PassengerProfileUpdateRequest) -> PassengerProfileResponse:
        profile = self._profile(db, passenger)
        if request.email is not None:
            duplicate = db.scalar(select(PassengerProfile).where(PassengerProfile.email == request.email.lower(), PassengerProfile.passenger_id != passenger.id))
            if duplicate:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='That email address is already used by another account.')
            profile.email = request.email.lower()
        if request.preferred_language is not None:
            profile.preferred_language = request.preferred_language.lower()
        if request.full_name is not None:
            passenger.full_name = request.full_name.strip()
        db.add_all([passenger, profile])
        db.commit()
        db.refresh(passenger); db.refresh(profile)
        return self._response(passenger, profile)

    @staticmethod
    def _response(passenger: Passenger, profile: PassengerProfile) -> PassengerProfileResponse:
        return PassengerProfileResponse(full_name=passenger.full_name, phone_number=passenger.phone_number, email=profile.email, preferred_language=profile.preferred_language)

    @staticmethod
    def _profile(db: Session, passenger: Passenger) -> PassengerProfile:
        profile = db.get(PassengerProfile, passenger.id)
        if profile:
            return profile
        profile = PassengerProfile(passenger_id=passenger.id)
        db.add(profile); db.flush()
        return profile
