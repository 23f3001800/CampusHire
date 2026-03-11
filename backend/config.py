import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()




class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///campushire.sqlite3?timeout=20"
    DEBUG = True 
    SECRET_KEY = "this-is-a-secret-key" 
    SECURITY_PASSWORD_HASH = "argon2"
    SECURITY_PASSWORD_SALT = "this-is-a-password-salt"
    WTF_CSRF_ENABLED = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"


    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}


    CACHE_TYPE = os.getenv('CACHE_TYPE', 'RedisCache')  # RedisCache, SimpleCache, FileSystemCache
    CACHE_REDIS_HOST = os.getenv('CACHE_REDIS_HOST', 'localhost')
    CACHE_REDIS_PORT = int(os.getenv('CACHE_REDIS_PORT', 6379))
    CACHE_REDIS_DB = int(os.getenv('CACHE_REDIS_DB', 1))  # Different from Celery DB (0)
    CACHE_REDIS_URL = os.getenv('CACHE_REDIS_URL', 'redis://localhost:6379/1')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))  # 5 minutes
    CACHE_KEY_PREFIX = 'campushire_'

    # Flask-Mail Configuration
    # MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    # MAIL_PORT = int(os.getenv('MAIL_PORT', 1025))
    # MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    # MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
    # MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'your-email@gmail.com')
    # MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your-app-password')
    # MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@campushire.edu')

    MAIL_SERVER = os.getenv('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 1025))
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = "noreply@campushire.edu"


    _broker = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    CELERY = {
        # ── Connection ────────────────────────────────────────────────────────
        'broker_url':                         _broker,
        'result_backend':                     _broker,

        # ── Serialization ─────────────────────────────────────────────────────
        'task_serializer':                    'json',
        'result_serializer':                  'json',
        'accept_content':                     ['json'],

        # ── Timezone ──────────────────────────────────────────────────────────
        'timezone':                           'Asia/Kolkata',
        'enable_utc':                         True,

        # ── Reliability ───────────────────────────────────────────────────────
        'task_acks_late':                     True,   # ack only after task succeeds
        'task_reject_on_worker_lost':         True,   # re-queue if worker crashes mid-task
        'worker_prefetch_multiplier':         1,      # one task at a time per worker thread

        # ── Results ───────────────────────────────────────────────────────────
        'task_ignore_result':                 False,
        'result_expires':                     3600,   # purge results after 1 hour

        # ── Startup ───────────────────────────────────────────────────────────
        'broker_connection_retry_on_startup': True,   # suppress Celery 6 startup warning
    }

    COLLEGE_NAME           = 'campus hire'
    FRONTEND_URL           = 'localhost:5173'
    ADMIN_EMAIL            = 'admin@campushire.edu' 

    ## caching configuration for development
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_HOST = os.getenv('CACHE_REDIS_HOST', 'localhost')
    CACHE_REDIS_PORT = int(os.getenv('CACHE_REDIS_PORT', 6379))
    CACHE_REDIS_DB = 1  # Use DB 1 (Celery uses DB 0)
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes default
    CACHE_KEY_PREFIX = 'placement_portal_'


    # CORS (if needed)
    #CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')

