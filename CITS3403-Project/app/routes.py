from flask import Blueprint, request, jsonify, render_template, redirect, url_for, abort, session, flash, current_app
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
import json
from app.forms import ManualBookForm, CombinedBookForm, RegistrationForm, LoginForm, PasswordResetRequestForm, PasswordResetForm
import secrets
from flask_mail import Mail, Message

mail = Mail()
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
        return redirect(url_for('main.home'))
    return render_template('landing.html')

@main.route('/home.html')
def home():
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    continue_reading = []
    completed_books  = []        
    chart_data       = []

    if user:
        continue_reading = [
            ub.book for ub in UserBook.query
                     .filter_by(user_id=user.user_id, completed=False)
                     .all()
        ]

        completed_books = [       
            ub.book for ub in UserBook.query
                     .filter_by(user_id=user.user_id, completed=True)
                     .all()
        ]

        today = datetime.utcnow().date()
        past_30_days = [today - timedelta(days=i) for i in range(29, -1, -1)]

        for day in past_30_days:
            total_pages = db.session.query(db.func.sum(ReadingLog.pages_read))\
                           .filter(ReadingLog.user_id == user.user_id,
                                   db.func.date(ReadingLog.date) == day)\
                           .scalar() or 0
            chart_data.append({'date': day.strftime('%Y-%m-%d'),
                               'pages_read': total_pages})

    return render_template('home.html',
                           username=username,
                           continue_reading=continue_reading,
                           completed_books=completed_books,   
                           chart_data=chart_data)



@main.route('/share', methods=['GET', 'POST'])
def share():
    user_id = session.get('user_id')  # Logged-in user's ID
    if not user_id:
        flash('You must be logged in to share books.', 'error')
        return redirect(url_for('main.login'))

    # Always generate chart_data for the preview chart
    chart_data = []
    today = datetime.utcnow().date()
    past_30_days = [today - timedelta(days=i) for i in range(29, -1, -1)]
    for day in past_30_days:
        total_pages = db.session.query(db.func.sum(ReadingLog.pages_read)).filter(
            ReadingLog.user_id == user_id,
            db.func.date(ReadingLog.date) == day
        ).scalar() or 0
        chart_data.append({'date': day.strftime('%Y-%m-%d'), 'pages_read': total_pages})

    if request.method == 'POST':
        data = request.get_json()
        recipient_username = data.get('username')
        book_id = data.get('book_id')

        # Validate recipient
        recipient = User.query.filter_by(username=recipient_username).first()
        if not recipient:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        # Prevent sharing to self
        current_user = User.query.get(user_id)
        if recipient_username == current_user.username:
            return jsonify({'status': 'error', 'message': 'You cannot share to yourself.'}), 400

        # Validate book
        book = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
        if not book:
            return jsonify({'status': 'error', 'message': 'Book not found or not owned by you'}), 404

        # Create a shared item with structured content_data
        shared_item = SharedItem(
            user_id=user_id,
            content_type='book',
            content_data=json.dumps({
                'title': book.book.title,
                'notes': book.notes,
                'rating': book.rating
            }),
            created_at=datetime.utcnow()
        )


        # Handle sharing stats
        if book_id == "stats":
            # Generate stats data for the current user (same as your dashboard)
            stats_chart_data = []
            for day in past_30_days:
                total_pages = db.session.query(db.func.sum(ReadingLog.pages_read)).filter(
                    ReadingLog.user_id == user_id,
                    db.func.date(ReadingLog.date) == day
                ).scalar() or 0
                stats_chart_data.append({'date': day.strftime('%Y-%m-%d'), 'pages_read': total_pages})

            shared_item = SharedItem(
                user_id=user_id,
                content_type='stats',
                content_data=json.dumps({
                    'title': 'Reading Stats (Last 30 Days)',
                    'chart_data': stats_chart_data
                }),
                created_at=datetime.utcnow()
            )
        else:
            # Validate book
            book = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
            if not book:
                return jsonify({'status': 'error', 'message': 'Book not found or not owned by you'}), 404

            shared_item = SharedItem(
                user_id=user_id,
                content_type='book',
                content_data=json.dumps({
                    'title': book.book.title,
                    'notes': book.notes,
                    'rating': book.rating
                }),
                created_at=datetime.utcnow()
            )

        db.session.add(shared_item)
        db.session.commit()

        # Link the shared item to the recipient
        shared_with = SharedWith(shared_item_id=shared_item.id, receiver_user_id=recipient.user_id)
        db.session.add(shared_with)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Shared successfully!'})

    # Fetch books added by the user
    user_books = UserBook.query.filter_by(user_id=user_id).all()

    # Fetch items shared by the user
    your_shared_items = []
    for item in SharedItem.query.filter_by(user_id=user_id).all():
        if not item.content_data:
            continue
        try:
            content_data = json.loads(item.content_data)
        except json.JSONDecodeError:
            continue

        if item.content_type == 'stats':
            your_shared_items.append({
                'id': item.id,
                'content_type': item.content_type,
                'title': content_data.get('title'),
                'chart_data': content_data.get('chart_data'),
                'created_at': item.created_at,
                'notes': content_data.get('notes', None),
            })
        else:
            book_title = content_data.get('title')
            book = Book.query.filter_by(title=book_title).first()
            cover_url = f"https://covers.openlibrary.org/b/id/{book.cover_id}-L.jpg" if book and book.cover_id else "https://via.placeholder.com/150"
            your_shared_items.append({
                'id': item.id,
                'content_type': item.content_type,
                'title': content_data.get('title'),
                'notes': content_data.get('notes'),
                'rating': content_data.get('rating'),
                'created_at': item.created_at,
                'cover_url': cover_url
            })

    # Fetch items shared with the user
    shared_to_user = []
    for item, user in (
        db.session.query(SharedItem, User)
        .join(SharedWith, SharedItem.id == SharedWith.shared_item_id)
        .join(User, SharedItem.user_id == User.user_id)
        .filter(SharedWith.receiver_user_id == user_id)
        .all()
    ):
        if not item.content_data:
            continue
        try:
            content_data = json.loads(item.content_data)
        except json.JSONDecodeError:
            continue

        if item.content_type == 'stats':
            shared_to_user.append({
                'id': item.id,
                'content_type': item.content_type,
                'title': content_data.get('title'),
                'chart_data': content_data.get('chart_data'),
                'created_at': item.created_at,
                'notes': content_data.get('notes', None),
                'shared_by': user.username
            })
        else:
            book_title = content_data.get('title')
            book = Book.query.filter_by(title=book_title).first()
            cover_url = f"https://covers.openlibrary.org/b/id/{book.cover_id}-L.jpg" if book and book.cover_id else "https://via.placeholder.com/150"
            shared_to_user.append({
                'id': item.id,
                'content_type': item.content_type,
                'title': content_data.get('title'),
                'notes': content_data.get('notes'),
                'rating': content_data.get('rating'),
                'created_at': item.created_at,
                'cover_url': cover_url,
                'shared_by': user.username
            })

    return render_template(
        'share.html',
        user_books=user_books,
        your_shared_items=your_shared_items,
        shared_to_user=shared_to_user,
        chart_data=chart_data
    )

@main.route('/search_users', methods=['GET'])
def search_users():
    query = request.args.get('q', '').strip()  # Get the search query from the request
    user_id = session.get('user_id')  # Get the logged-in user's ID

    if not query:
        return jsonify([])  # Return an empty list if no query is provided

    # Search for users whose usernames contain the query (case-insensitive) and exclude the current user
    users = User.query.filter(
        User.username.ilike(f'%{query}%'),
        User.user_id != user_id  # Exclude the current user
    ).all()

    # Return a list of matching usernames
    return jsonify([user.username for user in users])

@main.route('/uploadbook.html', methods=['GET', 'POST'])
def uploadbook():
    form = CombinedBookForm()
    if form.validate_on_submit():
        book_data = {
            'title': form.title.data,
            'author': form.author.data,
            'genres': form.genres.data,
            'description': form.description.data,
            'number_of_pages': form.number_of_pages.data
        }

        user_id = session.get('user_id')
        if not user_id:
            flash('You must be logged in to upload a book.', 'error')
            return redirect(url_for('main.login'))

        status, msg = manual_book_save(form, user_id=user_id)

        flash(msg, "success" if status == "success" else "error")

        if status == "success":
            if form.rating.data is not None or form.notes.data or form.completed.data:
                book = Book.query.filter_by(title=form.title.data, author=form.author.data).first()
                if book:
                    user_book = UserBook.query.filter_by(user_id=user_id, book_id=book.work_id).first()
                    if user_book:
                        if form.rating.data is not None:
                            user_book.rating = form.rating.data
                        if form.notes.data:
                            user_book.notes = form.notes.data
                        if form.completed.data:
                            user_book.completed = True
                        db.session.commit()

            return redirect(url_for('main.browse'))

    return render_template('uploadbook.html', form=form)

@main.route('/browse.html', methods=['GET', 'POST'])
def browse():
    form = ManualBookForm()

    if form.validate_on_submit():
        status, msg = manual_book_save(form, user_id=session.get('user_id'))
        flash(msg, "success" if status == "success" else "error")
        return redirect(url_for('main.browse'))
    return render_template('browse.html', form=form)

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    # If user is already logged in, redirect to home page
    if 'user_id' in session:
        return redirect(url_for('main.home'))

    # Create form instance
    form = RegistrationForm()
    errors = []
    show_errors = False

    if request.method == 'POST':
        # If form validation passes
        if form.validate_on_submit():
            # Check if username is already taken
            if User.query.filter_by(username=form.username.data).first():
                errors.append('Username has already been taken')
                show_errors = True
            # Check if email is already registered
            elif User.query.filter_by(email=form.email.data).first():
                errors.append('Email has already been taken')
                show_errors = True
            else:
                # Create new user
                hashed_password = generate_password_hash(form.password.data)
                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    password=hashed_password
                )

                try:
                    # Save to database
                    db.session.add(user)
                    db.session.commit()

                    # Set session
                    session.clear()
                    session['user_id'] = user.user_id
                    session['username'] = user.username

                    # Show success message
                    flash('Account created successfully', 'success')
                    return redirect(url_for('main.home'))

                except Exception as e:
                    # Rollback in case of database error
                    db.session.rollback()
                    errors.append('An error occurred while creating your account')
                    show_errors = True

        # Form validation failed or database error occurred
        show_errors = True

        # Collect specific error messages
        # 1. Username errors
        if form.username.errors:
            for error in form.username.errors:
                if 'already taken' in error or 'already exists' in error:
                    if 'Username has already been taken' not in errors:
                        errors.append('Username has already been taken')

        # 2. Email errors
        if form.email.errors:
            for error in form.email.errors:
                if 'already registered' in error or 'already exists' in error:
                    if 'Email has already been taken' not in errors:
                        errors.append('Email has already been taken')

        # 3. Password confirmation errors
        if form.confirm_password.errors:
            for error in form.confirm_password.errors:
                if 'must match' in error or 'don\'t match' in error or 'doesn\'t match' in error:
                    if 'Password confirmation doesn\'t match Password' not in errors:
                        errors.append('Password confirmation doesn\'t match Password')

        # 4. Password format errors
        if form.password.errors:
            for error in form.password.errors:
                if 'lowercase' in error or 'uppercase' in error or 'number' in error or 'special character' in error:
                    errors.append('Password: Must include at least one lowercase letter, one uppercase letter, one number, and one special character.')
                    break

        # 5. Other errors
        for field, field_errors in form.errors.items():
            for error in field_errors:
                # Skip already specifically handled errors
                if (field == 'username' and ('already' in error or 'taken' in error)) or \
                   (field == 'email' and ('already' in error or 'registered' in error)) or \
                   (field == 'confirm_password' and 'match' in error) or \
                   (field == 'password' and any(x in error for x in ['lowercase', 'uppercase', 'number', 'special character'])):
                    continue
                else:
                    errors.append(f"{field.replace('_', ' ').title()}: {error}")

    # Render the signup page with form and potential errors
    return render_template('signup.html', form=form, errors=errors, show_errors=show_errors)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    errors = []
    show_errors = False
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            errors.append('No account found with this email address')
            show_errors = True
        elif not check_password_hash(user.password, password):
            errors.append('Incorrect password')
            show_errors = True
        else:
            session.clear()
            session['user_id'] = user.user_id
            session['username'] = user.username
            flash('Logged in successfully', 'success')
            return redirect(url_for('main.home'))
    
    return render_template('login.html', form=form, errors=errors, show_errors=show_errors)

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.landing'))

@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if 'user_id' in session:
        return redirect(url_for('main.home'))

    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            reset_token = secrets.token_urlsafe(32)

            user.reset_token = reset_token
            user.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()

            reset_url = url_for(
                'main.reset_password',
                token=reset_token,
                _external=True
            )

            msg = Message(
                'Password Reset Request',
                recipients=[user.email],
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )


            msg.html = render_template('reset_email.html', reset_url=reset_url, user=user)


            msg.body = f"""
            Click the link below to reset your password:
            {reset_url}

            If you did not request a password reset, please ignore this email.

            This link will expire in 1 hour.
            """

            mail.send(msg)
            flash('A password reset link has been sent to your email.', 'success')
            return redirect(url_for('main.login'))

    return render_template('forgot_password.html', form=form)

@main.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if 'user_id' in session:
        return redirect(url_for('main.home'))

    user = User.query.filter_by(reset_token=token).first()
    errors = []
    show_errors = False

    if not user or not user.reset_token_expiration or user.reset_token_expiration < datetime.utcnow():
        flash('Invalid or expired reset link', 'error')
        return redirect(url_for('main.forgot_password'))

    form = PasswordResetForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_password = form.password.data

            if check_password_hash(user.password, new_password):
                flash('New password cannot be the same as the current password', 'error')
                errors.append('New password cannot be the same as the current password')
                show_errors = True
                return render_template('reset_password.html', form=form, token=token, errors=errors, show_errors=show_errors)

            hashed_password = generate_password_hash(new_password)
            user.password = hashed_password
            user.reset_token = None
            user.reset_token_expiration = None

            db.session.commit()

            flash('Password reset successful. Please log in.', 'success')
            return redirect(url_for('main.login'))
        else:
            # Form validation errors
            show_errors = True
            # Password errors
            if form.password.errors:
                for error in form.password.errors:
                    if 'lowercase' in error or 'uppercase' in error or 'number' in error or 'special character' in error:
                        errors.append('Password: Must include at least one lowercase letter, one uppercase letter, one number, and one special character.')
                        break

            # Password confirmation errors
            if form.confirm_password.errors:
                for error in form.confirm_password.errors:
                    if 'match' in error:
                        errors.append('Password confirmation doesn\'t match Password')
                        break

            # Other errors
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    # Skip already processed errors
                    if (field == 'password' and any(x in error for x in ['lowercase', 'uppercase', 'number', 'special character'])) or \
                        (field == 'confirm_password' and 'match' in error):
                        continue
                    else:
                        errors.append(f"{field.replace('_', ' ').title()}: {error}")

    return render_template('reset_password.html', form=form, token=token, errors=errors, show_errors=show_errors)
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
    from datetime import date

    # --- 1. current user --------------------------------------------------
    username = session.get('username') or abort(401)
    user = User.query.filter_by(username=username).first_or_404()

    # --- 2. book exists? ---------------------------------------------------
    Book.query.filter_by(work_id=book_id).first_or_404()

    # --- 3. get / create UserBook -----------------------------------------
    ub = UserBook.query.filter_by(user_id=user.user_id,
                                  book_id=book_id).first()
    if not ub:
        ub = UserBook(user_id=user.user_id, book_id=book_id)
        db.session.add(ub)

    # ---------- helper: recalc completion flag ----------------------------
    def _recalc_completion():
        if not ub.number_of_pages:           # unknown length
            return
        total = (db.session.query(db.func.coalesce(
                    db.func.sum(ReadingLog.pages_read), 0))
                 .filter_by(user_id=user.user_id, book_id=book_id)
                 .scalar())
        ub.completed = (total >= ub.number_of_pages)

    # ---------- simple fields (rating / status / notes) -------------------
    modified = False

    if 'rating' in request.form:
        try:
            ub.rating = float(request.form['rating']); modified = True
        except ValueError: pass

    status = request.form.get('status')
    if status is not None:
        ub.completed = (status == 'completed'); modified = True

    notes = request.form.get('notes')
    if notes is not None:
        ub.notes = notes; modified = True
    
    # --- pages_total update ---------------------------------------------------
    if 'pages_total' in request.form:
        try:
            new_pages = int(request.form['pages_total'])
            if new_pages <= 0:
                return jsonify(success=False, message="Pages must be > 0"), 400

            # guard – cannot be less than pages already read
            current_total = (db.session.query(db.func.coalesce(
                            db.func.sum(ReadingLog.pages_read), 0))
                            .filter_by(user_id=user.user_id, book_id=book_id)
                            .scalar())
            if current_total > new_pages:
                return jsonify(success=False,
                            message="New total cannot be less than pages already read."), 400

            ub.number_of_pages = new_pages
            _recalc_completion()            # update completed flag
            db.session.commit()
            return jsonify(success=True, new_pages=new_pages)

        except ValueError:
            return jsonify(success=False, message="Bad page number"), 400

    

    # ---------- reading-log actions ---------------------------------------
    # delete
    if 'delete_date' in request.form:
        ReadingLog.query.filter_by(user_id=user.user_id,
                                   book_id=book_id,
                                   date=request.form['delete_date']).delete()
        _recalc_completion()
        db.session.commit()
        return jsonify(success=True)

    # edit existing
    if 'edit_date' in request.form and 'page_read' in request.form:
        log = ReadingLog.query.filter_by(user_id=user.user_id,
                                         book_id=book_id,
                                         date=request.form['edit_date']).first_or_404()
        log.pages_read = int(request.form['page_read'])
        _recalc_completion()
        db.session.commit()
        return jsonify(success=True)

    # add new
    if 'date' in request.form and 'page_read' in request.form:
        try:
            pages_to_add = int(request.form['page_read'])
            log_date     = date.fromisoformat(request.form['date'])

            # A. future date
            if log_date > date.today():
                return jsonify(success=False,
                               message="That day is yet to come."), 400

            # B. overflow guard (uses ub.number_of_pages)
            if ub.number_of_pages:
                current_total = (db.session.query(db.func.coalesce(
                                   db.func.sum(ReadingLog.pages_read), 0))
                                 .filter_by(user_id=user.user_id,
                                            book_id=book_id)
                                 .scalar())
                if current_total + pages_to_add > ub.number_of_pages:
                    return jsonify(success=False,
                                   message="Book doesn't have that many pages."), 400

            # C. duplicate date
            if ReadingLog.query.filter_by(user_id=user.user_id,
                                          book_id=book_id,
                                          date=log_date).first():
                return jsonify(success=False,
                               message="Entry for this date already exists. "
                                       "Delete or edit it instead."), 409

            new_log = ReadingLog(user_id=user.user_id,
                                 book_id=book_id,
                                 date=log_date,
                                 pages_read=pages_to_add)
            db.session.add(new_log)
            _recalc_completion()
            db.session.commit()
            return jsonify(success=True,
                           new_log={'date': log_date.isoformat(),
                                    'pages_read': pages_to_add})
        except (ValueError, TypeError):
            return jsonify(success=False, message="Bad input"), 400

    # ---------- commit for rating / notes-only ----------------------------
    if modified:
        db.session.commit()
    return jsonify(success=True)





@main.route('/book/<string:book_id>', methods=['GET'])
def book_specific_page(book_id):
    # ---------- 1. Fallback  ----------
    fallback = {
        'title'      : 'Unknown Title',
        'author'     : 'Unknown Author',
        'pages'      : 0,
        'description': 'No description available.',
        'cover_url'  : 'https://covers.openlibrary.org/b/id/255844-M.jpg',
        'genres'     : []
    }

    # ---------- 2. Book row (still has title, author, etc.) ----------
    book_row = Book.query.filter_by(work_id=book_id).first()
    if not book_row:
        return render_template('bookspecificpage.html',
                               book=fallback,
                               user_data={},
                               book_id=book_id,
                               community_notes=[],
                               pages_read_total=0,
                               reading_logs=[])

    # ---------- 3. Current user & UserBook ----------
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    ub = None
    if user:
        ub = UserBook.query.filter_by(user_id=user.user_id,
                                      book_id=book_id).first()

    # ---------- 4. Build book dict ----------
    pages_for_user = ub.number_of_pages if ub and ub.number_of_pages else 0
    book = {
        'title'      : book_row.title,
        'author'     : book_row.author,
        'pages'      : pages_for_user,
        'description': book_row.description or fallback['description'],
        'cover_url'  : f"https://covers.openlibrary.org/b/id/{book_row.cover_id}-L.jpg"
                       if book_row.cover_id else fallback['cover_url'],
        'genres'     : []
    }

    # subjects → genres
    if book_row.subjects:
        try:
            import json
            subs = json.loads(book_row.subjects)
            book['genres'] = subs[:5] if isinstance(subs, list) else [
                s.strip() for s in book_row.subjects.split(',')
            ][:5]
        except Exception:
            book['genres'] = [s.strip() for s in book_row.subjects.split(',')][:5]

    # ---------- 5. User-specific aggregates ----------
    user_data        = {}
    pages_read_total = 0
    reading_logs     = []

    if user:
        if ub:
            user_data = {
                'rating' : ub.rating,
                'status' : 'Completed' if ub.completed else 'Reading',
                'notes'  : ub.notes
            }

        pages_read_total = db.session.query(
            db.func.coalesce(db.func.sum(ReadingLog.pages_read), 0)
        ).filter_by(user_id=user.user_id, book_id=book_id).scalar()

        # serialise logs → list[dict]
        for l in (ReadingLog.query
                  .filter_by(user_id=user.user_id, book_id=book_id)
                  .order_by(ReadingLog.date.asc())
                  .all()):
            reading_logs.append({
                'id'        : l.id,
                'date'      : l.date.isoformat(),
                'pages_read': l.pages_read
            })

    # ---------- 6. Render ----------
    return render_template('bookspecificpage.html',
                           book=book,
                           user_data=user_data,
                           book_id=book_id,
                           community_notes=[],
                           pages_read_total=pages_read_total,
                           reading_logs=reading_logs)


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