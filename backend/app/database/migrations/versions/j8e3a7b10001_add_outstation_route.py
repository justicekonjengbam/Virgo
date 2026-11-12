"""add outstation route details

Revision ID: j8e3a7b10001
Revises: i7d2f6a00001
"""

from alembic import op
import sqlalchemy as sa

revision = 'j8e3a7b10001'
down_revision = 'i7d2f6a00001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    columns = {column['name'] for column in sa.inspect(op.get_bind()).get_columns('outstation_bookings')}
    additions = {
        'pickup_place_id': sa.Column('pickup_place_id', sa.String(length=255)),
        'pickup_latitude': sa.Column('pickup_latitude', sa.Numeric(9, 6)),
        'pickup_longitude': sa.Column('pickup_longitude', sa.Numeric(9, 6)),
        'destination_place_id': sa.Column('destination_place_id', sa.String(length=255)),
        'destination_latitude': sa.Column('destination_latitude', sa.Numeric(9, 6)),
        'destination_longitude': sa.Column('destination_longitude', sa.Numeric(9, 6)),
        'route_geojson': sa.Column('route_geojson', sa.JSON()),
    }
    for name, column in additions.items():
        if name not in columns:
            op.add_column('outstation_bookings', column)


def downgrade() -> None:
    for name in ('route_geojson', 'destination_longitude', 'destination_latitude', 'destination_place_id', 'pickup_longitude', 'pickup_latitude', 'pickup_place_id'):
        op.drop_column('outstation_bookings', name)
