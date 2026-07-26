"""
init_db.py — DEVELOPMENT ONLY. Drops every table and reseeds test users.

For production use scripts/bootstrap_db.py, which is idempotent and destroys
nothing.
"""

import os
import sys

# Hard stop, checked BEFORE importing app so it fires regardless of whether the
# production secrets happen to be set. This script calls drop_all(); pointed at
# the production DATABASE_URL it would wipe the live database, and the only
# thing standing between a tired developer and that outcome is which shell they
# happen to be in.
if (os.getenv("APP_ENV") or os.getenv("FLASK_ENV") or "development").lower() == "production":
    sys.exit(
        "✗ Refusing to run init_db.py with APP_ENV=production — it calls drop_all().\n"
        "  Use `python -m scripts.bootstrap_db` instead."
    )

import uuid                                              # noqa: E402
from datetime import datetime, timezone                  # noqa: E402
from app import app                                      # noqa: E402
from models import db, User, Role, Student, Company      # noqa: E402
from flask_security.datastore import SQLAlchemyUserDatastore   # noqa: E402
from flask_security.utils import hash_password           # noqa: E402

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
    # Override with SEED_PASSWORD to avoid a well-known credential even locally.
    TEST_PASSWORD = os.getenv("SEED_PASSWORD", "changeme-dev-only")
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