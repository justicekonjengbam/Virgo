from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_URL = f"sqlite:///{(BACKEND_ROOT / 'cabapp.db').as_posix()}"
DEFAULT_FIREBASE_CREDENTIALS = (
    str(BACKEND_ROOT / 'firebase-service-account.json')
    if (BACKEND_ROOT / 'firebase-service-account.json').is_file()
    else None
)


class Settings(BaseSettings):
    app_name: str = 'CabApp API'
    environment: str = 'development'
    debug: bool = False
    api_v1_prefix: str = '/api/v1'
    database_url: str = DEFAULT_DATABASE_URL
    auto_migrate: bool = True
    jwt_secret_key: str = 'change-this-development-secret-before-production'
    jwt_algorithm: str = 'HS256'
    access_token_minutes: int = 60
    refresh_token_days: int = 3650  # 10 years permanent session (only sign out when manual)
    otp_expiry_minutes: int = 10
    firebase_credentials_path: str | None = DEFAULT_FIREBASE_CREDENTIALS
    admin_bootstrap_email: str | None = None
    admin_bootstrap_password: str | None = None
    admin_bootstrap_name: str = 'Virgo Operations Admin'
    admin_bootstrap_role: str = 'super_admin'
    geoapify_api_key: str | None = None
    maps_contact_email: str = 'support@virgocabs.com'

    # Development-only test simulation for physical testing outside service area
    dev_simulate_test_driver_imphal: bool = True
    dev_test_driver_phone: str = '+919876543220'
    dev_test_driver_latitude: float = 24.8170
    dev_test_driver_longitude: float = 93.9368

    # Imphal, Manipur service area configuration
    service_center_latitude: float = 24.8170
    service_center_longitude: float = 93.9368
    service_radius_km: float = 150.0
    service_area_name: str = 'Imphal, Manipur'
    service_bounds: list[float] = [92.50, 23.50, 95.50, 26.00]
    cors_origins: list[str] = ['*']

    # Storage configuration (AWS S3 / Cloudflare R2 / Local)
    storage_backend: str = 'local'  # 'local', 's3', 'r2'
    local_storage_dir: str = str(BACKEND_ROOT / 'storage' / 'documents')
    local_storage_encryption_key: str | None = None  # Key for at-rest authenticated AES-256-GCM encryption
    s3_bucket_name: str | None = None
    s3_region: str = 'ap-south-1'
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None
    s3_endpoint_url: str | None = None  # Custom endpoint for Cloudflare R2 or MinIO
    max_upload_size_bytes: int = 5 * 1024 * 1024  # 5 MB
    signed_url_expiry_seconds: int = 300  # 5 minutes

    @model_validator(mode='after')
    def validate_production_security(self) -> 'Settings':
        if self.environment == 'production':
            if (
                self.jwt_secret_key == 'change-this-development-secret-before-production'
                or len(self.jwt_secret_key) < 32
            ):
                raise ValueError(
                    'In production, jwt_secret_key must be configured with a secure secret of at least 32 characters.'
                )
            if self.storage_backend in ('s3', 'r2'):
                if not self.s3_bucket_name or not self.s3_access_key_id or not self.s3_secret_access_key:
                    raise ValueError(
                        f'Production storage backend {self.storage_backend} requires s3_bucket_name, s3_access_key_id, and s3_secret_access_key.'
                    )
                if self.storage_backend == 'r2' and not self.s3_endpoint_url:
                    raise ValueError(
                        "Cloudflare R2 storage backend requires 's3_endpoint_url' (e.g., https://<account_id>.r2.cloudflarestorage.com)."
                    )
        return self

    model_config = SettingsConfigDict(env_file=BACKEND_ROOT / '.env', extra='ignore')


@lru_cache
def get_settings() -> Settings:
    return Settings()
