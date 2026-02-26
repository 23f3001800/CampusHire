from flask_restful import Api
from flask import Blueprint
from resources.auth_api import auth_bp

from resources.api import (

    # ── Student ──────────────────────────────────────────────────────────
    StudentResource,
    StudentListResource,
    StudentResumeResource,
    StudentEligibleDrivesResource,
    StudentApplicationsResource,
    StudentApplyResource,
    StudentWithdrawResource,
    StudentInterviewResource,
    StudentPlacementHistoryResource,
    StudentCSVExportResource,
    StudentCSVExportStatusResource,
    StudentCSVDownloadResource,

    # ── Company ──────────────────────────────────────────────────────────
    CompanyResource,
    CompanyListResource,
    DrivesResource,
    CompanyDriveResource,
    CompanyDriveApplicantsResource,
    CompanyDriveApplicantResource,
    CompanyInterviewResource,
    CompanyUpdateSelectionResource,
    CompanyCSVExportResource,
    CompanyCSVExportStatusResource,
    CompanyCSVDownloadResource,

    # ── Public ───────────────────────────────────────────────────────────
    DriveListResource,
    DriveResource,

    # ── Admin ────────────────────────────────────────────────────────────
    AdminCompanyApprovalResource,
    AdminDriveApprovalResource,
    AdminDriveResource,
    AdminDriveApplicantsResource,
    AdminApplicationsResource,
    AdminSearchResource,
    AdminUserActiveResource,
    AdminStatsResource,
    AdminPlacementsResource,
    AdminExportDataResource,

    # ── File Serving ─────────────────────────────────────────────────────
    ResumeServeResource,
)

api_bp = Blueprint('api', __name__, url_prefix='/api')
api    = Api(api_bp)


# ── Student ───────────────────────────────────────────────────────────────────
api.add_resource(StudentListResource,             '/admin/students')
api.add_resource(StudentResource,                 '/student/<int:student_id>')
api.add_resource(StudentResumeResource,           '/student/<int:student_id>/resume')
api.add_resource(StudentEligibleDrivesResource,   '/student/<int:student_id>/eligible-drives')
api.add_resource(StudentApplicationsResource,     '/student/<int:student_id>/applications')
api.add_resource(StudentApplyResource,            '/student/<int:student_id>/apply/<int:drive_id>')
api.add_resource(StudentWithdrawResource,         '/student/<int:student_id>/applications/<int:application_id>')
api.add_resource(StudentInterviewResource,        '/student/<int:student_id>/applications/<int:application_id>/interview')
api.add_resource(StudentPlacementHistoryResource, '/student/<int:student_id>/placements')
api.add_resource(StudentCSVExportResource,        '/student/<int:student_id>/export-csv')
api.add_resource(StudentCSVExportStatusResource,  '/student/<int:student_id>/export-csv/<string:task_id>/status')
api.add_resource(StudentCSVDownloadResource,      '/student/<int:student_id>/export-csv/<string:filename>/download')


# ── Company ───────────────────────────────────────────────────────────────────
api.add_resource(CompanyListResource,            '/admin/companies')
api.add_resource(CompanyResource,                '/company/<int:company_id>')
api.add_resource(DrivesResource,                 '/company/<int:company_id>/drives')
api.add_resource(CompanyDriveResource,           '/company/<int:company_id>/drives/<int:drive_id>')
api.add_resource(CompanyDriveApplicantsResource, '/company/<int:company_id>/drives/<int:drive_id>/applicants')
api.add_resource(CompanyDriveApplicantResource,  '/company/<int:company_id>/drives/<int:drive_id>/applicants/<int:application_id>')
api.add_resource(CompanyInterviewResource,       '/company/<int:company_id>/applications/<int:application_id>/interview')
api.add_resource(CompanyUpdateSelectionResource, '/company/<int:company_id>/applications/<int:application_id>/selection')


# ── Company CSV Export ────────────────────────────────────────────────────────
api.add_resource(CompanyCSVExportResource,
                 '/company/<int:company_id>/drives/<int:drive_id>/export-csv')
api.add_resource(CompanyCSVExportStatusResource,
                 '/company/<int:company_id>/drives/<int:drive_id>/export-csv/<string:task_id>/status')
api.add_resource(CompanyCSVDownloadResource,
                 '/company/<int:company_id>/drives/<int:drive_id>/export-csv/<string:filename>/download')


# ── Public Drives ─────────────────────────────────────────────────────────────
api.add_resource(DriveListResource, '/drives')
api.add_resource(DriveResource,     '/drives/<int:drive_id>')


# ── Admin ─────────────────────────────────────────────────────────────────────
api.add_resource(AdminStatsResource,           '/admin/stats')
api.add_resource(AdminSearchResource,          '/admin/search')
api.add_resource(AdminApplicationsResource,    '/admin/applications')
api.add_resource(AdminCompanyApprovalResource, '/admin/companies/<int:company_id>/approval')
api.add_resource(AdminDriveResource,           '/admin/drives')
api.add_resource(AdminDriveApprovalResource,   '/admin/drives/<int:drive_id>/approval')
api.add_resource(AdminDriveApplicantsResource, '/admin/drives/<int:drive_id>/applicants')
api.add_resource(AdminUserActiveResource,      '/admin/users/<int:user_id>/active')
api.add_resource(AdminPlacementsResource,      '/admin/placements')
api.add_resource(AdminExportDataResource,      '/admin/export')


# ── File Serving ──────────────────────────────────────────────────────────────
api.add_resource(ResumeServeResource, '/uploads/resumes/<string:filename>')
