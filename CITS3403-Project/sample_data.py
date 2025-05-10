from datetime import datetime
from models import *
from app import create_app, db

app = create_app()

def populate_data():
    with app.app_context():
        db.session.query(ReadingLog).delete()
        db.session.query(UserBook).delete()
        db.session.query(Book).delete()
        db.session.commit()
        print("Cleared existing data.")

        book1 = Book(
            work_id="OL82563W",
            title="Harry Potter and the Philosopher's Stone",
            author="J.K. Rowling",
            description="Harry discovers he is a wizard on his 11th birthday.",
            subjects="Fantasy, Magic, Wizards",
            number_of_pages=223,
            cover_id=7984916,
            last_fetched=datetime.now(),
        )

        book2 = Book(
            work_id="OL73477W",
            title="1984",
            author="George Orwell",
            description="A dystopian novel set in a totalitarian society ruled by Big Brother.",
            subjects="Dystopia, Politics, Surveillance",
            number_of_pages=328,
            cover_id=7222246,
            last_fetched=datetime.now(),
        )

        book3 = Book(
            work_id="OL27448W",
            title="The Hobbit",
            author="J.R.R. Tolkien",
            description="Bilbo Baggins goes on a quest to reclaim treasure guarded by Smaug.",
            subjects="Fantasy, Adventure, Dragons",
            number_of_pages=310,
            cover_id=14625765,
            last_fetched=datetime.now(),
        )

        book4 = Book(
            work_id="OL45804W",
            title="Fantastic Mr Fox",
            author="Roald Dahl",
            description="The main character of Fantastic Mr. Fox is an extremely clever anthropomorphized fox named Mr. Fox. He lives with his wife and four little foxes. In order to feed his family, he steals food from the cruel, brutish farmers named Boggis, Bunce, and Bean every night.\r\n\r\nFinally tired of being constantly outwitted by Mr. Fox, the farmers attempt to capture and kill him. The foxes escape in time by burrowing deep into the ground. The farmers decide to wait outside the hole for the foxes to emerge. Unable to leave the hole and steal food, Mr. Fox and his family begin to starve. Mr. Fox devises a plan to steal food from the farmers by tunneling into the ground and borrowing into the farmer's houses.\r\n\r\nAided by a friendly Badger, the animals bring the stolen food back and Mrs. Fox prepares a great celebratory banquet attended by the other starving animals and their families. Mr. Fox invites all the animals to live with him underground and says that he will provide food for them daily thanks to his underground passages. All the animals live happily and safely, while the farmers remain waiting outside in vain for Mr. Fox to show up.",
            subjects="Animals, Hunger",
            number_of_pages=180,
            cover_id=6498519,
            last_fetched=datetime.now(),
        )

        book5 = Book(
            work_id="OL26320W",
            title="To Kill a Mockingbird",
            author="Harper Lee",
            description="A novel about racial injustice in the Deep South.",
            subjects="Racism, Law, Justice",
            number_of_pages=281,
            cover_id=5571418,
            last_fetched=datetime.now(),
        )

        db.session.merge(book1)
        db.session.merge(book2)
        db.session.merge(book3)
        db.session.merge(book4)
        db.session.merge(book5)
        db.session.commit()

        # currently hardcoded to user 1
        user_books = [
            UserBook(user_id=1, book_id=book1.work_id, rating=5.0, notes="Loved the magic.", completed=False),
            UserBook(user_id=1, book_id=book2.work_id, rating=4.5, notes="Disturbing but brilliant.", completed=False),
            UserBook(user_id=1, book_id=book3.work_id, rating=5.0, notes="Great adventure.", completed=False),
            UserBook(user_id=1, book_id=book4.work_id, rating=4.0, notes="Beautifully written.", completed=False),
            UserBook(user_id=1, book_id=book5.work_id, rating=5.0, notes="Timeless classic.", completed=False),
        ]
        for ub in user_books:
            db.session.merge(ub)
        db.session.commit()

        # currently hardcoded to user 1
        logs = [
            ReadingLog(user_id=1, book_id=book1.work_id, date=date(2025, 5, 1), pages_read=50),
            ReadingLog(user_id=1, book_id=book1.work_id, date=date(2025, 5, 2), pages_read=173),
            ReadingLog(user_id=1, book_id=book2.work_id, date=date(2025, 5, 3), pages_read=100),
            ReadingLog(user_id=1, book_id=book2.work_id, date=date(2025, 5, 4), pages_read=228),
            ReadingLog(user_id=1, book_id=book3.work_id, date=date(2025, 5, 5), pages_read=150),
            ReadingLog(user_id=1, book_id=book3.work_id, date=date(2025, 5, 6), pages_read=160),
            ReadingLog(user_id=1, book_id=book4.work_id, date=date(2025, 5, 7), pages_read=80),
            ReadingLog(user_id=1, book_id=book4.work_id, date=date(2025, 5, 8), pages_read=100),
            ReadingLog(user_id=1, book_id=book5.work_id, date=date(2025, 5, 9), pages_read=150),
            ReadingLog(user_id=1, book_id=book5.work_id, date=date(2025, 5, 10), pages_read=131),
        ]
        for log in logs:
            db.session.merge(log)
        db.session.commit()

if __name__ == "__main__":
    populate_data()
    print("Sample data populated successfully.")