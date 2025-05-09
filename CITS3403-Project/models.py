from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, date, timedelta

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    books = db.relationship('UserBook', backref='user', cascade="all, delete-orphan")
    reading_logs = db.relationship('ReadingLog', backref='user', cascade="all, delete-orphan")
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
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    rating = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)

    book = db.relationship('Book', backref='user_books')


class ReadingLog(db.Model):
    __tablename__ = 'reading_log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    book_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    pages_read = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', 'date', name='unique_user_book_date'),
    )

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

class Author(db.Model):
    __tablename__ = 'authors'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(200), unique=True, nullable=False)
    openlib_key   = db.Column(db.String, unique=True, nullable=True)
    last_fetched  = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    books         = db.relationship('Book', secondary=book_authors, back_populates='authors')

def init_db(app):
    with app.app_context():
        db.create_all()

        # --- ensure sample user exists ---
        if not User.query.first():
            user = User(
                username='test',
                email='test@test',
                password=generate_password_hash('test')
            )
            db.session.add(user)
            db.session.commit()

        # --- insert 4 hard-coded books if none exist ---
        if not Book.query.first():
            sample_books = [
                {
                    "work_key": "/works/OL82563W",
                    "edition_key": "/books/OL82563W1M",
                    "title": "Harry Potter and the Sorcerer's Stone",
                    "description": "A young boy discovers he is a wizard and attends Hogwarts School.",
                    "subjects": "Fantasy, Magic, Adventure",
                    "number_of_pages": 309,
                    "isbn_10": "0439708184",
                    "isbn_13": "9780439708180",
                    "publish_date": "1997-06-26",
                    "publishers": "Bloomsbury",
                    "cover_id": 8231856
                },
                {
                    "work_key": "/works/OL45804W",
                    "edition_key": "/books/OL45804W1M",
                    "title": "Fantastic Mr. Fox",
                    "description": "Mr. Fox outsmarts three farmers to feed his family.",
                    "subjects": "Children's fiction, Foxes, Wit",
                    "number_of_pages": 96,
                    "isbn_10": "014241823X",
                    "isbn_13": "9780142418230",
                    "publish_date": "1970-10-17",
                    "publishers": "Puffin Books",
                    "cover_id": 6498519
                },
                {
                    "work_key": "/works/OL45819W",
                    "edition_key": "/books/OL45819W1M",
                    "title": "1984",
                    "description": "A dystopian novel set in a totalitarian society under Big Brother.",
                    "subjects": "Dystopia, Political fiction, Classic",
                    "number_of_pages": 328,
                    "isbn_10": "0451524934",
                    "isbn_13": "9780451524935",
                    "publish_date": "1949-06-08",
                    "publishers": "Secker & Warburg",
                    "cover_id": 7222246
                },
                {
                    "work_key": "/works/OL27448W",
                    "edition_key": "/books/OL27448W1M",
                    "title": "To Kill a Mockingbird",
                    "description": "A novel about racial injustice in the Deep South.",
                    "subjects": "Classic, Racism, Law",
                    "number_of_pages": 281,
                    "isbn_10": "0061120081",
                    "isbn_13": "9780061120084",
                    "publish_date": "1960-07-11",
                    "publishers": "J.B. Lippincott & Co.",
                    "cover_id": 9876543
                }
            ]

            books = []
            for data in sample_books:
                b = Book(
                    work_key=data["work_key"],
                    edition_key=data["edition_key"],
                    title=data["title"],
                    description=data["description"],
                    subjects=data["subjects"],
                    number_of_pages=data["number_of_pages"],
                    isbn_10=data["isbn_10"],
                    isbn_13=data["isbn_13"],
                    publish_date=data["publish_date"],
                    publishers=data["publishers"],
                    cover_id=data["cover_id"]
                )
                books.append(b)

            db.session.add_all(books)
            db.session.commit()

        # --- link each of those 4 books to user_id=1 ---
        if not UserBook.query.filter_by(user_id=1).first():
            all_books = Book.query.limit(4).all()
            user_books = [
                UserBook(user_id=1, book_id=b.id, completed=False)
                for b in all_books
            ]
            db.session.add_all(user_books)
            db.session.commit()

        # --- add ReadingLog entries for each book ---
        if not ReadingLog.query.filter_by(user_id=1).first():
            logs = []
            today = date.today()
            # For each of the first 4 books, add two days of progress
            for b in Book.query.limit(4).all():
                # Day 1: 20% of pages
                logs.append(ReadingLog(
                    user_id=1,
                    book_id=b.id,
                    date=today - timedelta(days=1),
                    pages_read=int(b.number_of_pages * 0.2)
                ))
                # Day 2: additional 30% of pages
                logs.append(ReadingLog(
                    user_id=1,
                    book_id=b.id,
                    date=today,
                    pages_read=int(b.number_of_pages * 0.3)
                ))
            db.session.add_all(logs)
            db.session.commit()