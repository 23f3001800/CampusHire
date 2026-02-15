from flask_restful import fields

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _attr(fn):
    """Shorthand to create a String field with a lambda attribute."""
    return fields.String(attribute=fn)

def _date_attr(fn):
    return fields.String(attribute=lambda x: fn(x).isoformat() if fn(x) else None)

# ─── User Fields ──────────────────────────────────────────────────────────────

user_fields = {
    'id':         fields.Integer,
    'name':       fields.String,
    'email':      fields.String,
    'active':     fields.Boolean,
    'created_at': fields.DateTime(dt_format='iso8601'),
}

# ─── Student Fields ───────────────────────────────────────────────────────────

student_fields = {
    'id':      fields.Integer,
    'user_id': fields.Integer,

    # From User
    'name':  _attr(lambda x: x.user.name  if x.user else None),
    'email': _attr(lambda x: x.user.email if x.user else None),

    # Personal
    'roll_number':     fields.String,
    'phone':           fields.String,
    'alternate_phone': fields.String,
    'date_of_birth':   _attr(lambda x: x.date_of_birth.isoformat() if x.date_of_birth else None),
    'gender':          fields.String,
    'address':         fields.String,
    'city':            fields.String,
    'state':           fields.String,
    'pincode':         fields.String,

    # Education
    'college_name':        fields.String,
    'degree':              fields.String,
    'branch':              fields.String,
    'cgpa':                fields.Float,
    'tenth_percentage':    fields.Float,
    'twelfth_percentage':  fields.Float,
    'graduation_year':     fields.Integer,
    'current_semester':    fields.Integer,

    # Profile
    'skills': fields.String,
    'bio':    fields.String,

    # Social
    'linkedin_url':       fields.String,
    'github_url':         fields.String,
    'portfolio_url':      fields.String,
    'coding_profile_url': fields.String,

    # Resume
    'resume_link':     fields.String,
    'resume_filename': fields.String,

    'created_at': fields.DateTime(dt_format='iso8601'),
    'updated_at': fields.DateTime(dt_format='iso8601'),
}

# ─── Company Fields ───────────────────────────────────────────────────────────

company_fields = {
    'id':      fields.Integer,
    'user_id': fields.Integer,

    # From User (recruiter info)
    'recruiter_name':  _attr(lambda x: x.user.name  if x.user else None),
    'recruiter_email': _attr(lambda x: x.user.email if x.user else None),

    # Company
    'company_name': fields.String,
    'industry':     fields.String,
    'company_size': fields.String,
    'location':     fields.String,
    'website':      fields.String,
    'description':  fields.String,
    'logo_url':     fields.String,

    # HR
    'hr_email':    fields.String,
    'hr_contact':  fields.String,
    'department':  fields.String,
    'designation': fields.String,

    # Approval
    'approval_status': fields.String,
    'verified_at':     fields.DateTime(dt_format='iso8601'),

    'created_at': fields.DateTime(dt_format='iso8601'),
    'updated_at': fields.DateTime(dt_format='iso8601'),
}

# ─── Placement Drive Fields ───────────────────────────────────────────────────

drive_fields = {
    'id':         fields.Integer,
    'company_id': fields.Integer,

    # From Company
    'company_name':     _attr(lambda x: x.company.company_name if x.company else None),
    'company_logo':     _attr(lambda x: x.company.logo_url     if x.company else None),
    'company_location': _attr(lambda x: x.company.location     if x.company else None),

    # Drive Info
    'title':       fields.String,
    'description': fields.String,
    'job_type':    fields.String,
    'location':    fields.String,

    # Salary
    'salary_min': fields.Float,
    'salary_max': fields.Float,
    'currency':   fields.String,

    # Eligibility
    'min_cgpa':                 fields.Float,
    'eligible_branches':        fields.String,
    'eligible_graduation_year': fields.Integer,
    'experience_required':      fields.String,
    'skills_required':          fields.String,

    # Schedule
    'drive_date':           fields.DateTime(dt_format='iso8601'),
    'posted_date':          fields.DateTime(dt_format='iso8601'),
    'application_deadline': fields.DateTime(dt_format='iso8601'),
    'status':               fields.String,
    'admin_approval_status': fields.String,  # Pending/Approved/Rejected by admin

    # Stats
    'total_applications': fields.Integer(
        attribute=lambda x: len(x.applications) if x.applications else 0
    ),

    'created_at': fields.DateTime(dt_format='iso8601'),
    'updated_at': fields.DateTime(dt_format='iso8601'),
}

# ─── Application Fields ───────────────────────────────────────────────────────

application_fields = {
    'id':         fields.Integer,
    'student_id': fields.Integer,
    'drive_id':   fields.Integer,

    # From Student
    'student_name':   _attr(lambda x: x.student.user.name   if x.student and x.student.user else None),
    'student_email':  _attr(lambda x: x.student.user.email  if x.student and x.student.user else None),
    'student_roll':   _attr(lambda x: x.student.roll_number if x.student else None),
    'student_branch': _attr(lambda x: x.student.branch      if x.student else None),
    'student_cgpa':   fields.Float(attribute=lambda x: x.student.cgpa if x.student else None),
    'resume_link':    _attr(lambda x: x.student.resume_link if x.student else None),

    # From Drive
    'drive_title':  _attr(lambda x: x.drive.title                        if x.drive else None),
    'company_name': _attr(lambda x: x.drive.company.company_name         if x.drive and x.drive.company else None),

    # Application
    'status':        fields.String,
    'applied_date':  fields.DateTime(dt_format='iso8601'),
    'reviewed_date': fields.DateTime(dt_format='iso8601'),
    'cover_letter':  fields.String,
    'notes':         fields.String,

    'created_at': fields.DateTime(dt_format='iso8601'),
    'updated_at': fields.DateTime(dt_format='iso8601'),
}

# ─── Placement Fields ─────────────────────────────────────────────────────────

placement_fields = {
    'id':             fields.Integer,
    'student_id':     fields.Integer,
    'company_id':     fields.Integer,
    'application_id': fields.Integer,

    # From Student / Company
    'student_name': _attr(lambda x: x.student.user.name    if x.student and x.student.user else None),
    'company_name': _attr(lambda x: x.company.company_name if x.company else None),

    # Placement Info
    'position_title': fields.String,
    'salary':         fields.Float,
    'currency':       fields.String,
    'joining_date':   _attr(lambda x: x.joining_date.isoformat() if x.joining_date else None),
    'offer_letter':   fields.String,
    'status':         fields.String,

    'created_at': fields.DateTime(dt_format='iso8601'),
    'updated_at': fields.DateTime(dt_format='iso8601'),
}