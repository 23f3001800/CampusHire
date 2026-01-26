from flask import Blueprint, request, jsonify, current_app
from models import User, Role, Student, Company
from db import db, security
from flask_security.utils import verify_password, hash_password
import uuid

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    if (not email or not password):
        return jsonify({"message": "invalid input"}), 400
    
    user = User.query.filter_by(email = email).first_or_404()

    if not verify_password(password, user.password):
        return jsonify({"message": "invalid credentials"}), 401
    
    return jsonify({
        "token": user.get_auth_token(),
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.roles[0].name
        }
        }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data=request.get_json()
    name = data["name"]
    email = data["email"]
    password = data["password"]
    role= data["role"]

    active=True

    if (not name or not email or not password or not role in ["student", "company"]):
        return jsonify({"message": "invalid input"}), 400
    
    if role == "company":
        active = False

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"message": "user already exists"}), 400
    
    datastore = current_app.datastore

    datastore.create_user(name = name, email = email, password = hash_password(password), active = active)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"message": f"Error creating user: {e}"}, 400
    
    role = datastore.find_role(role)
    user = datastore.find_user(email = email)
    datastore.add_role_to_user(user, role)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"message": f"Error assigning role: {e}"}, 400
    
    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
    }), 201