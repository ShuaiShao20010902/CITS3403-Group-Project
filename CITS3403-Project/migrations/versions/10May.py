"""
After some dicussion with Melissa, we decided not to use the editions endpoint and so all data that 
was recieved from it is now gone. 
Furthermore i decided to remove the Authors table to make things
simpler as the main goal of the website is now to just track book progress so we will only store the 
author's name and thats it. 
Also i change the books table to use the work_id as PK instead of having another id field
And i also renamed a few fields - Enat
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    # association  and authors table
    op.drop_table('book_authors')
    op.drop_table('authors')

    # related to the books table
    op.drop_column('books', 'edition_key')
    op.drop_column('books', 'isbn_10')
    op.drop_column('books', 'isbn_13')
    op.drop_column('books', 'publish_date')
    op.drop_column('books', 'publishers')
    op.drop_column('books', 'id')
    op.add_column('books', sa.Column('author', sa.String(length=200), nullable=False))
    op.add_column('books', sa.Column('work_id', sa.String(), primary_key=True, nullable=False, unique=True))

def downgrade():
    op.drop_column('books', 'author')
    op.drop_column('books', 'work_id')

    op.create_table(
        'authors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('openlib_key', sa.String(), nullable=True),
        sa.Column('last_fetched', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('openlib_key')
    )

    op.create_table(
        'book_authors',
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['authors.id']),
        sa.ForeignKeyConstraint(['book_id'], ['books.id']),
        sa.PrimaryKeyConstraint('book_id', 'author_id')
    )

    op.add_column('books', sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True))
    op.add_column('books', sa.Column('edition_key', sa.String(), nullable=False))
    op.add_column('books', sa.Column('isbn_10', sa.String(length=20), nullable=True))
    op.add_column('books', sa.Column('isbn_13', sa.String(length=20), nullable=True))
    op.add_column('books', sa.Column('publish_date', sa.String(length=50), nullable=True))
    op.add_column('books', sa.Column('publishers', sa.Text(), nullable=True))