from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_driver():
    options = Options()
    options.add_argument("--headless=new")  # Use headless mode for WSL/servers
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def test_landing_page_loads():
    driver = get_driver()
    driver.get("http://127.0.0.1:5000/")
    assert "Sharing Dashboard" in driver.page_source or "landing" in driver.page_source
    driver.quit()

def test_signup_page_loads():
    driver = get_driver()
    driver.get("http://127.0.0.1:5000/signup")
    assert "Sign Up" in driver.page_source or "signup" in driver.page_source
    driver.quit()

def test_login_page_loads():
    driver = get_driver()
    driver.get("http://127.0.0.1:5000/login")
    assert "Login" in driver.page_source or "login" in driver.page_source
    driver.quit()

def test_browse_page_loads():
    driver = get_driver()
    driver.get("http://127.0.0.1:5000/browse.html")
    assert "Browse" in driver.page_source or "browse" in driver.page_source
    driver.quit()

def test_share_requires_login():
    driver = get_driver()
    driver.get("http://127.0.0.1:5000/share")
    assert "login" in driver.page_source.lower() or driver.current_url.endswith("/login")
    driver.quit()

def test_protected_page_requires_login():
    driver = get_driver()
    driver.get("http://127.0.0.1:5000/share")
    assert "login" in driver.page_source.lower() or driver.current_url.endswith("/login")
    driver.quit()

def test_signup_form_submission():
    driver = get_driver()
    driver.get("http://127.0.0.1:5000/signup")
    driver.find_element("name", "username").send_keys("testuser123")
    driver.find_element("name", "email").send_keys("testuser123@example.com")
    driver.find_element("name", "password").send_keys("TestPassword1!")
    driver.find_element("name", "confirm_password").send_keys("TestPassword1!")
    driver.find_element("css selector", "input.signup-btn").click()
    import time
    time.sleep(1)
    assert "login" in driver.page_source.lower() or "log in" in driver.page_source.lower() or "login" in driver.current_url.lower()
    driver.quit()

def test_signup_duplicate_username():
    driver = get_driver()
    driver.get("http://127.0.0.1:5000/signup")
    driver.find_element("name", "username").send_keys("testuser123")
    driver.find_element("name", "email").send_keys("testuser123@example.com")
    driver.find_element("name", "password").send_keys("TestPassword1!")
    driver.find_element("name", "confirm_password").send_keys("TestPassword1!")
    driver.find_element("css selector", "input.signup-btn").click()
    import time
    time.sleep(1)
    assert "has already been taken" in driver.page_source
    driver.quit()

def test_logout_flow():
    driver = get_driver()
    driver.get("http://127.0.0.1:5000/login")
    driver.find_element("name", "email").send_keys("testuser123@example.com")
    driver.find_element("name", "password").send_keys("TestPassword1!")
    driver.find_element("css selector", "button[type=submit]").click()
    # Click logout (adjust selector as needed)
    driver.find_element("xpath", "//button[contains(text(), 'Log Out')]").click()
    assert "login" in driver.page_source.lower()
    driver.quit()

def test_signup_form_validation_error():
    driver = get_driver()
    driver.get("http://127.0.0.1:5000/signup")
    # Leave fields blank and submit
    driver.find_element("css selector", "input.signup-btn").click()
    assert "required" in driver.page_source.lower() or "error" in driver.page_source.lower()
    driver.quit()