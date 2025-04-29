# Changelogs

---

## Unaccessible Pages
- `bookspecificpage.html` (to be added once backend is done)
- `sharepage.html`
- `sharestats.html`

---

## Issues (Make GitHub Issues Later)
- Navbar CSS issue in `uploadbook.html`
- Secret key for session is very vulnerable
- Book recommendations take ~10 seconds to load
- Book autofill suggestions in `uploadbook.html` are not very accurate (may be an API issue)
- After logout, old "Logged in successfully" message still visible when revisiting login page (should disappear)

---

## To-Do
- Recreate books tables to store some data locally for faster statistics analysis
- Remove and redo the current message feature
- Enable `uploadbook.html` to send data to database
- Complete `bookspecificpage.html` and backend integration

---

## Change Logs
_Track everything merged into `main`._

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