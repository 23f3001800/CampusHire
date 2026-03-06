"""
Flask-Caching configuration for the placement portal.
Provides server-side caching for API responses.
"""
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'RedisCache', 'CACHE_DEFAULT_TIMEOUT': 1})
