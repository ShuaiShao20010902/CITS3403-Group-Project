from flask import jsonify, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
import requests
import random
from werkzeug.security import generate_password_hash, check_password_hash
from models import DB_FILE, get_db_connection

#region Utility functions

def validate_input(value, field_name, required=True, value_type=int, min_value=None, max_value=None):
    """
    Parameters:
    - value: value to validate
    - field_name: name for error messages
    - required: if required to have a value
    - value_type: expected value type
    - min_value: minimum value
    - max_value: maximum value

    Returns:
    - validated value or None if invalid (no message even if required, wrong type etc.) with error messages
    """
    if required and not value:
        flash(f'{field_name} is required', 'error')
        return None
    try:
        value = value_type(value)
    except (ValueError, TypeError):
        flash(f'{field_name} must be a {value_type.__name__}', 'error')
        return None
    if min_value is not None and value < min_value:
        flash(f'{field_name} must be at least {min_value}', 'error')
        return None
    if max_value is not None and value > max_value:
        flash(f'{field_name} must be at most {max_value}', 'error')
        return None
    return value

# Routes for Pages
def setup_routes(app):
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
        return render_template(
            'share.html',
            your_shared_items=your_shared_items,
            shared_to_user=shared_to_user
        )

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

            conn = get_db_connection()
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

    # Routes for API
    @app.route('/api/books')
    def api_books():
        # 1. Fetch a pool of works via Open Library's search API
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
    
    #for user submitted info on book specific page
    @app.route('/book/<string:book_id>/update', methods=['POST'])
    def update_book(book_id):
        rating = request.form.get('rating')
        status = request.form.get('status')
        page_read = request.form.get('page_read')
        notes = request.form.get('notes')
        
        # Validate inputs
        rating = validate_input(rating, 'Rating', required=False, value_type=float, min_value=0.0, max_value=5.0)
        page_read = validate_input(page_read, 'Page Read', required=False, value_type=int, min_value=0)

        ALLOWED_STATUSES = {'reading', 'completed', 'on_hold', 'dropped'}
        if status not in ALLOWED_STATUSES:
            flash("Invalid reading status selected", "error")
            return redirect(url_for('book_specific_page', book_id=book_id))

        if rating is None or page_read is None:
            return redirect(url_for('book_specific_page', book_id=book_id))

        #ADD LATER - change to DB logic TESTING PURPOSES ONLY
        print(f"Rating: {rating}, Status: {status}, Page Read: {page_read}, Notes: {notes}")

        return jsonify({'success': True})

    # Book specific page
    @app.route('/book/<string:book_id>', methods=['GET', 'POST'])
    def book_specific_page(book_id):

        # In case API fails or missing fields
        fallback = {
            'title': 'Unknown Title',
            'author': 'Unknown Author',
            'pages': 0,
            'isbn': 'N/A',
            'year': 0,
            'description': 'No description available.',
            'cover_url': 'https://covers.openlibrary.org/b/id/255844-M.jpg',
            'genres': []
        }
        
        #1. check if basic book_id is valid or not (protect from crashes))
        try: 
            resp = requests.get(
                f'https://openlibrary.org/works/{book_id}.json'
            )
            resp.raise_for_status()  # Raise an error for bad responses
            book_data = resp.json()
        except requests.RequestException:
            return render_template('bookspecificpage.html', book=fallback, user_data={}, book_id=book_id, community_notes=[])

        #2. initial book dictionary (get information that is not edition specific)
        book = {
            'title': book_data.get('title', fallback['title']),
            'author': fallback['author'],  # Will fetch below
            'pages': fallback['pages'],
            'isbn': fallback['isbn'],
            'year': fallback['year'],
            'description': book_data.get('description', {}).get('value', 'No description available.') if isinstance(book_data.get('description'), dict) else book_data.get('description', 'No description available.'),
            'cover_url': f"https://covers.openlibrary.org/b/id/{book_data.get('covers', [])[0]}-L.jpg" if book_data.get('covers') else fallback['cover_url'],
            'genres': book_data.get('subjects', [])[:5]  # Top 5 genres
        }
        
        #3. get author information from the author api
        try:
            author_key = book_data['authors'][0]['author']['key'] 
            author_resp = requests.get(f'https://openlibrary.org{author_key}.json')
            author_resp.raise_for_status()
            book['author'] = author_resp.json().get('name', 'Unknown')
        except (IndexError, KeyError, requests.RequestException):
            pass

        #4. pages, isbn, year are edition information (will not be found in the standard .json), optional information? if too slow
        try:
            edition_resp = requests.get(f'https://openlibrary.org/works/{book_id}/editions.json?limit=1')
            edition_resp.raise_for_status()
            edition_data = edition_resp.json()['entries'][0]

            book['pages'] = edition_data.get('number_of_pages') or edition_data.get('pagination', 'N/A')
            isbn_10 = edition_data.get('isbn_10', ['N/A'])
            isbn_13 = edition_data.get('isbn_13', ['N/A'])
            book['isbn'] = isbn_10[0] if isbn_10[0] != 'N/A' else (isbn_13[0] if isbn_13 else 'N/A')
            book['year'] = edition_data.get('publish_date', fallback['year'])
        except (IndexError, KeyError, requests.RequestException):
            pass
        #5. return information to the template
        return render_template('bookspecificpage.html', book=book, user_data={}, book_id=book_id, community_notes=[])