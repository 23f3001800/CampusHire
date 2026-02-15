from models import PlacementDrive, db
from datetime import datetime


class DriveService:

    UPDATABLE = [
        'title', 'description', 'job_type', 'location',
        'salary_min', 'salary_max', 'currency',
        'min_cgpa', 'eligible_branches', 'eligible_graduation_year',
        'experience_required', 'skills_required', 'status',
    ]

    @staticmethod
    def get_all():
        """Returns only drives that are Open AND admin-approved."""
        return PlacementDrive.query.filter_by(status='Open', admin_approval_status='Approved')\
                                   .order_by(PlacementDrive.posted_date.desc()).all()

    @staticmethod
    def get_by_id(drive_id):
        return PlacementDrive.query.get(drive_id)

    @staticmethod
    def create(company_id, data):
        drive = PlacementDrive(
            company_id=company_id,
            title=data.get('title'),
            description=data.get('description'),
            job_type=data.get('job_type'),
            location=data.get('location'),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            currency=data.get('currency', 'INR'),
            min_cgpa=data.get('min_cgpa', 0.0),
            eligible_branches=data.get('eligible_branches'),
            eligible_graduation_year=data.get('eligible_graduation_year'),
            experience_required=data.get('experience_required'),
            skills_required=data.get('skills_required'),
            drive_date=datetime.fromisoformat(data['drive_date']) if data.get('drive_date') else None,
            application_deadline=datetime.fromisoformat(data['application_deadline']) if data.get('application_deadline') else None,
            status='Open',
        )
        db.session.add(drive)
        db.session.commit()
        return drive

    @staticmethod
    def update(drive_id, data):
        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return None
        for field in DriveService.UPDATABLE:
            if field in data and data[field] is not None:
                setattr(drive, field, data[field])
        if data.get('drive_date'):
            drive.drive_date = datetime.fromisoformat(data['drive_date'])
        if data.get('application_deadline'):
            drive.application_deadline = datetime.fromisoformat(data['application_deadline'])
        drive.updated_at = datetime.utcnow()
        db.session.commit()
        return drive

    @staticmethod
    def toggle_status(drive_id):
        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return None
        drive.status     = 'Closed' if drive.status == 'Open' else 'Open'
        drive.updated_at = datetime.utcnow()
        db.session.commit()
        return drive

    @staticmethod
    def delete(drive_id):
        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return False
        db.session.delete(drive)
        db.session.commit()
        return True