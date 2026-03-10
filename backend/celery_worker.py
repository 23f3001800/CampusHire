"""
celery_worker.py — Celery application factory
=============================================

Run worker:
    celery -A celery_worker.celery worker --loglevel=info

Run beat scheduler (separate terminal):
    celery -A celery_worker.celery beat --loglevel=info

Dev only (worker + beat together):
    celery -A celery_worker.celery worker --beat --loglevel=info
"""

from celery import Celery
from celery.schedules import crontab


def make_celery(app):
    celery = Celery(app.import_name)

    celery.conf.update(
        broker_url          = app.config.get('broker_url',      'redis://localhost:6379/0'),
        result_backend      = app.config.get('result_backend',  'redis://localhost:6379/0'),
        timezone            = app.config.get('CELERY_TIMEZONE', 'Asia/Kolkata'),
        task_serializer     = 'json',
        result_serializer   = 'json',
        accept_content      = ['json'],
        result_expires      = 86400,

        beat_schedule = {
            'daily-deadline-reminders': {
                'task':     'tasks.send_deadline_reminders',
                'schedule': crontab(hour=8, minute=0),
                'options':  {'expires': 3600},
            },
            'monthly-activity-report': {
                'task':     'tasks.send_monthly_activity_report',
                'schedule': crontab(hour=6, minute=0, day_of_month=1),
                'options':  {'expires': 7200},
            },
        },
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


# ── Entry point ───────────────────────────────────────────────────────────────
from app import create_app

flask_app = create_app()
celery    = make_celery(flask_app)

# FIX: autodiscover_tasks(['tasks']) looks for a *package* (folder with __init__.py).
# tasks.py is a flat module so just import it directly — Celery will pick up
# every @shared_task decorated function automatically on import.
import tasks  # noqa: E402, F401