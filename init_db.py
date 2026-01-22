from model import db, User, Role
from flask import Flask
from werkzeug.security import generate_password_hash

def init_database(app):
    """Initialize database and create admin user"""
    with app.app_context():
        db.create_all()
        
        # Create roles if they don't exist
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            admin_role = Role(name='Admin', description='Administrator')
            db.session.add(admin_role)
        
        student_role = Role.query.filter_by(name='Student').first()
        if not student_role:
            student_role = Role(name='Student', description='Student')
            db.session.add(student_role)
        
        company_role = Role.query.filter_by(name='Company').first()
        if not company_role:
            company_role = Role(name='Company', description='Company')
            db.session.add(company_role)
        
        db.session.commit()
        
        # Create default admin user if it doesn't exist
        admin_user = User.query.filter_by(email='admin@campushire.com').first()
        if not admin_user:
            admin_user = User(
                email='admin@campushire.com',
                password=generate_password_hash('admin123'),
                is_active=True
            )
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
            print("✓ Admin user created: admin@campushire.com")
        else:
            print("✓ Admin user already exists")

if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campushire.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    init_database(app)
    print("✓ Database initialized successfully")
