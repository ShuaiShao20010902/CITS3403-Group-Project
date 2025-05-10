from flask import Flask, request, session

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'this-is-the-super-secret-key'
    
    from app.models import db
    db.init_app(app)
    
    from app.routes import setup_routes
    setup_routes(app)
    
    @app.before_request
    def check_session():
        if request.path == '/' or request.path == '/home.html':
            if not request.referrer:
                session.clear()
    
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)