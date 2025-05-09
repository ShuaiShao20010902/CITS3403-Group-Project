import requests
from datetime import datetime, timezone
from models import db, Book, Author, UserBook

def add_book_to_dashboard_database(api_book_data: dict, user_id : int):
    """
    work_key -> "/works/OL166894W"
    edition_key -> "OL12345678M" or ["OL12345678M", ...]
    """

    edition_key = api_book_data.get('edition_key')
    if isinstance(edition_key, list):
        edition_key = edition_key[0]
    work_key = api_book_data.get('work_key')
    
    print(f"API Book Data: {api_book_data}")

    if not edition_key:
        edition_key = _edition_key(work_key) or f"UNKNOWN-{work_key.split('/')[-1]}-{int(datetime.now().timestamp())}" #UNKNOWN-KEY-TIMESTAMP (causing database issues if UNKNOWN (multiple) for unique key)

    if not work_key:
        raise ValueError("No work_key found in the API response")

    #check book if in database, if so, link to user (checks users as well in helper) and exit
    if not edition_key.startswith("UNKNOWN"):
        existing = Book.query.filter_by(edition_key=edition_key).first()
    else:
        existing = Book.query.filter_by(work_key=work_key, edition_key=edition_key).first()
    if existing:
        _link_user(existing.id, user_id)
        return existing
    
    #fetch WORK information (everything besides pages / ISBN / publishers) [FETCH 1]
    work_json = _error_check(f"https://openlibrary.org/{work_key}.json")

    #fetch EDITION information (pages / ISBN / publishers) [FETCH 2]
    edition_json = _error_check(f"https://openlibrary.org/books/{edition_key}.json")

    pages_s = edition_json.get('number_of_pages') or edition_json.get('pagination', "N/A")
    if isinstance(pages_s, str):  #if string convert to int
        digits = "".join(ch for ch in pages_s if ch.isdigit())
        pages = int(digits) if digits else 0
    else:
        pages = pages_s or 0

    # add book to database (build the row with the info from fetches 1 + 2)
    book = Book(
        edition_key=edition_key,
        work_key=work_key,
        title=work_json.get('title', 'Unknown Title'),
        description = _extract_description(work_json), #make sure its string (sometimes its a dictionary)
        subjects = ", ".join(work_json.get("subjects", [])),
        number_of_pages = pages,
        isbn_10=','.join(edition_json.get('isbn_10', [])) if edition_json.get('isbn_10') else None,
        isbn_13=','.join(edition_json.get('isbn_13', [])) if edition_json.get('isbn_13') else None,
        publish_date=edition_json.get('first_publish_year'),
        publishers=', '.join(edition_json.get('publisher', [])),
        cover_id=(work_json.get("covers", [None])[0]),
        last_fetched=datetime.now(timezone.utc),
    )

    db.session.add(book)
    print(f"Book '{book.title}' added to DB and linked to user ID {user_id}")
    db.session.flush()  # Assign book.id

    #add authors to author table (fetch 3)
    for entry in work_json.get("authors", []):
        a_key = entry.get("author", {}).get("key")
        if not a_key:
            continue
        a_json = _error_check(f"https://openlibrary.org{a_key}.json")
        name = a_json.get("name") if a_json else None
        if not name:
            continue

        author = Author.query.filter_by(name=name).first()
        if not author:
            author = Author(name=name, openlib_key=a_key)
            db.session.add(author)
            db.session.flush()
        book.authors.append(author)

    db.session.commit()

    # link to user
    _link_user(book.id, user_id)
    print(f"Linking book {book.id} to user {user_id}")

    return book

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
    return raw or ""

#edition keys are always missing from the search API (90% of the time in search API), backup to call editions API
def _edition_key(work_key: str) -> str | None:
    ed_json = _error_check(f"https://openlibrary.org/{work_key}/editions.json?limit=1")
    if ed_json and ed_json.get("entries"):
        return ed_json["entries"][0]["key"].split("/")[-1]   # "OL12345M"
    return None