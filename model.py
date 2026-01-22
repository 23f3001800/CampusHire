from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

# Many-to-Many: Student Skills
student_skills = db.Table('student_skills',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True)
)

# Many-to-Many: Job Position Required Skills
job_skills = db.Table('job_skills',
    db.Column('job_position_id', db.Integer, db.ForeignKey('job_position.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True)
)

# Many-to-Many: User Roles
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # 'Admin', 'Company', 'Student'
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)  # Required by Flask-Security
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    company_profile = db.relationship('Company', backref='user', uselist=False, cascade='all, delete-orphan')

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(15))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    
    # Education
    college_name = db.Column(db.String(255))
    degree = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    graduation_year = db.Column(db.Integer)
    
    # Resume
    resume_link = db.Column(db.String(500))
    resume_filename = db.Column(db.String(255))
    
    # Relationships
    skills = db.relationship('Skill', secondary=student_skills, backref=db.backref('students', lazy='dynamic'))
    applications = db.relationship('Application', backref='student', lazy=True, cascade='all, delete-orphan')
    placements = db.relationship('Placement', backref='student', lazy=True, cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    company_name = db.Column(db.String(255), nullable=False, index=True)
    industry = db.Column(db.String(100))
    company_size = db.Column(db.String(50))  # 'Startup', 'Small', 'Medium', 'Large'
    location = db.Column(db.String(255))
    website = db.Column(db.String(255))
    description = db.Column(db.Text)
    hr_email = db.Column(db.String(120))
    hr_contact = db.Column(db.String(15))
    
    # Company verification
    approval_status = db.Column(db.String(20), default='Pending')  # 'Pending', 'Approved', 'Rejected'
    verified_at = db.Column(db.DateTime)
    
    # Relationships
    job_positions = db.relationship('JobPosition', backref='company', lazy=True, cascade='all, delete-orphan')
    placements = db.relationship('Placement', backref='company', lazy=True, cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Skill(db.Model):
    __tablename__ = 'skill'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(100))  # 'Programming', 'Database', 'Framework', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JobPosition(db.Model):
    __tablename__ = 'job_position'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text)
    job_type = db.Column(db.String(50))  # 'Full-time', 'Internship', 'Contract'
    location = db.Column(db.String(255))
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    currency = db.Column(db.String(10), default='INR')
    min_cgpa = db.Column(db.Float, default=0.0)
    experience_required = db.Column(db.String(100))
    
    # Posting details
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    application_deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Open')  # 'Open', 'Closed', 'Filled'
    
    # Relationships
    skills_required = db.relationship('Skill', secondary=job_skills, backref=db.backref('job_positions', lazy='dynamic'))
    applications = db.relationship('Application', backref='job_position', lazy=True, cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Application(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    job_position_id = db.Column(db.Integer, db.ForeignKey('job_position.id'), nullable=False)
    status = db.Column(db.String(20), default='Applied')  # 'Applied', 'Shortlisted', 'Rejected', 'Selected'
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_date = db.Column(db.DateTime)
    cover_letter = db.Column(db.Text)
    
    # Relationships
    placement = db.relationship('Placement', backref='application', uselist=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Placement(db.Model):
    __tablename__ = 'placement'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), unique=True)
    position_title = db.Column(db.String(150), nullable=False)
    salary = db.Column(db.Float)
    currency = db.Column(db.String(10), default='INR')
    joining_date = db.Column(db.Date)
    offer_letter = db.Column(db.String(500))
    status = db.Column(db.String(20), default='Offered')  # 'Offered', 'Joined', 'Declined'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
