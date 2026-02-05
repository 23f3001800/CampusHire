from app import app
from models import db
from flask_security.datastore import SQLAlchemyUserDatastore
from flask_security.utils import hash_password

with app.app_context():
    db.drop_all()
    db.create_all()
    datastore: SQLAlchemyUserDatastore = app.datastore

    # Create roles
    admin_role = datastore.find_or_create_role("admin", description = "super user")
    student_role = datastore.find_or_create_role("student", description = "student user")
    company_role = datastore.find_or_create_role("company", description = "company user")

    if not datastore.find_user(email = "admin@study.com"):
        datastore.create_user(
            email = "admin@study.com",
            name = "admin_01",
            password = hash_password('123456'),
        )
    if not datastore.find_user(email = "student@study.com"):
        datastore.create_user(
            email = "student@study.com",
            name = "student_01",
            password = hash_password('123456'),
        )
    if not datastore.find_user(email = "abc@company.com"):
        datastore.create_user(
            email = "abc@company.com",
            name = "company_01",
            password = hash_password('123456'),
        ) 

    try:
        db.session.commit()
        print("Database initialized with roles in roles table and users in users table.") 
    except Exception as e:
        db.session.rollback()
        print(f"Error committing roles: {e}")

    # Create an admin user
    admin_user = datastore.find_user(email="admin@study.com")
    student_user = datastore.find_user(email="student@study.com")
    company_user = datastore.find_user(email="abc@company.com")

    admin_role = datastore.find_role("admin")
    student_role = datastore.find_role("student")
    company_role = datastore.find_role("company")

    datastore.add_role_to_user(admin_user, admin_role)
    datastore.add_role_to_user(student_user, student_role)
    datastore.add_role_to_user(company_user, company_role)
    try:
        db.session.commit() 
        print("Database initialized with default users and roles.")
    except Exception as e:
        db.session.rollback()
        print(f"Error committing user roles: {e}")
