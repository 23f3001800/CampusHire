import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_security import SQLAlchemyUserDatastore

from config import get_config
from extensions import cache, mail, security
from models import Role, User, db
from resources import api_bp, auth_bp


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

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
            "origins":         app.config["CORS_ORIGINS"],
            "methods":         ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers":   ["Content-Type", "Authentication-Token"],
            "expose_headers":  ["Authentication-Token", "Content-Disposition"],
        }
    })

    # ── Flask-Security ────────────────────────────────────────────────────────
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, datastore)
    app.datastore = datastore

    # ── Uploads ───────────────────────────────────────────────────────────────
    # Created once at boot so no request handler has to care whether it exists.
    for sub in ('resumes', 'offers'):
        os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], sub), exist_ok=True)

    # ── Blueprints ────────────────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/api/health")
    def health():
        """
        Liveness + dependency probe. Render polls this to decide whether a
        deploy succeeded, so it returns 200 only when the DB actually answers.
        """
        from sqlalchemy import text

        checks = {}
        status = 200

        try:
            db.session.execute(text("SELECT 1"))
            checks["database"] = "ok"
        except Exception as exc:
            checks["database"] = f"error: {exc.__class__.__name__}"
            status = 503

        # Redis is a soft dependency — the app degrades to DB reads without it,
        # so a cache outage is reported but does not fail the health check.
        try:
            cache.set("_health", "1", timeout=10)
            checks["cache"] = "ok" if cache.get("_health") == "1" else "degraded"
        except Exception as exc:
            checks["cache"] = f"degraded: {exc.__class__.__name__}"

        return jsonify({
            "status": "ok" if status == 200 else "unhealthy",
            "env":    os.getenv("APP_ENV", "development"),
            "checks": checks,
        }), status

    # ── DB bootstrap ──────────────────────────────────────────────────────────
    # Development only. In production the schema is created by the release
    # command (scripts/bootstrap_db.py) — running create_all() here would fire
    # once per Gunicorn worker and race on a cold database.
    if app.config.get("AUTO_CREATE_DB", app.config["DEBUG"]):
        with app.app_context():
            db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 5000)),
        debug=app.config["DEBUG"],
    )
