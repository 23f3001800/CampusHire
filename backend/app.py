from flask import Flask
from config import DevelopmentConfig
from models import db
from db import security
from resources import auth_bp, api_bp

from flask_security import SQLAlchemyUserDatastore
from models import User, Role 
from flask_cors import CORS



def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"] )
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