import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker

from app import app
from models import db, User, Role, Student, Company, PlacementDrive, Application, Placement
from flask_security.datastore import SQLAlchemyUserDatastore
from flask_security.utils import hash_password

fake = Faker()

with app.app_context():
    print("Dropping and recreating all tables...")
    db.drop_all()
    db.create_all()
    
    datastore: SQLAlchemyUserDatastore = app.datastore

    # ─── 1. Create Roles ──────────────────────────────────────────────────────
    print("Initializing roles...")
    admin_role = datastore.find_or_create_role("admin", description="super user")
    student_role = datastore.find_or_create_role("student", description="student user")
    company_role = datastore.find_or_create_role("company", description="company user")
    datastore.commit()

    # ─── 2. Create Fixed Test Users ───────────────────────────────────────────
    print("Creating default test users...")
    if not datastore.find_user(email="admin@study.com"):
        datastore.create_user(
            email="admin@study.com",
            name="admin_01",
            password=hash_password('12345678'),
            active=True,
            fs_uniquifier=str(uuid.uuid4()),
            roles=[admin_role]
        )
        
    if not datastore.find_user(email="student@study.com"):
        base_student = datastore.create_user(
            email="student@study.com",
            name="student_01",
            password=hash_password('12345678'),
            active=True,
            fs_uniquifier=str(uuid.uuid4()),
            roles=[student_role]
        )
        # Create a profile for the fixed test student
        db.session.add(Student(
            user=base_student,
            roll_number="TEST001",
            phone="1234567890",
            college_name="Tech University",
            degree="B.Tech",
            branch="Computer Science",
            cgpa=9.0,
            graduation_year=2026,
            skills="Python, Flask, SQL"
        ))

    if not datastore.find_user(email="abc@company.com"):
        base_company = datastore.create_user(
            email="abc@company.com",
            name="company_01",
            password=hash_password('12345678'),
            active=True,
            fs_uniquifier=str(uuid.uuid4()),
            roles=[company_role]
        )
        # Create a profile for the fixed test company
        db.session.add(Company(
            user=base_company,
            company_name="ABC Corp",
            industry="Technology",
            company_size="Large",
            location="New York, USA",
            approval_status="Approved"
        ))
        
    datastore.commit()
    print("Database initialized with default users and roles.")

    # ─── 3. Generate Dummy Data (Companies) ───────────────────────────────────
    print("Generating dummy companies...")
    companies = list(Company.query.all())  # Start with our base company
    for i in range(5):
        email = f"hr_{i}@hr.com"
        u = datastore.create_user(
            name=fake.company(),
            email=email,
            password=hash_password("12345678"), 
            active=True,
            fs_uniquifier=str(uuid.uuid4()),
            roles=[company_role]
        )
        datastore.commit() # Commit to get user ID

        c = Company(
            user_id=u.id,
            company_name=u.name,
            industry=random.choice(['Tech', 'Finance', 'Manufacturing', 'Retail']),
            company_size=random.choice(['Startup', 'Small', 'Medium', 'Large']),
            location=fake.city(),
            website=fake.url(),
            description=fake.catch_phrase(),
            approval_status='Approved'
        )
        db.session.add(c)
        companies.append(c)
    db.session.commit()

    # ─── 4. Generate Dummy Data (Students) ────────────────────────────────────
    print("Generating dummy students...")
    students = list(Student.query.all()) # Start with our base student
    for i in range(15):
        email = f"student_{i}@univ.edu"
        u = datastore.create_user(
            name=fake.name(),
            email=email,
            password=hash_password("12345678"),
            active=True,
            fs_uniquifier=str(uuid.uuid4()),
            roles=[student_role]
        )
        datastore.commit()

        skill_str = ", ".join(random.sample(['Python', 'Java', 'SQL', 'Flask', 'React'], k=3))
        s = Student(
            user_id=u.id,
            roll_number=f"2023CS{1000+i}",
            phone=fake.phone_number()[:15],
            college_name="Tech University",
            degree="B.Tech",
            branch=random.choice(["Computer Science", "IT", "Electronics"]),
            cgpa=round(random.uniform(7.0, 9.5), 2),
            graduation_year=2026,
            skills=skill_str 
        )
        db.session.add(s)
        students.append(s)
    db.session.commit()

    # ─── 5. Generate Dummy Data (Placement Drives) ────────────────────────────
    print("Generating dummy placement drives...")
    drives = []
    for comp in companies:
        drive = PlacementDrive(
            company_id=comp.id,
            title=f"{comp.company_name} Recruitment 2026",
            description=fake.paragraph(),
            job_type=random.choice(['Full-time', 'Internship']),
            location=comp.location,
            salary_min=500000.0,
            salary_max=1200000.0,
            currency='INR',
            drive_date=datetime.now(timezone.utc) + timedelta(days=random.randint(5, 30)),
            status='Open',
            admin_approval_status='Approved'
        )
        db.session.add(drive)
        drives.append(drive)
    db.session.commit()

    # ─── 6. Generate Dummy Data (Applications & Placements) ───────────────────
    print("Generating dummy applications and placements...")
    for student in students:
        # Every student applies to 1-2 random drives
        chosen_drives = random.sample(drives, k=random.randint(1, 2))
        for drive in chosen_drives:
            status = random.choice(['Applied', 'Shortlisted', 'Rejected', 'Selected'])
            
            app_record = Application(
                student_id=student.id,
                drive_id=drive.id,
                status=status,
                cover_letter=f"Application for {drive.title}."
            )
            db.session.add(app_record)
            
            if status == 'Selected':
                db.session.flush() # Ensure app_record gets an ID
                placement = Placement(
                    student_id=student.id,
                    company_id=drive.company_id,
                    application_id=app_record.id,
                    position_title=fake.job(),
                    salary=random.uniform(600000, 1000000),
                    currency='INR',
                    joining_date=(datetime.now() + timedelta(days=90)).date(),
                    status='Offered'
                )
                db.session.add(placement)
    
    try:
        db.session.commit()
        print("\n=== SUCCESS: Database fully initialized with dummy data! ===")
        print("Test Accounts (Password for all is '123456'):")
        print("  - Admin:   admin@study.com")
        print("  - Student: student@study.com")
        print("  - Company: abc@company.com")
    except Exception as e:
        db.session.rollback()
        print(f"\n!!! Error finalizing dummy data: {e}")