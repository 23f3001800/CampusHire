from flask import Blueprint, request, jsonify, current_app
from models import User, Student, Company
from db import db
from flask_security.utils import verify_password, hash_password
from flask_security import auth_required, current_user
import uuid
from tasks import send_welcome_email

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def _user_response(user):
    """Build standard user dict for auth responses."""
    role = user.roles[0].name.lower() if user.roles else None
    return {
        'id':         user.id,
        'name':       user.name,
        'email':      user.email,
        'role':       role,
        'active':     user.active,
        'student_id': user.student_profile.id if role == 'student' and user.student_profile else None,
        'company_id': user.company_profile.id if role == 'company' and user.company_profile else None,
    }


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password):
        return jsonify({'message': 'Invalid credentials'}), 401

    if not user.active:
        return jsonify({'message': 'Account is blocked.\n'
        'Please reach out to admin for more details admin@campushire.in'}), 403

    if not user.roles:
        return jsonify({'message': 'No role assigned to this user'}), 403

    return jsonify({'token': user.get_auth_token(), 'user': _user_response(user)}), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role     = data.get('role', '').strip().lower()

    if not all([name, email, password, role]):
        return jsonify({'message': 'name, email, password and role are required'}), 400

    # CRITICAL: Admin registration is BLOCKED - admin is pre-seeded via init_db.py
    if role not in ('student', 'company'):
        return jsonify({'message': 'Registration only allowed for students and companies. Admin accounts are pre-configured.'}), 400

    if len(password) < 8:
        return jsonify({'message': 'Password must be at least 8 characters'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    datastore = current_app.datastore
    active    = True   # companies start inactive until approved

    try:
        user = datastore.create_user(
            name=name, email=email,
            password=hash_password(password),
            active=active,
            fs_uniquifier=str(uuid.uuid4())
        )
        db.session.flush()

        role_obj = datastore.find_role(role)
        if not role_obj:
            db.session.rollback()
            return jsonify({'message': f"Role '{role}' not found in database"}), 400

        datastore.add_role_to_user(user, role_obj)

        if role == 'student':
            s = data.get('student', {})
            db.session.add(Student(
                user_id=user.id,
                roll_number=s.get('rollNumber'),
                branch=s.get('branch'),
                graduation_year=int(s['graduation']) if s.get('graduation') else None,
                phone=s.get('phone'),
            ))
        else:
            c = data.get('recruiter', {})
            db.session.add(Company(
                user_id=user.id,
                company_name=c.get('companyName', '').strip(),
                department=c.get('department'),
                designation=c.get('designation'),
                hr_contact=c.get('phone'),
                website=c.get('webUrl'),
                location=c.get('location'),
                hr_email=email,
                approval_status='Pending',
            ))

        db.session.commit()
        send_welcome_email.delay(user.id)

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

    return jsonify({
        'message': 'Registration successful. Please login.' if role == 'student'
                   else 'Registration successful. Await admin approval.',
        'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': role}
    }), 201


@auth_bp.route('/logout', methods=['POST'])
@auth_required('token')
def logout():
    # Flask-Security tokens are stateless; client discards the token
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/me', methods=['GET'])
@auth_required('token')
def me():
    return jsonify({'user': _user_response(current_user)}), 200