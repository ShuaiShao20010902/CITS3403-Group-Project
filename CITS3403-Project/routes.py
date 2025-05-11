from flask import request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from sqlalchemy.exc import IntegrityError
from utils import add_book_to_dashboard_database, manual_book_save
from models import db, User, SharedItem, SharedWith
import requests
import random
from datetime import datetime, timedelta
from forms import ManualBookForm, CombinedBookForm

# for data sanitisation
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
        user = User.query.filter_by(username=username).first()
        continue_reading = []
        chart_data = []

        if user:
            # Get books that aren't completed
            continue_reading = [
                ub.book for ub in UserBook.query.filter_by(user_id=user.user_id, completed=False).all()
            ]

            # Generate daily reading logs for last 30 days
            today = datetime.utcnow().date()
            past_30_days = [today - timedelta(days=i) for i in range(29, -1, -1)]

            for day in past_30_days:
                total_pages = db.session.query(db.func.sum(ReadingLog.pages_read)).filter(
                    ReadingLog.user_id == user.user_id,
                    db.func.date(ReadingLog.date) == day
                ).scalar() or 0
                chart_data.append({'date': day.strftime('%Y-%m-%d'), 'pages_read': total_pages})

        return render_template(
            'home.html',
            username=username,
            continue_reading=continue_reading,
            chart_data=chart_data
        )


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

    @app.route('/uploadbook.html', methods=['GET', 'POST'] )
    def uploadbook():
        form = CombinedBookForm()
        if form.validate_on_submit():
            status, msg = manual_book_save(form, user_id=session.get('user_id'))
            flash(msg, "success" if status == "success" else "error")
            return redirect(url_for('browse'))
        
        return render_template('uploadbook.html', form=form)

    @app.route('/browse.html', methods=['GET', 'POST'])
    def browse():
        form = ManualBookForm()

        if form.validate_on_submit():
            status, msg = manual_book_save(form, user_id=session.get('user_id'))
            flash(msg, "success" if status == "success" else "error")
            return redirect(url_for('browse'))
        return render_template('browse.html', form=form)

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
            user = User(username=username, email=email, password=hashed)
            db.session.add(user)
            db.session.commit()
            session.clear()
            session['user_id'] = user.user_id
            session['username'] = user.username
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
    
    @app.route('/forgot-password')
    def forgot_password():
        return render_template('forgot_password.html')

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


    @app.route('/book/<string:book_id>', methods=['GET', 'POST'])
    def book_specific_page(book_id):
        # Fallback in case book not found
        fallback = {
            'title': 'Unknown Title',
            'author': 'Unknown Author',
            'pages': 0,
            'description': 'No description available.',
            'cover_url': 'https://covers.openlibrary.org/b/id/255844-M.jpg',
            'genres': []
        }

        # Fetch the book from DB
        book_row = Book.query.filter_by(work_id=book_id).first()
        if not book_row:
            return render_template(
                'bookspecificpage.html',
                book=fallback,
                user_data={},
                book_id=book_id,
                community_notes=[],
                pages_read_total=0
            )

        # Build the book dict
        book = {
            'title': book_row.title,
            'author': book_row.author,
            'pages': book_row.number_of_pages,
            'description': book_row.description or fallback['description'],
            'cover_url': f"https://covers.openlibrary.org/b/id/{book_row.cover_id}-L.jpg" if book_row.cover_id else fallback['cover_url'],
            'genres': []
        }

        # Parse subjects into genres (JSON or CSV)
        if book_row.subjects:
            try:
                import json
                subs = json.loads(book_row.subjects)
                book['genres'] = subs[:5] if isinstance(subs, list) else [s.strip() for s in book_row.subjects.split(',')][:5]
            except:
                book['genres'] = [s.strip() for s in book_row.subjects.split(',')][:5]

        # Fetch user and user-specific data
        username = session.get('username')
        user = User.query.filter_by(username=username).first()
        user_data = {}
        pages_read_total = 0

        if user:
            # UserBook info
            ub = UserBook.query.filter_by(user_id=user.user_id, book_id=book_id).first()
            if ub:
                user_data = {
                    'rating': ub.rating,
                    'status': 'Completed' if ub.completed else 'Reading',
                    'notes': ub.notes,
                }

            # Sum pages_read from ReadingLog
            pages_read_total = db.session.query(
                db.func.coalesce(db.func.sum(ReadingLog.pages_read), 0)
            ).filter_by(user_id=user.user_id, book_id=book_id).scalar()

        return render_template(
            'bookspecificpage.html',
            book=book,
            user_data=user_data,
            book_id=book_id,
            community_notes=[],
            pages_read_total=pages_read_total
        )

    #endpoint to add book to dashboard (utils.py, browse.html, search)
    @app.route("/add_book", methods=["POST"])    
    def add_book():
        data = request.get_json()
        # print("/add_book route data sent:", data)

        pages = validate_input(data.get('number_of_pages'), 'Number of Pages', required=True, value_type=int, min_value=1)
        if pages is None:
             return jsonify({'status': 'fail'}), 400 
        data['number_of_pages'] = pages

        #comment this part out if want to hardcode to user 1 for testing
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'You must be logged in.'}), 401
        #------

        try:
            #result = add_book_to_dashboard_database(data, user_id = 1) #hard coded id for now
            result = add_book_to_dashboard_database(data, user_id)
            if result['status'] == 'success':
                msg = "Added to dashboard." if "linked" in result['message'].lower() or "added" in result['message'].lower() else "Added."
                return jsonify({'status': 'success', 'message': msg}), 200
            else:
                return jsonify({'status': 'fail', 'message': 'Book already exists!'}), 400
        except IntegrityError as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': 'Book already exists!'}), 400
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
