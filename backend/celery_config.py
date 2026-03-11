"""
celery_config.py
================
Celery application factory for CampusHire.

FILE NAMING — CRITICAL:
    This file MUST be named celery_config.py, never celery.py.
    Naming it celery.py shadows the installed package and causes:
        ImportError: cannot import name 'Celery' from partially
        initialized module 'celery' (circular import)

HOW TO START:
    # Worker only
    celery -A celery_config.celery_app worker --loglevel=info

    # Beat scheduler only (for cron tasks)
    celery -A celery_config.celery_app beat --loglevel=info

    # Both together (dev convenience — don't use in production)
    celery -A celery_config.celery_app worker --beat --loglevel=info

HOW IT WIRES INTO FLASK (in your create_app):
    from celery_config import celery_init_app
    celery_init_app(app)
    # Tasks can then use @shared_task and current_app freely.
"""

from celery import Celery, Task
from celery.schedules import crontab
from flask import Flask


def celery_init_app(app: Flask) -> Celery:
    """
    Create and configure a Celery instance bound to the Flask app.

    Design decisions:
      - Reads config from app.config["CELERY"] (a dict of lowercase keys).
        This is the only pattern that satisfies Flask (uppercase keys only)
        AND Celery 5+ (lowercase keys only) simultaneously.
      - FlaskTask.__call__ wraps every task body in app.app_context() so
        db, mail, current_app etc. are always available without manual setup.
      - celery.set_default() makes @shared_task find this instance
        automatically — no need to import the celery object in tasks.py.
      - The instance is stored on app.extensions["celery"] so any code
        that has the Flask app can retrieve it cleanly.
    """

    class FlaskTask(Task):
        """Pushes a Flask app context around every task execution."""
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.import_name, task_cls=FlaskTask)

    # Load ONLY Celery settings from the dedicated CELERY dict.
    # Do NOT use celery_app.conf.update(app.config) — that dumps every
    # Flask key (SECRET_KEY, SQLALCHEMY_URI, …) into Celery's namespace
    # and generates a wall of "Unknown setting" warnings.
    celery_app.config_from_object(app.config["CELERY"])

    # Tell the worker which modules contain tasks.
    # Without this the worker starts but @shared_task decorators never run,
    # so every task arrives as "unregistered" and gets discarded.
    celery_app.conf.imports = ("tasks",)

    # Beat schedule — cron tasks
    celery_app.conf.beat_schedule = {
        "daily-deadline-reminders": {
            "task":     "tasks.send_deadline_reminders",
            "schedule": crontab(hour=8, minute=0),                    # every day 08:00
        },
        "monthly-activity-report": {
            "task":     "tasks.send_monthly_activity_report",
             "schedule": crontab(hour=6, minute=0, day_of_month=1),    # 1st of month 06:00 #30.0
        },
    }

    # Required so @shared_task decorators in tasks.py resolve to this instance
    celery_app.set_default()

    # Store on the app so other modules can do:
    #   current_app.extensions["celery"]
    app.extensions["celery"] = celery_app

    return celery_app


# ---------------------------------------------------------------------------
# Module-level bootstrap
# ---------------------------------------------------------------------------
# When Celery CLI runs:
#   celery -A celery_config.celery_app worker
# Python imports this module and looks for an attribute called `celery_app`.
# We create the Flask app here so that attribute exists at module level.
#
# FLASK_ENV controls which config class is used (default: development).
# Set it in your shell or .env before starting the worker:
#   export FLASK_ENV=production
# ---------------------------------------------------------------------------
from app import create_app as _create_app  # noqa: E402

# create_app() takes no arguments — matches the actual app.py signature
_flask_app = _create_app()
celery_app = celery_init_app(_flask_app)