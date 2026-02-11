from flask_restful import fields




user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
    'role': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
}

student_fields = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    "roll_number": fields.String,
    "phone": fields.String,
    'cgpa': fields.Float,
    "date_of_birth": fields.String,
    "gender": fields.String,
    'full_name': fields.String,
    'degree': fields.String,
    'graduation_year': fields.Integer,
    'skills': fields.String,
    "user": fields.Nested(user_fields)
}

company_fields = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'company_name': fields.String,
    'industry': fields.String,
    'location': fields.String,
    'website': fields.String,
    "approval_status":fields.String,
    'user': fields.Nested(user_fields)
}

job_position_fields = {
    'id': fields.Integer,
    'company_id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'location': fields.String,
    'requirements': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
}
application_fields = {
    'id': fields.Integer,
    'student_id': fields.Integer,   
    'job_id': fields.Integer,
    'status': fields.String,
    'applied_at': fields.DateTime,
    'updated_at': fields.DateTime,
}
