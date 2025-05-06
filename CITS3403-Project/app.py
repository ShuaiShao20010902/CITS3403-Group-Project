from flask import Flask
from models import db, init_db
from routes import setup_routes

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'this-is-the-super-secret-key'

    db.init_app(app)             # from models
    setup_routes(app)            # register all routes
    return app

if __name__ == '__main__':
    app = create_app()
    init_db(app)
    app.run(debug=True)
