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

from extensions import cache
import storage
from datetime import datetime, timezone
import os
import csv
from io import StringIO


# ─── TTL Constants ────────────────────────────────────────────────────────────
TTL_SHORT  = 300    # 5 min  — applications, admin lists, stats
TTL_MEDIUM = 900    # 15 min — student/company/drive profiles
TTL_LONG   = 1800   # 30 min — placement history, interview details


def _json():
    return request.get_json() or {}


# ─── Student ──────────────────────────────────────────────────────────────────

class StudentResource(Resource):

    @auth_required('token')
    @roles_accepted('student', 'admin', 'company')
    @cache.memoize(timeout=TTL_MEDIUM)
    def get(self, student_id):
        s = StudentService.get_by_id(student_id)
        if not s:
            return {'message': 'Student not found'}, 404
        return marshal(s, student_fields), 200

    @auth_required('token')
    @roles_required('student')
    def put(self, student_id):
        s = StudentService.update(student_id, _json())
        if not s:
            return {'message': 'Student not found'}, 404
        cache.delete_memoized(StudentResource.get, StudentResource, student_id)
        cache.delete("admin_students")
        return marshal(s, student_fields), 200

    @auth_required('token')
    @roles_accepted('student', 'admin')
    def patch(self, student_id):
        s = StudentService.update(student_id, _json())
        if not s:
            return {'message': 'Student not found'}, 404
        cache.delete_memoized(StudentResource.get, StudentResource, student_id)
        # FIX: bust the admin list cache so block/unblock is immediately
        # reflected when the frontend re-fetches /admin/students.
        # Previously only the per-student detail cache was cleared, leaving
        # the StudentListResource response stale for up to TTL_SHORT (5 min),
        # which caused the frontend to show "Active" again after any refresh.
        cache.delete("admin_students")
        return marshal(s, student_fields), 200

    @auth_required('token')
    @roles_required('student')
    def delete(self, student_id):
        ok, err = StudentService.delete(student_id)
        if ok:
            cache.delete_memoized(StudentResource.get, StudentResource, student_id)
            cache.delete("admin_students")
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
        cache.delete_memoized(StudentResource.get, StudentResource, student_id)
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
            cache.delete_memoized(StudentResource.get, StudentResource, student_id)
        return ({'message': 'Resume deleted'}, 200) if ok \
            else ({'message': err}, 400)


class StudentApplicationsResource(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'student')
    @cache.memoize(timeout=TTL_SHORT)
    def get(self, student_id):
        apps = StudentService.get_applications(student_id)
        if apps is None:
            return {'message': 'Student not found'}, 404
        return marshal(apps, application_fields), 200


class StudentApplyResource(Resource):

    @auth_required('token')
    @roles_required('student')
    def post(self, student_id, drive_id):
        drive= PlacementDrive.query.get(drive_id)
        student= Student.query.get(student_id)
        if student.cgpa < drive.min_cgpa:
            return {'message': 'CGPA does not meet the minimum requirement'}, 400
        app, err = StudentService.apply(
            student_id, drive_id, _json().get('cover_letter'))
        if not app:
            return {'message': err}, 400
        cache.delete_memoized(StudentApplicationsResource.get, StudentApplicationsResource, student_id)
        cache.delete_memoized(CompanyDriveApplicantsResource.get, CompanyDriveApplicantsResource, app.drive.company_id, drive_id)
        cache.delete("admin_stats")
        return marshal(app, application_fields), 201


class StudentWithdrawResource(Resource):

    @auth_required('token')
    @roles_required('student')
    def delete(self, student_id, application_id):
        ok, err = StudentService.withdraw(student_id, application_id)
        if ok:
            cache.delete_memoized(StudentApplicationsResource.get, StudentApplicationsResource, student_id)
            cache.delete("admin_stats")
        return ({'message': 'Application withdrawn'}, 200) if ok \
            else ({'message': err}, 400)

# ─── Student: Placements ──────────────────────────────────────────────────────

class StudentPlacementHistoryResource(Resource):

    @auth_required('token')
    @roles_required('student')
    @cache.memoize(timeout=TTL_LONG)
    def get(self, student_id):
        placements = Placement.query.filter_by(student_id=student_id) \
                                    .order_by(Placement.created_at.desc()).all()
        return marshal(placements, placement_fields), 200



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
        joining_date_str = data.get('joining_date')
        joining_date = datetime.strptime(joining_date_str, '%Y-%m-%d').date() if joining_date_str else None

        if new_status == 'Selected' and not Placement.query.filter_by(
                application_id=application_id).first():
            db.session.add(Placement(
                student_id=application.student_id,
                company_id=company_id,
                application_id=application_id,
                position_title=application.drive.title,
                salary=data.get('salary', application.drive.salary_max),
                joining_date=joining_date,
                feedback=data.get('feedback'),
                currency=application.drive.currency,
                status='Offered',
            ))

        db.session.commit()
        return marshal(application, application_fields), 200
    


class StudentPlacementStatusResource(Resource):
    """
    PATCH /api/student/<student_id>/placements/<placement_id>
    Student accepts or declines an offer — both are fully reversible.

    Allowed transitions (any direction):
        Offered  ↔  Joined
        Offered  ↔  Declined
        Joined   →  Declined
        Declined →  Joined

    Payload:  { "status": "Joined" | "Declined" | "Offered" }
    """

    @auth_required('token')
    @roles_required('student')
    def put(self, student_id, placement_id):
        data   = _json()
        status = data.get('status')

        ALLOWED = ('Offered', 'Joined', 'Declined')
        if status not in ALLOWED:
            return {
                'message': f'status must be one of: {", ".join(ALLOWED)}'
            }, 400

        placement = Placement.query.filter_by(
            id=placement_id,
            student_id=student_id,
        ).first()

        if not placement:
            return {'message': 'Placement not found'}, 404

        # Reversible — no guard on current status, any → any is allowed
        placement.status = status

        # Optional joining date when accepting
        if status == 'Joined' and data.get('joining_date'):
            try:
                placement.joining_date = datetime.fromisoformat(data['joining_date'])
            except ValueError:
                return {'message': 'Invalid joining_date format. Use ISO 8601.'}, 400

        db.session.commit()

        # Bust placement cache so next GET reflects new status
        cache.delete_memoized(
            StudentPlacementHistoryResource.get,
            StudentPlacementHistoryResource,
            student_id,
        )

        return marshal(placement, placement_fields), 200


# ─── Student: CSV Export ──────────────────────────────────────────────────────

class StudentCSVExportResource(Resource):
    """
    GET /api/student/<student_id>/export/csv
    Streams the student's full application history as a CSV download.
    No Celery, no polling — synchronous, same pattern as AdminExportDataResource.
    """

    @auth_required('token')
    @roles_required('student')
    def get(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {'message': 'Student not found.'}, 404

        applications = (
            Application.query
            .filter_by(student_id=student_id)
            .order_by(Application.applied_date.desc())
            .all()
        )

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Application ID', 'Company', 'Drive Title',
            'Job Type', 'Location', 'Salary (Max)',
            'Applied Date', 'Status', 'Reviewed Date', 'Notes',
        ])

        for a in applications:
            d = a.drive
            writer.writerow([
                a.id,
                d.company.company_name if d and d.company else 'N/A',
                d.title    if d else 'N/A',
                d.job_type if d else 'N/A',
                d.location if d else 'N/A',
                d.salary_max if d else 'N/A',
                a.applied_date.strftime('%Y-%m-%d %H:%M')  if a.applied_date  else '',
                a.status,
                a.reviewed_date.strftime('%Y-%m-%d %H:%M') if a.reviewed_date else '',
                a.notes or '',
            ])

        response = make_response(output.getvalue())
        response.headers['Content-Type']        = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = (
            f'attachment; filename=applications_{student_id}.csv'
        )
        return response

# ─── Company ──────────────────────────────────────────────────────────────────

class CompanyResource(Resource):

    @auth_required('token')
    @roles_accepted('company', 'admin', 'student')
    @cache.memoize(timeout=TTL_MEDIUM)
    def get(self, company_id):
        c = CompanyService.get_by_id(company_id)
        if not c:
            return {'message': 'Company not found'}, 404
        return marshal(c, company_fields), 200

    @auth_required('token')
    @roles_required('company')
    def put(self, company_id):
        c = CompanyService.update(company_id, _json())
        if not c:
            return {'message': 'Company not found'}, 404
        cache.delete_memoized(CompanyResource.get, CompanyResource, company_id)
        cache.delete("admin_companies")
        return marshal(c, company_fields), 200

    @auth_required('token')
    @roles_accepted('company', 'admin')
    def patch(self, company_id):
        c = CompanyService.update(company_id, _json())
        if not c:
            return {'message': 'Company not found'}, 404
        cache.delete_memoized(CompanyResource.get, CompanyResource, company_id)
        cache.delete("admin_companies")
        return marshal(c, company_fields), 200

    @auth_required('token')
    @roles_accepted('company', 'admin')
    def delete(self, company_id):
        ok, err = CompanyService.delete(company_id)
        if ok:
            cache.delete_memoized(CompanyResource.get, CompanyResource, company_id)
            cache.delete("admin_companies")
            cache.delete("admin_stats")
        return ({'message': 'Company profile deleted successfully'}, 200) if ok \
            else ({'message': err}, 400)


class CompanyListResource(Resource):

    @auth_required('token')
    @roles_required('admin')
    @cache.cached(timeout=TTL_SHORT, key_prefix="admin_companies")
    def get(self):
        return marshal(CompanyService.get_all(), company_fields), 200


class DriveListResource(Resource):
    @auth_required('token')
    @roles_accepted('admin', 'student')
    @cache.cached(timeout=TTL_SHORT, key_prefix="all_drives")
    def get(self):
        return marshal(DriveService.get_all(), drive_fields), 200


class AdminPlacementsResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        placements = Placement.query.order_by(Placement.created_at.desc()).all()
        return marshal(placements, placement_fields), 200


class StudentListResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    @cache.cached(timeout=TTL_SHORT, key_prefix="admin_students")
    def get(self):
        return marshal(StudentService.get_all_students(), student_fields), 200


# ─── Company Drives ───────────────────────────────────────────────────────────

class DriveResource(Resource):
    @auth_required('token')
    @roles_accepted('company', 'admin', 'student')
    @cache.memoize(timeout=TTL_MEDIUM)
    def get(self, company_id):
        return marshal(CompanyService.get_drives(company_id), drive_fields), 200

    @auth_required('token')
    @roles_required('company')
    def post(self, company_id):
        drive = DriveService.create(company_id, _json())
        cache.delete_memoized(DriveResource.get, company_id)
        cache.delete("all_drives")
        cache.delete("admin_stats")
        return marshal(drive, drive_fields), 201


class CompanyDriveResource(Resource):
    @auth_required('token')
    @roles_accepted('company', 'admin',"student")
    @cache.memoize(timeout=TTL_MEDIUM)
    def get(self, company_id, drive_id):
        drive = DriveService.get_by_id(drive_id)
        if not drive or drive.company_id != company_id:
            return {'message': 'Drive not found'}, 404
        return marshal(drive, drive_fields), 200

    @auth_required('token')
    @roles_required('company')
    def put(self, company_id, drive_id):
        drive = DriveService.update(drive_id, _json())
        if not drive:
            return {'message': 'Drive not found'}, 404
        cache.delete_memoized(DriveResource.get, company_id)
        cache.delete("all_drives")
        cache.delete("admin_stats")
        return marshal(drive, drive_fields), 200

    @auth_required('token')
    @roles_accepted('company', 'admin')
    def patch(self, company_id, drive_id):
        drive = DriveService.update_drive(drive_id, **_json())
        if not drive:
            return {'message': 'Drive not found'}, 404
        cache.delete_memoized(DriveResource.get, company_id)
        cache.delete("all_drives")
        cache.delete("admin_stats")
        return marshal(drive, drive_fields), 200

    @auth_required('token')
    @roles_accepted('company', 'admin')
    def delete(self, company_id, drive_id):
        ok = DriveService.delete(drive_id)
        if ok:
            cache.delete_memoized(DriveResource.get, company_id)
            cache.delete("all_drives")
            cache.delete("admin_stats")
        return ({'message': 'Drive deleted'}, 200) if ok \
            else ({'message': 'Drive not found'}, 404)


# ─── Company Applicants ───────────────────────────────────────────────────────

class CompanyDriveApplicantsResource(Resource):

    @auth_required('token')
    @roles_accepted('company', 'admin')
    @cache.memoize(timeout=TTL_SHORT)
    def get(self, company_id, drive_id):
        apps, err = CompanyService.get_applicants(company_id, drive_id)
        if apps is None:
            return {'message': err}, 404
        return marshal(apps, application_fields), 200

class DriveApplicantsAPI(Resource):
    def get(self, drive_id):
        applications = Application.query.filter_by(
            drive_id=drive_id
        ).all()
        return marshal(applications, application_fields), 200

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
        cache.delete_memoized(StudentApplicationsResource.get, StudentApplicationsResource, app.student_id)
        cache.delete_memoized(CompanyDriveApplicantsResource.get, CompanyDriveApplicantsResource, company_id, drive_id)
        return marshal(app, application_fields), 200


class CompanyDriveExportResource(Resource):
    """
    GET /api/company/drives/<int:drive_id>/export/csv
    Download all applicants for a drive as a CSV file.
    Only the owning company (or admin) can access this.
    """

    @auth_required('token')
    @roles_accepted('company', 'admin')
    def get(self, drive_id):
        from flask_security import current_user

        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return {'message': 'Drive not found.'}, 404

        # Companies can only export their own drives
        if 'admin' not in [r.name for r in current_user.roles]:
            company = Company.query.filter_by(user_id=current_user.id).first()
            if not company or drive.company_id != company.id:
                return {'message': 'Access denied.'}, 403

        applications = (
            Application.query
            .filter_by(drive_id=drive_id)
            .order_by(Application.applied_date.desc())
            .all()
        )

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Application ID',
            'Student Name',
            'Email',
            'Phone',
            'Roll Number',
            'Branch',
            'CGPA',
            'Graduation Year',
            'Skills',
            'Applied Date',
            'Status',
            'Reviewed Date',
            'Recruiter Notes',
        ])

        for a in applications:
            s = a.student
            u = s.user if s else None
            writer.writerow([
                a.id,
                u.name              if u else 'N/A',
                u.email             if u else 'N/A',
                s.phone             if s else 'N/A',
                s.roll_number       if s else 'N/A',
                s.branch            if s else 'N/A',
                s.cgpa              if s else 'N/A',
                s.graduation_year   if s else 'N/A',
                s.skills            if s else 'N/A',
                a.applied_date.strftime('%Y-%m-%d %H:%M')  if a.applied_date  else '',
                a.status,
                a.reviewed_date.strftime('%Y-%m-%d %H:%M') if a.reviewed_date else '',
                a.notes or '',
            ])

        safe_title = (drive.title or f'drive_{drive_id}') \
            .replace(' ', '_') \
            .replace('/', '-')[:40]
        filename = f'applicants_{safe_title}_{drive_id}.csv'

        response = make_response(output.getvalue())
        response.headers['Content-Type']        = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
# ─── Company: Interview ───────────────────────────────────────────────────────

class CompanyInterviewResource(Resource):

    @auth_required('token')
    @roles_accepted('company', 'admin', 'student')
    def get(self, company_id, application_id):
        application = Application.query.filter_by(id=application_id).first()
        print("Application:", application)
        print("Interview:", application.interview)
        if not application:
            return {'message': 'Application not found'}, 404
        if application.drive.company_id != company_id:
            return {'message': 'Unauthorized'}, 403
        if not application.interview:
            return {'error': 'No interview scheduled for this application'}, 404
        return marshal(application.interview, interview_fields), 200

    @auth_required('token')
    @roles_required('company')
    def post(self, company_id, application_id):
        data        = _json()
        application = Application.query.filter_by(id=application_id).first()
        if not application:
            return {'message': 'Application not found'}, 404
        if application.drive.company_id != company_id:
            return {'message': 'Unauthorized'}, 403
        if application.interview:
            return {'message': 'Interview already scheduled. Use PUT to update.'}, 400
        if not data.get('interview_date'):
            return {'message': 'interview_date is required'}, 400

        interview = Interview(
            application_id=application_id,
            drive_id=application.drive_id,
            company_id=company_id,
            student_id=application.student_id,
            interview_type=data.get('interview_type', 'Technical'),
            interview_date=datetime.fromisoformat(data['interview_date']),
            interview_mode=data.get('interview_mode', 'Online'),
            interview_link=data.get('interview_link'),
            instructions=data.get('instructions'),
            interviewer=data.get('interviewer'),
        )
        db.session.add(interview)
        if application.status == 'Applied':
            application.status = 'Shortlisted'
        db.session.commit()
        cache.delete_memoized(StudentApplicationsResource.get, StudentApplicationsResource, application.student_id)
        return marshal(interview, interview_fields), 201

    @auth_required('token')
    @roles_accepted('company', 'admin')
    def put(self, company_id, application_id):
        data        = _json()
        application = Application.query.filter_by(id=application_id).first()
        if not application:
            return {'message': 'Application not found'}, 404
        if application.drive.company_id != company_id:
            return {'message': 'Unauthorized'}, 403
        if not application.interview:
            return {'message': 'No interview found. Use POST to schedule first.'}, 404

        interview = application.interview
        if data.get("status") == "completed":
            interview.status = "completed"
        for field in ('interview_type', 'interview_mode', 'interview_link',
                      'instructions', 'interviewer', 'feedback'):
            if field in data:
                setattr(interview, field, data[field])
        
        if data.get('interview_date'):
            interview.interview_date = datetime.fromisoformat(data['interview_date'])
        interview.updated_at = datetime.utcnow()
        db.session.commit()
        cache.delete_memoized(StudentApplicationsResource.get, StudentApplicationsResource, application.student_id)
        return marshal(interview, interview_fields), 200

    @auth_required('token')
    @roles_accepted('company', 'admin')
    def delete(self, company_id, application_id):
        application = Application.query.filter_by(id=application_id).first()
        if not application:
            return {'message': 'Application not found'}, 404
        if application.drive.company_id != company_id:
            return {'message': 'Unauthorized'}, 403
        db.session.delete(application.interview)
        db.session.commit()
        cache.delete_memoized(StudentApplicationsResource.get, StudentApplicationsResource, application.student_id)
        return {'message': 'Interview deleted'}, 200


# ─── Admin: Applications ─────────────────────────────────────────────────────

class AdminApplicationsResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        status     = request.args.get('status')
        drive_id   = request.args.get('drive_id',   type=int)
        company_id = request.args.get('company_id', type=int)
        student_id = request.args.get('student_id', type=int)
        search     = request.args.get('q', '').strip().lower()

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

        if company_id:
            apps = [a for a in apps
                    if a.drive and a.drive.company_id == company_id]
        if search:
            apps = [a for a in apps if (
                (a.student and a.student.user and
                 search in a.student.user.name.lower())          or
                (a.drive and a.drive.company and
                 search in a.drive.company.company_name.lower()) or
                (a.drive and search in a.drive.title.lower())
            )]

        result = marshal(apps, application_fields)
        cache.set(cache_key, result, timeout=TTL_SHORT)
        return result, 200


# ─── Admin: Search ────────────────────────────────────────────────────────────

class AdminSearchResource(Resource):
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
    @cache.cached(timeout=TTL_SHORT, key_prefix="admin_stats")
    def get(self):
        return {
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
        }, 200


# ─── Admin: Export ────────────────────────────────────────────────────────────

class AdminExportDataResource(Resource):

    @auth_required('token')
    @roles_required('admin')
    def get(self):
        export_type = request.args.get('type', 'students')
        output      = StringIO()
        writer      = csv.writer(output)

        if export_type == 'students':
            writer.writerow(['ID', 'Name', 'Email', 'Roll', 'Branch', 'CGPA', 'Year', 'Active'])
            for s in Student.query.all():
                writer.writerow([
                    s.id, s.user.name, s.user.email,
                    s.roll_number, s.branch, s.cgpa,
                    s.graduation_year, s.user.active,
                ])

        elif export_type == 'companies':
            writer.writerow(['ID', 'Name', 'Website', 'Industry', 'Status', 'Active'])
            for c in Company.query.all():
                writer.writerow([
                    c.id, c.company_name, c.website,
                    c.industry, c.approval_status, c.user.active,
                ])

        elif export_type == 'drives':
            writer.writerow([
                'ID', 'Title', 'Company', 'Location',
                'Salary Min', 'Salary Max', 'Status', 'Deadline', 'Applicants',
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
        response.headers['Content-Disposition'] = f'attachment; filename={export_type}.csv'
        return response


# ─── File Serving ─────────────────────────────────────────────────────────────

class ResumeServeResource(Resource):

    @auth_required('token')
    @roles_accepted('student', 'company', 'admin')
    def get(self, filename):
        file_path = storage.path_for(storage.RESUMES, filename)
        if file_path is None:
            return {'message': 'Invalid filename'}, 400

        if not os.path.exists(file_path):
            return {'message': 'File not found'}, 404

        return send_from_directory(
            storage.subdir(storage.RESUMES), filename, as_attachment=False
        )

# ─── Offer Letter Upload ───────────────────────────────────────────────────────

class OfferLetterUploadResource(Resource):

    @auth_required('token')
    @roles_accepted('company', 'admin')
    def post(self):

        student_id     = request.form.get('student_id',     '').strip()
        application_id = request.form.get('application_id', '').strip()
        offer_file     = request.files.get('offer_letter')

        if not student_id:
            return {'message': 'student_id is required.'}, 400
        if not application_id:
            return {'message': 'application_id is required.'}, 400
        if not offer_file:
            return {'message': 'offer_letter file is required.'}, 400

        if not student_id.isdigit() or not application_id.isdigit():
            return {'message': 'student_id and application_id must be numeric.'}, 400

        filename = f"offer_{application_id}_{student_id}.pdf"
        filepath = os.path.join(storage.subdir(storage.OFFERS), filename)
        offer_file.save(filepath)

        placement = Placement.query.filter_by(
            application_id=int(application_id)
        ).first()

        if not placement:
            if os.path.exists(filepath):
                os.remove(filepath)
            return {
                'message': (
                    f'No placement record found for application_id={application_id}. '
                    'Mark the candidate as Selected first.'
                )
            }, 404

        placement.offer_letter_filename       = filename
        placement.offer_letter_url            = f'/api/uploads/offers/{filename}'
        placement.offer_letter_generated_date = datetime.utcnow()
        db.session.commit()

        return {
            'message':               'Offer letter saved successfully.',
            'offer_letter_filename':  filename,
            'offer_letter_url':       placement.offer_letter_url,
        }, 200


# ─── Offer Letter Download ─────────────────────────────────────────────────────

class OfferLetterDownloadResource(Resource):

    @auth_required('token')
    @roles_accepted('student', 'company', 'admin')
    def get(self, filename):

        filepath = storage.path_for(storage.OFFERS, filename)
        if filepath is None:
            return {'message': 'Invalid filename.'}, 400

        if not os.path.exists(filepath):
            return {'message': 'Offer letter not found.'}, 404

        return send_from_directory(
            storage.subdir(storage.OFFERS),
            filename,
            mimetype='application/pdf',
            as_attachment=False
        )