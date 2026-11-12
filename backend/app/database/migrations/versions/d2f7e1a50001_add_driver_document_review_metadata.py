"""add driver document review metadata

Revision ID: d2f7e1a50001
Revises: c1d6e1b40001
"""

from alembic import op
import sqlalchemy as sa


revision = 'd2f7e1a50001'
down_revision = 'c1d6e1b40001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('driver_documents', sa.Column('review_note', sa.Text(), nullable=True))
    op.add_column('driver_documents', sa.Column('reviewed_by', sa.String(length=128), nullable=True))
    op.add_column('driver_documents', sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('driver_documents', 'reviewed_at')
    op.drop_column('driver_documents', 'reviewed_by')
    op.drop_column('driver_documents', 'review_note')
