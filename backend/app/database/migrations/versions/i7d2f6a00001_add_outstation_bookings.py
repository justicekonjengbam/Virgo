"""add outstation bookings

Revision ID: i7d2f6a00001
Revises: h6c1e5f90001
"""

from alembic import op
import sqlalchemy as sa

revision = 'i7d2f6a00001'
down_revision = 'h6c1e5f90001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    if 'outstation_bookings' in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        'outstation_bookings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('passenger_id', sa.Integer(), sa.ForeignKey('passengers.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('driver_id', sa.Integer(), sa.ForeignKey('drivers.id', ondelete='SET NULL')),
        sa.Column('vehicle_id', sa.Integer(), sa.ForeignKey('vehicles.id', ondelete='SET NULL')),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('pickup_address', sa.String(length=512), nullable=False),
        sa.Column('destination_address', sa.String(length=512), nullable=False),
        sa.Column('preferred_vehicle_type', sa.String(length=32)),
        sa.Column('status', sa.String(length=24), nullable=False, server_default='requested'),
        sa.Column('estimated_distance_km', sa.Numeric(8, 2)),
        sa.Column('estimated_fare_paise', sa.Integer()),
        sa.Column('support_note', sa.Text()),
        sa.Column('assigned_admin_id', sa.Integer(), sa.ForeignKey('admin_users.id', ondelete='SET NULL')),
        sa.Column('confirmed_at', sa.DateTime(timezone=True)),
        sa.Column('assigned_at', sa.DateTime(timezone=True)),
        sa.Column('cancelled_at', sa.DateTime(timezone=True)),
        sa.Column('cancellation_reason', sa.String(length=255)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('requested', 'confirmed', 'driver_assigned', 'completed', 'cancelled', 'rejected')", name='ck_outstation_booking_status'),
    )
    op.create_index('ix_outstation_passenger_scheduled', 'outstation_bookings', ['passenger_id', 'scheduled_at'])
    op.create_index('ix_outstation_driver_scheduled', 'outstation_bookings', ['driver_id', 'scheduled_at'])
    op.create_index('ix_outstation_status_scheduled', 'outstation_bookings', ['status', 'scheduled_at'])


def downgrade() -> None:
    op.drop_table('outstation_bookings')
