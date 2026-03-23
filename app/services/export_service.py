from __future__ import annotations

from app.exports.excel_export import generate_excel_report
from app.exports.pdf_export import generate_pdf_report
from app.exports.word_export import generate_word_report
from app.services.auth import require_role
from app.services.risk_engine import get_top_gaps, normalize_responses


class ExportService:
    def __init__(self, session):
        self.session = session

    def _build_findings(self, responses, recommendations, include_findings: bool):
        if not include_findings:
            return []

        rows = normalize_responses(responses)
        top_gaps = get_top_gaps(rows, limit=100)

        findings = []
        for item in top_gaps:
            findings.append(
                {
                    "title": item["question"],
                    "domain": item["domain"],
                    "criticality": item["risk"],
                    "score": item["score"],
                    "maturity": item.get("maturity_label", ""),
                    "notes": item.get("notes", ""),
                    "source": "gap_analysis",
                }
            )

        for rec in recommendations or []:
            priority = str(getattr(rec, "priority", "") or "").strip().lower()
            criticality_map = {
                "high": "Critical",
                "medium": "High",
                "low": "Medium",
            }

            findings.append(
                {
                    "title": getattr(rec, "title", "") or "",
                    "domain": getattr(rec, "domain_name", "") or "",
                    "criticality": criticality_map.get(priority, "Medium"),
                    "score": getattr(rec, "score", None),
                    "maturity": "",
                    "notes": getattr(rec, "description", "") or "",
                    "source": "recommendation",
                }
            )

        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        findings.sort(key=lambda x: priority_order.get(x["criticality"], 99))
        return findings

    def export_pdf(
        self,
        actor,
        *,
        company,
        assessment,
        responses,
        domain_scores,
        executive_summary=None,
        recommendations=None,
        include_findings: bool = True,
        include_annex: bool = True,
        logo_path: str | None = None,
        auditor_name: str | None = None,
        report_version: str | None = None,
        report_date: str | None = None,
    ):
        require_role(actor, "viewer")

        findings = self._build_findings(
            responses=responses,
            recommendations=recommendations,
            include_findings=include_findings,
        )

        return generate_pdf_report(
            company_name=company.name,
            assessment_name=assessment.name,
            framework_name=assessment.framework_name,
            responses=responses or [],
            domain_scores=domain_scores or {},
            executive_summary=executive_summary,
            recommendations=recommendations or [],
            findings=findings,
            logo_path=logo_path,
            include_annex=include_annex,
            auditor_name=auditor_name,
            report_version=report_version,
            report_date=report_date,
        )

    def export_word(
        self,
        actor,
        *,
        company,
        assessment,
        responses,
        domain_scores,
        executive_summary=None,
        recommendations=None,
        include_findings: bool = True,
        include_annex: bool = True,
        logo_path: str | None = None,
        auditor_name: str | None = None,
        report_version: str | None = None,
        report_date: str | None = None,
    ):
        require_role(actor, "viewer")

        findings = self._build_findings(
            responses=responses,
            recommendations=recommendations,
            include_findings=include_findings,
        )

        return generate_word_report(
            company_name=company.name,
            assessment_name=assessment.name,
            framework_name=assessment.framework_name,
            responses=responses or [],
            domain_scores=domain_scores or {},
            executive_summary=executive_summary,
            recommendations=recommendations or [],
            findings=findings,
            logo_path=logo_path,
            include_annex=include_annex,
            auditor_name=auditor_name,
            report_version=report_version,
            report_date=report_date,
        )

    def export_excel(
        self,
        actor,
        *,
        company,
        assessment,
        responses,
        domain_scores,
        executive_summary=None,
        recommendations=None,
    ):
        require_role(actor, "viewer")

        return generate_excel_report(
            company_name=company.name,
            assessment_name=assessment.name,
            framework_name=assessment.framework_name,
            responses=responses or [],
            domain_scores=domain_scores or {},
            executive_summary=executive_summary,
            recommendations=recommendations or [],
        )