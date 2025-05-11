from flask import Flask
from flask_migrate import Migrate
import os

# Create app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'this-is-the-super-secret-key'

# Import models after app instance is created to avoid circular imports
from app.models import db, init_db

# Initialize the database
db.init_app(app)

# Setup migrations
migrate = Migrate(app, db)

# Import and setup routes
from app.routes import setup_routes
setup_routes(app)

# Initialize database if needed
with app.app_context():
    db.create_all()

# This allows the app to be run directly
if __name__ == '__main__':
    app.run(debug=True)