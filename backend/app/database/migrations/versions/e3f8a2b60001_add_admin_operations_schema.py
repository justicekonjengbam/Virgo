"""add admin operations schema

Revision ID: e3f8a2b60001
Revises: d2f7e1a50001
"""

from alembic import op
import sqlalchemy as sa


revision = 'e3f8a2b60001'
down_revision = 'd2f7e1a50001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Local auto-migration can be triggered by two development reload processes.
    # Keep this migration safe to retry if one process completed only part of it.
    inspector = sa.inspect(op.get_bind())
    if 'admin_users' not in inspector.get_table_names():
        op.create_table(
            'admin_users',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('email', sa.String(length=320), nullable=False, unique=True),
            sa.Column('full_name', sa.String(length=120), nullable=False),
            sa.Column('password_hash', sa.String(length=255), nullable=False),
            sa.Column('role', sa.String(length=32), nullable=False, server_default='operations_admin'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column('last_login_at', sa.DateTime(timezone=True)),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        )
    inspector = sa.inspect(op.get_bind())
    if 'ix_admin_users_email' not in {item['name'] for item in inspector.get_indexes('admin_users')}:
        op.create_index('ix_admin_users_email', 'admin_users', ['email'])
    support_columns = {column['name'] for column in inspector.get_columns('support_tickets')}
    with op.batch_alter_table('support_tickets') as batch_op:
        if 'assigned_admin_id' not in support_columns:
            batch_op.add_column(sa.Column('assigned_admin_id', sa.Integer(), sa.ForeignKey('admin_users.id', ondelete='SET NULL')))
        if 'resolution_note' not in support_columns:
            batch_op.add_column(sa.Column('resolution_note', sa.Text()))
        if 'resolved_at' not in support_columns:
            batch_op.add_column(sa.Column('resolved_at', sa.DateTime(timezone=True)))


def downgrade() -> None:
    with op.batch_alter_table('support_tickets') as batch_op:
        batch_op.drop_column('resolved_at')
        batch_op.drop_column('resolution_note')
        batch_op.drop_column('assigned_admin_id')
    op.drop_index('ix_admin_users_email', table_name='admin_users')
    op.drop_table('admin_users')
