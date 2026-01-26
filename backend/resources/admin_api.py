from flask_security import auth_required, current_user
from flask_restful import Resource, reqparse
from models import User, Role   
from db import db


class AdminUserListAPI(Resource):
    @auth_required('admin')
    def get(self):
        users = User.query.all()
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "roles": [role.name for role in user.roles],
                "created_at": user.created_at,
            })
        return {"users": user_list}, 200
