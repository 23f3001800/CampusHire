# create_profile(user_id, data)
# update_profile(user_id, data)
# apply_for_job(student_id, job_id)



from models import Student, db

class StudentService:
    @staticmethod
    def get_all_students():
        return Student.query.all()
    

    @staticmethod
    def get_student_by_id(student_id):
        return Student.query.get(student_id)

    # @staticmethod
    # def create_student(user_id, data):
    #     new_student = Student(user_id=user_id, **data)
    #     db.session.add(new_student)
    #     db.session.commit()
    #     return new_student

    @staticmethod
    def update_student(user_id, data):
        student = Student.query.get(data['id'])
        if not student:
            return None
        for key, value in data.items():
            setattr(student, key, value)
        db.session.commit()
        return student

    @staticmethod
    def apply_for_job(student_id, job_id):
        student = Student.query.get(student_id)
        if not student:
            return None
        student.application.append(job_id)  # Assuming applied_jobs is a relationship
        db.session.commit()
        return student
    
    @staticmethod
    def delete_student(student_id):
        student = Student.query.get(student_id)
        if student:
            db.session.delete(student)
            db.session.commit()
            return True
        return False