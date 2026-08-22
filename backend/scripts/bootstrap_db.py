"""
bootstrap_db.py — safe, idempotent database bootstrap for deployment.

Unlike scripts/init_db.py (which calls drop_all() and is DEVELOPMENT ONLY),
this destroys nothing and is safe to run on every boot:

    * creates any missing tables
    * creates the admin/student/company roles if absent
    * creates the admin user if absent

Without this a fresh deployment has an empty role table, so login fails and
registration returns "Role 'student' not found in database".

Usage:
    python -m scripts.bootstrap_db

The admin password comes from ADMIN_PASSWORD. If no admin exists and that is
unset, the script says so and exits without creating a guessable account.
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app                                    # noqa: E402
from models import db                                  # noqa: E402
from flask_security.utils import hash_password         # noqa: E402

ROLES = [
    ("admin",   "Institute placement cell"),
    ("student", "Student user"),
    ("company", "Recruiting company user"),
]


def main():
    with app.app_context():
        print("-> creating any missing tables")
        db.create_all()

        datastore = app.datastore

        print("-> ensuring roles exist")
        for name, description in ROLES:
            if not datastore.find_role(name):
                datastore.find_or_create_role(name, description=description)
                print("   + created role: " + name)
        datastore.commit()

        admin_email = app.config.get("ADMIN_EMAIL", "admin@campushire.edu")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if datastore.find_user(email=admin_email):
            print("-> admin already exists (" + admin_email + ") - leaving it alone")
        elif not admin_password:
            print("!  no admin user, and ADMIN_PASSWORD is unset.")
            print("   Set ADMIN_PASSWORD and redeploy to create " + admin_email + ".")
        elif len(admin_password) < 12:
            sys.exit("x  ADMIN_PASSWORD must be at least 12 characters.")
        else:
            print("-> creating admin " + admin_email)
            datastore.create_user(
                email=admin_email,
                name=os.getenv("ADMIN_NAME", "Placement Cell Admin"),
                password=hash_password(admin_password),
                active=True,
                fs_uniquifier=str(uuid.uuid4()),
                roles=[datastore.find_role("admin")],
            )
            datastore.commit()
            print("   + admin created")

        db.session.commit()
        print("bootstrap complete")


if __name__ == "__main__":
    main()
