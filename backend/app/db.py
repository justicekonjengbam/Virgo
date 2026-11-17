from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings, normalize_database_url

settings = get_settings()
database_url = normalize_database_url(settings.database_url)
engine = create_engine(
    database_url,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_database() -> None:
    """Apply versioned migrations locally; production deployments run them explicitly."""
    if settings.environment.lower() == 'production' and settings.auto_migrate:
        raise RuntimeError('Set AUTO_MIGRATE=false in production and apply Alembic migrations separately.')
    if not settings.auto_migrate:
        return
    backend_root = Path(__file__).resolve().parent.parent
    alembic_config = Config(str(backend_root / 'alembic.ini'))
    alembic_config.set_main_option('script_location', str(backend_root / 'app' / 'database' / 'migrations'))
    alembic_config.set_main_option('sqlalchemy.url', database_url.replace('%', '%%'))
    command.upgrade(alembic_config, 'head')
