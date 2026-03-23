from __future__ import annotations

from app.db.models import User


class UserRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, user_id: int):
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str):
        return self.session.query(User).filter(User.username == username).first()

    def list_all(self):
        return self.session.query(User).order_by(User.username.asc()).all()

    def create(self, **kwargs):
        obj = User(**kwargs)
        self.session.add(obj)
        self.session.flush()
        return obj

    def delete(self, obj):
        self.session.delete(obj)