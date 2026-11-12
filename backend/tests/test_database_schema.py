from sqlalchemy import create_engine, inspect

from app.db import Base
import app.models  # noqa: F401


def test_core_ride_hailing_schema_is_connected() -> None:
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    tables = set(inspect(engine).get_table_names())

    assert {'passengers', 'passenger_profiles', 'drivers', 'vehicles', 'rides', 'fare_quotes', 'payments', 'device_sessions', 'audit_logs', 'outbox_events'} <= tables
