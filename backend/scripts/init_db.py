import uuid
from datetime import datetime, timezone
from app import app
from models import db, User, Role, Student, Company
from flask_security.datastore import SQLAlchemyUserDatastore
from flask_security.utils import hash_password

def create_user_if_not_exists(datastore, email, name, password, roles):
    user = datastore.find_user(email=email)
    if user:
        return user
    new_user = datastore.create_user(
        email=email,
        name=name,
        password=password,
        active=True,
        fs_uniquifier=str(uuid.uuid4()),
        roles=roles
    )
    datastore.commit()
    return new_user

with app.app_context():
    print("🧹 Dropping and recreating all tables...")
    db.drop_all()
    db.create_all()

    datastore: SQLAlchemyUserDatastore = app.datastore

    print("🔑 Initializing roles...")
    admin_role = datastore.find_or_create_role("admin", description="super user")
    student_role = datastore.find_or_create_role("student", description="student user")
    company_role = datastore.find_or_create_role("company", description="company user")
    datastore.commit()

    print("👤 Creating core test users...")
    TEST_PASSWORD = 'password123'
    HASHED_PW = hash_password(TEST_PASSWORD)

    # 1. Admin
    create_user_if_not_exists(datastore, "admin@study.com", "Admin User", HASHED_PW, [admin_role])

    # 2. Base Student
    student_user = create_user_if_not_exists(datastore, "student@study.com", "Vikas Rajput", HASHED_PW, [student_role])
    if not Student.query.filter_by(user_id=student_user.id).first():
        db.session.add(Student(
            user=student_user, roll_number="23F3001800", phone="9876543210", alternate_phone="9876543211",
            date_of_birth=datetime(2004, 5, 14).date(), gender="Male",
            address="Hostel 4, Campus Setup", city="Chennai", state="Tamil Nadu", pincode="600036",
            college_name="IIT Madras", degree="B.Tech", branch="Computer Science",
            cgpa=9.2, tenth_percentage=96.5, twelfth_percentage=95.0, graduation_year=2026, current_semester=6,
            skills="Python, FastAPI, Machine Learning, React", bio="Passionate about AI and scalable web systems.",
            linkedin_url="https://linkedin.com/in/test-student", github_url="https://github.com/test-student",
            portfolio_url="https://test-student.dev"
        ))

    # 3. Base Company
    company_user = create_user_if_not_exists(datastore, "abc@company.com", "Cognishield AI", HASHED_PW, [company_role])
    if not Company.query.filter_by(user_id=company_user.id).first():
        db.session.add(Company(
            user=company_user, company_name="Cognishield AI", industry="Technology",
            company_size="Startup", location="Bengaluru, Karnataka", website="https://cognishield.ai",
            description="Building secure and robust AI agents for enterprise environments.",
            hr_email="careers@cognishield.ai", hr_contact="9876500001", department="Engineering", designation="Head of Talent",
            approval_status="Approved", verified_at=datetime.now(timezone.utc)
        ))
    
    db.session.commit()
    print("✅ Core database initialized successfully!\n")