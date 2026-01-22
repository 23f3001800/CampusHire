from flask import Flask
from .config import DevelopmentConfig
from .models import db
from .db import security
from flask_security import SQLAlchemyUserDatastore
from .models import User, Role 



def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    datastore=SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, datastore)
    app.datastore=datastore
    with app.app_context():
        db.create_all()
    return app

app=create_app()


if __name__ == "__main__":
    app.run(debug=True)