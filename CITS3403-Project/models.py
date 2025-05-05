from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    books = db.relationship('UserBook', backref='user', cascade="all, delete-orphan")
    shared_items = db.relationship('SharedItem', backref='user', cascade="all, delete-orphan")



class SharedItem(db.Model):
    __tablename__ = 'shared_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    content_type = db.Column(db.String(50))
    content_data = db.Column(db.Text)
    created_at = db.Column(db.String(50))

class SharedWith(db.Model):
    __tablename__ = 'shared_with'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shared_item_id = db.Column(db.Integer, db.ForeignKey('shared_items.id'))
    receiver_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))


class UserBook(db.Model):
    __tablename__ = 'user_books'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    book_id = db.Column(db.Integer, primary_key=True)
    read_percent = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)

# Association table
book_authors = db.Table(
    'book_authors',
    db.Column('book_id',      db.Integer, db.ForeignKey('books.id'),   primary_key=True),
    db.Column('author_id',    db.Integer, db.ForeignKey('authors.id'), primary_key=True)
)

class Book(db.Model):
    __tablename__    = 'books'
    id               = db.Column(db.Integer, primary_key=True)
    work_key         = db.Column(db.String, index=True, nullable=False)
    edition_key      = db.Column(db.String, unique=True, nullable=False)
    title            = db.Column(db.String, nullable=False)
    description      = db.Column(db.Text)
    subjects         = db.Column(db.Text)    # JSON or CSV
    number_of_pages  = db.Column(db.Integer)
    isbn_10          = db.Column(db.String(20))
    isbn_13          = db.Column(db.String(20))
    publish_date     = db.Column(db.String(50))
    publishers       = db.Column(db.Text)
    cover_id         = db.Column(db.Integer)
    last_fetched     = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    authors          = db.relationship('Author', secondary=book_authors, back_populates='books')

    #@property
    #def cover_url(self):
        #return f"https://covers.openlibrary.org/b/id/{self.cover_id}-L.jpg" if self.cover_id else None

class Author(db.Model):
    __tablename__ = 'authors'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(200), unique=True, nullable=False)
    openlib_key   = db.Column(db.String, unique=True, nullable=True)  # e.g. "/authors/OL23919A"
    last_fetched  = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    books         = db.relationship('Book', secondary=book_authors, back_populates='authors')


def init_db(app):
    with app.app_context():
        db.create_all()
        # Initial data seeding can be added here if needed
