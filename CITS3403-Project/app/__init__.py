from flask import Flask
from flask_migrate import Migrate
from flask_mail import Mail
from app.config import Config
import os

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
def ensure_email_env_vars():
    # Get the path to the .env file in the project root directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

    # Define email-related environment variables
    email_vars = {
        'MAIL_SERVER': 'smtp.gmail.com',
        'MAIL_PORT': '587',
        'MAIL_USE_TLS': 'True',
        'MAIL_USE_SSL': 'False',
        'MAIL_USERNAME': 'booktracker00@gmail.com',
        'MAIL_PASSWORD': 'rhlw kjwh purj ihqe',
        'MAIL_DEFAULT_SENDER': 'booktracker00@gmail.com'
    }

    # Read existing .env file lines
    existing_lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            existing_lines = f.readlines()

    # Create a set of existing environment variable names
    existing_vars = {line.split('=')[0].strip() for line in existing_lines if '=' in line}

    # Prepare new variables to be added
    to_add = []
    for var, val in email_vars.items():
        # Only add variables that don't already exist
        if var not in existing_vars:
            to_add.append(f"{var}={val}\n")

    # Append new variables to the .env file
    if to_add:
        with open(env_path, 'a') as f:
            # Ensure we start on a new line
            if existing_lines and not existing_lines[-1].endswith('\n'):
                f.write('\n')

            # Write new environment variables
            f.writelines(to_add)

ensure_email_env_vars()


# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)