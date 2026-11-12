"""add live ride tracking and active ride guards

Revision ID: g5b0d4e80001
Revises: f4a9c3d70001
"""

from alembic import op
import sqlalchemy as sa


revision = 'g5b0d4e80001'
down_revision = 'f4a9c3d70001'
branch_labels = None
depends_on = None

ACTIVE_STATUSES = "'requested','searching','driver_assigned','driver_arriving','driver_arrived','in_progress'"


def upgrade() -> None:
    with op.batch_alter_table('rides') as batch:
        batch.drop_constraint('ck_rides_status', type_='check')
        batch.create_check_constraint(
            'ck_rides_status',
            "status IN ('requested', 'searching', 'driver_assigned', 'driver_arriving', 'driver_arrived', 'in_progress', 'completed', 'cancelled')",
        )
        batch.add_column(sa.Column('cancelled_by', sa.String(length=20)))
        batch.add_column(sa.Column('route_geojson', sa.JSON()))
    with op.batch_alter_table('driver_current_locations') as batch:
        batch.add_column(sa.Column('accuracy_meters', sa.Numeric(7, 2)))
        batch.add_column(sa.Column('speed_mps', sa.Numeric(7, 2)))
    op.execute(sa.text(f"""
        WITH ranked AS (
            SELECT id, ROW_NUMBER() OVER (PARTITION BY passenger_id ORDER BY requested_at DESC, id DESC) AS position
            FROM rides WHERE status IN ({ACTIVE_STATUSES})
        )
        UPDATE rides SET status='cancelled', cancelled_at=CURRENT_TIMESTAMP,
            cancelled_by='system', cancellation_reason='duplicate_active_ride_migration'
        WHERE id IN (SELECT id FROM ranked WHERE position > 1)
    """))
    op.execute(sa.text(f"""
        WITH ranked AS (
            SELECT id, ROW_NUMBER() OVER (PARTITION BY driver_id ORDER BY requested_at DESC, id DESC) AS position
            FROM rides WHERE driver_id IS NOT NULL AND status IN ({ACTIVE_STATUSES})
        )
        UPDATE rides SET status='cancelled', cancelled_at=CURRENT_TIMESTAMP,
            cancelled_by='system', cancellation_reason='duplicate_driver_ride_migration'
        WHERE id IN (SELECT id FROM ranked WHERE position > 1)
    """))
    op.create_index(
        'uq_rides_one_active_passenger', 'rides', ['passenger_id'], unique=True,
        postgresql_where=sa.text(f'status IN ({ACTIVE_STATUSES})'),
        sqlite_where=sa.text(f'status IN ({ACTIVE_STATUSES})'),
    )
    op.create_index(
        'uq_rides_one_active_driver', 'rides', ['driver_id'], unique=True,
        postgresql_where=sa.text(f'driver_id IS NOT NULL AND status IN ({ACTIVE_STATUSES})'),
        sqlite_where=sa.text(f'driver_id IS NOT NULL AND status IN ({ACTIVE_STATUSES})'),
    )


def downgrade() -> None:
    op.drop_index('uq_rides_one_active_driver', table_name='rides')
    op.drop_index('uq_rides_one_active_passenger', table_name='rides')
    with op.batch_alter_table('driver_current_locations') as batch:
        batch.drop_column('speed_mps')
        batch.drop_column('accuracy_meters')
    with op.batch_alter_table('rides') as batch:
        batch.drop_column('route_geojson')
        batch.drop_column('cancelled_by')
        batch.drop_constraint('ck_rides_status', type_='check')
        batch.create_check_constraint(
            'ck_rides_status',
            "status IN ('requested', 'searching', 'driver_assigned', 'driver_arriving', 'in_progress', 'completed', 'cancelled')",
        )
