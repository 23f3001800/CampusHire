from flask_restful import Resource, marshal
from flask import request, send_from_directory, current_app
from flask_security import auth_required, roles_required, roles_accepted
from resources.field_marshal import (
    student_fields, company_fields,
    drive_fields, application_fields, placement_fields
)
from services.StudentService import StudentService
from services.CompanyService import CompanyService
from services.DriveService import DriveService
from models import Company, User, db
from datetime import datetime
import os

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _json():
    """Return parsed JSON body or empty dict."""
    return request.get_json() or {}

# ─── Student ──────────────────────────────────────────────────────────────────

class StudentResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def get(self, student_id):
        s = StudentService.get_by_id(student_id)
        return (marshal(s, student_fields), 200) if s else ({'message': 'Student not found'}, 404)

    @auth_required('token')
    @roles_required('student')
    def put(self, student_id):
        data = _json()
        s = StudentService.update(student_id, data)
        return (marshal(s, student_fields), 200) if s else ({'message': 'Student not found'}, 404)


class StudentResumeResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def post(self, student_id):
        if 'resume' not in request.files:
            return {'message': 'No resume file provided'}, 400
        s, err = StudentService.upload_resume(student_id, request.files['resume'])
        if err:
            return {'message': err}, 400
        return {'message': 'Resume uploaded', 'resume_link': s.resume_link, 'resume_filename': s.resume_filename}, 200

    @auth_required('token')
    @roles_required('student')
    def delete(self, student_id):
        ok, err = StudentService.delete_resume(student_id)
        return ({'message': 'Resume deleted'}, 200) if ok else ({'message': err}, 400)


class StudentEligibleDrivesResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def get(self, student_id):
        drives = StudentService.get_eligible_drives(student_id)
        return (marshal(drives, drive_fields), 200) if drives is not None else ({'message': 'Student not found'}, 404)


class StudentApplicationsResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def get(self, student_id):
        apps = StudentService.get_applications(student_id)
        return (marshal(apps, application_fields), 200) if apps is not None else ({'message': 'Student not found'}, 404)


class StudentApplyResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def post(self, student_id, drive_id):
        app, err = StudentService.apply(student_id, drive_id, _json().get('cover_letter'))
        return (marshal(app, application_fields), 201) if app else ({'message': err}, 400)


class StudentWithdrawResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def delete(self, student_id, application_id):
        ok, err = StudentService.withdraw(student_id, application_id)
        return ({'message': 'Application withdrawn'}, 200) if ok else ({'message': err}, 400)


class StudentListResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        return marshal(StudentService.get_all_students(), student_fields), 200

# ─── Company ──────────────────────────────────────────────────────────────────

class CompanyResource(Resource):
    @auth_required('token')
    @roles_accepted('company', 'admin')
    def get(self, company_id):
        c = CompanyService.get_by_id(company_id)
        return (marshal(c, company_fields), 200) if c else ({'message': 'Company not found'}, 404)

    @auth_required('token')
    @roles_required('company')
    def put(self, company_id):
        c = CompanyService.update(company_id, _json())
        return (marshal(c, company_fields), 200) if c else ({'message': 'Company not found'}, 404)


class CompanyListResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        return marshal(CompanyService.get_all(), company_fields), 200

# ─── Company Drives ───────────────────────────────────────────────────────────

class CompanyDrivesResource(Resource):
    @auth_required('token')
    @roles_required('company')
    def get(self, company_id):
        return marshal(CompanyService.get_drives(company_id), drive_fields), 200

    @auth_required('token')
    @roles_required('company')
    def post(self, company_id):
        drive = DriveService.create(company_id, _json())
        return marshal(drive, drive_fields), 201


class CompanyDriveResource(Resource):
    @auth_required('token')
    @roles_required('company')
    def put(self, company_id, drive_id):
        drive = DriveService.update(drive_id, _json())
        return (marshal(drive, drive_fields), 200) if drive else ({'message': 'Drive not found'}, 404)

    @auth_required('token')
    @roles_required('company')
    def patch(self, company_id, drive_id):
        drive = DriveService.toggle_status(drive_id)
        return (marshal(drive, drive_fields), 200) if drive else ({'message': 'Drive not found'}, 404)

    @auth_required('token')
    @roles_required('company')
    def delete(self, company_id, drive_id):
        ok = DriveService.delete(drive_id)
        return ({'message': 'Drive deleted'}, 200) if ok else ({'message': 'Drive not found'}, 404)

# ─── Company Applicants ───────────────────────────────────────────────────────

class CompanyDriveApplicantsResource(Resource):
    @auth_required('token')
    @roles_required('company')
    def get(self, company_id, drive_id):
        apps, err = CompanyService.get_applicants(company_id, drive_id)
        return (marshal(apps, application_fields), 200) if apps is not None else ({'message': err}, 404)


class CompanyDriveApplicantResource(Resource):
    @auth_required('token')
    @roles_required('company')
    def put(self, company_id, drive_id, application_id):
        data   = _json()
        status = data.get('status')
        if not status:
            return {'message': 'status is required'}, 400
        app, err = CompanyService.update_application_status(
            company_id, drive_id, application_id, status, data.get('notes')
        )
        return (marshal(app, application_fields), 200) if app else ({'message': err}, 400)

# ─── Public Drives ────────────────────────────────────────────────────────────

class DriveListResource(Resource):
    def get(self):
        return marshal(DriveService.get_all(), drive_fields), 200


class DriveResource(Resource):
    def get(self, drive_id):
        drive = DriveService.get_by_id(drive_id)
        return (marshal(drive, drive_fields), 200) if drive else ({'message': 'Drive not found'}, 404)

# ─── Admin ────────────────────────────────────────────────────────────────────

class AdminCompanyApprovalResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def put(self, company_id):
        data   = _json()
        status = data.get('status')
        if status not in ('Approved', 'Rejected'):
            return {'message': 'status must be Approved or Rejected'}, 400

        company = CompanyService.get_by_id(company_id)
        if not company:
            return {'message': 'Company not found'}, 404

        company.approval_status = status
        if status == 'Approved':
            company.user.active  = True
            company.verified_at  = datetime.utcnow()

        db.session.commit()
        return marshal(company, company_fields), 200

class AdminDriveApprovalResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def put(self, drive_id):
        """Admin approve or reject a placement drive."""
        data = _json()
        status = data.get('status')
        if status not in ('Approved', 'Rejected'):
            return {'message': 'status must be Approved or Rejected'}, 400

        drive = DriveService.get_by_id(drive_id)
        if not drive:
            return {'message': 'Drive not found'}, 404

        drive.admin_approval_status = status
        db.session.commit()
        return marshal(drive, drive_fields), 200

class AdminDriveApplicantsResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self, drive_id):
        """Admin view all applicants for a specific drive."""
        from models import Application
        applicants = Application.query.filter_by(drive_id=drive_id)\
                                       .order_by(Application.applied_date.desc()).all()
        return marshal(applicants, application_fields), 200

# ─── Admin: stats ────────────────────────────────────────────────────────────

class AdminStatsResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        from models import Student, Company, PlacementDrive, Application, Placement
        return {
            'total_students':         Student.query.count(),
            'total_companies':        Company.query.count(),
            'pending_companies':      Company.query.filter_by(approval_status='Pending').count(),
            'approved_companies':     Company.query.filter_by(approval_status='Approved').count(),
            'total_drives':           PlacementDrive.query.count(),
            'open_drives':            PlacementDrive.query.filter_by(status='Open').count(),
            'total_applications':     Application.query.count(),
            'total_placements':       Placement.query.count(),
            'placements_offered':     Placement.query.filter_by(status='Offered').count(),
            'placements_joined':      Placement.query.filter_by(status='Joined').count(),
            'placements_declined':    Placement.query.filter_by(status='Declined').count(),
        }, 200

# ─── Admin: placements list ───────────────────────────────────────────────────

class AdminPlacementsResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        from models import Placement
        placements = Placement.query.order_by(Placement.created_at.desc()).all()
        return marshal(placements, placement_fields), 200

# ─── Admin: toggle user active ────────────────────────────────────────────────

class AdminUserActiveResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def put(self, user_id):
        data   = _json()
        active = data.get('active')
        if active is None:
            return {'message': 'active (bool) is required'}, 400
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        user.active = bool(active)
        db.session.commit()
        return {'message': f"User {'activated' if active else 'blocked'}", 'active': user.active}, 200

# ─── Admin: drive management ──────────────────────────────────────────────────

class AdminDriveResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def patch(self, drive_id):
        """Admin force-close a drive."""
        drive = DriveService.toggle_status(drive_id)
        return (marshal(drive, drive_fields), 200) if drive else ({'message': 'Drive not found'}, 404)

    @auth_required('token')
    @roles_required('admin')
    def delete(self, drive_id):
        ok = DriveService.delete(drive_id)
        return ({'message': 'Drive deleted'}, 200) if ok else ({'message': 'Drive not found'}, 404)

class StudentPlacementHistoryResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def get(self, student_id):
        """Get placement history for a student."""
        from models import Placement
        placements = Placement.query.filter_by(student_id=student_id)\
                                     .order_by(Placement.created_at.desc()).all()
        return marshal(placements, placement_fields), 200


class StudentCSVExportResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def post(self, student_id):
        """Trigger async CSV export task."""
        from tasks import export_applications_csv
        task = export_applications_csv.delay(student_id)
        return {'task_id': task.id, 'status': 'PENDING'}, 202


class StudentCSVExportStatusResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def get(self, student_id, task_id):
        """Check CSV export task status."""
        from celery.result import AsyncResult
        task = AsyncResult(task_id)
        
        if task.state == 'PENDING':
            return {'status': 'PENDING', 'progress': 0}, 200
        elif task.state == 'SUCCESS':
            result = task.result
            return {
                'status': 'SUCCESS',
                'download_url': f"/api/student/{student_id}/export-csv/{result['filename']}/download",
                'filename': result['filename'],
                'record_count': result['record_count']
            }, 200
        elif task.state == 'FAILURE':
            return {'status': 'FAILURE', 'error': str(task.info)}, 200
        else:
            return {'status': task.state}, 200


class StudentCSVDownloadResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def get(self, student_id, filename):
        """Download generated CSV file."""
        from flask import send_file
        filepath = f"/tmp/exports/{filename}"
        if not os.path.exists(filepath):
            return {'message': 'File not found or expired'}, 404
        return send_file(filepath, as_attachment=True, download_name=filename)


# ─── File Serving ─────────────────────────────────────────────────────────────

class ResumeServeResource(Resource):
    @auth_required('token')
    def get(self, filename):
        folder = os.path.join(current_app.root_path, 'uploads', 'resumes')
        return send_from_directory(folder, filename)