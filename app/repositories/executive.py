from __future__ import annotations

from app.db.models import ExecutiveSummary


class ExecutiveRepository:
    def __init__(self, session):
        self.session = session

    def get_by_assessment_id(self, assessment_id: int):
        return (
            self.session.query(ExecutiveSummary)
            .filter(ExecutiveSummary.assessment_id == assessment_id)
            .first()
        )

    def upsert(
        self,
        *,
        assessment_id: int,
        summary_text: str | None,
        strengths_text: str | None,
        gaps_text: str | None,
        recommendations_text: str | None,
        updated_by: int | None,
    ):
        obj = self.get_by_assessment_id(assessment_id)

        if not obj:
            obj = ExecutiveSummary(
                assessment_id=assessment_id,
            )
            self.session.add(obj)

        obj.summary_text = summary_text
        obj.strengths_text = strengths_text
        obj.gaps_text = gaps_text
        obj.recommendations_text = recommendations_text
        obj.updated_by = updated_by

        self.session.flush()
        return obj