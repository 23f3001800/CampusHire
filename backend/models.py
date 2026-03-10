from extensions import db
from flask_security import UserMixin, RoleMixin
from datetime import datetime

# ─── Association Tables ───────────────────────────────────────────────────────

user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

# ─── Auth Models ──────────────────────────────────────────────────────────────

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(120), nullable=False)
    email          = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password       = db.Column(db.String(255), nullable=False)
    active         = db.Column(db.Boolean, default=True)
    fs_uniquifier  = db.Column(db.String(64), unique=True, nullable=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles           = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    company_profile = db.relationship('Company', backref='user', uselist=False, cascade='all, delete-orphan')

# ─── Student Model ────────────────────────────────────────────────────────────

class Student(db.Model):
    __tablename__ = 'student'
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

    # Personal
    roll_number    = db.Column(db.String(50), unique=True, nullable=True, index=True)
    phone          = db.Column(db.String(15))
    alternate_phone= db.Column(db.String(15))
    date_of_birth  = db.Column(db.Date)
    gender         = db.Column(db.String(10))
    address        = db.Column(db.String(500))
    city           = db.Column(db.String(100))
    state          = db.Column(db.String(100))
    pincode        = db.Column(db.String(10))

    # Education
    college_name       = db.Column(db.String(255))
    degree             = db.Column(db.String(100))
    branch             = db.Column(db.String(100))
    cgpa               = db.Column(db.Float)
    tenth_percentage   = db.Column(db.Float)
    twelfth_percentage = db.Column(db.Float)
    graduation_year    = db.Column(db.Integer)
    current_semester   = db.Column(db.Integer)

    # Profile
    skills             = db.Column(db.Text)   # comma-separated: "Python,Django,SQL"
    bio                = db.Column(db.Text)

    # Social
    linkedin_url       = db.Column(db.String(500))
    github_url         = db.Column(db.String(500))
    portfolio_url      = db.Column(db.String(500))
    coding_profile_url = db.Column(db.String(500))

    # Resume
    resume_link        = db.Column(db.String(500))
    resume_filename    = db.Column(db.String(255))

    application = db.relationship('Application', backref='student', lazy=True, cascade='all, delete-orphan')
    placements   = db.relationship('Placement',   backref='student', lazy=True, cascade='all, delete-orphan')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ─── Company Model ────────────────────────────────────────────────────────────

class Company(db.Model):
    __tablename__ = 'company'
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

    # Company Info
    company_name = db.Column(db.String(255))
    industry     = db.Column(db.String(100))
    company_size = db.Column(db.String(50))   # 'Startup','Small','Medium','Large'
    location     = db.Column(db.String(255))
    website      = db.Column(db.String(255))
    description  = db.Column(db.Text)
    logo_url     = db.Column(db.String(500))

    # HR / Recruiter
    hr_email     = db.Column(db.String(120))
    hr_contact   = db.Column(db.String(15))
    department   = db.Column(db.String(100))
    designation  = db.Column(db.String(100))

    # Approval
    approval_status = db.Column(db.String(20), default='Pending')  # 'Pending','Approved','Rejected'
    verified_at     = db.Column(db.DateTime)

    drives     = db.relationship('PlacementDrive', backref='company', lazy=True, cascade='all, delete-orphan')
    placements = db.relationship('Placement',      backref='company', lazy=True, cascade='all, delete-orphan')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ─── Placement Drive Model ────────────────────────────────────────────────────

class PlacementDrive(db.Model):
    __tablename__ = 'placement_drive'
    id         = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    # Drive Info
    title               = db.Column(db.String(150), nullable=False, index=True)
    description         = db.Column(db.Text)
    job_type            = db.Column(db.String(50))   # 'Full-time','Internship','Contract'
    location            = db.Column(db.String(255))

    # Salary
    salary_min  = db.Column(db.Float)
    salary_max  = db.Column(db.Float)
    currency    = db.Column(db.String(10), default='INR')

    # Eligibility
    min_cgpa                = db.Column(db.Float, default=0.0)
    eligible_branches       = db.Column(db.Text)    # "CSE,ECE,IT"
    eligible_graduation_year= db.Column(db.Integer)
    experience_required     = db.Column(db.String(100))
    skills_required         = db.Column(db.Text)    # "Python,Django,SQL"

    # Schedule
    drive_date            = db.Column(db.DateTime)
    posted_date           = db.Column(db.DateTime, default=datetime.utcnow)
    application_deadline  = db.Column(db.DateTime)
    status                = db.Column(db.String(20), default='Open')  # 'Open','Closed','Completed'
    admin_approval_status = db.Column(db.String(20), default='Pending')  # 'Pending','Approved','Rejected'

    applications = db.relationship('Application', backref='drive', lazy=True, cascade='all, delete-orphan')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ─── Application Model ────────────────────────────────────────────────────────

class Application(db.Model):
    __tablename__ = 'application'
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id   = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)

    status         = db.Column(db.String(20), default='Applied')  # 'Applied','Shortlisted','Rejected','Selected'
    applied_date   = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_date  = db.Column(db.DateTime)
    cover_letter   = db.Column(db.Text)
    notes          = db.Column(db.Text)
    # FIX 1: Added feedback column — visible to student on their applications page
    feedback       = db.Column(db.Text)

    placement = db.relationship('Placement', backref='application', uselist=False)
    interview = db.relationship('Interview', backref='application', uselist=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ─── Interview Model ──────────────────────────────────────────────────────────

class Interview(db.Model):
    __tablename__ = 'interview'
    id             = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False, unique=True)
    drive_id       = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    company_id     = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    # FIX 2: Renamed Student_id (capital S typo) → student_id
    student_id     = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    interview_type  = db.Column(db.String(50))   # 'HR','Technical','Managerial'
    interview_date  = db.Column(db.DateTime)
    interview_mode  = db.Column(db.String(50))   # 'Online','Onsite','Phone'
    interview_link  = db.Column(db.String(500))  # For online interviews
    instructions    = db.Column(db.Text)
    interviewer     = db.Column(db.String(255))
    feedback        = db.Column(db.Text)
    status          = db.Column(db.String(20), default='Scheduled')  # 'Scheduled','Completed','Cancelled'

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ─── Placement Model ──────────────────────────────────────────────────────────

class Placement(db.Model):
    __tablename__ = 'placement'
    id             = db.Column(db.Integer, primary_key=True)
    # FIX 3: Added missing student_id FK column — Student.placements relationship requires it
    student_id     = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    company_id     = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), unique=True)

    position_title = db.Column(db.String(150), nullable=False)
    salary         = db.Column(db.Float)
    currency       = db.Column(db.String(10), default='INR')
    joining_date   = db.Column(db.Date)
    # FIX 4: Added feedback column — visible to student on their placements page
    feedback       = db.Column(db.Text)

    # Offer letter fields
    offer_letter_filename       = db.Column(db.String(255))
    offer_letter_url            = db.Column(db.String(500))
    offer_letter_generated_date = db.Column(db.DateTime)
    # JSON backup of letter fields (studentName, role, companyName, etc.)
    offer_letter_data = db.Column(db.JSON)

    status = db.Column(db.String(20), default='Offered')  # 'Offered','Joined','Declined'

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)