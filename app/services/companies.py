from __future__ import annotations

from app.audit.service import audit_log
from app.repositories.companies import CompanyRepository
from app.services.auth import require_role


class CompanyService:
    def __init__(self, session):
        self.session = session
        self.repo = CompanyRepository(session)

    def list_companies(self, actor):
        require_role(actor, "viewer")
        return self.repo.list_all()

    def create_company(self, actor, name: str, industry: str = "", country: str = "", size: str = ""):
        require_role(actor, "auditor")

        name = (name or "").strip()
        if not name:
            raise ValueError("Company name este obligatoriu.")

        if self.repo.get_by_name(name):
            raise ValueError("Compania exista deja.")

        obj = self.repo.create(
            name=name,
            industry=(industry or "").strip() or None,
            country=(country or "").strip() or None,
            size=(size or "").strip() or None,
            is_active=True,
        )
        audit_log(self.session, actor.id, "create", "company", obj.id, {"name": name})
        self.session.commit()
        return obj