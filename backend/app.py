from flask import Flask
from flask_cors import CORS
from flask_security import SQLAlchemyUserDatastore

from config import DevelopmentConfig
from extensions import cache, mail, security
from models import Role, User, db
from resources import api_bp, auth_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)
    mail.init_app(app)
    cache.init_app(app)

    # ── Celery — must be init'd here so app.extensions["celery"] exists ───────
    from celery_config import celery_init_app
    celery_init_app(app)

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS(app, resources={
        r"/api/*": {
            "origins":         app.config.get("CORS_ORIGINS", "http://localhost:5173"),
            "methods":         ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "allow_headers":   ["Content-Type", "Authentication-Token"],
            "expose_headers":  ["Authentication-Token"],
        }
    })

    # ── Flask-Security ────────────────────────────────────────────────────────
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, datastore)
    app.datastore = datastore

    # ── Blueprints ────────────────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    # ── DB ────────────────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)