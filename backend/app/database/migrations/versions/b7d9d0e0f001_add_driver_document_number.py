"""add driver document number"""
from alembic import op
import sqlalchemy as sa

revision = "b7d9d0e0f001"
down_revision = "841c1f195299"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("driver_documents", sa.Column("document_number", sa.String(length=128), nullable=False, server_default=""))

def downgrade() -> None:
    op.drop_column("driver_documents", "document_number")
