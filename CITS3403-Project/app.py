from flask import Flask
import os
from models import init_db
from routes import setup_routes

def create_app():
    # Create and configure the app
    app = Flask(__name__)
    
    # Security Risk note (preserved from original)
    # I am aware this is bad practice but this will be a problem for the future - Enat
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this-is-the-super-secret-key')
    
    # Set up all routes
    setup_routes(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    init_db()  # Initialize database
    app.run(debug=True)