from __future__ import annotations

from app.audit.service import audit_log
from app.repositories.recommendations import RecommendationRepository
from app.services.auth import require_role
from app.services.crosswalk_service import CrosswalkService
from app.services.risk_engine import (
    get_domain_name,
    get_question_name,
    get_risk_label,
    get_score,
    normalize_responses,
    score_to_maturity,
)


class RecommendationService:
    def __init__(self, session):
        self.session = session
        self.repo = RecommendationRepository(session)
        self.crosswalk = CrosswalkService()

    def list_for_assessment(self, actor, assessment_id: int):
        require_role(actor, "viewer")
        return self.repo.list_for_assessment(assessment_id)

    def create_manual(
        self,
        actor,
        *,
        assessment_id: int,
        title: str,
        description: str | None = None,
        priority: str = "medium",
        domain_code: str | None = None,
        domain_name: str | None = None,
        question_code: str | None = None,
        score: float | None = None,
    ):
        require_role(actor, "auditor")

        title = (title or "").strip()
        if not title:
            raise ValueError("Titlul recomandarii este obligatoriu.")

        priority = (priority or "medium").strip().lower()
        if priority not in {"high", "medium", "low"}:
            raise ValueError("Prioritate invalida.")

        obj = self.repo.create(
            assessment_id=assessment_id,
            domain_code=domain_code,
            domain_name=domain_name,
            question_code=question_code,
            title=title,
            description=(description or "").strip() or None,
            priority=priority,
            status="open",
            source="manual",
            score=score,
            updated_by=getattr(actor, "id", None),
        )

        audit_log(
            self.session,
            getattr(actor, "id", None),
            "create",
            "recommendation",
            obj.id,
            {
                "assessment_id": assessment_id,
                "title": title,
                "priority": priority,
            },
        )
        self.session.commit()
        return obj

    def regenerate_from_responses(self, actor, assessment_id: int, responses, framework_code: str | None = None):
        require_role(actor, "auditor")

        self.repo.delete_for_assessment(assessment_id)

        rows = normalize_responses(responses)
        created = []

        if not rows:
            obj = self.repo.create(
                assessment_id=assessment_id,
                domain_code=None,
                domain_name="General",
                question_code=None,
                title="Complete the assessment",
                description="There are not enough answers recorded to generate targeted recommendations.",
                priority="medium",
                status="open",
                source="auto",
                score=None,
                updated_by=getattr(actor, "id", None),
            )
            created.append(obj)
        else:
            for row in rows:
                score = get_score(row)
                if score is None:
                    continue

                maturity = score_to_maturity(score)
                if score >= 70 and maturity >= 3:
                    continue

                risk = get_risk_label(row)
                domain = get_domain_name(row)
                question = get_question_name(row)
                qcode = row.get("question_code") or row.get("question_id")

                family = self.crosswalk.suggest_family_from_question(question, domain)
                mapping = self.crosswalk.get_for_family(family)

                if risk == "Critical" or score < 40:
                    priority = "high"
                elif risk == "High" or score < 60:
                    priority = "medium"
                else:
                    priority = "low"

                base_desc = (
                    f"Control weakness identified in '{domain}'. Current score is {score:.1f}, "
                    f"maturity is '{maturity}'. Strengthen control design, implementation evidence, "
                    f"and periodic review."
                )

                if mapping:
                    crosswalk_note = (
                        f" Related crosswalk: ISO 27001 [{', '.join(mapping.get('iso27001', []))}], "
                        f"NIST CSF [{', '.join(mapping.get('nist_csf', []))}], "
                        f"NIS2 [{', '.join(mapping.get('nis2', []))}]."
                    )
                else:
                    crosswalk_note = ""

                if framework_code and framework_code.lower().startswith("tprm"):
                    title = f"Strengthen vendor control: {question[:80]}"
                    description = (
                        base_desc
                        + " Review onboarding due diligence, contract clauses, monitoring cadence, and vendor remediation tracking."
                        + crosswalk_note
                    )
                else:
                    title = f"Improve control: {question[:80]}"
                    description = base_desc + crosswalk_note

                obj = self.repo.create(
                    assessment_id=assessment_id,
                    domain_code=row.get("domain_code") or row.get("domain_id"),
                    domain_name=domain,
                    question_code=qcode,
                    title=title,
                    description=description,
                    priority=priority,
                    status="open",
                    source="auto",
                    score=score,
                    updated_by=getattr(actor, "id", None),
                )
                created.append(obj)

            if not created:
                obj = self.repo.create(
                    assessment_id=assessment_id,
                    domain_code=None,
                    domain_name="General",
                    question_code=None,
                    title="Maintain current control posture",
                    description="Current scores are relatively strong. Focus on testing quality, evidence refresh, and continuous improvement.",
                    priority="low",
                    status="open",
                    source="auto",
                    score=None,
                    updated_by=getattr(actor, "id", None),
                )
                created.append(obj)

        audit_log(
            self.session,
            getattr(actor, "id", None),
            "regenerate",
            "recommendation",
            None,
            {
                "assessment_id": assessment_id,
                "count": len(created),
                "framework_code": framework_code,
            },
        )
        self.session.commit()
        return created
