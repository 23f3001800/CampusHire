# create_profile(user_id, data)
# post_job(company_id, data)
# review_applicants(job_id)


from models import Company, JobPosition, db

class CompanyService:
    @staticmethod
    def get_all_companies():
        return Company.query.all()
    
    @staticmethod
    def get_company_by_id(company_id):
        return Company.query.get(company_id)

    # @staticmethod
    # def create_profile(user_id, data):
    #     new_company = Company(user_id=user_id, **data)
    #     db.session.add(new_company)
    #     db.session.commit()
    #     return new_company
    
    @staticmethod
    def update_profile(user_id, data):
        company = Company.query.filter_by(user_id=user_id).first()
        if not company:
            return None
        for key, value in data.items():
            setattr(company, key, value)
        db.session.commit()
        return company
    
    @staticmethod
    def delete_profile(company_id):
        company = Company.query.get(company_id)
        if company:
            db.session.delete(company)
            db.session.commit()
            return True
        return False

    @staticmethod
    def post_job(company_id, data):
        company = Company.query.get(company_id)
        if not company:
            return None
        new_job = JobPosition(company_id=company_id, **data)
        db.session.add(new_job)
        db.session.commit()
        return new_job