from __future__ import annotations

from app.config import settings
from app.db.base import Base
from app.db.models import User
from app.db.session import engine, get_session
from app.security import hash_password


def init_db(create_admin: bool = True) -> None:
    Base.metadata.create_all(bind=engine)

    if create_admin:
        seed_default_admin()


def seed_default_admin() -> bool:
    username = settings.default_admin_username.strip()
    password = settings.default_admin_password.strip()

    if not username or not password:
        return False

    session = get_session()
    try:
        existing = session.query(User).filter(User.username == username).first()
        if existing:
            changed = False

            if existing.role != "admin":
                existing.role = "admin"
                changed = True

            if not existing.is_active:
                existing.is_active = True
                changed = True

            if changed:
                session.commit()

            return False

        session.add(
            User(
                username=username,
                password_hash=hash_password(password),
                role="admin",
                is_active=True,
            )
        )
        session.commit()
        return True
    finally:
        session.close()