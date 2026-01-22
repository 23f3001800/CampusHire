from celery import Celery

def make_celery(app_name):
    celery = Celery(
        app_name,
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0'
    )
    return celery

celery_app = make_celery('placement_system')