"""
Changed the created_at field from STRING to DATETIME.

Revision ID: e2c4f6b1a7c0
Revises:      d7b55723e330
Create Date:  2025-05-13
"""
from alembic import op
import sqlalchemy as sa

revision      = "e2c4f6b1a7c0"
down_revision = "d7b55723e330"
branch_labels = None
depends_on    = None



def upgrade():
    with op.batch_alter_table("shared_items", recreate="always") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.String(length=50),
            type_=sa.DateTime(),
            server_default=sa.func.now(),
            existing_nullable=True,
        )

def downgrade():
    with op.batch_alter_table("shared_items", recreate="always") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            type_=sa.String(length=50),
            server_default=None,
            existing_nullable=True,
        )