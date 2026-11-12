import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import get_db
from app.models.ride_hailing import Driver

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_driver(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Driver:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication is required.')
    try:
        payload = jwt.decode(credentials.credentials, get_settings().jwt_secret_key, algorithms=[get_settings().jwt_algorithm])
        if payload.get('type') != 'access' or payload.get('actor') != 'driver':
            raise ValueError
        driver = db.get(Driver, int(payload['sub']))
    except (jwt.PyJWTError, KeyError, TypeError, ValueError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Driver access token.') from error
    if not driver or driver.status in {'suspended', 'deactivated'}:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Your Driver account is not available.')
    return driver
