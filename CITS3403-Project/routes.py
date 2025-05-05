from flask import request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, SharedItem, SharedWith
import requests
import random
from datetime import datetime


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


def setup_routes(app):
    @app.route('/')
    def landing():
        if 'user_id' in session:
            return redirect(url_for('home'))
        return render_template('landing.html')

    @app.route('/home.html')
    def home():
        username = session.get('username')
        return render_template('home.html', username=username)

    @app.route('/share', methods=['GET', 'POST'])
    def share():
        user_id = session.get('user_id')
        if not user_id:
            flash('You must be logged in to share.', 'error')
            return redirect(url_for('login'))

        if request.method == 'POST':
            data = request.get_json() or {}
            recipient = data.get('username', '').strip()
            receiver = User.query.filter_by(username=recipient).first()
            if not receiver:
                return jsonify({'status': 'error', 'message': 'User not found'}), 404

            items = SharedItem.query.filter_by(user_id=user_id).all()
            for item in items:
                exists = SharedWith.query.filter_by(
                    shared_item_id=item.id,
                    receiver_user_id=receiver.user_id
                ).first()
                if not exists:
                    db.session.add(SharedWith(
                        shared_item_id=item.id,
                        receiver_user_id=receiver.user_id
                    ))
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Shared successfully!'}), 200

        owned = SharedItem.query.filter_by(user_id=user_id).all()
        shared = (
            db.session.query(SharedItem, User)
            .join(SharedWith, SharedItem.id == SharedWith.shared_item_id)
            .join(User, SharedWith.receiver_user_id == User.user_id)
            .filter(SharedWith.receiver_user_id == user_id)
            .all()
        )
        return render_template('share.html', your_shared_items=owned, shared_to_user=shared)

    @app.route('/uploadbook.html')
    def uploadbook():
        return render_template('uploadbook.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')

            if User.query.filter_by(username=username).first():
                flash('Username already in use', 'error')
                return redirect(url_for('signup'))
            if User.query.filter_by(email=email).first():
                flash('Email already in use', 'error')
                return redirect(url_for('signup'))

            hashed = generate_password_hash(password)
            db.session.add(User(username=username, email=email, password=hashed))
            db.session.commit()
            flash('Account created successfully', 'success')
            return redirect(url_for('home'))

        return render_template('signup.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            user = User.query.filter_by(email=email).first()
            if not user or not check_password_hash(user.password, password):
                flash('Invalid credentials', 'error')
                return redirect(url_for('login'))

            session.clear()
            session['user_id'] = user.user_id
            session['username'] = user.username
            flash('Logged in successfully', 'success')
            return redirect(url_for('home'))

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('landing'))

    @app.route('/api/books')
    def api_books():
        resp = requests.get('https://openlibrary.org/search.json', params={'q': 'romance', 'limit': 10})
        docs = resp.json().get('docs', [])
        sample = random.sample(docs, min(10, len(docs)))
        books = []
        for w in sample:
            key = w.get('key', '')
            cover = w.get('cover_i')
            books.append({
                'id': key.split('/')[-1],
                'title': w.get('title'),
                'authors': w.get('author_name', []),
                'year': w.get('first_publish_year'),
                'cover_url': cover and f"https://covers.openlibrary.org/b/id/{cover}-L.jpg",
                'subjects': w.get('subject', [])[:5]
            })
        return jsonify(books)

    @app.route('/book/<string:book_id>/update', methods=['POST'])
    def update_book(book_id):
        rating = validate_input(request.form.get('rating'), 'Rating', required=False, value_type=float, min_value=0.0, max_value=5.0)
        status = request.form.get('status')
        page_read = validate_input(request.form.get('page_read'), 'Page Read', required=False, value_type=int, min_value=0)
        notes = request.form.get('notes')

        valid_status = {'reading', 'completed', 'on_hold', 'dropped'}
        if status not in valid_status:
            flash('Invalid reading status selected', 'error')
            return redirect(url_for('book_specific_page', book_id=book_id))
        if rating is None or page_read is None:
            return redirect(url_for('book_specific_page', book_id=book_id))

        # TODO: persist to database
        print(f"Rating: {rating}, Status: {status}, Page Read: {page_read}, Notes: {notes}")
        return jsonify({'success': True}), 200

    @app.route('/book/<string:book_id>', methods=['GET'])
    def book_specific_page(book_id):
        fallback = {
            'title': 'Unknown Title', 'author': 'Unknown Author',
            'pages': 0, 'isbn': 'N/A', 'year': 0,
            'description': 'No description available.',
            'cover_url': 'https://covers.openlibrary.org/b/id/255844-M.jpg',
            'genres': []
        }

        try:
            resp = requests.get(f'https://openlibrary.org/works/{book_id}.json')
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException:
            return render_template('bookspecificpage.html', book=fallback, user_data={}, book_id=book_id, community_notes=[])

        book = {
            'title': data.get('title', fallback['title']),
            'description': (data.get('description', {}).get('value')
                            if isinstance(data.get('description'), dict)
                            else data.get('description', fallback['description'])),
            'cover_url': (f"https://covers.openlibrary.org/b/id/{data.get('covers')[0]}-L.jpg"
                          if data.get('covers') else fallback['cover_url']),
            'genres': data.get('subjects', [])[:5],
            'author': fallback['author'], 'pages': fallback['pages'],
            'isbn': fallback['isbn'], 'year': fallback['year']
        }
        try:
            akey = data['authors'][0]['author']['key']
            ar = requests.get(f'https://openlibrary.org{akey}.json')
            ar.raise_for_status()
            book['author'] = ar.json().get('name', fallback['author'])
        except Exception:
            pass

        try:
            ed = requests.get(f'https://openlibrary.org/works/{book_id}/editions.json?limit=1')
            ed.raise_for_status()
            ed0 = ed.json()['entries'][0]
            book['pages'] = ed0.get('number_of_pages') or ed0.get('pagination', fallback['pages'])
            isbn10 = ed0.get('isbn_10', [None])[0]
            isbn13 = ed0.get('isbn_13', [None])[0]
            book['isbn'] = isbn10 or isbn13 or fallback['isbn']
            book['year'] = ed0.get('publish_date', fallback['year'])
        except Exception:
            pass

        return render_template('bookspecificpage.html', book=book, user_data={}, book_id=book_id, community_notes=[] )
