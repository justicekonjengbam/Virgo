from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get('/health', response_model=HealthResponse)
@router.get('/api/v1/health', response_model=HealthResponse)
async def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status='OK',
        version='1.0',
        environment=settings.environment,
    )
