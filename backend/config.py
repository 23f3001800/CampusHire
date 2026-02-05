import os
from datetime import timedelta


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