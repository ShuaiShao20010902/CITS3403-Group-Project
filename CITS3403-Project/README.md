In index.html, there are 4 main elements i made
- book list (specific to user)
- recommendations (every book in database rotating in a carousel)
- chat room (only messages to user are visible)
- bar graph (curently set to display number of books in bar graph by genre)

Each of those 4 elemnents take data from the database which is currently filled up with sample data in app.py

Introduction of database. 
There are currently 4 tables and their schemas look like this: 

CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )

CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            synopsis TEXT,
            cover_url TEXT
        )

CREATE TABLE IF NOT EXISTS user_books (
            user_id INTEGER,
            book_id INTEGER,
            read_percent INTEGER DEFAULT 0,
            notes TEXT,
            PRIMARY KEY (user_id, book_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
        )

CREATE TABLE IF NOT EXISTS user_chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender INTEGER,
            receiver INTEGER,
            datestamp TEXT,
            message TEXT,
            FOREIGN KEY (sender) REFERENCES users(user_id),
            FOREIGN KEY (receiver) REFERENCES users(user_id)
        )


Please look through my code and let me know if there are better ways to implement things. 
Like for example is storing every message in a db with unique id the best way to create a chat room? 
What other information should we store about the books? Publisher date? Page length? 
What other statistics should be displayed in the dashboard? 