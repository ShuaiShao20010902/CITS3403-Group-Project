from flask import request, jsonify, render_template, redirect, url_for, abort, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import *
from sqlalchemy.exc import IntegrityError
from app.utils import add_book_to_dashboard_database, manual_book_save
from app.models import db, User, SharedItem, SharedWith
import requests
import random
from datetime import datetime, timedelta, date
from app.forms import ManualBookForm, CombinedBookForm
from app.blueprints import main

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


@main.route('/')
def landing():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('landing.html')

@main.route('/home.html')
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


@main.route('/share', methods=['GET', 'POST'])
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

@main.route('/uploadbook.html', methods=['GET', 'POST'] )
def uploadbook():
    form = CombinedBookForm()
    if form.validate_on_submit():
        status, msg = manual_book_save(form, user_id=session.get('user_id'))
        flash(msg, "success" if status == "success" else "error")
        return redirect(url_for('browse'))
    
    return render_template('uploadbook.html', form=form)

@main.route('/browse.html', methods=['GET', 'POST'])
def browse():
    form = ManualBookForm()

    if form.validate_on_submit():
        status, msg = manual_book_save(form, user_id=session.get('user_id'))
        flash(msg, "success" if status == "success" else "error")
        return redirect(url_for('browse'))
    return render_template('browse.html', form=form)

@main.route('/signup', methods=['GET', 'POST'])
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

@main.route('/login', methods=['GET', 'POST'])
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

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

@main.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

@main.route('/api/books')
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

@main.route('/update_book/<string:book_id>', methods=['POST'])
def update_book(book_id):
    # 1. Current user
    username = session.get('username') or abort(401)
    user = User.query.filter_by(username=username).first_or_404()

    # 2. Ensure book exists
    Book.query.filter_by(work_id=book_id).first_or_404()

    # 3. Get / create UserBook (same as before) …
    ub = UserBook.query.filter_by(user_id=user.user_id,
                                book_id=book_id).first()
    if not ub:
        ub = UserBook(user_id=user.user_id, book_id=book_id)
        db.session.add(ub)

    # ——— handle UserBook fields (rating, status, notes) exactly as you had ——— #

    # 4. Handle reading-log actions -----------------------------------------
    # (A) delete-latest takes priority over add/update
    # inside update_book, before handling page_read
    
    if 'delete_date' in request.form:
        d = request.form['delete_date']
        ReadingLog.query.filter_by(user_id=user.user_id,
                                book_id=book_id,
                                date=d).delete()
        db.session.commit()
        return jsonify(success=True)

    if 'edit_date' in request.form and 'page_read' in request.form:
        d = request.form['edit_date']
        pages = int(request.form['page_read'])
        log = ReadingLog.query.filter_by(user_id=user.user_id,
                                        book_id=book_id,
                                        date=d).first_or_404()
        log.pages_read = pages
        db.session.commit()
        return jsonify(success=True)


    if 'page_read' in request.form:
        try:
            pages = int(request.form['page_read'])
            today = date.today()
            log = (ReadingLog.query
                .filter_by(user_id=user.user_id,
                            book_id=book_id,
                            date=today)
                .first())
            if not log:
                log = ReadingLog(user_id=user.user_id,
                                book_id=book_id,
                                date=today,
                                pages_read=pages)
                db.session.add(log)
            else:
                log.pages_read = pages
            db.session.commit()
            return jsonify(success=True,
                        new_log={'date': today.isoformat(),
                                    'pages_read': pages})
        except (TypeError, ValueError):
            pass

    db.session.commit()
    return jsonify(success=True)



@main.route('/book/<string:book_id>', methods=['GET', 'POST'])
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

    reading_logs = []
    if user:
        logs = (ReadingLog
                .query
                .filter_by(user_id=user.user_id, book_id=book_id)
                .order_by(ReadingLog.date.asc())
                .all())
        # serialize to simple dicts
        for l in logs:
            reading_logs.append({
                'id': l.id,
                'date': l.date.isoformat(),
                'pages_read': l.pages_read
            })

    return render_template(
        'bookspecificpage.html',
        book=book,
        user_data=user_data,
        book_id=book_id,
        community_notes=[],
        pages_read_total=pages_read_total,
        reading_logs=reading_logs
    )

#endpoint to add book to dashboard (utils.py, browse.html, search)
@main.route("/add_book", methods=["POST"])    
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
