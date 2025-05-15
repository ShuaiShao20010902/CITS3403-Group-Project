"""This one addes a few fields to the users table for password reset functionality. 
Also currently the latest one.

Revision ID: 07b460742caf
Revises: e2c4f6b1a7c0
Create Date: 2025-05-15 11:15:08.034236

"""
from alembic import op
import sqlalchemy as sa

revision = '07b460742caf'
down_revision = 'e2c4f6b1a7c0'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reset_token', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('reset_token_expiration', sa.DateTime(), nullable=True))
        batch_op.create_unique_constraint(None, ['reset_token'])

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('reset_token_expiration')
        batch_op.drop_column('reset_token')

