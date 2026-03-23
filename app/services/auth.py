from __future__ import annotations

from app.repositories.users import UserRepository
from app.security import verify_password

ROLE_RANK = {"viewer": 1, "auditor": 2, "admin": 3}


def authenticate(session, username: str, password: str):
    username = (username or "").strip()
    password = password or ""

    if not username or not password:
        return None

    repo = UserRepository(session)
    user = repo.get_by_username(username)

    if not user or not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def require_role(user, min_role: str):
    if not user:
        raise PermissionError("Authentication required")

    if not getattr(user, "is_active", False):
        raise PermissionError("User is inactive")

    if ROLE_RANK.get(getattr(user, "role", ""), 0) < ROLE_RANK[min_role]:
        raise PermissionError(f"{min_role} role required")