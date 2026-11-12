import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import get_db
from app.models.user import AdminUser
from app.services.admin_auth_service import ROLE_PERMISSIONS

admin_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(admin_bearer_scheme),
    db: Session = Depends(get_db),
) -> AdminUser:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Admin authentication is required.')
    try:
        payload = jwt.decode(credentials.credentials, get_settings().jwt_secret_key, algorithms=[get_settings().jwt_algorithm])
        if payload.get('type') != 'access' or payload.get('actor') != 'admin':
            raise ValueError
        admin = db.get(AdminUser, int(payload['sub']))
        if admin and payload.get('ver') != admin.token_version:
            raise ValueError
    except (jwt.PyJWTError, KeyError, TypeError, ValueError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Admin session.') from error
    if not admin or not admin.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Your Admin account is unavailable.')
    return admin


def require_admin_permission(permission: str):
    def dependency(admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
        if permission not in ROLE_PERMISSIONS.get(admin.role, set()):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Your Admin role does not permit this action.')
        return admin
    return dependency
