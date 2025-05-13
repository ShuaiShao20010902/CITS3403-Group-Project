from flask import Flask
from flask_migrate import Migrate
import os

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'this-is-the-super-secret-key'

    # Import models
    from app.models import db

    # Initialize database
    db.init_app(app)

    # Setup migrations
    migrate = Migrate(app, db)

    # Import and register blueprints
    from app.blueprints import main
    app.register_blueprint(main)

    # Create tables
    with app.app_context():
        db.create_all()

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)