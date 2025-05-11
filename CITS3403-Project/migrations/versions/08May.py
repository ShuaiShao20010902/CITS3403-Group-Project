"""
Migration Script added on the 8th of May where I added a table to keep track of reading 
progress for each book of each user - Enat
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'reading_log',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('book_id', sa.Integer, nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('pages_read', sa.Integer, nullable=False),
        sa.UniqueConstraint('user_id', 'book_id', 'date', name='unique_user_book_date')
    )

    op.drop_column('user_books', 'read_percent')

def downgrade():
    op.add_column('user_books', sa.Column('read_percent', sa.Integer, default=0))
    op.drop_table('reading_log')
