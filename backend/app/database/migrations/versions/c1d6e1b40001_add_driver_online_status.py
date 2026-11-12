"""add persisted driver online status

Revision ID: c1d6e1b40001
Revises: b7d9d0e0f001, 28bc77a50115
"""

from alembic import op
import sqlalchemy as sa


revision = "c1d6e1b40001"
down_revision = ("b7d9d0e0f001", "28bc77a50115")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("drivers", sa.Column("is_online", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("drivers", "is_online")
