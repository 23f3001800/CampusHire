# Package initialization
from flask_restful import Api
from flask import Blueprint
from resources.auth_api import auth_bp
from resources.api import StudentListResource,StudentResource, CompanyListResource, companyresource, JobListResource, JobResource


api_bp = Blueprint('api', __name__, url_prefix='/api')

api = Api(api_bp)

api.add_resource(StudentListResource, '/admin/students')
api.add_resource(StudentResource, '/admin/students/<int:student_id>')
api.add_resource(CompanyListResource, '/admin/companies')
api.add_resource(companyresource, '/company/<int:company_id>')
api.add_resource(JobListResource, '/admin/jobs')
api.add_resource(JobResource, '/jobs/<int:job_id>')