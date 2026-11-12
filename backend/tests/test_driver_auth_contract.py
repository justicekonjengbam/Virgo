import pytest
from pydantic import ValidationError

from app.schemas.auth import DriverFirebaseLoginRequest, DriverFirebaseSignupRequest


def test_driver_login_request_accepts_only_a_firebase_token() -> None:
    request = DriverFirebaseLoginRequest(id_token="firebase-token")

    assert request.id_token == "firebase-token"


def test_driver_signup_requires_a_real_name() -> None:
    with pytest.raises(ValidationError):
        DriverFirebaseSignupRequest(id_token="firebase-token", full_name="")

    request = DriverFirebaseSignupRequest(id_token="firebase-token", full_name="Asha Driver")
    assert request.full_name == "Asha Driver"


def test_driver_dev_otp_request_and_verify() -> None:
    from app.db import SessionLocal
    from app.services.driver_auth_service import DriverAuthService
    from fastapi import HTTPException

    db = SessionLocal()
    service = DriverAuthService()
    try:
        # Preflight for active seeded test driver
        service.ensure_login_allowed(db, "9876543220")

        # Dev OTP request
        otp = service.request_otp(db, "9876543220")
        assert len(otp) == 6
        assert otp.isdigit()

        # Dev OTP verify with generated code
        res = service.verify_otp(db, "9876543220", otp)
        assert res.driver.phone_number == "+919876543220"
        assert res.driver.full_name == "Test Driver"
        assert res.access_token is not None

        # Dev OTP verify with static dev fallback 123456
        res2 = service.verify_otp(db, "9876543220", "123456")
        assert res2.driver.phone_number == "+919876543220"

        # Wrong OTP raises 400
        with pytest.raises(HTTPException) as exc:
            service.verify_otp(db, "9876543220", "000000")
        assert exc.value.status_code == 400

        # Preflight for non-existent driver raises 404
        with pytest.raises(HTTPException) as exc:
            service.ensure_login_allowed(db, "9999999999")
        assert exc.value.status_code == 404
    finally:
        db.close()

