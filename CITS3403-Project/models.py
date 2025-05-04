import sqlite3
from werkzeug.security import generate_password_hash

# Database file
DB_FILE = 'books.db'

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database, create tables and add sample data"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create users table
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Create user_books table
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS user_books (
            user_id INTEGER,
            book_id INTEGER,
            read_percent INTEGER DEFAULT 0,
            rating REAL DEFAULT FALSE,
            notes TEXT,
            completed BOOLEAN DEFAULT 0,
            PRIMARY KEY (user_id, book_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')

    # Create user_chat table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender INTEGER,
            receiver INTEGER,
            datestamp TEXT,
            message TEXT,
            FOREIGN KEY (sender) REFERENCES users(user_id),
            FOREIGN KEY (receiver) REFERENCES users(user_id)
        )
    ''')

    # Add sample messages if none exist
    c.execute("SELECT COUNT(*) FROM user_chat")
    if c.fetchone()[0] == 0:
        sample_msgs = [
            (2, 1, "2025-04-18 10:00", "Hey John, how are you?"),
            (2, 1, "2025-04-18 10:05", "Check out this new book."),
            (1, 2, "2025-04-18 10:10", "Thanks Jane, will do!")
        ]
        c.executemany('''
            INSERT INTO user_chat (sender, receiver, datestamp, message)
            VALUES (?, ?, ?, ?)
        ''', sample_msgs)

    # Check if there are any users in the users table before inserting
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.executemany(''' 
            INSERT INTO users (username, password, email) VALUES (?, ?, ?)
        ''', [
            ('john_doe', 'password123', 'johndoe@gmail.com'),
            ('jane_doe', 'password456', 'janedoe@outlook.com')
        ])

    # Table for items a user chooses to share
    c.execute('''
        CREATE TABLE IF NOT EXISTS shared_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content_type TEXT,
            content_data TEXT,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    # Table to track which users receive shared items
    c.execute('''
        CREATE TABLE IF NOT EXISTS shared_with (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shared_item_id INTEGER,
            receiver_user_id INTEGER,
            FOREIGN KEY (shared_item_id) REFERENCES shared_items(id),
            FOREIGN KEY (receiver_user_id) REFERENCES users(user_id)
        )
    ''')

    conn.commit()
    conn.close()

    #models updated as per SQLAlchemy

    from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    books = db.relationship('UserBook', backref='user', cascade="all, delete-orphan")
    sent_messages = db.relationship('UserChat', foreign_keys='UserChat.sender', backref='sender_user', cascade="all, delete-orphan")
    received_messages = db.relationship('UserChat', foreign_keys='UserChat.receiver', backref='receiver_user', cascade="all, delete-orphan")
    shared_items = db.relationship('SharedItem', backref='user', cascade="all, delete-orphan")


class UserBook(db.Model):
    __tablename__ = 'user_books'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    book_id = db.Column(db.Integer, primary_key=True)
    read_percent = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)


class UserChat(db.Model):
    __tablename__ = 'user_chat'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    receiver = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    datestamp = db.Column(db.String(50))
    message = db.Column(db.Text)


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


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

        # Add sample data if tables are empty
        if not User.query.first():
            user1 = User(username='john_doe', email='johndoe@gmail.com', password=generate_password_hash('password123'))
            user2 = User(username='jane_doe', email='janedoe@outlook.com', password=generate_password_hash('password456'))
            db.session.add_all([user1, user2])
            db.session.commit()

        if not UserChat.query.first():
            sample_msgs = [
                UserChat(sender=2, receiver=1, datestamp="2025-04-18 10:00", message="Hey John, how are you?"),
                UserChat(sender=2, receiver=1, datestamp="2025-04-18 10:05", message="Check out this new book."),
                UserChat(sender=1, receiver=2, datestamp="2025-04-18 10:10", message="Thanks Jane, will do!")
            ]
            db.session.add_all(sample_msgs)
            db.session.commit()