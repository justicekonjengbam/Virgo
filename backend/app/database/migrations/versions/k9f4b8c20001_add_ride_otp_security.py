"""add ride otp security

Revision ID: k9f4b8c20001
Revises: j8e3a7b10001
"""

from alembic import op
import sqlalchemy as sa

revision = 'k9f4b8c20001'
down_revision = 'j8e3a7b10001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    columns = {column['name'] for column in sa.inspect(op.get_bind()).get_columns('rides')}
    additions = {
        'start_otp_hash': sa.Column('start_otp_hash', sa.String(length=255), nullable=True),
        'otp_salt': sa.Column('otp_salt', sa.String(length=64), nullable=True),
        'otp_attempts': sa.Column('otp_attempts', sa.Integer(), nullable=False, server_default='0'),
    }
    for name, column in additions.items():
        if name not in columns:
            op.add_column('rides', column)


def downgrade() -> None:
    for name in ('otp_attempts', 'otp_salt', 'start_otp_hash'):
        op.drop_column('rides', name)

