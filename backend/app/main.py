from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

import app.models  # noqa: F401
from app.api.v1.router import api_router
from app.api.v1.routes.health import router as health_router
from app.core.config import get_settings
from app.db import SessionLocal, initialize_database
from app.services.admin_auth_service import AdminAuthService
from app.services.realtime_service import realtime_hub


@asynccontextmanager
async def lifespan(_: FastAPI):
    realtime_hub.bind_running_loop()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    initialize_database()
    db = SessionLocal()
    try:
        AdminAuthService().bootstrap(db)
    finally:
        db.close()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    # Cross-Origin Resource Sharing (CORS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Security Headers Middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(self), camera=(), microphone=()"
        return response

    app.include_router(health_router, tags=["health"])
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    admin_app_directory = Path(__file__).resolve().parents[2] / "admin-app"
    if admin_app_directory.is_dir():
        app.mount("/admin", StaticFiles(directory=admin_app_directory, html=True), name="admin-app")
    return app


app = create_app()
