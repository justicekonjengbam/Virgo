from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.ride_hailing import AuditLog
from app.models.user import AdminUser
from app.schemas.admin import AdminAuthResponse, AdminLoginRequest, AdminPasswordChangeRequest, AdminProfileResponse

password_hash = PasswordHash.recommended()
ROLE_PERMISSIONS = {
    'super_admin': {
        'drivers:read',
        'documents:review',
        'documents:upload',
        'documents:delete',
        'support:manage',
        'outstation:manage',
        'admins:manage',
        'aadhaar:unmasked',
        'rides:read',
        'rides:manage',
        'rate_cards:read',
        'rate_cards:manage',
    },
    'operations_admin': {
        'drivers:read',
        'documents:review',
        'documents:upload',
        'support:manage',
        'outstation:manage',
        'rides:read',
        'rides:manage',
        'rate_cards:read',
        'rate_cards:manage',
    },
    'document_reviewer': {'drivers:read', 'documents:review', 'documents:upload', 'rides:read'},
    'support_admin': {'drivers:read', 'support:manage', 'outstation:manage', 'rides:read', 'rides:manage', 'rate_cards:read'},
}


class AdminAuthService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def bootstrap(self, db: Session) -> None:
        email, password = self.settings.admin_bootstrap_email, self.settings.admin_bootstrap_password
        if not email or not password:
            if self.settings.environment == 'development':
                email = 'admin@virgo.com'
                password = 'admin12345'
            else:
                return
        normalized = email.strip().lower()
        existing = db.scalar(select(AdminUser).where(AdminUser.email == normalized))
        if existing:
            if existing.role != self.settings.admin_bootstrap_role:
                existing.role = self.settings.admin_bootstrap_role
                db.add(existing)
                db.commit()
            return
        db.add(AdminUser(email=normalized, full_name=self.settings.admin_bootstrap_name, password_hash=password_hash.hash(password), role=self.settings.admin_bootstrap_role))
        db.commit()

    def login(self, db: Session, request: AdminLoginRequest) -> AdminAuthResponse:
        admin = db.scalar(select(AdminUser).where(AdminUser.email == request.email))
        now = datetime.now(UTC)
        if admin and admin.locked_until and self._aware(admin.locked_until) > now:
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail='This Admin ID is temporarily locked. Try again in 15 minutes.')
        if not admin or not admin.is_active or not password_hash.verify(request.password, admin.password_hash):
            if admin and admin.is_active:
                admin.failed_login_attempts += 1
                if admin.failed_login_attempts >= 5:
                    admin.locked_until = now + timedelta(minutes=15)
                    admin.failed_login_attempts = 0
                db.add(admin)
                db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect email or password.')
        admin.last_login_at = now
        admin.failed_login_attempts = 0
        admin.locked_until = None
        db.add(admin)
        db.add(AuditLog(actor_type='admin', actor_id=admin.id, action='admin.login', entity_type='admin_user', entity_id=str(admin.id), metadata_json=None))
        db.commit()
        return AdminAuthResponse(access_token=self._encode(admin), admin=self._profile(admin))

    def change_password(self, db: Session, admin: AdminUser, request: AdminPasswordChangeRequest) -> None:
        if not password_hash.verify(request.current_password, admin.password_hash):
            raise HTTPException(status_code=400, detail='The current password is incorrect.')
        admin.password_hash = password_hash.hash(request.new_password)
        admin.password_changed_at = datetime.now(UTC)
        admin.token_version += 1
        db.add(admin)
        db.add(AuditLog(actor_type='admin', actor_id=admin.id, action='admin.password_changed', entity_type='admin_user', entity_id=str(admin.id), metadata_json=None))
        db.commit()

    def _encode(self, admin: AdminUser) -> str:
        return jwt.encode({'sub': str(admin.id), 'type': 'access', 'actor': 'admin', 'role': admin.role, 'ver': admin.token_version, 'exp': datetime.now(UTC) + timedelta(minutes=self.settings.access_token_minutes)}, self.settings.jwt_secret_key, algorithm=self.settings.jwt_algorithm)

    @staticmethod
    def _profile(admin: AdminUser) -> AdminProfileResponse:
        return AdminProfileResponse(id=admin.id, email=admin.email, full_name=admin.full_name, role=admin.role, permissions=sorted(ROLE_PERMISSIONS.get(admin.role, set())), last_login_at=admin.last_login_at)

    @staticmethod
    def _aware(value: datetime) -> datetime:
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value
