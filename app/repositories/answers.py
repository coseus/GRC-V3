from __future__ import annotations

from app.db.models import Answer


class AnswerRepository:
    def __init__(self, session):
        self.session = session

    def list_for_assessment(self, assessment_id: int):
        return (
            self.session.query(Answer)
            .filter(Answer.assessment_id == assessment_id)
            .order_by(Answer.domain_name.asc().nullsfirst(), Answer.question_code.asc())
            .all()
        )

    def get_by_assessment_and_question_code(self, assessment_id: int, question_code: str):
        return (
            self.session.query(Answer)
            .filter(
                Answer.assessment_id == assessment_id,
                Answer.question_code == question_code,
            )
            .first()
        )

    def upsert(
        self,
        *,
        assessment_id: int,
        question_code: str,
        question_text: str | None,
        domain_code: str | None,
        domain_name: str | None,
        selected_value: str | None,
        score: float | None,
        max_score: float | None,
        weight: float,
        comment: str | None,
        evidence: str | None,
        answered_by: int | None,
        answered_at,
    ):
        obj = self.get_by_assessment_and_question_code(assessment_id, question_code)

        if not obj:
            obj = Answer(
                assessment_id=assessment_id,
                question_code=question_code,
            )
            self.session.add(obj)

        obj.question_text = question_text
        obj.domain_code = domain_code
        obj.domain_name = domain_name
        obj.selected_value = selected_value
        obj.score = score
        obj.max_score = max_score
        obj.weight = weight or 1.0
        obj.comment = comment
        obj.evidence = evidence
        obj.answered_by = answered_by
        obj.answered_at = answered_at
        obj.status = "answered" if selected_value not in (None, "") else "draft"

        self.session.flush()
        return obj