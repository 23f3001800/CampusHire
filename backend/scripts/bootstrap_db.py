"""
bootstrap_db.py — safe, idempotent database bootstrap
=====================================================

This is what production runs. Unlike scripts/init_db.py (which calls drop_all()
and is DEVELOPMENT ONLY), this script never destroys data:

    * creates any missing tables            (create_all is a no-op for existing ones)
    * creates the three roles if absent
    * creates the admin user if absent

Safe to run on every deploy. Used as Render's preDeployCommand.

Usage:
    python -m scripts.bootstrap_db

The admin password comes from ADMIN_PASSWORD. The script refuses to invent one
in production — an unattended default admin password on a public URL is how
these projects get taken over.
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app                              # noqa: E402
from models import db                                   # noqa: E402
from flask_security.utils import hash_password           # noqa: E402

ROLES = [
    ("admin",   "Institute placement cell — full control"),
    ("student", "Student user"),
    ("company", "Recruiting company user"),
]


def main():
    app = create_app()

    with app.app_context():
        print("→ Creating any missing tables…")
        db.create_all()

        datastore = app.datastore

        print("→ Ensuring roles exist…")
        for name, description in ROLES:
            if not datastore.find_role(name):
                datastore.find_or_create_role(name, description=description)
                print(f"   + created role: {name}")
        datastore.commit()

        admin_email    = app.config["ADMIN_EMAIL"]
        admin_password = os.getenv("ADMIN_PASSWORD")

        if datastore.find_user(email=admin_email):
            print(f"→ Admin already exists ({admin_email}) — leaving it alone.")
        elif not admin_password:
            # Do not silently seed a guessable credential.
            msg = (
                f"No admin user exists and ADMIN_PASSWORD is not set.\n"
                f"   Set ADMIN_PASSWORD in the environment and re-run to create {admin_email}."
            )
            if app.config["DEBUG"]:
                print(f"⚠  {msg}")
            else:
                sys.exit(f"✗ {msg}")
        elif len(admin_password) < 12:
            sys.exit("✗ ADMIN_PASSWORD must be at least 12 characters.")
        else:
            print(f"→ Creating admin user {admin_email}…")
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
        print("✅ Bootstrap complete.")


if __name__ == "__main__":
    main()
