from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime
import requests
import random
from werkzeug.security import generate_password_hash, check_password_hash

#region Security Risk
# I am aware this is bad practice but this will be a problem for the future - Enat
app = Flask(__name__)
DB_FILE = 'books.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this-is-the-super-secret-key')

#region Database setup
def init_db():
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

#region Routes for Pages
@app.route('/')
def landing():
    if 'user_id' in session:
        return redirect(url_for('home'))  # Redirect logged-in users to the home
    return render_template('landing.html')  # Show landing page if not logged in

@app.route('/home.html')
def home():
    username = session.get('username')   # will be None if not logged in
    return render_template('home.html', username=username)

@app.route('/share', methods=['GET', 'POST'])
def share():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    current_user_id = session['user_id']

    if request.method == 'POST':
        data = request.get_json()
        recipient_username = data['username']

        c.execute('SELECT user_id FROM users WHERE username = ?', (recipient_username,))
        receiver = c.fetchone()
        if not receiver:
            conn.close()
            return jsonify({'status': 'error', 'message': 'User not found'})

        receiver_user_id = receiver[0]

        # Fetch user's shared items
        c.execute('SELECT id FROM shared_items WHERE user_id = ?', (current_user_id,))
        items = c.fetchall()

        for (item_id,) in items:
            # Check if already shared to prevent duplicates
            c.execute('''
                SELECT 1 FROM shared_with 
                WHERE shared_item_id = ? AND receiver_user_id = ?
            ''', (item_id, receiver_user_id))
            if not c.fetchone():
                c.execute('''
                    INSERT INTO shared_with (shared_item_id, receiver_user_id)
                    VALUES (?, ?)
                ''', (item_id, receiver_user_id))

        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Shared successfully!'})

    # GET method - render page
    c.execute('''
        SELECT id, content_type, content_data, created_at FROM shared_items
        WHERE user_id = ?
    ''', (current_user_id,))
    your_shared_items = [dict(zip(['id', 'content_type', 'content_data', 'created_at'], row)) for row in c.fetchall()]

    c.execute('''
        SELECT si.content_type, si.content_data, si.created_at, u.username
        FROM shared_items si
        JOIN shared_with sw ON si.id = sw.shared_item_id
        JOIN users u ON si.user_id = u.user_id
        WHERE sw.receiver_user_id = ?
    ''', (current_user_id,))
    shared_to_user = [
        {'content_type': row[0], 'content_data': row[1], 'created_at': row[2], 'sharer_username': row[3]}
        for row in c.fetchall()
    ]

    conn.close()
    
    return render_template('share.html', your_shared_items=your_shared_items, shared_to_user=shared_to_user)

@app.route('/uploadbook.html')
def public_uploadbook():
    return render_template('uploadbook.html')

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        password = request.form['password']

        hashed = generate_password_hash(password)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Check for existing username
        cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            flash('Username already in use', 'error')
            return redirect(url_for('signup'))

        # Check for existing email
        cursor.execute('SELECT 1 FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            flash('Email already in use', 'error')
            return redirect(url_for('signup'))

        # If we reach here, both are unique—insert new user
        try:
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, hashed)
            )
            conn.commit()
        finally:
            conn.close()

        flash('Account created successfully', 'success')
        return redirect(url_for('home'))

    # GET
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email'].strip()
        password = request.form['password']

        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cur.fetchone()
        conn.close()

        # validate & redirect on error
        if not email:
            flash('Email is required', 'error')
            return redirect(url_for('login'))
        if not password:
            flash('Password is required', 'error')
            return redirect(url_for('login'))
        if user is None:
            flash('No account with that email', 'error')
            return redirect(url_for('login'))
        if not check_password_hash(user['password'], password):
            flash('Password does not match', 'error')
            return redirect(url_for('login'))

        # success
        session.clear()
        session['user_id'] = user['user_id']
        session['username']  = user['username']
        flash('Logged in successfully', 'success')
        return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  
    return redirect(url_for('landing'))  

@app.route('/test.html')
def test():
    return render_template('test.html')

#region Routes for API
#@app.route('/api/user_books')
#def api_user_books():
    user_id = request.args.get('user_id', 1)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT ub.book_id, b.title, ub.read_percent
        FROM user_books ub
        JOIN books b ON ub.book_id = b.book_id
        WHERE ub.user_id = ?
    ''', (user_id,))
    books = [{"book_id": row[0], "title": row[1], "read_percent": row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify(books)

@app.route('/api/books')
def api_books():
    # 1. Fetch a pool of works via Open Library’s search API
    resp = requests.get(
        'https://openlibrary.org/search.json',
        params={'q': 'the', 'limit': 100}  # a broad query to get a sizeable pool
    )
    data = resp.json().get('docs', [])

    # 2. 10 books from the api
    sample = random.sample(data, min(10, len(data)))

    # 3. Shape each work into only the fields we need
    books = []
    for w in sample:
        ol_key = w.get('key', '')             # e.g. "/works/OL82563W"
        cover_id = w.get('cover_i')           # numeric cover ID
        books.append({
            "id": ol_key.split('/')[-1],      # "OL82563W"
            "title": w.get('title'),
            "authors": w.get('author_name', []),
            "year": w.get('first_publish_year'),
            "cover_url": cover_id and f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg",
            "subjects": w.get('subject', [])[:5]   # top 5 subjects
        })

    return jsonify(books)

@app.route('/api/user_chat')
def api_user_chat():
    user_id = int(request.args.get('user_id', 1))
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    query = '''
        SELECT u1.username AS sender_name, u2.username AS receiver_name, uc.datestamp, uc.message
        FROM user_chat uc
        JOIN users u1 ON uc.sender = u1.user_id
        JOIN users u2 ON uc.receiver = u2.user_id
        WHERE uc.receiver = ?
        ORDER BY uc.datestamp ASC
    '''
    c.execute(query, (user_id,))
    messages = [
        {
            "sender": row[0],
            "receiver": row[1],
            "datestamp": row[2],
            "message": row[3]
        } for row in c.fetchall()
    ]
    conn.close()
    return jsonify(messages)

# Removed for now, I will do the statistics later - enat
#@app.route('/api/user_books_by_genre')
#def user_books_by_genre():
    
@app.route('/book/<int:book_id>')
def book_specific_page(book_id):
    # Random data for testing
    book = {
        'title': 'Test Book',
        'author': 'Author Name',
        'pages': 300,
        'isbn': '1234567890',
        'year': 2020,
        'description': 'One Ring to rule them all, One Ring to find them, One Ring to bring them all and in the darkness bind them. In ancient times the Rings of Power were crafted by the Elven-smiths, and Sauron, the Dark Lord, forged the One Ring, filling it with his own power so that he could rule all others. But the One Ring was taken from him, and though he sought it throughout Middle-earth, it remained lost to him. After many ages it fell into the hands of Bilbo Baggins, as told in The Hobbit.',
        'cover_url': 'https://covers.openlibrary.org/b/id/255844-M.jpg',
        'genres': ['Fantasy', 'Adventure']
        
    }
    user_data = {
        'rating': 4.5,
        'page_read': 150,
        'notes': 'I love this'
    }

    community_notes = [
        {
            'username': 'user1',
            'note': 'I love this book!',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'username': 'user2',
            'note': 'It was okay, got bored at the middle section.',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    return render_template('bookspecificpage.html', book=book, user_data=user_data, book_id = book_id, community_notes=community_notes)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
