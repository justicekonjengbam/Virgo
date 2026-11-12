"""add driver document metadata

Revision ID: l0e5c9d30001
Revises: k9f4b8c20001
"""

from alembic import op
import sqlalchemy as sa

revision = 'l0e5c9d30001'
down_revision = 'k9f4b8c20001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    columns = {column['name'] for column in sa.inspect(op.get_bind()).get_columns('driver_documents')}
    additions = {
        'rejection_reason': sa.Column('rejection_reason', sa.Text(), nullable=True),
        'original_filename': sa.Column('original_filename', sa.String(length=255), nullable=True),
        'mime_type': sa.Column('mime_type', sa.String(length=100), nullable=True),
        'file_size_bytes': sa.Column('file_size_bytes', sa.Integer(), nullable=True),
    }
    for name, column in additions.items():
        if name not in columns:
            op.add_column('driver_documents', column)


def downgrade() -> None:
    for name in ('file_size_bytes', 'mime_type', 'original_filename', 'rejection_reason'):
        op.drop_column('driver_documents', name)

