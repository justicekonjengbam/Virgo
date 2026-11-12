from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rate_limit import login_limiter, otp_request_limiter, otp_verify_limiter, rate_limit
from app.db import get_db
from app.schemas.auth import FirebaseLoginRequest, OtpRequest, OtpRequestResponse, OtpVerificationRequest, PassengerSignupRequest, PasswordLoginRequest, RefreshRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix='/auth/passengers', tags=['passenger-auth'])
service = AuthService()


@router.post('/signup', response_model=OtpRequestResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit(otp_request_limiter, 'passenger_signup'))])
def signup(request: PassengerSignupRequest, db: Session = Depends(get_db)) -> OtpRequestResponse:
    passenger = service.signup(db, request)
    otp = service.request_otp(db, passenger.phone_number)
    return OtpRequestResponse(message='Account created. Verify the OTP to continue.', development_otp=otp if get_settings().environment == 'development' else None)


@router.post('/otp/request', response_model=OtpRequestResponse, dependencies=[Depends(rate_limit(otp_request_limiter, 'passenger_otp_request'))])
def request_otp(request: OtpRequest, db: Session = Depends(get_db)) -> OtpRequestResponse:
    otp = service.request_otp(db, request.phone_number)
    return OtpRequestResponse(message='OTP sent.', development_otp=otp if get_settings().environment == 'development' else None)


@router.post('/otp/verify', response_model=TokenResponse, dependencies=[Depends(rate_limit(otp_verify_limiter, 'passenger_otp_verify'))])
def verify_otp(request: OtpVerificationRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return service.verify_otp(db, request.phone_number, request.otp)


@router.post('/login', response_model=TokenResponse, dependencies=[Depends(rate_limit(login_limiter, 'passenger_login'))])
def login(request: PasswordLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return service.login(db, request.phone_number, request.password)


@router.post('/refresh', response_model=TokenResponse)
def refresh(request: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return service.refresh(db, request.refresh_token)


@router.post('/firebase/login', response_model=TokenResponse, dependencies=[Depends(rate_limit(login_limiter, 'passenger_fb_login'))])
def firebase_login(request: FirebaseLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return service.firebase_login(db, request.id_token)


@router.post('/firebase/signup', response_model=TokenResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit(login_limiter, 'passenger_fb_signup'))])
def firebase_signup(request: FirebaseLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return service.firebase_signup(db, request.id_token, request.full_name)


@router.post('/firebase/login/preflight', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(rate_limit(otp_request_limiter, 'passenger_preflight'))])
def firebase_login_preflight(request: OtpRequest, db: Session = Depends(get_db)) -> None:
    service.ensure_firebase_login_allowed(db, request.phone_number)
