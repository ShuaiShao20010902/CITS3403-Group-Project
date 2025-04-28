from flask import Flask, jsonify, render_template, request
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_FILE = 'books.db'

# Initialize the database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create users table
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Create books table
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            synopsis TEXT,
            cover_url TEXT
        )
    ''')

    # Create user_books table
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS user_books (
            user_id INTEGER,
            book_id INTEGER,
            read_percent INTEGER DEFAULT 0,
            notes TEXT,
            PRIMARY KEY (user_id, book_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
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
            INSERT INTO users (username, password) VALUES (?, ?)
        ''', [
            ('john_doe', 'password123'),
            ('jane_doe', 'password456')
        ])

    # Check if there are any books in the books table before inserting
    c.execute("SELECT COUNT(*) FROM books")
    if c.fetchone()[0] == 0:
        book_data = [
            ('The Hobbit', 'J.R.R. Tolkien', 'Fantasy', 'A hobbit goes on an adventure with dwarves.', 'https://example.com/covers/hobbit.jpg'),
            ('1984', 'George Orwell', 'Dystopian', 'A man struggles in a totalitarian society.', 'https://example.com/covers/1984.jpg'),
            ('Sapiens', 'Yuval Noah Harari', 'Non-Fiction', 'A history of the human species.', 'https://example.com/covers/sapiens.jpg'),
            ('Atomic Habits', 'James Clear', 'Self-Help', 'A guide to building better habits.', 'https://example.com/covers/atomichabits.jpg'),
            ('Dune', 'Frank Herbert', 'Sci-Fi', 'A sci-fi saga on a desert planet.', 'https://example.com/covers/dune.jpg'),
            ('Project Hail Mary', 'Andy Weir', 'Sci-Fi', 'A man wakes up on a spaceship with amnesia.', 'https://example.com/covers/hailmary.jpg'),
            ('Educated', 'Tara Westover', 'Memoir', 'A memoir of escaping a survivalist family.', 'https://example.com/covers/educated.jpg'),
            ('The Alchemist', 'Paulo Coelho', 'Fiction', 'A boy travels in search of treasure.', 'https://example.com/covers/alchemist.jpg'),
            ('Becoming', 'Michelle Obama', 'Biography', 'The story of Michelle Obama\'s life.', 'https://example.com/covers/becoming.jpg'),
            ('Thinking, Fast and Slow', 'Daniel Kahneman', 'Psychology', 'Insights into how we think.', 'https://example.com/covers/thinking.jpg'),
            ('The Martian', 'Andy Weir', 'Sci-Fi', 'An astronaut stranded on Mars.', 'https://example.com/covers/martian.jpg'),
            ('The Catcher in the Rye', 'J.D. Salinger', 'Fiction', 'A teen\'s angst and rebellion.', 'https://example.com/covers/catcher.jpg'),
            ('To Kill a Mockingbird', 'Harper Lee', 'Fiction', 'A story of racial injustice.', 'https://example.com/covers/mockingbird.jpg'),
            ('Rich Dad Poor Dad', 'Robert Kiyosaki', 'Finance', 'Lessons on money and investing.', 'https://example.com/covers/richdad.jpg'),
            ('The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', 'A man pursues his lost love.', 'https://example.com/covers/gatsby.jpg'),
            ('Meditations', 'Marcus Aurelius', 'Philosophy', 'Stoic reflections of an emperor.', 'https://example.com/covers/meditations.jpg'),
            ('The Power of Habit', 'Charles Duhigg', 'Self-Help', 'Understanding habit formation.', 'https://example.com/covers/habit.jpg'),
            ('Man\'s Search for Meaning', 'Viktor Frankl', 'Psychology', 'A Holocaust survivor\'s insights.', 'https://example.com/covers/meaning.jpg'),
            ('Brave New World', 'Aldous Huxley', 'Dystopian', 'A futuristic society of engineered happiness.', 'https://example.com/covers/bravenewworld.jpg'),
            ('The Subtle Art of Not Giving a F*ck', 'Mark Manson', 'Self-Help', 'A counterintuitive approach to living well.', 'https://example.com/covers/subtleart.jpg'),
            ('Crime and Punishment', 'Fyodor Dostoevsky', 'Fiction', 'A man battles guilt after a crime.', 'https://example.com/covers/crime.jpg'),
            ('The Name of the Wind', 'Patrick Rothfuss', 'Fantasy', 'A gifted young man becomes a legend.', 'https://example.com/covers/nameofthewind.jpg'),
            ('The Silent Patient', 'Alex Michaelides', 'Thriller', 'A woman stops speaking after a crime.', 'https://example.com/covers/silentpatient.jpg'),
            ('A Brief History of Time', 'Stephen Hawking', 'Science', 'Understanding the universe.', 'https://example.com/covers/briefhistory.jpg'),
            ('Normal People', 'Sally Rooney', 'Fiction', 'Two people navigate a complex relationship.', 'https://example.com/covers/normalpeople.jpg'),
            ('The Midnight Library', 'Matt Haig', 'Fiction', 'A library of lives you could have lived.', 'https://example.com/covers/midnightlibrary.jpg'),
            ('Outliers', 'Malcolm Gladwell', 'Non-Fiction', 'What makes high-achievers different?', 'https://example.com/covers/outliers.jpg'),
            ('The Road', 'Cormac McCarthy', 'Post-Apocalyptic', 'A father and son travel through a desolate world.', 'https://example.com/covers/theroad.jpg'),
            ('Can’t Hurt Me', 'David Goggins', 'Memoir', 'The story of pushing beyond limits.', 'https://example.com/covers/canthurtme.jpg'),
            ('The Four Agreements', 'Don Miguel Ruiz', 'Self-Help', 'A practical guide to personal freedom.', 'https://example.com/covers/fouragreements.jpg')
        ]
        c.executemany(''' 
            INSERT INTO books (title, author, genre, synopsis, cover_url)
            VALUES (?, ?, ?, ?, ?)
        ''', book_data)


    # User 1 owns all 30 books if they don't already own them
    c.execute("SELECT COUNT(*) FROM user_books WHERE user_id = 1")
    if c.fetchone()[0] == 0:
        user_books_data = [(1, book_id + 1, (book_id + 1) * 5 % 101, f'Note for book {book_id + 1}') for book_id in range(30)]
        c.executemany(''' 
            INSERT INTO user_books (user_id, book_id, read_percent, notes)
            VALUES (?, ?, ?, ?)
        ''', user_books_data)

    conn.commit()
    conn.close()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/Signup_and_login.html')
def signup_login():
    return render_template('Signup_and_login.html')

@app.route('/signup.html')
def signup():
    return render_template('signup.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')


@app.route('/publicshare.html')
def public_share():
    return render_template('publicshare.html')

@app.route('/api/user_books')
def api_user_books():
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
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT book_id, title, synopsis, cover_url FROM books")
    recs = [{"book_id": row[0], "title": row[1], "synopsis": row[2], "cover_url": row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify(recs)

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

@app.route('/api/user_books_by_genre')
def user_books_by_genre():
    user_id = request.args.get('user_id')
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT b.genre, COUNT(*) 
        FROM user_books ub
        JOIN books b ON ub.book_id = b.book_id
        WHERE ub.user_id = ?
        GROUP BY b.genre
    ''', (user_id,))
    rows = c.fetchall()
    conn.close()
    return jsonify({genre: count for genre, count in rows})

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
