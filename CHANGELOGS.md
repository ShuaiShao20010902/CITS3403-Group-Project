# Changelogs

_Track everything merged into `main`._

### 5th May
- Updated Backend
    - Added the schema for books to be stored locally
    - Backend no longer uses SQLite3 but now uses SQLalchemy
    - Added a script for testing in /static/tests
    - Added a migration script in /migrations/versions
- Updated bookspecificpage.html
    - Links the book recommendation from home page to their book specific page
    - bookspecificpage.html currently makes 3 requests to Open Libraries' API for each book
- Bug Fixes
    - Fixed nav.html not showing in share.html 
    - Fixed route for uploadbook and forgot_password (it seems that the earlier commit did not use the latest version of main at the time)
    - session now starts after signing up 

### 4th May
- app.py is separated into three files
    - models.py： Database models and initialization. This file is responsible for all database-related operations and structures
    - routes.py - All routes and API endpoints. This file handles the HTTP routing and request processing
    - app.py - Main Application Entry Point. This file serves as the application's entry point and coordinator
- Critical Bug Fix
    - Unexpected indent 

### 3rd May
- Created the HTML, CSS, JS and route for share.html

### 29th April
- Finally fixed `README.md` so it displays more information
- Renamed `index.html` ➔ `home.html` (new homepage)
- Renamed `Signup_and_login.html` ➔ `landing.html` (for non-logged-in users) 
- Temporarily removed the `books` table (may re-add later)
- Removed `/venv` that was added in the previous commit
- Implemented login and logout functionality 
    - Passwords are hashed and stored in database
    - Added error messages for incorrect login or duplicate credentials
    - Additionally, `landing.html` is now `/` and `home.html` is moved to `/home.html`
    - Furthermore, users must log in to see `/home.html`, otherwise they are stuck in the landing page
- Updated `home.html`
    - Disabled most features on `home.html` pending backend completion
    - Replaced book recommendations section on home page so that it pulls from API instead of sample data
    - Added a "Welcome back" text that is able to display the user's username used during signup
- Updated `nav.html` 
    - Now has two states (logged in vs logged out)
    - Added "Home" button to `nav.html`
    - Replaced "Sign Up / Login" with "Logout" when logged in
- Updated `uploadbook.html` 
    - Added "Add Book" button in navbar linking to `uploadbook.html`
    - Implemented search and autofill (author, genre) in `uploadbook.html`

### 28th April
- Updated styling and structure for signup and login pages
- Mistakenly included `/venv` (should be ignored)
- Added `bookspecificpage.html` with CSS and HTML
- Added `uploadbook.html` with CSS and HTML

### 26th April
- Separated `nav.html` from `index.html`
- Created CSS and HTML for signup/login page
- Linked `Signup_and_login.html` with `nav.html`
- Linked `publicshare.html` to `nav.html`
- Minor changes on `index.html`

### 21st April
- `index.html` dashboard displays:
  - Book list (user-specific)
  - Book recommendations carousel (all books)
  - Chat room (user-specific messages)
  - Bar graph (books by genre)
- Flask backend set up with routes for `index.html`
- Created database with four tables (`user_chat`, `user_books`, `books`, `users`)
- Added test HTML files in `/templates/`

### 18th April
- Created basic HTML for `Signup_and_login.html`

### 26th March
- Project started

---