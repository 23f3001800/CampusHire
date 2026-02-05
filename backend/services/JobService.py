# create_job(data)
# get_jobs(filters)
# close_job(job_id)


from models import JobPosition, db
class JobService:
    @staticmethod
    def get_all_jobs():
        return JobPosition.query.all()
    
    @staticmethod
    def get_jobs(id):
        query = JobPosition.query.filter(JobPosition.id == id)
        return query.all()
    
    # @staticmethod
    # def create_job(data):
    #     new_job = JobPosition(**data)
    #     db.session.add(new_job)
    #     db.session.commit()
    #     return new_job

    
    @staticmethod
    def update_job(job_id, data):
        job = JobPosition.query.get(job_id)
        if not job:
            return None
        for key, value in data.items():
            setattr(job, key, value)
        db.session.commit()
        return job
    

    @staticmethod
    def delete_job(job_id):
        job = JobPosition.query.get(job_id)
        if job:
            db.session.delete(job)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def review_applicants(job_id):
        job = JobPosition.query.get(job_id)
        if not job:
            return None
        return job.applications  

    @staticmethod
    def close_job(job_id):
        job = JobPosition.query.get(job_id)
        if not job:
            return None
        job.status = 'Closed'
        db.session.commit()
        return job
    