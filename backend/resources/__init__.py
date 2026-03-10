from flask_restful import Api
from flask import Blueprint
from resources.auth_api import auth_bp

from resources.api import (

    # ── Student ──────────────────────────────────────────────────────────
    DriveApplicantsAPI,
    OfferLetterDownloadResource,
    StudentResource,
    StudentListResource,
    StudentResumeResource,
    StudentApplicationsResource,
    StudentApplyResource,
    StudentWithdrawResource,
    StudentPlacementHistoryResource,
    StudentCSVExportResource,

    # ── Company ──────────────────────────────────────────────────────────
    CompanyResource,
    CompanyListResource,
    CompanyDriveResource,
    CompanyDriveApplicantsResource,
    CompanyDriveApplicantResource,
    CompanyInterviewResource,
    CompanyUpdateSelectionResource,
    CompanyDriveExportResource,


    # ── Public ───────────────────────────────────────────────────────────
    DriveListResource,
    DriveResource,
    StudentPlacementStatusResource,


    # ── Admin ────────────────────────────────────────────────────────────
    AdminApplicationsResource,
    AdminSearchResource,
    AdminStatsResource,
    AdminPlacementsResource,
    AdminExportDataResource,

    # ── File Serving ─────────────────────────────────────────────────────
    ResumeServeResource,
    OfferLetterDownloadResource,
    OfferLetterUploadResource
)

api_bp = Blueprint('api', __name__, url_prefix='/api')
api    = Api(api_bp)


# ── Student ───────────────────────────────────────────────────────────────────
api.add_resource(StudentListResource,             '/admin/students')
api.add_resource(StudentResource,                 '/student/<int:student_id>')
api.add_resource(StudentResumeResource,           '/student/<int:student_id>/resume')
api.add_resource(StudentApplicationsResource,     '/student/<int:student_id>/applications')
api.add_resource(StudentApplyResource,            '/student/<int:student_id>/apply/<int:drive_id>')
api.add_resource(StudentWithdrawResource,         '/student/<int:student_id>/applications/<int:application_id>')
api.add_resource(StudentPlacementHistoryResource, '/student/<int:student_id>/placements')
api.add_resource(StudentCSVExportResource,        '/student/<int:student_id>/export/csv')


# ── Company ───────────────────────────────────────────────────────────────────
api.add_resource(CompanyListResource,            '/admin/companies')
api.add_resource(CompanyResource,                '/company/<int:company_id>') # For POST (create)
api.add_resource(CompanyDriveResource,           '/company/<int:company_id>/drives/<int:drive_id>')
api.add_resource(CompanyDriveApplicantsResource, '/company/<int:company_id>/drives/<int:drive_id>/applicants')
api.add_resource(CompanyDriveApplicantResource,  '/company/<int:company_id>/drives/<int:drive_id>/applicants/<int:application_id>')
api.add_resource(CompanyInterviewResource,       '/company/<int:company_id>/applications/<int:application_id>/interview')
api.add_resource(CompanyUpdateSelectionResource, '/company/<int:company_id>/applications/<int:application_id>/selection')
api.add_resource(CompanyDriveExportResource,
    '/company/drives/<int:drive_id>/export/csv')



api.add_resource(DriveListResource, '/drives')
api.add_resource(DriveResource,     '/company/<int:company_id>/drives')
api.add_resource(
    StudentPlacementStatusResource,
    '/student/<int:student_id>/placements/<int:placement_id>'
)    

# ── Admin ─────────────────────────────────────────────────────────────────────
api.add_resource(AdminStatsResource,           '/admin/stats')
api.add_resource(AdminSearchResource,          '/admin/search')
api.add_resource(AdminApplicationsResource,    '/admin/applications')
api.add_resource(AdminPlacementsResource,      '/admin/placements')
api.add_resource(AdminExportDataResource,      '/admin/export')
api.add_resource(
    DriveApplicantsAPI,
    "/admin/drives/<int:drive_id>/applicants"
)


# ── File Serving ──────────────────────────────────────────────────────────────
api.add_resource(ResumeServeResource, '/uploads/resumes/<string:filename>')
api.add_resource(
    OfferLetterDownloadResource, 
    '/uploads/offers/<string:filename>'
)
api.add_resource(OfferLetterUploadResource, '/upload-offer')

