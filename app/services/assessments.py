from __future__ import annotations

import json
from datetime import datetime

from app.audit.service import audit_log
from app.frameworks.loader import load_framework_data
from app.repositories.assessments import AssessmentRepository
from app.services.auth import require_role


VALID_STATUSES = {"draft", "in_progress", "reviewed", "approved", "archived"}


class AssessmentService:
    def __init__(self, session):
        self.session = session
        self.repo = AssessmentRepository(session)

    def list_for_company(self, actor, company_id: int):
        require_role(actor, "viewer")
        return self.repo.list_for_company(company_id)

    def get_by_id(self, actor, assessment_id: int):
        require_role(actor, "viewer")
        return self.repo.get_by_id(assessment_id)

    def create_assessment(
        self,
        actor,
        *,
        company_id: int,
        name: str,
        framework_code: str,
        framework_name: str,
        framework_version: str = "1.0",
    ):
        require_role(actor, "auditor")

        name = (name or "").strip()
        framework_code = (framework_code or "").strip()
        framework_name = (framework_name or "").strip()

        if not name:
            raise ValueError("Assessment name este obligatoriu.")
        if not framework_code:
            raise ValueError("Framework code este obligatoriu.")
        if not framework_name:
            raise ValueError("Framework name este obligatoriu.")

        existing = self.repo.get_by_company_and_name(company_id, name)
        if existing:
            raise ValueError("Exista deja o evaluare cu acest nume pentru compania selectata.")

        framework_data = load_framework_data(framework_code)

        obj = self.repo.create(
            company_id=company_id,
            name=name,
            framework_code=framework_code,
            framework_name=framework_name,
            framework_version=framework_version,
            status="draft",
            is_locked=False,
            created_by=actor.id,
            framework_snapshot_json=json.dumps(framework_data, ensure_ascii=False),
        )
        audit_log(
            self.session,
            actor.id,
            "create",
            "assessment",
            obj.id,
            {
                "name": name,
                "framework_code": framework_code,
                "framework_name": framework_name,
            },
        )
        self.session.commit()
        return obj

    def update_status(self, actor, assessment_id: int, status: str):
        require_role(actor, "auditor")

        if status not in VALID_STATUSES:
            raise ValueError("Status invalid.")

        obj = self.repo.get_by_id(assessment_id)
        if not obj:
            raise ValueError("Assessment not found")

        if obj.is_locked and status != obj.status:
            raise ValueError("Assessment este blocata si nu mai poate fi modificata.")

        obj.status = status
        if status == "approved":
            obj.is_locked = True
            obj.completed_at = datetime.utcnow()

        audit_log(
            self.session,
            actor.id,
            "update_status",
            "assessment",
            obj.id,
            {"status": status},
        )
        self.session.commit()
        return obj