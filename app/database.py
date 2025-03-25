from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

def init_db(app):
    # Create db directory if it doesn't exist
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db')
    os.makedirs(db_dir, exist_ok=True)
    
    # Set database path
    db_path = os.path.join(db_dir, 'bloodpressure.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the app with the extension
    db.init_app(app)
    
    # Import models here to ensure they're known to SQLAlchemy
    from app.models import User, Measurement
    
    # Create tables
    with app.app_context():
        db.create_all()
        db.session.commit()