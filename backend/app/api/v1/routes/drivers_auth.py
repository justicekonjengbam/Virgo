from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.driver_auth import get_current_driver
from app.core.config import get_settings
from app.core.rate_limit import login_limiter, otp_request_limiter, otp_verify_limiter, rate_limit
from app.db import get_db
from app.models.ride_hailing import Driver
from app.schemas.auth import (
    DriverAuthResponse,
    DriverFirebaseLoginRequest,
    DriverFirebaseSignupRequest,
    DriverOnboardingRequest,
    DriverProfileUpdateRequest,
    DriverProfileResponse,
    DriverRegistrationRequest,
    OtpRequest,
    OtpRequestResponse,
    OtpVerificationRequest,
    RefreshRequest,
)
from app.services.driver_auth_service import DriverAuthService

router = APIRouter(prefix="/auth/drivers", tags=["driver-auth"])
service = DriverAuthService()


@router.post("/firebase/login/preflight", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(rate_limit(otp_request_limiter, 'driver_preflight'))])
def firebase_login_preflight(request: OtpRequest, db: Session = Depends(get_db)) -> None:
    service.ensure_login_allowed(db, request.phone_number)


@router.post("/otp/request", response_model=OtpRequestResponse, dependencies=[Depends(rate_limit(otp_request_limiter, 'driver_otp_request'))])
def request_otp(request: OtpRequest, db: Session = Depends(get_db)) -> OtpRequestResponse:
    otp = service.request_otp(db, request.phone_number)
    return OtpRequestResponse(
        message="OTP sent.",
        development_otp=otp if get_settings().environment == "development" else None,
    )


@router.post("/otp/verify", response_model=DriverAuthResponse, dependencies=[Depends(rate_limit(otp_verify_limiter, 'driver_otp_verify'))])
def verify_otp(request: OtpVerificationRequest, db: Session = Depends(get_db)) -> DriverAuthResponse:
    return service.verify_otp(db, request.phone_number, request.otp)


@router.post("/firebase/login", response_model=DriverAuthResponse, dependencies=[Depends(rate_limit(login_limiter, 'driver_login'))])
def firebase_login(
    request: DriverFirebaseLoginRequest, db: Session = Depends(get_db)
) -> DriverAuthResponse:
    return service.login(db, request)


@router.post("/firebase/signup", response_model=DriverAuthResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit(login_limiter, 'driver_signup'))])
def firebase_signup(request: DriverFirebaseSignupRequest, db: Session = Depends(get_db)) -> DriverAuthResponse:
    return service.signup(db, request)


@router.post("/firebase/register", response_model=DriverAuthResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit(login_limiter, 'driver_register'))])
def register(request: DriverRegistrationRequest, db: Session = Depends(get_db)) -> DriverAuthResponse:
    return service.complete_registration(db, request)


@router.post("/refresh", response_model=DriverAuthResponse)
def refresh(request: RefreshRequest, db: Session = Depends(get_db)) -> DriverAuthResponse:
    return service.refresh(db, request.refresh_token)


@router.get("/me", response_model=DriverProfileResponse)
def get_me(
    driver: Driver = Depends(get_current_driver), db: Session = Depends(get_db)
) -> DriverProfileResponse:
    return service.profile(db, driver)


@router.patch('/me', response_model=DriverProfileResponse)
def update_me(
    request: DriverProfileUpdateRequest,
    driver: Driver = Depends(get_current_driver), db: Session = Depends(get_db)
) -> DriverProfileResponse:
    return service.update_profile(db, driver, request)


@router.post("/onboarding", response_model=DriverProfileResponse)
def complete_onboarding(
    request: DriverOnboardingRequest,
    driver: Driver = Depends(get_current_driver),
    db: Session = Depends(get_db),
) -> DriverProfileResponse:
    return service.complete_onboarding(db, driver, request)
