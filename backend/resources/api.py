from flask_restful import Resource, reqparse, marshal_with, marshal
from flask import request, jsonify, current_app
from services.JobService import JobService
from resources.field_marshal import job_position_fields, company_fields, student_fields, application_fields, user_fields
from flask import request, jsonify
from models import db
from services.CompanyService import CompanyService
from services.StudentService import StudentService
from flask_security import auth_required, roles_required, current_user, roles_accepted


studparser = reqparse.RequestParser()
studparser.add_argument('full_name', type=str, required=True)
studparser.add_argument('university', type=str, required=True)
studparser.add_argument('degree', type=str, required=True)
studparser.add_argument('graduation_year', type=int, required=True)
studparser.add_argument('skills', type=str, required=True)
studparser.add_argument('student_id', type=int, required=False)



class StudentResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def get(self, student_id):
        student = StudentService.get_student_by_id(student_id)
        if not student:
            return {'message': 'Student not found'}, 404
        return marshal(student, student_fields), 200
    
    @auth_required('token')
    @roles_required('student')
    def put(self, student_id):
        args = studparser.parse_args()
        data = {
            'full_name': args['full_name'],
            'university': args['university'],
            'degree': args['degree'],
            'graduation_year': args['graduation_year'],
            'skills': args['skills']
        }
        updated_student = StudentService.update_student(student_id, data)
        if not updated_student:
            return {'message': 'Student not found'}, 404
        return marshal(updated_student, student_fields), 200
    
    @auth_required('token')
    @roles_required('student')
    def patch(self, student_id):
        args = studparser.parse_args()
        data = {key: value for key, value in args.items() if value is not None}
        updated_student = StudentService.update_student(student_id, data)
        if not updated_student:
            return {'message': 'Student not found'}, 404
        return marshal(updated_student, student_fields), 200
    
    @auth_required('token')
    @roles_required('student')
    def delete(self, student_id):
        deleted = StudentService.delete_student(student_id)
        if not deleted:
            return {'message': 'Student not found'}, 404
        return {'message': 'Student deleted successfully'}, 200
    
class StudentListResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        students = StudentService.get_all_students()
        return marshal(students, student_fields), 200


comparser= reqparse.RequestParser()
comparser.add_argument('company_name', type=str, required=True) 
comparser.add_argument('industry', type=str, required=True)
comparser.add_argument('location', type=str, required=True)


class companyresource(Resource):
    @auth_required('token')
    @roles_required('company')
    def get(self, company_id):
        company = CompanyService.get_company_by_id(company_id)
        if not company:
            return {'message': 'Company not found'}, 404
        return marshal(company, company_fields), 200
    
    @auth_required('token')
    @roles_required('company')
    def put(self, company_id):
        args = comparser.parse_args()
        data = {
            'company_name': args['company_name'],
            'industry': args['industry'],
            'location': args['location']
        }
        updated_company = CompanyService.update_profile(company_id, data)
        if not updated_company:
            return {'message': 'Company not found'}, 404
        return marshal(updated_company, company_fields), 200
    
    @auth_required('token')
    @roles_required('company')
    def patch(self, company_id):
        args = comparser.parse_args()
        data = {key: value for key, value in args.items() if value is not None}
        updated_company = CompanyService.update_profile(company_id, data)
        if not updated_company:
            return {'message': 'Company not found'}, 404
        return marshal(updated_company, company_fields), 200
    
    @auth_required('token')
    @roles_required('company')
    def delete(self, company_id):
        deleted = CompanyService.delete_profile(company_id)
        if not deleted:
            return {'message': 'Company not found'}, 404
        return {'message': 'Company deleted successfully'}, 200
    
class CompanyListResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        companies = CompanyService.get_all_companies()
        return marshal(companies, company_fields), 200


jobparser = reqparse.RequestParser()
jobparser.add_argument('title', type=str, required=True)
jobparser.add_argument('description', type=str, required=True)
jobparser.add_argument('location', type=str, required=True)
jobparser.add_argument('requirements', type=str, required=True)
jobparser.add_argument('company_id', type=int, required=True)


class JobResource(Resource):
    def get(self, job_id):
        job = JobService.get_jobs(job_id)
        if not job:
            return {'message': 'Job not found'}, 404
        return marshal(job, job_position_fields), 200
    
    @auth_required('token')
    @roles_required('company')
    def post(self):
        args = jobparser.parse_args()
        data = {
            'title': args['title'],
            'description': args['description'],
            'location': args['location'],
            'requirements': args['requirements'],
            'company_id': args['company_id']
        }
        new_job = JobService.create_job(data)
        return marshal(new_job, job_position_fields), 201
    
    @auth_required('token')
    @roles_required('company')
    def put(self, job_id):
        args = jobparser.parse_args()
        data = {
            'title': args['title'],
            'description': args['description'],
            'location': args['location'],
            'requirements': args['requirements']
        }
        updated_job = JobService.update_job(job_id, data)
        if not updated_job:
            return {'message': 'Job not found'}, 404
        return marshal(updated_job, job_position_fields), 200
    
    def patch(self, job_id):
        args = jobparser.parse_args()
        data = {key: value for key, value in args.items() if value is not None}
        updated_job = JobService.update_job(job_id, data)
        if not updated_job:
            return {'message': 'Job not found'}, 404
        return marshal(updated_job, job_position_fields), 200
    
    def delete(self, job_id):
        deleted = JobService.delete_job(job_id)
        if not deleted:
            return {'message': 'Job not found'}, 404
        return {'message': 'Job deleted successfully'}, 200


class JobListResource(Resource):
    def get(self):
        jobs = JobService.get_all_jobs()
        return marshal(jobs, job_position_fields), 200
    