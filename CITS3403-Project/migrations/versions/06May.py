"""Migration Script addded on the 6th of May where I added two new tables to the database - Enat"""
from alembic import op
import sqlalchemy as sa

revision = '06May'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'authors',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False, unique=True),
        sa.Column('openlib_key', sa.String(), nullable=True, unique=True),
        sa.Column('last_fetched', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )

    op.create_table(
        'books',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('work_key', sa.String(), nullable=False, index=True),
        sa.Column('edition_key', sa.String(), nullable=False, unique=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('subjects', sa.Text(), nullable=True),
        sa.Column('number_of_pages', sa.Integer(), nullable=True),
        sa.Column('isbn_10', sa.String(length=20), nullable=True),
        sa.Column('isbn_13', sa.String(length=20), nullable=True),
        sa.Column('publish_date', sa.String(length=50), nullable=True),
        sa.Column('publishers', sa.Text(), nullable=True),
        sa.Column('cover_id', sa.Integer(), nullable=True),
        sa.Column('last_fetched', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )

    op.create_table(
        'book_authors',
        sa.Column('book_id', sa.Integer(), sa.ForeignKey('books.id'), primary_key=True),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('authors.id'), primary_key=True)
    )


def downgrade():
    op.drop_table('book_authors')
    op.drop_table('books')
    op.drop_table('authors')
