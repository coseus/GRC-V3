from __future__ import annotations

from app.audit.service import audit_log
from app.config import settings
from app.repositories.users import UserRepository
from app.security import hash_password, validate_password_strength
from app.services.auth import require_role


class UserService:
    def __init__(self, session):
        self.session = session
        self.repo = UserRepository(session)

    def list_users(self, actor):
        require_role(actor, "admin")
        return self.repo.list_all()

    def create_user(self, actor, username: str, password: str, role: str):
        require_role(actor, "admin")

        username = (username or "").strip()
        password = password or ""
        role = (role or "").strip()

        if not username:
            raise ValueError("Username este obligatoriu.")

        if role not in {"admin", "auditor", "viewer"}:
            raise ValueError("Rol invalid.")

        validate_password_strength(password)

        if self.repo.get_by_username(username):
            raise ValueError("Username already exists")

        obj = self.repo.create(
            username=username,
            password_hash=hash_password(password),
            role=role,
            is_active=True,
        )
        audit_log(
            self.session,
            actor.id,
            "create",
            "user",
            obj.id,
            {"username": username, "role": role},
        )
        self.session.commit()
        return obj

    def update_user(self, actor, user_id: int, username: str, role: str, is_active: bool):
        require_role(actor, "admin")

        username = (username or "").strip()
        role = (role or "").strip()

        if not username:
            raise ValueError("Username este obligatoriu.")

        if role not in {"admin", "auditor", "viewer"}:
            raise ValueError("Rol invalid.")

        obj = self.repo.get_by_id(user_id)
        if not obj:
            raise ValueError("User not found")

        existing = self.repo.get_by_username(username)
        if existing and existing.id != user_id:
            raise ValueError("Username already exists")

        obj.username = username
        obj.role = role
        obj.is_active = bool(is_active)

        audit_log(
            self.session,
            actor.id,
            "update",
            "user",
            obj.id,
            {"username": username, "role": role, "is_active": is_active},
        )
        self.session.commit()
        return obj

    def change_password(self, actor, user_id: int, new_password: str):
        require_role(actor, "admin")

        validate_password_strength(new_password)

        obj = self.repo.get_by_id(user_id)
        if not obj:
            raise ValueError("User not found")

        obj.password_hash = hash_password(new_password)
        audit_log(self.session, actor.id, "change_password", "user", obj.id, {})
        self.session.commit()
        return obj

    def delete_user(self, actor, user_id: int):
        require_role(actor, "admin")

        obj = self.repo.get_by_id(user_id)
        if not obj:
            raise ValueError("User not found")

        if obj.id == actor.id:
            raise ValueError("Nu iti poti sterge propriul cont.")

        protected_admin = settings.default_admin_username or "admin"
        if obj.username == protected_admin:
            raise ValueError("Default admin cannot be deleted")

        audit_log(
            self.session,
            actor.id,
            "delete",
            "user",
            obj.id,
            {"username": obj.username},
        )
        self.repo.delete(obj)
        self.session.commit()