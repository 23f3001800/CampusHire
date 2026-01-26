# Package initialization
from flask_restful import Api
from flask import Blueprint
from resources.auth_api import auth_bp

api_bp = Blueprint('api', __name__, url_prefix='/api')

api = Api(api_bp)
