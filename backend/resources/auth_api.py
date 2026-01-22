"/login"
"register"

from flask import Blueprint
from ..models import User
from flask_security.utils import verify_password, hash_password

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data=request.get_json()
    email=data["email"]
    password=data["password"]

    if (not email) or (not password):
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first_or_404()
    if not verify_password(password, user.password):
        return jsonify({"message": "Invalid credentials"}), 401

    return jsonify(
        {
            "email":user.email,
            "name": user.name,
            "token": user.get_auth_token()
        }
    )

@auth_bp.route('/register', methods=['POST'])
def register():
    data=request.get_json()
    email=data["email"]
    password=data["password"]
    name=data["name"]
    role=data["role"]
    active=True
    if (not email) or (not password) or (not name) or (not role in ['student', 'company']):
        return jsonify({"message": "All fields are required and role must be valid"}), 400
    
    if role == 'company':
        active = False  # Companies need admin approval
    user = User(email=email, name=name, role=role, active=active, password=hash_password(password))