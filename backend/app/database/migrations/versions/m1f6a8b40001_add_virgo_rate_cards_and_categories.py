"""add virgo rate cards and categories

Revision ID: m1f6a8b40001
Revises: l0e5c9d30001
"""

from alembic import op
import sqlalchemy as sa

revision = 'm1f6a8b40001'
down_revision = 'l0e5c9d30001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if 'rate_cards' not in tables:
        op.create_table(
            'rate_cards',
            sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
            sa.Column('category_code', sa.String(length=32), nullable=False),
            sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column('base_fare_paise', sa.Integer(), nullable=False),
            sa.Column('first_tier_km', sa.Float(), nullable=False, server_default='6.0'),
            sa.Column('first_tier_rate_paise', sa.Integer(), nullable=False),
            sa.Column('second_tier_rate_paise', sa.Integer(), nullable=False),
            sa.Column('waiting_charge_per_minute_paise', sa.Integer(), nullable=False, server_default='200'),
            sa.Column('waiting_grace_period_minutes', sa.Integer(), nullable=False, server_default='3'),
            sa.Column('surcharge_distance_threshold_km', sa.Float(), nullable=False, server_default='12.0'),
            sa.Column('surcharge_percentage', sa.Float(), nullable=False, server_default='0.15'),
            sa.Column('cancellation_fee_paise', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('gst_rate', sa.Float(), nullable=False, server_default='0.05'),
            sa.Column('commission_rate', sa.Float(), nullable=False, server_default='0.10'),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index('ix_rate_cards_category_version', 'rate_cards', ['category_code', 'version'])

    # Add columns to rides
    rides_cols = {col['name'] for col in inspector.get_columns('rides')}
    rides_additions = {
        'arrived_at': sa.Column('arrived_at', sa.DateTime(timezone=True), nullable=True),
        'rate_card_version': sa.Column('rate_card_version', sa.Integer(), nullable=True),
        'actual_waiting_minutes': sa.Column('actual_waiting_minutes', sa.Float(), nullable=True),
    }
    for col_name, col in rides_additions.items():
        if col_name not in rides_cols:
            op.add_column('rides', col)

    # Add columns to fare_quotes
    fare_quotes_cols = {col['name'] for col in inspector.get_columns('fare_quotes')}
    fare_quotes_additions = {
        'rate_card_version': sa.Column('rate_card_version', sa.Integer(), nullable=True),
        'base_fare_paise': sa.Column('base_fare_paise', sa.Integer(), nullable=True),
        'distance_fare_paise': sa.Column('distance_fare_paise', sa.Integer(), nullable=True),
        'waiting_charge_paise': sa.Column('waiting_charge_paise', sa.Integer(), nullable=True),
        'surcharge_paise': sa.Column('surcharge_paise', sa.Integer(), nullable=True),
        'subtotal_paise': sa.Column('subtotal_paise', sa.Integer(), nullable=True),
        'discount_paise': sa.Column('discount_paise', sa.Integer(), nullable=True),
        'gst_paise': sa.Column('gst_paise', sa.Integer(), nullable=True),
        'commission_paise': sa.Column('commission_paise', sa.Integer(), nullable=True),
        'driver_net_paise': sa.Column('driver_net_paise', sa.Integer(), nullable=True),
    }
    for col_name, col in fare_quotes_additions.items():
        if col_name not in fare_quotes_cols:
            op.add_column('fare_quotes', col)


def downgrade() -> None:
    for name in (
        'driver_net_paise',
        'commission_paise',
        'gst_paise',
        'discount_paise',
        'subtotal_paise',
        'surcharge_paise',
        'waiting_charge_paise',
        'distance_fare_paise',
        'base_fare_paise',
        'rate_card_version',
    ):
        op.drop_column('fare_quotes', name)

    for name in ('actual_waiting_minutes', 'rate_card_version', 'arrived_at'):
        op.drop_column('rides', name)

    op.drop_index('ix_rate_cards_category_version', table_name='rate_cards')
    op.drop_table('rate_cards')

