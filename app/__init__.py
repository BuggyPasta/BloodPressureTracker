from flask import Flask
from .database import init_db
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    app.config['PREFERRED_URL_SCHEME'] = 'http'

    # Ensure data directories exist
    os.makedirs('db', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('config', exist_ok=True)

    # Initialize database
    init_db(app)

    # Register blueprints
    from .routes import bp
    app.register_blueprint(bp)

    return app