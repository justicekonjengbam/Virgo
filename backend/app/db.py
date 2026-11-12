from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()
engine = create_engine(
    settings.database_url,
    connect_args={'check_same_thread': False} if settings.database_url.startswith('sqlite') else {},
    pool_pre_ping=not settings.database_url.startswith('sqlite'),
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
    """Apply versioned migrations locally; production deployments run the same command explicitly."""
    if not settings.auto_migrate:
        return
    backend_root = Path(__file__).resolve().parent.parent
    alembic_config = Config(str(backend_root / 'alembic.ini'))
    alembic_config.set_main_option('script_location', str(backend_root / 'app' / 'database' / 'migrations'))
    command.upgrade(alembic_config, 'head')
