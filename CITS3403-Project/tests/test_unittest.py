import pytest
from app import create_app
from app.models import db

@pytest.fixture
def client():
    app = create_app()  # <-- Create the app instance here
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_landing_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Sharing Dashboard" in response.data or b"landing" in response.data

def test_signup_page(client):
    response = client.get('/signup')
    assert response.status_code == 200
    assert b"Sign Up" in response.data or b"signup" in response.data

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data or b"login" in response.data

def test_browse_page(client):
    response = client.get('/browse.html')
    assert response.status_code == 200
    assert b"Browse" in response.data or b"browse" in response.data

def test_share_page_requires_login(client):
    response = client.get('/share')
    # Should redirect to login if not logged in
    assert response.status_code in (302, 401)
