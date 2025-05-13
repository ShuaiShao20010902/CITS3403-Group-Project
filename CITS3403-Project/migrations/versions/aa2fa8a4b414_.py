"""Removes the read_percent column and relaces it with the Reading Log table
Do keep in mind that initially the database schema used SQLlite so after that was changed to SQLAlchemy this is the first migration script. 
Also the Alembic comments were pretty ugly so I removed them lol. 

Revision ID: aa2fa8a4b414
Revises: 
Create Date: 2025-05-08 

"""
from alembic import op
import sqlalchemy as sa

revision = "aa2fa8a4b414"
down_revision = None         
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "reading_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("pages_read", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            name="fk_reading_log_user_id_users",
        ),
        sa.UniqueConstraint(
            "user_id",
            "book_id",
            "date",
            name="unique_user_book_date",
        ),
    )

    with op.batch_alter_table("user_books") as batch_op:
        batch_op.drop_column("read_percent")
        batch_op.create_foreign_key(
            "fk_user_books_book_id_books", 
            "books",                      
            ["book_id"],                 
            ["id"],                       
        )

def downgrade():
    with op.batch_alter_table("user_books") as batch_op:
        batch_op.drop_constraint(
            "fk_user_books_book_id_books", type_="foreignkey"
        )
        batch_op.add_column(
            sa.Column(
                "read_percent",
                sa.Integer(),
                nullable=True,
                server_default="0",
            )
        )

    op.drop_table("reading_log")
