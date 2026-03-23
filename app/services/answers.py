from __future__ import annotations

from datetime import datetime

from app.audit.service import audit_log
from app.repositories.answers import AnswerRepository
from app.repositories.assessments import AssessmentRepository
from app.services.auth import require_role


SCORE_MAP = {
    "yes": 100.0,
    "partial": 50.0,
    "no": 0.0,
    "n/a": None,
    "na": None,
    "not_applicable": None,
    "fail": 0.0,
    "pass": 100.0,
}


class AnswerService:
    def __init__(self, session):
        self.session = session
        self.repo = AnswerRepository(session)
        self.assessment_repo = AssessmentRepository(session)

    def list_for_assessment(self, actor, assessment_id: int):
        require_role(actor, "viewer")
        return self.repo.list_for_assessment(assessment_id)

    def save_answer(
        self,
        actor,
        *,
        assessment_id: int,
        question_code: str | None = None,
        question_id: str | None = None,
        question_text: str | None = None,
        domain_code: str | None = None,
        domain_name: str | None = None,
        domain_id=None,
        domain=None,
        selected_value: str | None = None,
        answer_value: str | None = None,
        value: str | None = None,
        score: float | None = None,
        max_score: float | None = 100.0,
        weight: float = 1.0,
        comment: str | None = None,
        evidence: str | None = None,
        notes: str | None = None,
        proof: str | None = None,
        **kwargs,
    ):
        require_role(actor, "viewer")

        assessment = self.assessment_repo.get_by_id(assessment_id)
        if not assessment:
            raise ValueError("Assessment not found")

        if assessment.is_locked:
            raise ValueError("Assessment este blocata si nu mai poate fi modificata.")

        final_question_code = (question_code or question_id or "").strip()
        if not final_question_code:
            raise ValueError("question_code este obligatoriu.")

        final_selected_value = selected_value
        if final_selected_value is None:
            final_selected_value = answer_value
        if final_selected_value is None:
            final_selected_value = value

        final_comment = comment if comment is not None else notes
        final_evidence = evidence if evidence is not None else proof

        if domain_name is None and isinstance(domain, dict):
            domain_name = domain.get("name") or domain.get("title")
            domain_code = domain_code or domain.get("code") or domain.get("id")

        if domain_code is None and domain_id is not None:
            domain_code = str(domain_id)

        normalized = (final_selected_value or "").strip().lower()
        if score is None and normalized in SCORE_MAP:
            score = SCORE_MAP[normalized]

        obj = self.repo.upsert(
            assessment_id=assessment_id,
            question_code=final_question_code,
            question_text=question_text,
            domain_code=domain_code,
            domain_name=domain_name,
            selected_value=final_selected_value,
            score=score,
            max_score=max_score,
            weight=weight,
            comment=final_comment,
            evidence=final_evidence,
            answered_by=actor.id,
            answered_at=datetime.utcnow(),
        )

        if assessment.status == "draft":
            assessment.status = "in_progress"

        audit_log(
            self.session,
            actor.id,
            "save_answer",
            "answer",
            obj.id,
            {
                "assessment_id": assessment_id,
                "question_code": final_question_code,
                "selected_value": final_selected_value,
                "score": score,
            },
        )
        self.session.commit()
        return obj

    def get_responses_saved_dict(self, actor, assessment_id: int):
        require_role(actor, "viewer")

        rows = self.repo.list_for_assessment(assessment_id)
        result = {}
        for row in rows:
            result[row.question_code] = {
                "question_code": row.question_code,
                "question_id": row.question_code,
                "selected_value": row.selected_value,
                "answer_value": row.selected_value,
                "value": row.selected_value,
                "score": row.score,
                "comment": row.comment,
                "notes": row.comment,
                "evidence": row.evidence,
                "proof": row.evidence,
                "domain_code": row.domain_code,
                "domain_id": row.domain_code,
                "domain_name": row.domain_name,
                "domain": row.domain_name,
                "question_text": row.question_text,
                "question": row.question_text,
                "weight": row.weight,
                "max_score": row.max_score,
            }
        return result

    def get_saved_answers(self, actor, assessment_id: int):
        return self.get_responses_saved_dict(actor, assessment_id)