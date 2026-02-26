import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker

# Make sure these match your actual import paths
from app import app
from models import db, User, Role, Student, Company, PlacementDrive, Application, Placement, Interview
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
    TEST_PASSWORD = 'password123'
    HASHED_PW = hash_password(TEST_PASSWORD)

    if not datastore.find_user(email="admin@study.com"):
        datastore.create_user(
            email="admin@study.com", name="Admin User", password=HASHED_PW,
            active=True, fs_uniquifier=str(uuid.uuid4()), roles=[admin_role]
        )
        
    if not datastore.find_user(email="student@study.com"):
        base_student = datastore.create_user(
            email="student@study.com", name="Test Student", password=HASHED_PW,
            active=True, fs_uniquifier=str(uuid.uuid4()), roles=[student_role]
        )
        db.session.add(Student(
            user=base_student, roll_number="TEST001", phone="1234567890",
            college_name="Tech University", degree="B.Tech", branch="Computer Science",
            cgpa=9.2, graduation_year=2026, skills="Python, Flask, SQL, VueJS"
        ))

    if not datastore.find_user(email="abc@company.com"):
        base_company = datastore.create_user(
            email="abc@company.com", name="ABC Corp HR", password=HASHED_PW,
            active=True, fs_uniquifier=str(uuid.uuid4()), roles=[company_role]
        )
        db.session.add(Company(
            user=base_company, company_name="ABC Corp", industry="Technology",
            company_size="Large", location="Bangalore, India", approval_status="Approved"
        ))
        
    datastore.commit()

    # ─── 3. Generate Dummy Companies ──────────────────────────────────────────
    print("Generating dummy companies (Mixed Statuses)...")
    companies = list(Company.query.all()) 
    
    # Create 10 more companies with various approval statuses
    for i in range(10):
        u = datastore.create_user(
            name=fake.company(), email=f"hr_{i}@company.com", password=HASHED_PW,
            active=True, fs_uniquifier=str(uuid.uuid4()), roles=[company_role]
        )
        datastore.commit()

        status = random.choices(['Approved', 'Pending', 'Rejected'], weights=[7, 2, 1])[0]
        c = Company(
            user_id=u.id, company_name=u.name,
            industry=random.choice(['Tech', 'Finance', 'Manufacturing', 'EdTech']),
            company_size=random.choice(['Startup', 'Small', 'Medium', 'Large']),
            location=fake.city(), website=fake.url(), description=fake.catch_phrase(),
            approval_status=status
        )
        db.session.add(c)
        companies.append(c)
    db.session.commit()

    # ─── 4. Generate Dummy Students ───────────────────────────────────────────
    print("Generating dummy students...")
    students = list(Student.query.all())
    branches = ["Computer Science", "Information Technology", "Electronics", "Mechanical", "Civil"]
    
    for i in range(30): # Create 30 students
        u = datastore.create_user(
            name=fake.name(), email=f"student_{i}@univ.edu", password=HASHED_PW,
            active=True, fs_uniquifier=str(uuid.uuid4()), roles=[student_role]
        )
        datastore.commit()

        skill_str = ", ".join(random.sample(['Python', 'Java', 'SQL', 'React', 'Docker', 'AWS', 'C++'], k=random.randint(2, 5)))
        s = Student(
            user_id=u.id, roll_number=f"2023CS{1000+i}", phone=fake.phone_number()[:15],
            college_name="Tech University", degree="B.Tech", branch=random.choice(branches),
            cgpa=round(random.uniform(6.5, 9.8), 2), graduation_year=random.choice([2025, 2026]),
            skills=skill_str 
        )
        db.session.add(s)
        students.append(s)
    db.session.commit()

    # ─── 5. Generate Dummy Placement Drives ───────────────────────────────────
    print("Generating dummy placement drives...")
    drives = []
    # Only approved companies can have drives
    approved_companies = [c for c in companies if c.approval_status == 'Approved']
    
    for comp in approved_companies:
        # Create 1 to 3 drives per company
        for _ in range(random.randint(1, 3)):
            drive_status = random.choices(['Open', 'Closed', 'Completed'], weights=[5, 3, 2])[0]
            drive_date = datetime.now(timezone.utc) + timedelta(days=random.randint(-30, 30))
            deadline = drive_date - timedelta(days=5)

            drive = PlacementDrive(
                company_id=comp.id,
                title=f"{random.choice(['SDE', 'Data Analyst', 'Frontend Developer', 'Mechanical Engineer'])} Role",
                description=fake.paragraph(nb_sentences=5),
                job_type=random.choice(['Full-time', 'Internship']),
                location=comp.location,
                salary_min=random.uniform(300000, 700000),
                salary_max=random.uniform(800000, 1500000),
                currency='INR',
                min_cgpa=random.choice([6.0, 7.0, 7.5, 8.0]),
                drive_date=drive_date,
                application_deadline=deadline,
                status=drive_status,
                admin_approval_status=random.choices(['Approved', 'Pending'], weights=[8, 2])[0]
            )
            db.session.add(drive)
            drives.append(drive)
    db.session.commit()

    # ─── 6. Generate Applications, Interviews & Placements ────────────────────
    print("Generating applications, interviews, and placements...")
    for student in students:
        # Each student applies to 3 to 7 random drives
        chosen_drives = random.sample(drives, k=random.randint(3, 7))
        
        for drive in chosen_drives:
            status = random.choices(
                ['Applied', 'Shortlisted', 'Rejected', 'Selected'], 
                weights=[4, 3, 2, 1]
            )[0]
            
            app_record = Application(
                student_id=student.id, drive_id=drive.id, status=status,
                cover_letter=fake.paragraph(nb_sentences=2)
            )
            db.session.add(app_record)
            db.session.flush() # CRITICAL: Generates app_record.id immediately
            
            # If Shortlisted or Selected, they likely had an interview
            if status in ['Shortlisted', 'Selected']:
                interview_mode = random.choice(['Online', 'Onsite'])
                interview = Interview(
                    application_id=app_record.id,
                    interview_type=random.choice(['Technical', 'HR', 'Managerial']),
                    interview_date=datetime.now(timezone.utc) + timedelta(days=random.randint(-10, 10)),
                    interview_mode=interview_mode,
                    interview_link=fake.url() if interview_mode == 'Online' else None,
                    instructions="Be prepared for coding questions." if status == 'Shortlisted' else "Final HR round.",
                    interviewer=fake.name(),
                    feedback="Good candidate." if status == 'Selected' else None
                )
                db.session.add(interview)

            # If Selected, generate a Placement Offer
            if status == 'Selected':
                placement_status = random.choices(['Offered', 'Joined', 'Declined'], weights=[2, 7, 1])[0]
                placement = Placement(
                    student_id=student.id, company_id=drive.company_id,
                    application_id=app_record.id, position_title=drive.title,
                    salary=drive.salary_max, currency=drive.currency,
                    joining_date=(datetime.now(timezone.utc) + timedelta(days=random.randint(30, 90))).date(),
                    status=placement_status
                )
                db.session.add(placement)
                
    db.session.commit()

    print("\n" + "="*50)
    print("SUCCESS: Database fully initialized with massive dummy data!")
    print("Test Accounts (Password for ALL is 'password123'):")
    print("  - Admin:   admin@study.com")
    print("  - Student: student@study.com")
    print("  - Company: abc@company.com")
    print("="*50 + "\n")