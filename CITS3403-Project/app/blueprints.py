from flask import Blueprint

# Create blueprint
main = Blueprint('main', __name__)

# Import routes to register them with this blueprint
# This must be after the blueprint creation to avoid circular imports
from app.routes import *