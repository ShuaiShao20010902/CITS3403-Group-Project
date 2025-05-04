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