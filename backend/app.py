from cache import cache
from flask import Flask
from config import DevelopmentConfig
from models import db
from db import security
from resources import auth_bp, api_bp
from flask_mail import Mail
from flask_security import SQLAlchemyUserDatastore
from models import User, Role 
from flask_cors import CORS


# Initialize Flask-Mail globally
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    # Initialize Flask-Mail
    mail.init_app(app)
     # Initialize Flask-Caching
    cache.init_app(app)
     # ADDED: Enable CORS for frontend communication
    # REASON: Frontend runs on :5173, backend on :5000 - CORS required
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', 'http://localhost:5173'),
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "allow_headers": ["Content-Type", "Authentication-Token"],
            "expose_headers": ["Authentication-Token"],
        }
    })    
    #CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"] )
    datastore=SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, datastore)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.datastore=datastore
    with app.app_context():
        db.create_all()
    return app

app=create_app()


if __name__ == "__main__":
    app.run(debug=True)