from datetime import UTC, datetime, timedelta
import logging
import secrets

import jwt
from fastapi import HTTPException, status
from firebase_admin import auth as firebase_auth
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.ride_hailing import Driver, DriverDocument, Vehicle
from app.repositories.driver_repository import DriverRepository
from app.schemas.auth import (
    DriverAuthResponse,
    DriverFirebaseLoginRequest,
    DriverFirebaseSignupRequest,
    DriverOnboardingRequest,
    DriverProfileResponse,
    DriverProfileUpdateRequest,
    DriverRegistrationRequest,
)
from app.services.firebase_service import initialize_firebase

logger = logging.getLogger(__name__)

_dev_driver_otps: dict[str, tuple[str, datetime]] = {}


class DriverAuthService:
    """Driver-specific Firebase identity and onboarding service."""

    def __init__(self, repository: DriverRepository | None = None):
        self.repository = repository or DriverRepository()
        self.settings = get_settings()

    def ensure_login_allowed(self, db: Session, phone_number: str) -> None:
        digits = "".join(c for c in phone_number if c.isdigit())
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]
        driver = self.repository.get_by_phone(db, digits)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Virgo Driver account exists for this number. Please register first.",
            )
        if driver.status in {"suspended", "deactivated"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your Driver account is not active.",
            )

    def request_otp(self, db: Session, phone_number: str) -> str:
        digits = "".join(c for c in phone_number if c.isdigit())
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]
        otp = f"{secrets.randbelow(1_000_000):06d}"
        _dev_driver_otps[digits] = (
            otp,
            datetime.now(UTC) + timedelta(minutes=self.settings.otp_expiry_minutes),
        )
        return otp

    def verify_otp(self, db: Session, phone_number: str, otp: str) -> DriverAuthResponse:
        digits = "".join(c for c in phone_number if c.isdigit())
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]

        if self.settings.environment == "development":
            record = _dev_driver_otps.get(digits)
            now = datetime.now(UTC)
            is_valid = (
                otp == "123456"
                or (record is not None and record[0] == otp and record[1] >= now)
            )
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired OTP.",
                )
            _dev_driver_otps.pop(digits, None)
            driver = self.repository.get_by_phone(db, digits)
            if not driver:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No Virgo Driver account exists for this number. Please register first.",
                )
            if driver.status in {"suspended", "deactivated"}:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your Driver account is not active.",
                )
            return self._auth_response(db, driver)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Direct OTP verification is only available in development.",
        )

    def signup(self, db: Session, request: DriverFirebaseSignupRequest) -> DriverAuthResponse:
        firebase_uid, phone_number = self._verified_firebase_identity(request.id_token)
        existing = self.repository.get_by_firebase_uid(
            db, firebase_uid
        ) or self.repository.get_by_phone(db, phone_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A Driver account already exists for this number. Please log in.",
            )
        driver = self.repository.create(
            db,
            Driver(
                firebase_uid=firebase_uid,
                phone_number=phone_number,
                full_name=request.full_name.strip(),
                status="pending",
            ),
        )
        return self._auth_response(db, driver)

    def login(self, db: Session, request: DriverFirebaseLoginRequest) -> DriverAuthResponse:
        firebase_uid, phone_number = self._verified_firebase_identity(request.id_token)
        driver = self.repository.get_by_firebase_uid(
            db, firebase_uid
        ) or self.repository.get_by_phone(db, phone_number)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Virgo Driver account exists for this number. Please register first.",
            )
        driver.firebase_uid = firebase_uid
        self.repository.save(db, driver)
        return self._auth_response(db, driver)

    def refresh(self, db: Session, refresh_token: str) -> DriverAuthResponse:
        payload = self._decode(refresh_token, "refresh")
        driver = db.get(Driver, int(payload["sub"]))
        if not driver or driver.status in {"suspended", "deactivated"}:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your Driver account is not available.",
            )
        return self._auth_response(db, driver)

    def complete_registration(self, db: Session, request: DriverRegistrationRequest) -> DriverAuthResponse:
        firebase_uid, phone_number = self._verified_firebase_identity(request.id_token)
        existing = self.repository.get_by_firebase_uid(db, firebase_uid) or self.repository.get_by_phone(db, phone_number)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A Driver account already exists for this number. Please log in.")
        driver = Driver(firebase_uid=firebase_uid, phone_number=phone_number, full_name=request.full_name.strip(), status="pending", operating_city=request.operating_city.strip())
        vehicle = Vehicle(registration_number=request.registration_number, make=request.vehicle_make.strip(), model=request.vehicle_model.strip(), year=request.vehicle_year, color=request.vehicle_color.strip() if request.vehicle_color else None, category_code=request.vehicle_category, seat_count=request.seat_count, verification_status="pending")
        documents = [DriverDocument(driver_id=0, document_type=item.document_type, document_number=item.document_number.strip(), storage_key=item.storage_key, verification_status="pending") for item in request.documents]
        try:
            driver = self.repository.create_complete_registration(db, driver, vehicle, documents)
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Unable to save the Driver application. Check unique vehicle and document values.") from error
        return self._auth_response(db, driver)

    def complete_onboarding(
        self, db: Session, driver: Driver, request: DriverOnboardingRequest
    ) -> DriverProfileResponse:
        if self.repository.get_active_assignment(db, driver.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Driver onboarding is already complete.",
            )
        driver.operating_city = request.operating_city.strip()
        vehicle = Vehicle(
            registration_number=request.registration_number,
            make=request.vehicle_make.strip(),
            model=request.vehicle_model.strip(),
            year=request.vehicle_year,
            color=request.vehicle_color.strip() if request.vehicle_color else None,
            category_code=request.vehicle_category,
            seat_count=request.seat_count,
            verification_status="pending",
        )
        try:
            self.repository.create_vehicle_and_assignment(db, driver, vehicle)
        except Exception as error:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="That vehicle registration number is already in use.",
            ) from error
        self.repository.save(db, driver)
        return self.profile(db, driver)

    def profile(self, db: Session, driver: Driver) -> DriverProfileResponse:
        return DriverProfileResponse(
            id=driver.id,
            full_name=driver.full_name,
            phone_number=driver.phone_number,
            status=driver.status,
            operating_city=driver.operating_city,
            onboarding_completed=self.repository.get_active_assignment(db, driver.id) is not None,
        )

    def update_profile(self, db: Session, driver: Driver, request: DriverProfileUpdateRequest) -> DriverProfileResponse:
        if request.full_name is not None:
            driver.full_name = request.full_name.strip()
        if request.operating_city is not None:
            driver.operating_city = request.operating_city.strip()
        self.repository.save(db, driver)
        return self.profile(db, driver)

    def _auth_response(self, db: Session, driver: Driver) -> DriverAuthResponse:
        return DriverAuthResponse(
            access_token=self._encode(
                driver.id, "access", timedelta(minutes=self.settings.access_token_minutes)
            ),
            refresh_token=self._encode(
                driver.id, "refresh", timedelta(days=self.settings.refresh_token_days)
            ),
            driver=self.profile(db, driver),
        )

    def _verified_firebase_identity(self, id_token: str) -> tuple[str, str]:
        if self.settings.environment == "development":
            if id_token == "test-driver-token" or id_token.startswith("dev-driver:") or not self.settings.firebase_credentials_path:
                if id_token.startswith("dev-driver:"):
                    parts = id_token.split(":")
                    phone = parts[1] if len(parts) > 1 else "9876543220"
                    uid = parts[2] if len(parts) > 2 else f"dev_driver_{phone}"
                    return uid, phone
                return "test_driver_uid_9876543220", "9876543220"

        initialize_firebase()
        try:
            # Mobile devices can be slightly ahead/behind the API host. A small
            # tolerance avoids rejecting an otherwise fresh Firebase OTP session.
            decoded = firebase_auth.verify_id_token(id_token, clock_skew_seconds=60)
        except Exception as error:
            error_name = type(error).__name__
            logger.warning("Firebase Driver token verification failed: %s", error_name, exc_info=True)
            if error_name in {"ExpiredIdTokenError", "RevokedIdTokenError"}:
                detail = "Your phone verification has expired. Request a new OTP and try again."
            elif error_name in {"CertificateFetchError", "UnavailableError"}:
                detail = "Secure sign-in is temporarily unavailable. Please check your connection and try again."
            elif error_name == "InvalidIdTokenError":
                detail = "This OTP session is no longer valid. Request a new OTP and try again."
            else:
                detail = "We could not securely verify this phone session. Request a new OTP and try again."
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=detail,
            ) from error
        firebase_uid = decoded.get("uid")
        phone_number = decoded.get("phone_number")
        if not firebase_uid or not phone_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A verified Firebase phone number is required.",
            )
        return firebase_uid, "".join(character for character in phone_number if character.isdigit())

    def _encode(self, driver_id: int, token_type: str, expires_in: timedelta) -> str:
        return jwt.encode(
            {
                "sub": str(driver_id),
                "type": token_type,
                "actor": "driver",
                "exp": datetime.now(UTC) + expires_in,
            },
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm,
        )

    def _decode(self, token: str, token_type: str) -> dict:
        try:
            payload = jwt.decode(
                token, self.settings.jwt_secret_key, algorithms=[self.settings.jwt_algorithm]
            )
            if payload.get("type") != token_type or payload.get("actor") != "driver":
                raise ValueError
            return payload
        except (jwt.PyJWTError, ValueError) as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Driver refresh token."
            ) from error
