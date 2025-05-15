from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, date, timedelta
import secrets

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)

    books = db.relationship('UserBook', backref='user', cascade="all, delete-orphan")
    reading_logs = db.relationship('ReadingLog', backref='user', cascade="all, delete-orphan")
    shared_items = db.relationship('SharedItem', backref='user', cascade="all, delete-orphan")
def generate_reset_token(self):
    """Generate a secure reset token"""
    self.reset_token = secrets.token_urlsafe(32)
    self.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
    return self.reset_token

def verify_reset_token(self, token):
    """Check if token is valid and not expired"""
    return (self.reset_token == token and
            self.reset_token_expiration and
            self.reset_token_expiration > datetime.utcnow())

class SharedItem(db.Model):
    __tablename__ = 'shared_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    content_type = db.Column(db.String(50))
    content_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SharedWith(db.Model):
    __tablename__ = 'shared_with'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shared_item_id = db.Column(db.Integer, db.ForeignKey('shared_items.id'))
    receiver_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

class UserBook(db.Model):
    __tablename__ = 'user_books'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    book_id = db.Column(db.String, db.ForeignKey('books.work_id'), primary_key=True)
    number_of_pages = db.Column(db.Integer)
    rating = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)

    book = db.relationship('Book', backref='user_books')

class ReadingLog(db.Model):
    __tablename__ = 'reading_log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    book_id = db.Column(db.String, db.ForeignKey('books.work_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    pages_read = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', 'date', name='unique_user_book_date'),
    )

class Book(db.Model):
    __tablename__ = 'books'
    work_id = db.Column(db.String, primary_key=True, nullable=False, unique=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    subjects = db.Column(db.Text)
    cover_id = db.Column(db.Integer)
    last_fetched = db.Column(db.DateTime, default=datetime.now(timezone.utc))

def init_db(app):
    with app.app_context():
        db.create_all()