"""We decided that we longer want to use the editions endpoint and to store as little information as possibl, so I removed all the fields that would have gotten their data from that endpoint and also removed the authors table. -Enat

Revision ID: d7b55723e330
Revises:     aa2fa8a4b414
Create Date: 2025-05-11
"""
from alembic import op
import sqlalchemy as sa

revision     = "d7b55723e330"
down_revision = "aa2fa8a4b414"
branch_labels = None
depends_on    = None


def upgrade():
    op.drop_table("book_authors")
    op.drop_table("authors")

    with op.batch_alter_table("books") as batch_op:
        batch_op.add_column(sa.Column("work_id", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("author",  sa.String(length=200), nullable=True))

    op.execute("UPDATE books SET work_id = work_key")

    with op.batch_alter_table("books", recreate="always") as batch_op:
        batch_op.drop_index("ix_books_work_key")
        batch_op.drop_column("publish_date")
        batch_op.drop_column("edition_key")
        batch_op.drop_column("isbn_13")
        batch_op.drop_column("publishers")
        batch_op.drop_column("isbn_10")
        batch_op.drop_column("work_key")
        batch_op.drop_column("id")          

        batch_op.alter_column("work_id", nullable=False)
        batch_op.create_primary_key("pk_books", ["work_id"])

    with op.batch_alter_table("reading_log") as batch_op:
        batch_op.alter_column(
            "book_id",
            existing_type=sa.INTEGER(),
            type_=sa.String(),
            nullable=False,
        )
        batch_op.create_foreign_key(
            "fk_reading_log_book_id_books",
            "books",
            ["book_id"],
            ["work_id"],
        )


    with op.batch_alter_table("user_books") as batch_op:
        batch_op.drop_constraint(
            "fk_user_books_book_id_books", type_="foreignkey"
        )
        batch_op.alter_column(
            "book_id",
            existing_type=sa.INTEGER(),
            type_=sa.String(),
            nullable=False,
        )
        batch_op.create_foreign_key(
            "fk_user_books_book_id_books_workid",
            "books",
            ["book_id"],
            ["work_id"],
        )

def downgrade():
    with op.batch_alter_table("user_books") as batch_op:
        batch_op.drop_constraint(
            "fk_user_books_book_id_books_workid", type_="foreignkey"
        )
        batch_op.alter_column(
            "book_id",
            existing_type=sa.String(),
            type_=sa.INTEGER(),
            nullable=False,
        )
        batch_op.create_foreign_key(
            "fk_user_books_book_id_books", "books", ["book_id"], ["id"]
        )

    with op.batch_alter_table("reading_log") as batch_op:
        batch_op.drop_constraint(
            "fk_reading_log_book_id_books", type_="foreignkey"
        )
        batch_op.alter_column(
            "book_id",
            existing_type=sa.String(),
            type_=sa.INTEGER(),
            nullable=False,
        )

    with op.batch_alter_table("books", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("id", sa.Integer(), autoincrement=True))
        batch_op.add_column(sa.Column("work_key", sa.String(), nullable=False))
        batch_op.add_column(sa.Column("isbn_10", sa.String(20)))
        batch_op.add_column(sa.Column("isbn_13", sa.String(20)))
        batch_op.add_column(sa.Column("edition_key", sa.String(), nullable=False))
        batch_op.add_column(sa.Column("publishers", sa.Text()))
        batch_op.add_column(sa.Column("publish_date", sa.String(50)))
        batch_op.drop_column("author")
        batch_op.drop_column("work_id")
        batch_op.create_index("ix_books_work_key", ["work_key"])
        batch_op.create_primary_key("pk_books", ["id"])

    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False, unique=True),
        sa.Column("openlib_key", sa.String(), unique=True),
        sa.Column("last_fetched", sa.DateTime()),
    )
    op.create_table(
        "book_authors",
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"]),
        sa.ForeignKeyConstraint(["author_id"], ["authors.id"]),
        sa.PrimaryKeyConstraint("book_id", "author_id"),
    )