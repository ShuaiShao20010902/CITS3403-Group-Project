# Changelogs

_Track everything merged into `main`._

### 12th May
- Backend Improvements
    - Move the backend and frontend to the app folder to make it easier to manage and looks well structured.
    - Created blueprints to improve code organization, scalability, reusability and the URL Prefix Management.
- Bug Fix
    - Rating and Notes now correctly update the database.

### 11th May
- Browse Page Functionality
    - Removed all searches relating to editions.json
    - requirement.txt flask 3.0 not able to be used with flask caching so changed to 2.3.3
    - Updated search.js to now pull from the search endpoint
    - Created utils.py to store functions that pull info from the API back to database
    - User manually enter information via flask forms
    - Functional manual add into database
    - Updated uploadbook to add the correct information + css
- Updated uploadbook
    - Make uploadbook look a little bit better + sort button look better
    - Deleted comments
    - Added sort function
- Updated bookspecificpage.html (Now has 3 functional parts)
    - Rating System and Notes system both properly updates field in database but design may need to be updated 
    - Tracking reading progress is partially implemented so that it is able to retrieve and modify entries in the Reading Log table. However there are errors when trying to update the entries of existing entries.
        

### 10th May
- Updated Backend
    - Authors and Books table added (requires API data from editions.json)
    - Authors table has been deleted and replaced with a author field in the books table
    - All fields whose information were from the editions endpoint has been deleted (isbn, publisher, edition IDs, publish date has been removed)
    - This means that page number will be forced to be inputted by the user
    - ID field of books has been deleted and the work_id is now used as Primary key

### 9th May
- Updated Dashboard
    - Added a continue reading section
    - Removed the recommendations (will now be in the browse page)
    - Database has been migrated again
    - Updated home.html and home.css and the route for it
    - Removed a route that's no longer in use (user_chat)
- Created Browse Page
    - Replaces the old uploadbook.html page 
    - Added the routes + search.js that links to the Open Library API
- Browse page Functionality 
    - Add books into database (Partially implemented)
    - There are many edge cases that would cause errors paticularly related to edition.json
    - Book editions are selected by looking through a lot of the editions to find the best one
    - However, errors may happen since it is not garanteed that editions.json will not having missing data


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