## Book Tracker 
A book tracking website that allows users to search for books and track their reading progress and thoughts on it. Mian feature allows users to create reading log entries for each book and see the progress on a graph. Book information is also retrieved from an API so users do not have to type in so much data which helps with the user experience. Also includes a social aspect where users can share data with one another. 

## Setup Guide

1. **Clone this repository**
   ```sh
   git clone https://github.com/ShuaiShao20010902/CITS3403-Group-Project
   cd <repository_folder>
   ```

2. **Create a Virtual Environment**
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Requirements**
```
pip install -r requirements.txt
```

4. **Setup Session Key**
In the root directory, create a file named **.env** and in it define the session key
```
SECRET_KEY=somelongandsecurekey123
```

5. **Run the Program**
In the root directory run this:
```
flask run
```

## CITS3403 Group 80 Members
- 24006703 Raynard Djauhari
- 22921802 Melissa Lam
- 23701834 Shuai Shao
- 23994848 Jonathan Clyde

## Automated Testing

### Unit Tests

Unit tests are provided in the `tests/` directory and use `pytest`.  
To run all unit tests:

```sh
pytest
```

### Selenium Browser Tests

Selenium tests simulate real user interactions in a browser.

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