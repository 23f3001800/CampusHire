"""
seed_data.py — DEVELOPMENT ONLY. Creates dummy students, companies and drives,
all sharing a well-known password.

Never run this against a real deployment: it would create working accounts whose
credentials are published in this file.
"""

import os
import sys

# Checked before importing app so it fires regardless of environment state.
if (os.getenv("APP_ENV") or os.getenv("FLASK_ENV") or "development").lower() == "production":
    sys.exit(
        "✗ Refusing to run seed_data.py with APP_ENV=production — it creates\n"
        "  working accounts that all share one seed password."
    )

import uuid                                                              # noqa: E402
import random                                                            # noqa: E402
from datetime import datetime, timezone, date, timedelta                 # noqa: E402
from app import app                                                      # noqa: E402
from models import db, User, Student, Company, PlacementDrive, Application  # noqa: E402
from flask_security.utils import hash_password                           # noqa: E402

def seed_extended_data():
    with app.app_context():
        datastore = app.datastore
        student_role = datastore.find_role("student")
        company_role = datastore.find_role("company")
        
        # Override with SEED_PASSWORD to avoid a well-known credential even in
        # shared dev environments.
        TEST_PASSWORD = hash_password(os.getenv("SEED_PASSWORD", "changeme-dev-only"))

        # ─── 10 STUDENTS ──────────────────────────────────────────────────────
        print("👨‍🎓 Seeding 10 Students...")
        student_data = [
            ("Vanya rajput", "vanya@study.com", "23F3001811",  9.2, "Computer Science"),
            ("Ananya Sharma", "ananya@study.com", "23F3001801", 8.5, "Information Technology"),
            ("Rohan Das", "rohan@study.com", "23F3001802", 7.8, "Electronics"),
            ("Priya Verma", "priya@study.com", "23F3001803", 9.5, "Computer Science"),
            ("Arjun Mehta", "arjun@study.com", "23F3001804", 8.2, "Mechanical"),
            ("Sneha Iyer", "sneha@study.com", "23F3001805", 8.9, "Information Technology"),
            ("Kabir Singh", "kabir@study.com", "23F3001806", 7.5, "Electrical"),
            ("Ishita Paul", "ishita@study.com", "23F3001807", 9.1, "Computer Science"),
            ("Aditya Joshi", "aditya@study.com", "23F3001808", 8.4, "Electronics"),
            ("Meera Nair", "meera@study.com", "23F3001809", 8.0, "Mechanical")
        ]

        cities = ["Chennai", "Mumbai", "Bengaluru", "Delhi", "Hyderabad", "Pune"]
        skills_list = ["Python", "Java", "React", "SQL", "AWS", "Docker", "FastAPI"]

        for name, email, roll, cgpa, branch in student_data:
            user = datastore.find_user(email=email)
            if not user:
                user = datastore.create_user(
                    email=email, name=name, password=TEST_PASSWORD,
                    active=True, fs_uniquifier=str(uuid.uuid4()), roles=[student_role]
                )
                db.session.flush()

            if not Student.query.filter_by(user_id=user.id).first():
                db.session.add(Student(
                    user=user, roll_number=roll, phone=f"98765{random.randint(10000, 99999)}",
                    date_of_birth=date(2004, 5, 14), gender=random.choice(["Male", "Female"]),
                    city=random.choice(cities), state="India", college_name="IIT Madras",
                    degree="B.Tech", branch=branch, cgpa=cgpa, tenth_percentage=95.0,
                    twelfth_percentage=92.0, graduation_year=2026, current_semester=6,
                    skills=", ".join(random.sample(skills_list, 3)),
                    bio=f"Future {branch} professional looking for growth."
                ))

        # ─── 10 COMPANIES ─────────────────────────────────────────────────────
        print("🏢 Seeding 10 Companies...")
        company_names = [
            ("Love solutions", "hr@lovesolutions.com", "Technology"),
            ("FinEdge Systems", "hr@finedge.com", "Finance"),
            ("HealthTrack", "careers@healthtrack.io", "Healthcare"),
            ("AutoDrive Robotics", "talent@autodrive.com", "Automotive"),
            ("CloudNexus", "recruitment@cloudnexus.net", "Cloud Computing"),
            ("GreenGrid Energy", "jobs@greengrid.in", "Renewable Energy"),
            ("SwiftCommerce", "hiring@swift.com", "E-commerce"),
            ("CyberSentry", "security@cybersentry.com", "Cybersecurity"),
            ("EduFlow", "hr@eduflow.edu", "EdTech"),
            ("NanoChip Corp", "careers@nanochip.com", "Semiconductors")
        ]

        for name, email, industry in company_names:
            user = datastore.find_user(email=email)
            if not user:
                user = datastore.create_user(
                    email=email, name=name, password=TEST_PASSWORD,
                    active=True, fs_uniquifier=str(uuid.uuid4()), roles=[company_role]
                )
                db.session.flush()

            if not Company.query.filter_by(user_id=user.id).first():
                db.session.add(Company(
                    user=user, company_name=name, industry=industry,
                    company_size=random.choice(["Startup", "Medium", "Large"]),
                    location=random.choice(cities), website=f"https://{name.lower().replace(' ', '')}.com",
                    description=f"Leading solutions in {industry}.",
                    hr_email=email, hr_contact="9876500001", approval_status="Approved",
                    verified_at=datetime.now(timezone.utc)
                ))

        db.session.commit()
        
        # ─── MOCK PLACEMENT DRIVES ───────────────────────────────────────────
        print("📢 Creating Active Drives for Testing...")
        all_companies = Company.query.all()
        for i in range(min(5, len(all_companies))):
            drive = PlacementDrive(
                company_id=all_companies[i].id,
                title=f"Software Engineer - {all_companies[i].company_name}",
                description="Hiring for 2026 batch. Technical assessment required.",
                job_type="Full-time", location=all_companies[i].location,
                salary_min=10.0, salary_max=15.0, min_cgpa=8.0,
                eligible_branches="Computer Science, Information Technology",
                eligible_graduation_year=2026,
                drive_date=datetime.now() + timedelta(days=15),
                application_deadline=datetime.now() + timedelta(days=7),
                status="Open", admin_approval_status="Approved"
            )
            db.session.add(drive)

        db.session.commit()
        print("✅ Data Seeded Successfully!")

if __name__ == "__main__":
    seed_extended_data()