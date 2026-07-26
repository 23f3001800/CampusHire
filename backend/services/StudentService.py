from models import Student, Application, PlacementDrive, db
from datetime import datetime
from werkzeug.utils import secure_filename
import os

import storage

ALLOWED_EXT = {'pdf', 'doc', 'docx'}


def _allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


class StudentService:

    # ── Read ────────────────────────────────────────────────────────────────

    @staticmethod
    def get_all_students():
        return Student.query.all()

    @staticmethod
    def get_by_id(student_id):
        return Student.query.get(student_id)

    # ── Update ──────────────────────────────────────────────────────────────

    UPDATABLE = [
        'phone', 'alternate_phone', 'date_of_birth', 'gender',
        'address', 'city', 'state', 'pincode',
        'college_name', 'degree', 'branch', 'cgpa',
        'tenth_percentage', 'twelfth_percentage',
        'graduation_year', 'current_semester',
        'skills', 'bio',
        'linkedin_url', 'github_url', 'portfolio_url', 'coding_profile_url',"active",
    ]

    @staticmethod
    def update(student_id, data):
        student = Student.query.get(student_id)
        if not student:
            return None
        if "active" in data and student.user:
            student.user.active = bool(data["active"])

        for field in StudentService.UPDATABLE:
            if field in data:
                value = data[field]

                # Convert date string to Python date
                if field == "date_of_birth" and value:
                    value = datetime.strptime(value, "%Y-%m-%d").date()

                setattr(student, field, value)

        student.updated_at = datetime.utcnow()
        db.session.commit()
        return student

    # ── Resume ──────────────────────────────────────────────────────────────

    @staticmethod
    def upload_resume(student_id, file):
        student = Student.query.get(student_id)
        if not student:
            return None, 'Student not found'
        if not file or not file.filename:
            return None, 'No file provided'
        if not _allowed(file.filename):
            return None, 'Only PDF, DOC, DOCX allowed'

        resume_dir = storage.subdir(storage.RESUMES)
        ext        = secure_filename(file.filename).rsplit('.', 1)[1].lower()
        filename   = f'resume_{student_id}_{int(datetime.utcnow().timestamp())}.{ext}'
        file.save(os.path.join(resume_dir, filename))

        if student.resume_filename:
            old = storage.path_for(storage.RESUMES, student.resume_filename)
            if old and os.path.exists(old):
                os.remove(old)

        # Served by ResumeServeResource — must match the route registered in
        # resources/__init__.py, not the on-disk layout.
        student.resume_link     = f'/api/uploads/resumes/{filename}'
        student.resume_filename = filename
        student.updated_at      = datetime.utcnow()
        db.session.commit()
        return student, None

    @staticmethod
    def delete_resume(student_id):
        student = Student.query.get(student_id)
        if not student:
            return False, 'Student not found'
        if student.resume_filename:
            path = storage.path_for(storage.RESUMES, student.resume_filename)
            if path and os.path.exists(path):
                os.remove(path)
        student.resume_link     = None
        student.resume_filename = None
        student.updated_at      = datetime.utcnow()
        db.session.commit()
        return True, None

    # ── Drives & Applications ───────────────────────────────────────────────

    @staticmethod
    def get_eligible_drives(student_id):
        student = Student.query.get(student_id)
        if not student:
            return None
        applied_ids = {app.drive_id for app in student.applications}
        drives      = PlacementDrive.query.filter_by(
            status='Open', admin_approval_status='Approved').all()
        eligible = []
        for drive in drives:
            if drive.id in applied_ids:
                continue
            if drive.min_cgpa and student.cgpa and student.cgpa < drive.min_cgpa:
                continue
            if drive.eligible_branches and student.branch:
                allowed = [b.strip().lower() for b in drive.eligible_branches.split(',')]
                if student.branch.lower() not in allowed:
                    continue
            if drive.eligible_graduation_year and student.graduation_year:
                if student.graduation_year != drive.eligible_graduation_year:
                    continue
            eligible.append(drive)
        return eligible

    @staticmethod
    def apply(student_id, drive_id, cover_letter=None):
        student = Student.query.get(student_id)
        if not student:
            return None, 'Student not found'
        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return None, 'Placement drive not found'
        if drive.status != 'Open':
            return None, 'This drive is no longer accepting applications'
        if drive.application_deadline and datetime.utcnow() > drive.application_deadline:
            return None, 'Application deadline has passed'
        if Application.query.filter_by(
                student_id=student_id, drive_id=drive_id).first():
            return None, 'Already applied to this drive'
        app = Application(
            student_id=student_id,
            drive_id=drive_id,
            status='Applied',
            cover_letter=cover_letter,
            applied_date=datetime.utcnow()
        )
        db.session.add(app)
        db.session.commit()
        return app, None

    @staticmethod
    def get_applications(student_id):
        if not Student.query.get(student_id):
            return None
        return Application.query.filter_by(student_id=student_id)\
                                .order_by(Application.applied_date.desc()).all()

    @staticmethod
    def withdraw(student_id, application_id):
        app = Application.query.filter_by(
            id=application_id, student_id=student_id).first()
        if not app:
            return False, 'Application not found'
        if app.status != 'Applied':
            return False, 'Cannot withdraw a reviewed application'
        db.session.delete(app)
        db.session.commit()
        return True, None

    # ── Delete ──────────────────────────────────────────────────────────────

    @staticmethod
    def delete(student_id):
        student = Student.query.get(student_id)
        if not student:
            return False, 'Student not found'
        db.session.delete(student)
        db.session.commit()
        return True, None
