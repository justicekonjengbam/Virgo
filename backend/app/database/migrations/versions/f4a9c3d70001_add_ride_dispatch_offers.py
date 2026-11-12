"""add durable ride dispatch offers

Revision ID: f4a9c3d70001
Revises: e3f8a2b60001
"""

from alembic import op
import sqlalchemy as sa


revision = 'f4a9c3d70001'
down_revision = 'e3f8a2b60001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ride_dispatch_offers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('ride_id', sa.Integer(), sa.ForeignKey('rides.id', ondelete='CASCADE'), nullable=False),
        sa.Column('driver_id', sa.Integer(), sa.ForeignKey('drivers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('offered_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('responded_at', sa.DateTime(timezone=True)),
        sa.UniqueConstraint('ride_id', 'driver_id', name='uq_ride_dispatch_offer_driver'),
    )
    op.create_index('ix_ride_dispatch_offers_driver_status_expires', 'ride_dispatch_offers', ['driver_id', 'status', 'expires_at'])


def downgrade() -> None:
    op.drop_index('ix_ride_dispatch_offers_driver_status_expires', table_name='ride_dispatch_offers')
    op.drop_table('ride_dispatch_offers')
