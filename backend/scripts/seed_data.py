import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
from db import db
from models import User, Role, Skill, Student, Company, JobPosition, Application, Placement
from flask_security.utils import hash_password

fake = Faker()

def seed_data():
    print("--- Starting Database Seeding ---")

    # 1. Seed Roles
    roles = {}
    for role_name in ['admin', 'company', 'student']:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=f"{role_name} access")
            db.session.add(role)
        roles[role_name] = role
    
    # 2. Seed Skills
    skill_list = [
        ('Python', 'Programming'), ('Java', 'Programming'), ('SQL', 'Database'),
        ('React', 'Framework'), ('Flask', 'Framework'), ('AWS', 'Cloud'),
        ('Data Analysis', 'Data Science'), ('Communication', 'Soft Skills')
    ]
    all_skills = []
    for s_name, s_cat in skill_list:
        skill = Skill.query.filter_by(name=s_name).first()
        if not skill:
            skill = Skill(name=s_name, category=s_cat)
            db.session.add(skill)
        all_skills.append(skill)
    
    db.session.commit() # Initial commit to ensure Roles and Skills exist

    # 3. Create Companies
    companies = []
    for i in range(5):
        u = User(
            name=fake.company(),
            email=f"hr{i}@company.com",
            password=hash_password("password123"), 
            active=True, # Added active=True for Flask-Security
            fs_uniquifier=str(uuid.uuid4()),
            roles=[roles['company']]
        )
        db.session.add(u)
        db.session.flush() 

        c = Company(
            user_id=u.id,
            industry=fake.job(),
            company_size=random.choice(['Startup', 'Small', 'Medium', 'Large']),
            location=fake.city(),
            website=fake.url(),
            description=fake.catch_phrase(),
            approval_status='Approved'
        )
        db.session.add(c)
        companies.append(c)

    # 4. Create Students
    students = []
    for i in range(15):
        u = User(
            name=fake.name(),
            email=f"student{i}@univ.edu",
            password=hash_password("password123"),
            active=True,
            fs_uniquifier=str(uuid.uuid4()),
            roles=[roles['student']]
        )
        db.session.add(u)
        db.session.flush()

        s = Student(
            user_id=u.id,
            roll_number=f"2023CS{100+i}",
            phone=fake.phone_number()[:15],
            college_name="Tech University",
            degree="B.Tech",
            branch="Computer Science",
            cgpa=round(random.uniform(7.0, 9.8), 2),
            graduation_year=2026,
            skills=random.sample(all_skills, k=3)
        )
        db.session.add(s)
        students.append(s)

    # 5. Create Job Positions
    jobs = []
    for comp in companies:
        for _ in range(2):
            job = JobPosition(
                company_id=comp.id,
                title=fake.job(),
                description=fake.paragraph(),
                job_type=random.choice(['Full-time', 'Internship']),
                location=comp.location,
                salary_min=500000,
                salary_max=1200000,
                # FIX: Use timezone-aware datetime for Python 3.12+
                application_deadline=datetime.now(timezone.utc) + timedelta(days=30),
                skills_required=random.sample(all_skills, k=2)
            )
            db.session.add(job)
            jobs.append(job)
    
    # CRITICAL FIX: Flush here so JobPosition objects get their IDs before Step 6
    db.session.flush()

    # 6. Create Applications & Some Placements
    for student in students:
        applied_jobs = random.sample(jobs, k=2)
        for job in applied_jobs:
            status = random.choice(['Applied', 'Shortlisted', 'Rejected', 'Selected'])
            app = Application(
                student_id=student.id,
                job_position_id=job.id, # Now job.id is guaranteed to be an integer
                status=status,
                cover_letter=fake.sentence()
            )
            db.session.add(app)
            
            if status == 'Selected':
                db.session.flush() # Get app.id
                placement = Placement(
                    student_id=student.id,
                    company_id=job.company_id,
                    application_id=app.id,
                    position_title=job.title,
                    salary=job.salary_max,
                    status='Joined'
                )
                db.session.add(placement)

    try:
        db.session.commit()
        print("--- Seeding Completed Successfully! ---")
    except Exception as e:
        db.session.rollback()
        print(f"Error during commit: {e}")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        seed_data()