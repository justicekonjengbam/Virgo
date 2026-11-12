# backend/app/schemas/auth.py

## 1. Purpose
This file holds the message shapes for sign-up, login, OTP, refresh tokens and driver registration. It also holds `normalize_phone`, which turns Indian phone numbers into one format. The auth routes use these classes; the passenger app and driver app send this JSON. It calls only `pydantic`.

## 2. Imports, one by one
- `from pydantic import BaseModel, Field, field_validator, model_validator` (`auth.py:1`). **Pydantic** checks data against type hints. `BaseModel` is the base class. `Field` adds limits (`min_length`, `ge` = greater or equal, `pattern` = regular expression). `field_validator` checks or changes one field. `model_validator(mode="after")` checks the finished object. *Example:* `Field(ge=1, le=8)` accepts 1 to 8.

## 3. Walk through the code, top to bottom
### `normalize_phone(value: str) -> str` (4-10)
Input: any text. Output: `91` plus ten digits.
1. Line 5 keeps only digits: `"".join(c for c in value if c.isdigit())`. `"98765 43210"` becomes `"9876543210"`.
2. Lines 6-7: exactly 10 digits and the first is 6, 7, 8 or 9 (Indian mobile numbers start there) returns `"91" + digits`.
3. Lines 8-9: exactly 12 digits that start with `91` and whose third digit is 6-9 returns as is.
4. Line 10: else `raise ValueError("Enter a valid 10-digit Indian mobile number.")`.
Example: `"+91 98765-43210"` returns `"919876543210"`. `"12345"` raises.

### Classes
- `PassengerSignupRequest` (13-22). Name 2-120, phone 10-20 characters, password 8-128. `validate_phone` (18-22) is a `@field_validator("phone_number")` plus `@classmethod`; it calls `normalize_phone`. The `normalized` variable is not needed (see section 6).
- `PasswordLoginRequest` (25-29). Line 29: `_normalize_phone = field_validator("phone_number")(normalize_phone)` applies the decorator by hand to a plain function. I ran it: it works with pydantic 2.14.1 and gives `919876543210`. The name starts with `_` so pydantic does not treat it as a field.
- `OtpRequest` (32-34). Same trick. **OTP** (One-Time Password, the SMS code).
- `OtpVerificationRequest(OtpRequest)` (37-38). **Inheritance** (a class that copies another class's fields and adds more). It adds `otp` with pattern `^\d{6}$`: exactly six digits.
- `RefreshRequest` (41-42). Holds `refresh_token`, a long-life token used to get a new access token.
- `FirebaseLoginRequest` (45-47). `id_token` (proof from Firebase, a Google login service) and optional `full_name`.
- `DriverFirebaseLoginRequest` (50-53). Only `id_token`. `DriverFirebaseSignupRequest` (56-59) inherits it and requires `full_name`.
- `DriverOnboardingRequest` (62-75). City, plate, make, model, `vehicle_year` 1990-2100, optional color, `vehicle_category` must match `^(car|bike|auto)$`, `seat_count` 1-8. `normalize_registration_number` (72-75) uppercases and removes spaces: `"ka 01 ab 1234"` becomes `"KA01AB1234"`.
- `DriverDocumentInput` (78-81). `document_type` one of four names; number; `storage_key` (where the uploaded file is kept).
- `DriverRegistrationRequest(DriverFirebaseSignupRequest)` (84-100). Has all onboarding fields (copied by hand, see section 6) plus `documents` as a list of exactly four (`min_length=4, max_length=4`). `require_each_document_once` (95-100) compares the set of types to the expected four. If it differs (a repeat or a missing type), it raises. Note that it does not normalize the plate, unlike `DriverOnboardingRequest`.
- `DriverProfileResponse` (103-109). Returned profile.
- `DriverProfileUpdateRequest` (112-120). Both fields optional; the validator raises if both are `None`.
- `TokenResponse` (123-126). `access_token`, `refresh_token`, `token_type` default `"bearer"`.
- `DriverAuthResponse(TokenResponse)` (129-130). Adds nested `driver`.
- `OtpRequestResponse` (133-135). `message` and `development_otp` (optional). The latter is for local testing only.

Errors: failed rules produce HTTP 422 from FastAPI with the message.

## 4. How data flows
```
passenger-app --POST {"phone_number":"98765 43210","otp":"123456"}--> FastAPI
  -> OtpVerificationRequest: normalize_phone -> "919876543210"; otp matches 6 digits
  -> route -> service -> TokenResponse JSON back
```

## 5. Try it
```zsh
cd backend
uv run python -c "
from app.schemas.auth import normalize_phone, DriverOnboardingRequest as D
print(normalize_phone('+91 98765-43210'))
print(D(operating_city='Pune',registration_number='ka 01 ab 1234',vehicle_make='Maruti',vehicle_model='Dzire',vehicle_year=2020,vehicle_category='car',seat_count=4).registration_number)"
```
Expected: `919876543210`, then `KA01AB1234`.

## 6. Can it be better?
- Good: phone and plate cleaning is done once, early; patterns block bad categories and document types.
- Weak: `DriverRegistrationRequest` repeats the vehicle fields of `DriverOnboardingRequest` and misses the plate normalization (a real bug risk: `"ka 01"` and `"KA01"` count as different). The `documents` list check and `Field(min_length=4, max_length=4)` overlap. `validate_phone` has a needless variable. The phone fields in `PasswordLoginRequest` and `OtpRequest` have no length limits before normalization. `development_otp` in a response is risky if it leaks to production.
- Cleaner way:
```python
class VehicleFields(BaseModel): ...   # shared fields + plate validator
class DriverOnboardingRequest(VehicleFields): ...
class DriverRegistrationRequest(DriverFirebaseSignupRequest, VehicleFields): documents: ...
```
- Security: make sure `development_otp` is `None` unless debug mode is on (check the service). Never log `id_token` or `password`.

## 7. Check yourself
1. What does `normalize_phone("098765 43210")` do, and why?
2. Why must `DriverRegistrationRequest.documents` hold each type exactly once?
