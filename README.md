
## Book Tracker 
A web application that allows users to search for books, track their reading progress, and log their thoughts.  
Key features include:
- **Reading Progress Tracking** with daily log entries and graph visualization.
- **Automatic Book Details** fetched from Open Library API.
- **Social Features** for sharing your reading activity with others.


## CITS3403 Group 80 Members

| Student Number | Name             | GitHub user       |
| -------------- | ---------------- | ----------------- |
| 24006703       | Raynard Djauhari | IIEnat            |
| 22921802       | Melissa Lam      | melmelissa-lam    |
| 23701834       | Shuai Shao       | ShuaiShao20010902 |
| 23994848       | Jonathan Clyde   | Jonno421          |


## How to run the "Book Tracker"


1. **Unzip or clone the app data onto your local device**:  
   ```bash
   git clone https://github.com/ShuaiShao20010902/CITS3403-Group-Project.git
2. **Create a Virtual Environment**
   **For MacOS/Linux:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
   **For Windows:**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   Once activated the terminal prompt should show (venv).
2. **Installing the necessary packages**
   ```bash
   pip install -r requirements.txt
   ```
3. **Initalise the database**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```
4. **Setting up your own secret key to run the web app in your local environment**

   ***Note**: Make sure to replace the "this-is-the-super-secret-key" to your own secret key message.

   **For MacOS/Linux:**
   ```bash
   export SECRET_KEY='this-is-the-super-secret-key'
    ```

   **For Windows:**
   ```bash
   $env:SECRET_KEY = "this-is-the-super-secret-key"
   ```

## Automated Testing

### Unit Tests

Unit tests are provided in the `tests/` directory and use `pytest`.  
All required testing packages, including `pytest`, should be installed automatically when you run:

```sh
pip install -r requirements.txt
```

If for any reason `pytest` is not installed, you can install it manually:

```sh
pip install pytest
```

To run all unit tests:

```sh
pytest
```

### Selenium Browser Tests

Selenium tests simulate real user interactions in a browser.  
All required packages, including `selenium`, should also be installed via `requirements.txt`.  
If not, you can install it manually:

```sh
pip install selenium
```

**Google Chrome must be installed** on your system for these tests to work.

#### Why is Chrome needed?

Selenium uses ChromeDriver to automate the Chrome browser for end-to-end testing.  
If Chrome is not installed, Selenium tests will fail.

#### Installing Google Chrome

- **Windows/Mac:**  
  Download and install from [https://www.google.com/chrome/](https://www.google.com/chrome/)

- **Ubuntu/Debian Linux:**
  ```sh
  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  sudo apt install ./google-chrome-stable_current_amd64.deb
  ```

#### Running Selenium Tests

1. **Start your Flask server** in one terminal:
    ```sh
    flask run
    ```
2. **In another terminal, run:**
    ```sh
    pytest tests/test_selenium.py
    ```


[View Changelog](./CHANGELOGS.md)