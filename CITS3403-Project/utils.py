import requests
from datetime import datetime, timezone
from models import db, Book, UserBook

def add_book_to_dashboard_database(api_book_data: dict, user_id : int):
    raw_work_key = api_book_data.get('work_key')
    if not raw_work_key or not raw_work_key.startswith("/works/"):
        return {'status': 'error', 'message': 'Invalid or missing work_key from API data.'}
    
    work_id_str = raw_work_key.split('/')[-1]

    pages = api_book_data.get("number_of_pages") or 0

    # print(f"[DEBUG]: Processing for work_id: {work_id_str}, User ID: {user_id}")
    # print(f"[DEBUG]: Initial API Book Data received: {api_book_data}")

    #check book if in database, if so, link to user (checks users as well in helper) and exit
    book = Book.query.get(work_id_str)
    if book:
        # print("[DEBUG]: Book already exists in DB.")
        if UserBook.query.filter_by(user_id=user_id, book_id=book.work_id).first():
            return {'status': 'error', 'message': 'You have already added this book!'}
        db.session.add(UserBook(user_id=user_id, book_id=book.work_id))
        db.session.commit()
        return {'status': 'success', 'message': f"Book '{book.title}' linked to dashboard."}
    
    #fetch WORK information (everything besides pages / ISBN / publishers) [FETCH 1]
    work_json = _error_check(f"https://openlibrary.org{raw_work_key}.json")

    authors = []
    for entry in work_json.get("authors", []):
        a_key = entry.get("author", {}).get("key") or entry.get("key")
        if not a_key:
            continue
        a_json = _error_check(f"https://openlibrary.org{a_key}.json")
        if a_json and a_json.get("name"):
            authors.append(a_json["name"])
    author_str = ", ".join(authors) or "Unknown Author"

    # add book to database (build the row with the info from fetches 1)
    book = Book(
        work_id=work_id_str,
        title=work_json.get('title', 'Unknown Title'),
        author = author_str,
        description = _extract_description(work_json), #make sure its string (sometimes its a dictionary)
        subjects = ", ".join(work_json.get("subjects", [])),
        number_of_pages = pages,
        cover_id=(work_json.get("covers", [None])[0]),
        last_fetched=datetime.now(timezone.utc),
    )

    db.session.add(book)
    db.session.add(UserBook(user_id=user_id, book_id=work_id_str))
    # print(f"[DEBUG] Book '{book.title}' added to DB and linked to user ID {user_id}")
    db.session.commit()

    # print(f"[DEBUG] Book added: {book.title}")
    # print(f"[DEBUG] Work Key: {book.work_id}")
    # print(f"[DEBUG] Number of Pages: {book.number_of_pages}")
    # print(f"[DEBUG] Authors: {book.author}")

    return {
        'status': 'success',
        'message': f"Book '{book.title}' added to DB and linked to dashboard.",
        'book_id': book.work_id
    }

#helper functions

#try + check for errors (make sure json is ok)
def _error_check(url: str):
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return {}

def _link_user(book_id: int, user_id: int):
    if not UserBook.query.filter_by(user_id=user_id, book_id=book_id).first():
        db.session.add(UserBook(user_id=user_id, book_id=book_id))
        db.session.commit()

def _extract_description(work_json: dict) -> str:
    raw = work_json.get("description")
    if isinstance(raw, dict):
        return raw.get("value", "")
    return raw or "No description available."