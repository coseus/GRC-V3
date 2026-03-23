from __future__ import annotations

from app.db.models import Company


class CompanyRepository:
    def __init__(self, session):
        self.session = session

    def list_all(self):
        return self.session.query(Company).filter(Company.is_active.is_(True)).order_by(Company.name.asc()).all()

    def get_by_id(self, company_id: int):
        return self.session.query(Company).filter(Company.id == company_id).first()

    def get_by_name(self, name: str):
        return self.session.query(Company).filter(Company.name == name).first()

    def create(self, **kwargs):
        obj = Company(**kwargs)
        self.session.add(obj)
        self.session.flush()
        return obj