"""
Celery configuration for background jobs.
"""
from celery import Celery
from celery.schedules import crontab

celery = Celery('placement_portal',
                broker='redis://localhost:6379/0',
                backend='redis://localhost:6379/0',
                include=['tasks'])

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    
    # Celery Beat schedule for recurring tasks
    beat_schedule={
        # Daily reminder - runs at 8 AM every day
        'daily-application-reminders': {
            'task': 'tasks.send_daily_reminders',
            'schedule': crontab(hour=8, minute=0),
        },
        # Monthly report - first day of month at 9 AM
        'monthly-activity-report': {
            'task': 'tasks.generate_monthly_report',
            'schedule': crontab(day_of_month=1, hour=9, minute=0),
        },
    }
)

# # Auto-discover tasks
# celery.autodiscover_tasks(['backend'])