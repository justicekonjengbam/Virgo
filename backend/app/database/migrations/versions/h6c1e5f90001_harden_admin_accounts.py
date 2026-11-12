"""harden admin accounts

Revision ID: h6c1e5f90001
Revises: g5b0d4e80001
"""

from alembic import op
import sqlalchemy as sa

revision = 'h6c1e5f90001'
down_revision = 'g5b0d4e80001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column['name'] for column in inspector.get_columns('admin_users')}
    if 'token_version' not in columns:
        op.add_column('admin_users', sa.Column('token_version', sa.Integer(), nullable=False, server_default='1'))
    if 'failed_login_attempts' not in columns:
        op.add_column('admin_users', sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'))
    if 'locked_until' not in columns:
        op.add_column('admin_users', sa.Column('locked_until', sa.DateTime(timezone=True)))
    if 'password_changed_at' not in columns:
        op.add_column('admin_users', sa.Column('password_changed_at', sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_column('admin_users', 'password_changed_at')
    op.drop_column('admin_users', 'locked_until')
    op.drop_column('admin_users', 'failed_login_attempts')
    op.drop_column('admin_users', 'token_version')
