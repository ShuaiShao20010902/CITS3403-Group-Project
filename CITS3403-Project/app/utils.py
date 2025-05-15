import requests
from datetime import datetime, timezone, date
from sqlalchemy.exc import IntegrityError
from app.models import db, Book, UserBook, ReadingLog   # adjust import path as needed


# ────────────────────────────────────────────────────────────────────────────
#  PUBLIC HELPERS
# ────────────────────────────────────────────────────────────────────────────
def add_book_to_dashboard_database(api_book_data: dict, user_id: int):
    """
    • Fetches work-level info from OpenLibrary.
    • Adds/links the book row (Book table)         – without number_of_pages.
    • Adds/links the user row (UserBook table)     – with number_of_pages.
    """
    raw_work_key = api_book_data.get('work_key')
    if not raw_work_key or not raw_work_key.startswith("/works/"):
        return {'status': 'error', 'message': 'Invalid or missing work_key.'}

    work_id_str = raw_work_key.split('/')[-1]
    pages       = api_book_data.get('number_of_pages') or 0

    # ── If the Book already exists, just link to user ────────────────────
    book = Book.query.get(work_id_str)
    if book:
        if UserBook.query.filter_by(user_id=user_id, book_id=book.work_id).first():
            return {'status': 'error', 'message': 'You have already added this book!'}
        db.session.add(UserBook(user_id=user_id,
                                book_id=book.work_id,
                                number_of_pages=pages))
        db.session.commit()
        return {'status': 'success',
                'message': f"Book '{book.title}' linked to dashboard."}

    # ── Fetch WORK-level data ─────────────────────────────────────────────
    work_json = _error_check(f"https://openlibrary.org{raw_work_key}.json")

    # authors string
    authors = []
    for entry in work_json.get("authors", []):
        a_key = entry.get("author", {}).get("key") or entry.get("key")
        if not a_key:
            continue
        a_json = _error_check(f"https://openlibrary.org{a_key}.json")
        if a_json and a_json.get("name"):
            authors.append(a_json["name"])
    author_str = ", ".join(authors) or "Unknown Author"

    # ── Create Book row (NO pages column) ────────────────────────────────
    book = Book(
        work_id      = work_id_str,
        title        = work_json.get('title', 'Unknown Title'),
        author       = author_str,
        description  = _extract_description(work_json),
        subjects     = ", ".join(work_json.get("subjects", [])),
        cover_id     = (work_json.get("covers", [None])[0]),
        last_fetched = datetime.now(timezone.utc),
    )
    db.session.add(book)

    # ── Create UserBook row WITH number_of_pages ─────────────────────────
    db.session.add(UserBook(user_id         = user_id,
                            book_id         = work_id_str,
                            number_of_pages = pages))
    db.session.commit()

    return {
        'status' : 'success',
        'message': f"Book '{book.title}' added to DB and linked to dashboard.",
        'book_id': book.work_id
    }


def manual_book_save(form, user_id=None):
    """
    Create or update a MANUAL- entry.

    • number_of_pages stored on UserBook if linked to a user.
    """
    try:
        title       = form.title.data.strip()
        author      = form.author.data.strip()
        genres      = form.genres.data.strip()
        description = form.description.data.strip()
        pages       = form.number_of_pages.data
        work_id     = f"MANUAL-{title[:10].replace(' ', '_')}-{author[:10].replace(' ', '_')}".upper()

        # Book row (no pages column)
        book = Book.query.get(work_id)
        if book is None:
            book = Book(
                work_id      = work_id,
                title        = title,
                author       = author,
                subjects     = genres,
                description  = description,
                last_fetched = datetime.now(timezone.utc)
            )
            db.session.add(book)

        # Optional UserBook link
        if user_id:
            link = UserBook.query.filter_by(user_id=user_id, book_id=work_id).first()
            if link is None:
                link = UserBook(user_id=user_id,
                                book_id=work_id,
                                number_of_pages=pages)
                db.session.add(link)

            # optional user-specific fields
            if hasattr(form, "rating")   and form.rating.data is not None:
                link.rating = form.rating.data
            if hasattr(form, "notes")    and form.notes.data:
                link.notes  = form.notes.data.strip()
            if hasattr(form, "completed"):
                link.completed = bool(form.completed.data)
            link.number_of_pages = pages  # sync pages on update too

        db.session.commit()
        return "success", "Book added successfully."

    except Exception as e:
        db.session.rollback()
        return "error", f"Unexpected error: {e}"


# Private Helpers
def _error_check(url: str):
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return {}


def _extract_description(work_json: dict) -> str:
    raw = work_json.get("description")
    if isinstance(raw, dict):
        return raw.get("value", "")
    return raw or "No description available."
