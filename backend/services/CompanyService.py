from models import Company, PlacementDrive, Application, Placement, db
from datetime import datetime


class CompanyService:

    UPDATABLE = [
        'company_name', 'industry', 'company_size',
        'location', 'website', 'description', 'logo_url',
        'hr_email', 'hr_contact', 'department', 'designation',"approval_status", "active"
    ]

    # ── Company Profile ─────────────────────────────────────────────────────

    @staticmethod
    def get_all():
        return Company.query.all()

    @staticmethod
    def get_by_id(company_id):
        return Company.query.get(company_id)

    @staticmethod
    def update(company_id, data):
        company = db.session.get(Company, company_id)

        if not company:
            return None

        if "active" in data:
            new_active = bool(data["active"])

            if company.user:
                company.user.active = new_active

            company.active = new_active

            drives = PlacementDrive.query.filter_by(company_id=company.id).all()

            if not new_active:
                # BLOCK company → reject and close drives
                for d in drives:
                    if d.admin_approval_status != "Rejected":
                        d.admin_approval_status = "Rejected"
                    d.status = "Closed"

        # update other fields
        for field in CompanyService.UPDATABLE:
            if field in data:
                setattr(company, field, data[field])

        company.updated_at = datetime.utcnow()

        db.session.commit()

        return company
        

    @staticmethod
    def delete(company_id):
        company = Company.query.get(company_id)
        if not company:
            return False, 'Company not found'
        db.session.delete(company)
        db.session.commit()
        return True, None

    # ── Drives ──────────────────────────────────────────────────────────────

    @staticmethod
    def get_drives(company_id):
        return PlacementDrive.query.filter_by(company_id=company_id)\
                                   .order_by(PlacementDrive.posted_date.desc()).all()

    # ── Applicants ──────────────────────────────────────────────────────────

    @staticmethod
    def get_applicants(company_id, drive_id):
        drive = PlacementDrive.query.filter_by(
            id=drive_id, company_id=company_id).first()
        if not drive:
            return None, 'Drive not found or does not belong to this company'
        apps = Application.query.filter_by(drive_id=drive_id)\
                                .order_by(Application.applied_date.desc()).all()
        return apps, None

    @staticmethod
    def update_application_status(company_id, drive_id, application_id, status, notes=None):
        VALID = ('Applied', 'Shortlisted', 'Rejected', 'Selected')
        if status not in VALID:
            return None, f'Status must be one of: {", ".join(VALID)}'
        drive = PlacementDrive.query.filter_by(
            id=drive_id, company_id=company_id).first()
        if not drive:
            return None, 'Drive not found'
        app = Application.query.filter_by(
            id=application_id, drive_id=drive_id).first()
        if not app:
            return None, 'Application not found'
        app.status        = status
        app.reviewed_date = datetime.utcnow()
        if notes:
            app.notes = notes
        # Auto-create Placement when Selected
        if status == 'Selected' and not Placement.query.filter_by(
                application_id=application_id).first():
            db.session.add(Placement(
                student_id=app.student_id,
                company_id=company_id,
                application_id=application_id,
                position_title=drive.title,
                salary=drive.salary_max,
                currency=drive.currency,
                status='Offered',
            ))
        db.session.commit()
        return app, None
