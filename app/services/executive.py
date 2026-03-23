from __future__ import annotations

from app.audit.service import audit_log
from app.repositories.executive import ExecutiveRepository
from app.services.auth import require_role


class ExecutiveService:
    def __init__(self, session):
        self.session = session
        self.repo = ExecutiveRepository(session)

    def get_for_assessment(self, actor, assessment_id: int):
        require_role(actor, "viewer")
        return self.repo.get_by_assessment_id(assessment_id)

    def save_for_assessment(
        self,
        actor,
        *,
        assessment_id: int,
        summary_text: str | None = None,
        strengths_text: str | None = None,
        gaps_text: str | None = None,
        recommendations_text: str | None = None,
    ):
        require_role(actor, "auditor")

        obj = self.repo.upsert(
            assessment_id=assessment_id,
            summary_text=summary_text,
            strengths_text=strengths_text,
            gaps_text=gaps_text,
            recommendations_text=recommendations_text,
            updated_by=getattr(actor, "id", None),
        )

        audit_log(
            self.session,
            getattr(actor, "id", None),
            "save",
            "executive_summary",
            obj.id,
            {"assessment_id": assessment_id},
        )
        self.session.commit()
        return obj

    # Backward-compatible aliases
    def get(self, actor, assessment_id: int):
        return self.get_for_assessment(actor, assessment_id)

    def save(
        self,
        actor,
        assessment_id: int,
        summary_text: str | None = None,
        strengths_text: str | None = None,
        gaps_text: str | None = None,
        recommendations_text: str | None = None,
    ):
        return self.save_for_assessment(
            actor,
            assessment_id=assessment_id,
            summary_text=summary_text,
            strengths_text=strengths_text,
            gaps_text=gaps_text,
            recommendations_text=recommendations_text,
        )