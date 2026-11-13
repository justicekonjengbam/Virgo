import secrets
import logging
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status
from firebase_admin import auth as firebase_auth
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.user import Passenger
from app.repositories.passenger_repository import PassengerRepository
from app.schemas.auth import PassengerSignupRequest, TokenResponse
from app.services.firebase_service import initialize_firebase

password_hash = PasswordHash.recommended()
logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, repository: PassengerRepository | None = None):
        self.repository = repository or PassengerRepository()
        self.settings = get_settings()

    def signup(self, db: Session, request: PassengerSignupRequest) -> Passenger:
        if self.repository.get_by_phone(db, request.phone_number):
            raise HTTPException(status_code=409, detail='An account already exists for this phone number.')
        return self.repository.create(db, Passenger(full_name=request.full_name, phone_number=request.phone_number, password_hash=password_hash.hash(request.password)))

    def request_otp(self, db: Session, phone_number: str) -> str:
        passenger = self.repository.get_by_phone(db, phone_number)
        if not passenger:
            # OTP login is passwordless on the Passenger app. A minimal pending
            # account is created here and becomes authenticated only after OTP verification.
            passenger = self.repository.create(
                db,
                Passenger(
                    full_name='Passenger',
                    phone_number=phone_number,
                    password_hash=password_hash.hash(secrets.token_urlsafe(32)),
                ),
            )
        otp = f'{secrets.randbelow(1_000_000):06d}'
        passenger.otp_hash = password_hash.hash(otp)
        passenger.otp_expires_at = datetime.now(UTC) + timedelta(minutes=self.settings.otp_expiry_minutes)
        self.repository.save(db, passenger)
        return otp

    @staticmethod
    def _aware(value: datetime) -> datetime:
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)

    def verify_otp(self, db: Session, phone_number: str, otp: str) -> TokenResponse:
        passenger = self._get_passenger(db, phone_number)
        now = datetime.now(UTC)
        expires_at = self._aware(passenger.otp_expires_at) if passenger.otp_expires_at else None
        if not passenger.otp_hash or not expires_at or expires_at < now or not password_hash.verify(otp, passenger.otp_hash):
            raise HTTPException(status_code=400, detail='Invalid or expired OTP.')
        passenger.is_phone_verified = True
        passenger.otp_hash = None
        passenger.otp_expires_at = None
        self.repository.save(db, passenger)
        return self._tokens(passenger)

    def login(self, db: Session, phone_number: str, password: str) -> TokenResponse:
        passenger = self._get_passenger(db, phone_number)
        if not password_hash.verify(password, passenger.password_hash):
            raise HTTPException(status_code=401, detail='Invalid phone number or password.')
        if not passenger.is_phone_verified:
            raise HTTPException(status_code=403, detail='Verify your phone number before logging in.')
        return self._tokens(passenger)

    def refresh(self, db: Session, refresh_token: str) -> TokenResponse:
        payload = self._decode(refresh_token, 'refresh')
        passenger_id = int(payload['sub'])
        passenger = self.repository.get(db, passenger_id)
        if not passenger or passenger.deleted_at is not None or passenger.status != 'active':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Your account is not available.')
        return self._tokens(passenger)

    def firebase_login(self, db: Session, id_token: str, full_name: str | None = None) -> TokenResponse:
        firebase_uid, phone_number = self._verified_firebase_identity(id_token)
        passenger = self.repository.get_by_firebase_uid(db, firebase_uid) or self.repository.get_verified_by_phone(db, phone_number)
        if not passenger:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No verified Virgo account exists for this number. Please sign up first.')
        passenger.firebase_uid = firebase_uid
        passenger.is_phone_verified = True
        passenger.last_login_at = datetime.now(UTC)
        self.repository.save(db, passenger)
        return self._tokens(passenger)

    def firebase_signup(self, db: Session, id_token: str, full_name: str | None, password: str | None = None) -> TokenResponse:
        firebase_uid, phone_number = self._verified_firebase_identity(id_token)
        existing = self.repository.get_by_firebase_uid(db, firebase_uid) or self.repository.get_by_phone(db, phone_number)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='An account already exists for this number. Please log in.')
        pwd = password.strip() if password and len(password.strip()) >= 4 else secrets.token_urlsafe(32)
        passenger = Passenger(
            full_name=full_name.strip() if full_name else 'Passenger',
            phone_number=phone_number,
            firebase_uid=firebase_uid,
            password_hash=password_hash.hash(pwd),
            is_phone_verified=True,
            last_login_at=datetime.now(UTC),
        )
        passenger = self.repository.create(db, passenger)
        self.repository.create_profile(db, passenger.id)
        return self._tokens(passenger)

    def ensure_firebase_login_allowed(self, db: Session, phone_number: str) -> None:
        if not self.repository.get_verified_by_phone(db, phone_number):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No verified Virgo account exists for this number. Please sign up first.')

    def _verified_firebase_identity(self, id_token: str) -> tuple[str, str]:
        if self.settings.environment == "development":
            if id_token == "test-passenger-token" or id_token.startswith("dev-passenger:") or not self.settings.firebase_credentials_path:
                if id_token.startswith("dev-passenger:"):
                    parts = id_token.split(":")
                    phone = parts[1] if len(parts) > 1 else "9876543210"
                    uid = parts[2] if len(parts) > 2 else f"dev_passenger_{phone}"
                    return uid, phone
                return "test_passenger_uid_9876543210", "9876543210"

        initialize_firebase()
        try:
            decoded = firebase_auth.verify_id_token(id_token, clock_skew_seconds=60)
        except Exception as error:
            error_name = type(error).__name__
            logger.warning('Firebase Passenger token verification failed: %s', error_name, exc_info=True)
            if error_name in {'ExpiredIdTokenError', 'RevokedIdTokenError'}:
                detail = 'Your phone verification has expired. Request a new OTP and try again.'
            elif error_name in {'CertificateFetchError', 'UnavailableError'}:
                detail = 'Secure sign-in is temporarily unavailable. Check your connection and try again.'
            elif error_name == 'InvalidIdTokenError':
                detail = 'This OTP session is no longer valid. Request a new OTP and try again.'
            else:
                detail = 'We could not securely verify this phone session. Request a new OTP and try again.'
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail) from error

        firebase_uid = decoded.get('uid')
        phone_number = decoded.get('phone_number')
        if not firebase_uid or not phone_number:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='A verified Firebase phone number is required.')
        return firebase_uid, ''.join(character for character in phone_number if character.isdigit())

    def _tokens(self, passenger: Passenger) -> TokenResponse:
        return TokenResponse(access_token=self._encode(passenger.id, 'access', timedelta(minutes=self.settings.access_token_minutes)), refresh_token=self._encode(passenger.id, 'refresh', timedelta(days=self.settings.refresh_token_days)))

    def _encode(self, passenger_id: int, token_type: str, expires_in: timedelta) -> str:
        return jwt.encode(
            {
                'sub': str(passenger_id),
                'type': token_type,
                'actor': 'passenger',
                'exp': datetime.now(UTC) + expires_in,
            },
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm,
        )

    def _decode(self, token: str, token_type: str) -> dict:
        try:
            payload = jwt.decode(token, self.settings.jwt_secret_key, algorithms=[self.settings.jwt_algorithm])
            if payload.get('type') != token_type:
                raise ValueError
            if payload.get('actor') not in (None, 'passenger'):
                raise ValueError
            return payload
        except (jwt.PyJWTError, ValueError) as error:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token.') from error

    def _get_passenger(self, db: Session, phone_number: str) -> Passenger:
        passenger = self.repository.get_by_phone(db, phone_number)
        if not passenger:
            raise HTTPException(status_code=404, detail='No account exists for this phone number.')
        return passenger
