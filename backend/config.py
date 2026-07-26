"""
config.py — CampusHire configuration
====================================

Three classes:
    Config             shared defaults, everything env-overridable
    DevelopmentConfig  local: SQLite, Mailpit, localhost Redis, DEBUG on
    ProductionConfig   Render: Postgres, real SMTP, managed Redis, DEBUG off

Selection happens in app.py via APP_ENV (default: development).
Nothing secret is hardcoded here — production reads SECRET_KEY and
SECURITY_PASSWORD_SALT from the environment and refuses to boot without them.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


def _csv(name, default=''):
    """Comma-separated env var -> list of stripped, non-empty strings."""
    return [v.strip() for v in os.getenv(name, default).split(',') if v.strip()]


def _normalize_db_url(url):
    """
    Render (and Heroku) hand out postgres:// URLs. SQLAlchemy 2.x dropped that
    alias and only accepts postgresql://. Rewrite it, and pin the psycopg2
    driver explicitly so the dialect never guesses wrong.
    """
    if not url:
        return url
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    if url.startswith('postgresql://'):
        url = url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    return url


def _celery_settings():
    broker = os.getenv('CELERY_BROKER_URL') or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    return {
        'broker_url':     broker,
        'result_backend': os.getenv('CELERY_RESULT_BACKEND') or broker,

        'task_serializer':   'json',
        'result_serializer': 'json',
        'accept_content':    ['json'],

        'timezone':   os.getenv('CELERY_TIMEZONE', 'Asia/Kolkata'),
        'enable_utc': True,

        'task_acks_late':             True,
        'task_reject_on_worker_lost': True,
        'worker_prefetch_multiplier': 1,

        'task_ignore_result': False,
        'result_expires':     3600,

        'broker_connection_retry_on_startup': True,
    }


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # ── Core ──────────────────────────────────────────────────────────────────
    DEBUG   = False
    TESTING = False

    SECRET_KEY             = os.getenv('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')

    # ── Database ──────────────────────────────────────────────────────────────
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Off by default: in production the schema is owned by the release command,
    # not by whichever Gunicorn worker happens to boot first.
    AUTO_CREATE_DB = _bool('AUTO_CREATE_DB', False)
    SQLALCHEMY_ENGINE_OPTIONS = {
        # Render's managed Postgres drops idle connections; recycle before it does
        # and verify liveness on checkout so a stale socket never reaches a request.
        'pool_pre_ping': True,
        'pool_recycle':  280,
    }

    # ── Flask-Security ────────────────────────────────────────────────────────
    SECURITY_PASSWORD_HASH               = 'argon2'
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    SECURITY_TOKEN_MAX_AGE               = int(os.getenv('SECURITY_TOKEN_MAX_AGE', 86400))
    WTF_CSRF_ENABLED                     = False   # token auth, no cookies/forms
    SECURITY_CSRF_PROTECT_MECHANISMS     = []

    # ── Uploads ───────────────────────────────────────────────────────────────
    # Single source of truth. Every upload/serve path in the app resolves through
    # this — see resources/storage.py. Absolute, so it never depends on CWD.
    UPLOAD_FOLDER      = os.path.abspath(os.getenv('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'uploads')))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))   # 5 MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

    # ── Redis / cache ─────────────────────────────────────────────────────────
    REDIS_URL             = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE            = os.getenv('CACHE_TYPE', 'RedisCache')
    CACHE_REDIS_URL       = os.getenv('CACHE_REDIS_URL') or os.getenv('REDIS_URL', 'redis://localhost:6379/1')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    CACHE_KEY_PREFIX      = os.getenv('CACHE_KEY_PREFIX', 'campushire_')

    # ── Mail ──────────────────────────────────────────────────────────────────
    MAIL_SERVER         = os.getenv('MAIL_SERVER', 'localhost')
    MAIL_PORT           = int(os.getenv('MAIL_PORT', 1025))
    MAIL_USE_TLS        = _bool('MAIL_USE_TLS', False)
    MAIL_USE_SSL        = _bool('MAIL_USE_SSL', False)
    MAIL_USERNAME       = os.getenv('MAIL_USERNAME') or None
    MAIL_PASSWORD       = os.getenv('MAIL_PASSWORD') or None
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@campushire.edu')
    MAIL_SUPPRESS_SEND  = _bool('MAIL_SUPPRESS_SEND', False)

    # ── App identity / URLs ───────────────────────────────────────────────────
    COLLEGE_NAME = os.getenv('COLLEGE_NAME', 'CampusHire')
    ADMIN_EMAIL  = os.getenv('ADMIN_EMAIL', 'admin@campushire.edu')
    # Must include the scheme — these get embedded in outgoing email links.
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173').rstrip('/')
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000').rstrip('/')

    CORS_ORIGINS = _csv('CORS_ORIGINS', 'http://localhost:5173')

    # ── Celery ────────────────────────────────────────────────────────────────
    # Plain dict, not a @property: Flask's from_object() is called with the config
    # *class*, and getattr on a class returns the property object itself rather
    # than evaluating it. Celery would then receive a property and blow up.
    CELERY = _celery_settings()


class DevelopmentConfig(Config):
    DEBUG          = True
    AUTO_CREATE_DB = _bool('AUTO_CREATE_DB', True)

    SECRET_KEY             = os.getenv('SECRET_KEY', 'dev-only-secret-key-not-for-production')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', 'dev-only-password-salt')

    SQLALCHEMY_DATABASE_URI = _normalize_db_url(os.getenv('DATABASE_URL')) or \
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'campushire.sqlite3')}?timeout=20"

    # SQLite ignores pooling options and errors on some of them.
    SQLALCHEMY_ENGINE_OPTIONS = {}


class ProductionConfig(Config):
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = _normalize_db_url(os.getenv('DATABASE_URL'))

    # Behind Render's TLS terminator, so cookies/redirects must stay https-aware.
    PREFERRED_URL_SCHEME  = 'https'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    @classmethod
    def validate(cls):
        """
        Fail fast at boot rather than 500-ing on the first request — or worse,
        silently running production on the development secret key.
        """
        missing = [
            name for name in ('SECRET_KEY', 'SECURITY_PASSWORD_SALT', 'SQLALCHEMY_DATABASE_URI')
            if not getattr(cls, name, None)
        ]
        if missing:
            raise RuntimeError(
                'ProductionConfig is missing required environment variables: '
                + ', '.join('DATABASE_URL' if m == 'SQLALCHEMY_DATABASE_URI' else m for m in missing)
            )
        if not cls.CORS_ORIGINS:
            raise RuntimeError('CORS_ORIGINS must be set in production (comma-separated origins).')


CONFIG_MAP = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
}


def get_config(name=None):
    """Resolve a config class from APP_ENV (or an explicit name)."""
    env = (name or os.getenv('APP_ENV') or os.getenv('FLASK_ENV') or 'development').strip().lower()
    cfg = CONFIG_MAP.get(env, DevelopmentConfig)
    if hasattr(cfg, 'validate'):
        cfg.validate()
    return cfg
