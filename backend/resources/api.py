from flask_restful import Resource, marshal
from flask import request, send_from_directory, current_app, make_response, send_file
from flask_security import auth_required, roles_required, roles_accepted, current_user
from resources.field_marshal import (
    student_fields, company_fields, drive_fields,
    application_fields, placement_fields, interview_fields,
)
from services.StudentService import StudentService
from services.CompanyService import CompanyService
from services.DriveService    import DriveService
from models import (
    Company, User, Interview, Application,
    PlacementDrive, Placement, Student, db,
)
from cache import (
    cache,
    clear_student_cache, clear_company_cache,
    clear_drive_cache, clear_application_cache, clear_interview_cache,
    key_student_profile, key_student_applications, key_student_eligible_drives,
    key_student_placements, key_student_interview,
    key_company_profile, key_company_drives,
    key_drive, key_drive_applicants,
    KEY_ALL_DRIVES, KEY_ADMIN_DRIVES,
    KEY_ADMIN_STUDENTS, KEY_ADMIN_COMPANIES, KEY_ADMIN_STATS,
    TTL_SHORT, TTL_MEDIUM, TTL_LONG,
)
from datetime import datetime
import os
import csv
from io import StringIO


def _json():
    return request.get_json() or {}


# ─── Student ──────────────────────────────────────────────────────────────────


class StudentResource(Resource):
    @auth_required('token')
    @roles_accepted('student', 'admin', 'company')
    def get(self, student_id):
        cached = cache.get(key_student_profile(student_id))
        if cached:
            return cached, 200
        s = StudentService.get_by_id(student_id)
        if not s:
            return {'message': 'Student not found'}, 404
        result = marshal(s, student_fields)
        cache.set(key_student_profile(student_id), result, timeout=TTL_MEDIUM)
        return result, 200

    @auth_required('token')
    @roles_required('student')
    def put(self, student_id):
        s = StudentService.update(student_id, _json())
        if not s:
            return {'message': 'Student not found'}, 404
        clear_student_cache(student_id)
        return marshal(s, student_fields), 200

    @auth_required('token')
    @roles_required('student')
    def patch(self, student_id):
        s = StudentService.update(student_id, _json())
        if not s:
            return {'message': 'Student not found'}, 404
        clear_student_cache(student_id)
        return marshal(s, student_fields), 200

    @auth_required('token')
    @roles_required('student')
    def delete(self, student_id):
        ok, err = StudentService.delete(student_id)
        if ok:
            clear_student_cache(student_id)
        return ({'message': 'Profile deleted successfully'}, 200) if ok \
            else ({'message': err}, 400)


class StudentResumeResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def post(self, student_id):
        if 'resume' not in request.files:
            return {'message': 'No resume file provided'}, 400
        s, err = StudentService.upload_resume(student_id, request.files['resume'])
        if err:
            return {'message': err}, 400
        clear_student_cache(student_id)
        return {
            'message':         'Resume uploaded',
            'resume_link':     s.resume_link,
            'resume_filename': s.resume_filename,
        }, 200

    @auth_required('token')
    @roles_required('student')
    def delete(self, student_id):
        ok, err = StudentService.delete_resume(student_id)
        if ok:
            clear_student_cache(student_id)
        return ({'message': 'Resume deleted'}, 200) if ok \
            else ({'message': err}, 400)


class StudentEligibleDrivesResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def get(self, student_id):
        cached = cache.get(key_student_eligible_drives(student_id))
        if cached:
            return cached, 200
        drives = StudentService.get_eligible_drives(student_id)
        if drives is None:
            return {'message': 'Student not found'}, 404
        result = marshal(drives, drive_fields)
        cache.set(key_student_eligible_drives(student_id), result, timeout=TTL_MEDIUM)
        return result, 200


class StudentApplicationsResource(Resource):
    @auth_required('token')
    @roles_accepted("admin","student")
    def get(self, student_id):
        cached = cache.get(key_student_applications(student_id))
        if cached:
            return cached, 200
        apps = StudentService.get_applications(student_id)
        if apps is None:
            return {'message': 'Student not found'}, 404
        result = marshal(apps, application_fields)
        cache.set(key_student_applications(student_id), result, timeout=TTL_SHORT)
        return result, 200


class StudentApplyResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def post(self, student_id, drive_id):
        app, err = StudentService.apply(
            student_id, drive_id, _json().get('cover_letter'))
        if not app:
            return {'message': err}, 400
        clear_application_cache(student_id, drive_id)
        return marshal(app, application_fields), 201


class StudentWithdrawResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def delete(self, student_id, application_id):
        ok, err = StudentService.withdraw(student_id, application_id)
        if ok:
            clear_application_cache(student_id)
        return ({'message': 'Application withdrawn'}, 200) if ok \
            else ({'message': err}, 400)


class StudentListResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        cached = cache.get(KEY_ADMIN_STUDENTS)
        if cached:
            return cached, 200
        result = marshal(StudentService.get_all_students(), student_fields)
        cache.set(KEY_ADMIN_STUDENTS, result, timeout=TTL_SHORT)
        return result, 200


# ─── Student: Interview ───────────────────────────────────────────────────────


class StudentInterviewResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def get(self, student_id, application_id):
        cached = cache.get(key_student_interview(application_id))
        if cached:
            return cached, 200
        app = Application.query.filter_by(
            id=application_id, student_id=student_id).first()
        if not app:
            return {'message': 'Application not found'}, 404
        if not app.interview:
            return {'message': 'No interview scheduled yet'}, 404
        result = marshal(app.interview, interview_fields)
        cache.set(key_student_interview(application_id), result, timeout=TTL_SHORT)
        return result, 200


# ─── Student: Placements ──────────────────────────────────────────────────────


class StudentPlacementHistoryResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def get(self, student_id):
        cached = cache.get(key_student_placements(student_id))
        if cached:
            return cached, 200
        placements = Placement.query.filter_by(student_id=student_id)\
                                    .order_by(Placement.created_at.desc()).all()
        result = marshal(placements, placement_fields)
        cache.set(key_student_placements(student_id), result, timeout=TTL_MEDIUM)
        return result, 200


# ─── Student: CSV Export ──────────────────────────────────────────────────────


class StudentCSVExportResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def post(self, student_id):
        from tasks import export_applications_csv
        task = export_applications_csv.delay(student_id)
        return {'task_id': task.id, 'status': 'PENDING'}, 202


class StudentCSVExportStatusResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def get(self, student_id, task_id):
        from celery.result import AsyncResult
        task = AsyncResult(task_id)
        if task.state == 'PENDING':
            return {'status': 'PENDING', 'progress': 0}, 200
        if task.state == 'SUCCESS':
            result = task.result
            return {
                'status':       'SUCCESS',
                'filename':     result['filename'],
                'record_count': result['record_count'],
                'download_url': (
                    f"/api/student/{student_id}"
                    f"/export-csv/{result['filename']}/download"
                ),
            }, 200
        if task.state == 'FAILURE':
            return {'status': 'FAILURE', 'error': str(task.info)}, 200
        return {'status': task.state}, 200


class StudentCSVDownloadResource(Resource):
    @auth_required('token')
    @roles_required('student')
    def get(self, student_id, filename):
        if '..' in filename or '/' in filename:
            return {'message': 'Invalid filename'}, 400
        filepath = f'/tmp/exports/{filename}'
        if not os.path.exists(filepath):
            return {'message': 'File not found or expired'}, 404
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv',
        )


# ─── Company ──────────────────────────────────────────────────────────────────


class CompanyResource(Resource):
    @auth_required('token')
    @roles_accepted('company', 'admin', 'student')
    def get(self, company_id):
        cached = cache.get(key_company_profile(company_id))
        if cached:
            return cached, 200
        c = CompanyService.get_by_id(company_id)
        if not c:
            return {'message': 'Company not found'}, 404
        result = marshal(c, company_fields)
        cache.set(key_company_profile(company_id), result, timeout=TTL_MEDIUM)
        return result, 200

    @auth_required('token')
    @roles_required('company')
    def put(self, company_id):
        c = CompanyService.update(company_id, _json())
        if not c:
            return {'message': 'Company not found'}, 404
        clear_company_cache(company_id)
        return marshal(c, company_fields), 200

    @auth_required('token')
    @roles_required('company')
    def patch(self, company_id):
        c = CompanyService.update(company_id, _json())
        if not c:
            return {'message': 'Company not found'}, 404
        clear_company_cache(company_id)
        return marshal(c, company_fields), 200

    @auth_required('token')
    @roles_required('company')
    def delete(self, company_id):
        ok, err = CompanyService.delete(company_id)
        if ok:
            clear_company_cache(company_id)
        return ({'message': 'Company profile deleted successfully'}, 200) if ok \
            else ({'message': err}, 400)


class CompanyListResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        cached = cache.get(KEY_ADMIN_COMPANIES)
        if cached:
            return cached, 200
        result = marshal(CompanyService.get_all(), company_fields)
        cache.set(KEY_ADMIN_COMPANIES, result, timeout=TTL_SHORT)
        return result, 200


# ─── Company Drives ───────────────────────────────────────────────────────────


class DrivesResource(Resource):
    @auth_required('token')
    @roles_accepted('company', 'admin', 'student')
    def get(self, company_id):
        cached = cache.get(key_company_drives(company_id))
        if cached:
            return cached, 200
        result = marshal(CompanyService.get_drives(company_id), drive_fields)
        cache.set(key_company_drives(company_id), result, timeout=TTL_MEDIUM)
        return result, 200

    @auth_required('token')
    @roles_required('company')
    def post(self, company_id):
        drive = DriveService.create(company_id, _json())
        clear_drive_cache(company_id=company_id)
        return marshal(drive, drive_fields), 201


class CompanyDriveResource(Resource):
    @auth_required('token')
    @roles_required('company')
    def put(self, company_id, drive_id):
        drive = DriveService.update(drive_id, _json())
        if not drive:
            return {'message': 'Drive not found'}, 404
        clear_drive_cache(drive_id=drive_id, company_id=company_id)
        return marshal(drive, drive_fields), 200

    @auth_required('token')
    @roles_accepted('company', 'admin')
    def patch(self, company_id, drive_id):
        drive = DriveService.toggle_status(drive_id)
        if not drive:
            return {'message': 'Drive not found'}, 404
        clear_drive_cache(drive_id=drive_id, company_id=company_id)
        return marshal(drive, drive_fields), 200

    @auth_required('token')
    @roles_accepted('company', 'admin')
    def delete(self, company_id, drive_id):
        ok = DriveService.delete(drive_id)
        if ok:
            clear_drive_cache(drive_id=drive_id, company_id=company_id)
        return ({'message': 'Drive deleted'}, 200) if ok \
            else ({'message': 'Drive not found'}, 404)


# ─── Company Applicants ───────────────────────────────────────────────────────


class CompanyDriveApplicantsResource(Resource):
    @auth_required('token')
    @roles_accepted('company', 'admin')
    def get(self, company_id, drive_id):
        cached = cache.get(key_drive_applicants(drive_id))
        if cached:
            return cached, 200
        apps, err = CompanyService.get_applicants(company_id, drive_id)
        if apps is None:
            return {'message': err}, 404
        result = marshal(apps, application_fields)
        cache.set(key_drive_applicants(drive_id), result, timeout=TTL_SHORT)
        return result, 200


class CompanyDriveApplicantResource(Resource):
    @auth_required('token')
    @roles_required('company')
    def put(self, company_id, drive_id, application_id):
        data   = _json()
        status = data.get('status')
        if not status:
            return {'message': 'status is required'}, 400
        app, err = CompanyService.update_application_status(
            company_id, drive_id, application_id,
            status, data.get('notes'),
        )
        if not app:
            return {'message': err}, 400
        clear_application_cache(app.student_id, drive_id)
        return marshal(app, application_fields), 200


# ─── Company: Interview ───────────────────────────────────────────────────────


class CompanyInterviewResource(Resource):
    @auth_required('token')
    @roles_required('company')
    def post(self, company_id, application_id):
        """Schedule a new interview for an application."""
        data        = _json()
        application = Application.query.filter_by(id=application_id).first()
        if not application:
            return {'message': 'Application not found'}, 404
        if application.drive.company_id != company_id:
            return {'message': 'Unauthorized'}, 403
        if application.interview:
            return {'message': 'Interview already scheduled. Use PUT to update.'}, 400

        interview_date_raw = data.get('interview_date')
        if not interview_date_raw:
            return {'message': 'interview_date is required'}, 400

        interview = Interview(
            application_id=application_id,
            interview_type=data.get('interview_type', 'Technical'),
            interview_date=datetime.fromisoformat(interview_date_raw),
            interview_mode=data.get('interview_mode', 'Online'),
            interview_link=data.get('interview_link'),
            instructions=data.get('instructions'),
            interviewer=data.get('interviewer'),
        )
        db.session.add(interview)

        # Auto-shortlist if still at Applied
        if application.status == 'Applied':
            application.status = 'Shortlisted'

        db.session.commit()
        clear_application_cache(application.student_id, application.drive_id)
        clear_interview_cache(application_id)
        return marshal(interview, interview_fields), 201

    @auth_required('token')
    @roles_required('company')
    def put(self, company_id, application_id):
        """Update interview — date, mode, link, feedback, interviewer."""
        data        = _json()
        application = Application.query.filter_by(id=application_id).first()
        if not application:
            return {'message': 'Application not found'}, 404
        if application.drive.company_id != company_id:
            return {'message': 'Unauthorized'}, 403
        if not application.interview:
            return {'message': 'No interview found. Use POST to schedule first.'}, 404

        interview = application.interview
        for field in ('interview_type', 'interview_mode',
                      'interview_link', 'instructions',
                      'interviewer', 'feedback'):
            if field in data:
                setattr(interview, field, data[field])

        if data.get('interview_date'):
            interview.interview_date = datetime.fromisoformat(data['interview_date'])

        interview.updated_at = datetime.utcnow()
        db.session.commit()
        clear_application_cache(application.student_id, application.drive_id)
        clear_interview_cache(application_id)
        return marshal(interview, interview_fields), 200


# ─── Company: Final Selection ─────────────────────────────────────────────────


class CompanyUpdateSelectionResource(Resource):
    @auth_required('token')
    @roles_required('company')
    def put(self, company_id, application_id):
        """Finalize — Selected or Rejected. Auto-creates Placement on Selected."""
        data        = _json()
        application = Application.query.filter_by(id=application_id).first()
        if not application:
            return {'message': 'Application not found'}, 404
        if application.drive.company_id != company_id:
            return {'message': 'Unauthorized'}, 403

        new_status = data.get('status')
        if new_status not in ('Selected', 'Rejected'):
            return {'message': 'status must be Selected or Rejected'}, 400

        application.status        = new_status
        application.reviewed_date = datetime.utcnow()

        if new_status == 'Selected' and not Placement.query.filter_by(
                application_id=application_id).first():
            db.session.add(Placement(
                student_id=application.student_id,
                company_id=company_id,
                application_id=application_id,
                position_title=application.drive.title,
                salary=data.get('salary', application.drive.salary_max),
                currency=application.drive.currency,
                status='Offered',
            ))

        db.session.commit()
        clear_application_cache(application.student_id, application.drive_id)
        clear_student_cache(application.student_id)     # placement history changed
        return marshal(application, application_fields), 200


# ─── Company: CSV Export ──────────────────────────────────────────────────────


class CompanyCSVExportResource(Resource):
    @auth_required('token')
    @roles_required('company')
    def post(self, company_id, drive_id):
        """Trigger async CSV export of all applicants for a drive."""
        drive = PlacementDrive.query.filter_by(
            id=drive_id, company_id=company_id).first()
        if not drive:
            return {'message': 'Drive not found'}, 404
        from tasks import export_company_applicants_csv
        task = export_company_applicants_csv.delay(company_id, drive_id)
        return {'task_id': task.id, 'status': 'PENDING'}, 202


class CompanyCSVExportStatusResource(Resource):
    @auth_required('token')
    @roles_required('company')
    def get(self, company_id, drive_id, task_id):
        """Poll export task status."""
        from celery.result import AsyncResult
        task = AsyncResult(task_id)
        if task.state == 'PENDING':
            return {'status': 'PENDING', 'progress': 0}, 200
        if task.state == 'SUCCESS':
            result = task.result
            return {
                'status':       'SUCCESS',
                'filename':     result['filename'],
                'record_count': result['record_count'],
                'drive_title':  result['drive_title'],
                'download_url': (
                    f"/api/company/{company_id}"
                    f"/drives/{drive_id}"
                    f"/export-csv/{result['filename']}/download"
                ),
            }, 200
        if task.state == 'FAILURE':
            return {'status': 'FAILURE', 'error': str(task.info)}, 200
        return {'status': task.state}, 200


class CompanyCSVDownloadResource(Resource):
    @auth_required('token')
    @roles_accepted('company', 'admin')
    def get(self, company_id, drive_id, filename):
        """Serve generated CSV file."""
        if '..' in filename or '/' in filename:
            return {'message': 'Invalid filename'}, 400
        filepath = f'/tmp/exports/{filename}'
        if not os.path.exists(filepath):
            return {'message': 'File not found or expired'}, 404
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv',
        )


# ─── Public Drives ────────────────────────────────────────────────────────────


class DriveListResource(Resource):
    # Intentionally public — students browse before login
    def get(self):
        cached = cache.get(KEY_ALL_DRIVES)
        if cached:
            return cached, 200
        result = marshal(DriveService.get_all(), drive_fields)
        cache.set(KEY_ALL_DRIVES, result, timeout=TTL_MEDIUM)
        return result, 200


class DriveResource(Resource):
    def get(self, drive_id):
        cached = cache.get(key_drive(drive_id))
        if cached:
            return cached, 200
        drive = DriveService.get_by_id(drive_id)
        if not drive:
            return {'message': 'Drive not found'}, 404
        result = marshal(drive, drive_fields)
        cache.set(key_drive(drive_id), result, timeout=TTL_MEDIUM)
        return result, 200


# ─── Admin: Approvals ─────────────────────────────────────────────────────────


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
            company.user.active = True
            company.verified_at = datetime.utcnow()
        db.session.commit()
        clear_company_cache(company_id)
        return marshal(company, company_fields), 200


class AdminDriveApprovalResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def put(self, drive_id):
        data   = _json()
        status = data.get('status')
        if status not in ('Approved', 'Rejected'):
            return {'message': 'status must be Approved or Rejected'}, 400
        drive = DriveService.get_by_id(drive_id)
        if not drive:
            return {'message': 'Drive not found'}, 404
        drive.admin_approval_status = status
        db.session.commit()
        clear_drive_cache(drive_id=drive_id, company_id=drive.company_id)
        return marshal(drive, drive_fields), 200


# ─── Admin: Drives ────────────────────────────────────────────────────────────


class AdminDriveResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        """List ALL drives — all statuses, all approval states."""
        cached = cache.get(KEY_ADMIN_DRIVES)
        if cached:
            return cached, 200
        result = marshal(DriveService.get_all_admin(), drive_fields)
        cache.set(KEY_ADMIN_DRIVES, result, timeout=TTL_SHORT)
        return result, 200


# ─── Admin: Applications ──────────────────────────────────────────────────────


class AdminDriveApplicantsResource(Resource):
    """Applicants for a specific drive — used on drive detail page."""
    @auth_required('token')
    @roles_required('admin')
    def get(self, drive_id):
        cached = cache.get(key_drive_applicants(drive_id))
        if cached:
            return cached, 200
        applicants = Application.query.filter_by(drive_id=drive_id)\
                                      .order_by(Application.applied_date.desc()).all()
        result = marshal(applicants, application_fields)
        cache.set(key_drive_applicants(drive_id), result, timeout=TTL_SHORT)
        return result, 200


class AdminApplicationsResource(Resource):
    """
    All applications across all drives.
    Supports ?status= ?drive_id= ?company_id= ?student_id= ?q=
    """
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        status     = request.args.get('status')
        drive_id   = request.args.get('drive_id',   type=int)
        company_id = request.args.get('company_id', type=int)
        student_id = request.args.get('student_id', type=int)
        search     = request.args.get('q', '').strip().lower()

        # Dynamic cache key — different filter combos don't collide
        cache_key = (
            f'admin_applications'
            f'_s{status}_d{drive_id}'
            f'_c{company_id}_st{student_id}'
            f'_q{search}'
        )
        cached = cache.get(cache_key)
        if cached:
            return cached, 200

        query = Application.query
        if status:     query = query.filter(Application.status     == status)
        if drive_id:   query = query.filter(Application.drive_id   == drive_id)
        if student_id: query = query.filter(Application.student_id == student_id)
        apps = query.order_by(Application.applied_date.desc()).all()

        # In-memory filters (avoids complex join — record count is manageable)
        if company_id:
            apps = [a for a in apps
                    if a.drive and a.drive.company_id == company_id]
        if search:
            apps = [a for a in apps if (
                (a.student and a.student.user and
                 search in a.student.user.name.lower())     or
                (a.drive and a.drive.company and
                 search in a.drive.company.company_name.lower()) or
                (a.drive and search in a.drive.title.lower())
            )]

        result = marshal(apps, application_fields)
        cache.set(cache_key, result, timeout=TTL_SHORT)
        return result, 200


# ─── Admin: Search ────────────────────────────────────────────────────────────


class AdminSearchResource(Resource):
    """
    Unified search for admin.
    GET /api/admin/search?q=john&type=students
    GET /api/admin/search?q=google&type=companies
    GET /api/admin/search?q=python&type=drives
    GET /api/admin/search?q=python          ← searches all three
    """
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        q           = request.args.get('q', '').strip().lower()
        search_type = request.args.get('type', 'all')

        if not q:
            return {'message': 'q (search query) is required'}, 400

        cache_key = f'admin_search_{search_type}_{q}'
        cached    = cache.get(cache_key)
        if cached:
            return cached, 200

        result = {}

        if search_type in ('students', 'all'):
            students = Student.query.join(Student.user).filter(
                db.or_(
                    User.name.ilike(f'%{q}%'),
                    User.email.ilike(f'%{q}%'),
                    Student.roll_number.ilike(f'%{q}%'),
                    Student.branch.ilike(f'%{q}%'),
                )
            ).all()
            result['students'] = marshal(students, student_fields)

        if search_type in ('companies', 'all'):
            companies = Company.query.join(Company.user).filter(
                db.or_(
                    User.name.ilike(f'%{q}%'),
                    Company.company_name.ilike(f'%{q}%'),
                    Company.industry.ilike(f'%{q}%'),
                    Company.location.ilike(f'%{q}%'),
                )
            ).all()
            result['companies'] = marshal(companies, company_fields)

        if search_type in ('drives', 'all'):
            drives = PlacementDrive.query.filter(
                db.or_(
                    PlacementDrive.title.ilike(f'%{q}%'),
                    PlacementDrive.description.ilike(f'%{q}%'),
                    PlacementDrive.skills_required.ilike(f'%{q}%'),
                    PlacementDrive.location.ilike(f'%{q}%'),
                )
            ).all()
            result['drives'] = marshal(drives, drive_fields)

        cache.set(cache_key, result, timeout=TTL_SHORT)
        return result, 200


# ─── Admin: Stats ─────────────────────────────────────────────────────────────


class AdminStatsResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        cached = cache.get(KEY_ADMIN_STATS)
        if cached:
            return cached, 200
        result = {
            'total_students':      Student.query.count(),
            'total_companies':     Company.query.count(),
            'pending_companies':   Company.query.filter_by(approval_status='Pending').count(),
            'approved_companies':  Company.query.filter_by(approval_status='Approved').count(),
            'total_drives':        PlacementDrive.query.count(),
            'open_drives':         PlacementDrive.query.filter_by(status='Open').count(),
            'total_applications':  Application.query.count(),
            'total_placements':    Placement.query.count(),
            'placements_offered':  Placement.query.filter_by(status='Offered').count(),
            'placements_joined':   Placement.query.filter_by(status='Joined').count(),
            'placements_declined': Placement.query.filter_by(status='Declined').count(),
        }
        cache.set(KEY_ADMIN_STATS, result, timeout=TTL_SHORT)
        return result, 200


# ─── Admin: Placements ────────────────────────────────────────────────────────


class AdminPlacementsResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        placements = Placement.query.order_by(Placement.created_at.desc()).all()
        return marshal(placements, placement_fields), 200


# ─── Admin: Toggle User Active ────────────────────────────────────────────────


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
        # Invalidate both — we don't know if this user is student or company
        clear_student_cache(user_id)
        clear_company_cache(user_id)
        return {
            'message': f"User {'activated' if active else 'blocked'}",
            'active':  user.active,
        }, 200


# ─── Admin: Export (sync — all data types) ───────────────────────────────────


class AdminExportDataResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        export_type = request.args.get('type', 'students')
        output      = StringIO()
        writer      = csv.writer(output)

        if export_type == 'students':
            writer.writerow([
                'ID', 'Name', 'Email', 'Roll',
                'Branch', 'CGPA', 'Year', 'Active',
            ])
            for s in Student.query.all():
                writer.writerow([
                    s.id, s.user.name, s.user.email,
                    s.roll_number, s.branch, s.cgpa,
                    s.graduation_year, s.user.active,
                ])

        elif export_type == 'companies':
            writer.writerow([
                'ID', 'Name', 'Website',
                'Industry', 'Status', 'Active',
            ])
            for c in Company.query.all():
                writer.writerow([
                    c.id, c.company_name, c.website,
                    c.industry, c.approval_status, c.user.active,
                ])

        elif export_type == 'drives':
            writer.writerow([
                'ID', 'Title', 'Company', 'Location',
                'Salary Min', 'Salary Max', 'Status',
                'Deadline', 'Applicants',
            ])
            for d in PlacementDrive.query.all():
                count = Application.query.filter_by(drive_id=d.id).count()
                writer.writerow([
                    d.id, d.title,
                    d.company.company_name if d.company else 'N/A',
                    d.location, d.salary_min, d.salary_max,
                    d.status, d.application_deadline, count,
                ])

        elif export_type == 'placements':
            writer.writerow([
                'ID', 'Student', 'Company', 'Position',
                'Salary', 'Currency', 'Status', 'Joining Date',
            ])
            for p in Placement.query.all():
                writer.writerow([
                    p.id,
                    p.student.user.name    if p.student and p.student.user else 'N/A',
                    p.company.company_name if p.company else 'N/A',
                    p.position_title, p.salary, p.currency,
                    p.status, p.joining_date,
                ])

        else:
            return {'message': f'Unknown export type: {export_type}'}, 400

        response = make_response(output.getvalue())
        response.headers['Content-Type']        = 'text/csv'
        response.headers['Content-Disposition'] = (
            f'attachment; filename={export_type}.csv'
        )
        return response


# ─── File Serving ─────────────────────────────────────────────────────────────


class ResumeServeResource(Resource):
    @auth_required('token')
    @roles_accepted('student', 'company', 'admin')
    def get(self, filename):
        upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads/resumes')
        if '..' in filename or '/' in filename:
            return {'message': 'Invalid filename'}, 400
        if not os.path.exists(os.path.join(upload_dir, filename)):
            return {'message': 'File not found'}, 404
        return send_from_directory(upload_dir, filename, as_attachment=True)
