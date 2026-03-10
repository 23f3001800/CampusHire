from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_security import Security


db=SQLAlchemy()
security=Security()


mail = Mail()
db = SQLAlchemy()
cache = Cache()

