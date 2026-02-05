# seed.py
import os
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash


def _table_exists(db, table_name: str) -> bool:
    try:
        inspector = inspect(db.engine)
        return table_name in inspector.get_table_names()
    except Exception:
        return False


def seed_all(db):
    # If migrations haven't created tables yet, do nothing.
    # This prevents flask db init/migrate from exploding.
    if not _table_exists(db, "admin"):
        return

    seed_admin(db)
    seed_user_profile(db)
    seed_foundation_about(db)
    seed_journey_defaults(db)
    db.session.commit()


def seed_admin(db):
    from models import Admin

    if Admin.query.first():
        return

    email = os.getenv("INIT_ADMIN_EMAIL", "admin@example.com")
    password = os.getenv("INIT_ADMIN_PASSWORD", "change-me-now")

    db.session.add(Admin(
        email=email,
        password=generate_password_hash(password),
        totp_enabled=False,
    ))


def seed_user_profile(db):
    from models import User

    if User.query.first():
        return

    db.session.add(User(
        name=os.getenv("INIT_PROFILE_NAME", "Artist Name"),
        short_about=os.getenv("INIT_PROFILE_SHORT_ABOUT", "Edit this in the CMS.")
    ))


def seed_foundation_about(db):
    from models import FoundationAbout

    defaults = [
        {"id": 1, "title": "paragraph_one", "paragraphs": "Edit this in the CMS."},
        {"id": 2, "title": "paragraph_two", "paragraphs": "Edit this in the CMS."},
    ]

    for row in defaults:
        if not FoundationAbout.query.get(row["id"]):
            db.session.add(FoundationAbout(**row))


def seed_journey_defaults(db):
    from models import Journey

    defaults = [
        {"year": 2015, "desc": "Started writing and performing original material."},
        {"year": 2018, "desc": "Released early demos and refined artistic direction."},
    ]

    for row in defaults:
        if not Journey.query.filter_by(year=row["year"]).first():
            db.session.add(Journey(**row))
