from __future__ import annotations

from app.db.models import Assessment


class AssessmentRepository:
    def __init__(self, session):
        self.session = session

    def list_for_company(self, company_id: int):
        return (
            self.session.query(Assessment)
            .filter(Assessment.company_id == company_id)
            .order_by(Assessment.created_at.desc(), Assessment.id.desc())
            .all()
        )

    def get_by_id(self, assessment_id: int):
        return self.session.query(Assessment).filter(Assessment.id == assessment_id).first()

    def get_by_company_and_name(self, company_id: int, name: str):
        return (
            self.session.query(Assessment)
            .filter(Assessment.company_id == company_id, Assessment.name == name)
            .first()
        )

    def create(self, **kwargs):
        obj = Assessment(**kwargs)
        self.session.add(obj)
        self.session.flush()
        return obj

    def delete(self, obj):
        self.session.delete(obj)