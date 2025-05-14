from flask import Flask
from flask_migrate import Migrate
from flask_mail import Mail
from app.config import Config

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Import models
    from app.models import db

    # Initialize database
    db.init_app(app)

    # Setup migrations
    migrate = Migrate(app, db)

    # Initialize Mail
    mail.init_app(app)

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