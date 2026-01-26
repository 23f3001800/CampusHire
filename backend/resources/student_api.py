from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user  
student_bp = Blueprint('student', __name__, url_prefix='/api/student')
@student_bp.route('/dashboard', methods=['GET'])





@auth_required('token')
def student_dashboard():
    return jsonify({
        "email": current_user.email,
        "role": current_user.roles[0].name
    })