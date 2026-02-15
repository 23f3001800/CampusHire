# Package initialization
from flask_restful import Api
from flask import Blueprint
from resources.auth_api import auth_bp

from resources.api import (
    AdminDriveApplicantsResource, AdminDriveApprovalResource, StudentCSVDownloadResource, StudentCSVExportResource, StudentCSVExportStatusResource, StudentPlacementHistoryResource, StudentResource, StudentListResource,
    StudentResumeResource, StudentEligibleDrivesResource,
    StudentApplicationsResource, StudentApplyResource, StudentWithdrawResource,
    CompanyResource, CompanyListResource,
    CompanyDrivesResource, CompanyDriveResource,
    CompanyDriveApplicantsResource, CompanyDriveApplicantResource,
    DriveResource, DriveListResource,
    AdminCompanyApprovalResource,
    AdminUserActiveResource,
    AdminDriveResource,
    AdminStatsResource,
    AdminPlacementsResource,
    ResumeServeResource,
)


api_bp = Blueprint('api', __name__, url_prefix='/api')

api = Api(api_bp)

# ── Student ──────────────────────────────────────────────────────────────
api.add_resource(StudentListResource,              '/admin/students')
api.add_resource(StudentResource,                  '/student/<int:student_id>')
api.add_resource(StudentResumeResource,            '/student/<int:student_id>/resume')
api.add_resource(StudentEligibleDrivesResource,    '/student/<int:student_id>/eligible-drives')
api.add_resource(StudentApplicationsResource,      '/student/<int:student_id>/applications')
api.add_resource(StudentApplyResource,             '/student/<int:student_id>/apply/<int:drive_id>')
api.add_resource(StudentWithdrawResource,          '/student/<int:student_id>/applications/<int:application_id>')
api.add_resource(StudentPlacementHistoryResource,  '/student/<int:student_id>/placements')
api.add_resource(StudentCSVExportResource,         '/student/<int:student_id>/export-csv')
api.add_resource(StudentCSVExportStatusResource,   '/student/<int:student_id>/export-csv/<string:task_id>/status')
api.add_resource(StudentCSVDownloadResource,       '/student/<int:student_id>/export-csv/<string:filename>/download')

# ── Company ──────────────────────────────────────────────────────────────
api.add_resource(CompanyListResource,               '/admin/companies')
api.add_resource(CompanyResource,                   '/company/<int:company_id>')
api.add_resource(CompanyDrivesResource,             '/company/<int:company_id>/drives')
api.add_resource(CompanyDriveResource,              '/company/<int:company_id>/drives/<int:drive_id>')
api.add_resource(CompanyDriveApplicantsResource,    '/company/<int:company_id>/drives/<int:drive_id>/applicants')
api.add_resource(CompanyDriveApplicantResource,     '/company/<int:company_id>/drives/<int:drive_id>/applicants/<int:application_id>')
# ── Public Drives ─────────────────────────────────────────────────────────
api.add_resource(DriveListResource, '/drives')
api.add_resource(DriveResource,     '/drives/<int:drive_id>')

# ── Admin ─────────────────────────────────────────────────────────────────
api.add_resource(AdminCompanyApprovalResource,  '/admin/companies/<int:company_id>/approval')
api.add_resource(AdminDriveApprovalResource,    '/admin/drives/<int:drive_id>/approval')
api.add_resource(AdminDriveApplicantsResource,  '/admin/drives/<int:drive_id>/applicants')
api.add_resource(AdminUserActiveResource,       '/admin/users/<int:user_id>/active')
api.add_resource(AdminDriveResource,            '/admin/drives/<int:drive_id>')
api.add_resource(AdminStatsResource,            '/admin/stats')
api.add_resource(AdminPlacementsResource,       '/admin/placements')

# ── Static Files ──────────────────────────────────────────────────────────
api.add_resource(ResumeServeResource, '/uploads/resumes/<string:filename>')


