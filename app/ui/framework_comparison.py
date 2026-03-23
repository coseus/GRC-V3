from __future__ import annotations

import streamlit as st

from app.db.session import get_session
from app.services.answers import AnswerService
from app.services.assessments import AssessmentService
from app.services.risk_engine import (
    apply_risk_penalty,
    calculate_overall_weighted_score,
    calculate_risk_score,
    get_maturity_level,
)


def _build_assessment_metrics(answer_service, actor, assessment_id: int):
    try:
        answers = answer_service.list_for_assessment(actor, assessment_id)
    except Exception:
        return {
            "answers_count": 0,
            "overall_score": None,
            "adjusted_score": None,
            "maturity": "",
            "risk_score": None,
        }

    responses = []
    for a in answers or []:
        responses.append(
            {
                "domain_name": getattr(a, "domain_name", "") or "",
                "question_text": getattr(a, "question_text", "") or "",
                "score": getattr(a, "score", None),
                "weight": getattr(a, "weight", 1) if hasattr(a, "weight") else 1,
                "risk": getattr(a, "risk", "Medium") if hasattr(a, "risk") else "Medium",
                "notes": getattr(a, "notes", None) or getattr(a, "comment", "") or "",
            }
        )

    if not responses:
        return {
            "answers_count": 0,
            "overall_score": None,
            "adjusted_score": None,
            "maturity": "",
            "risk_score": None,
        }

    overall = calculate_overall_weighted_score(responses)
    adjusted = apply_risk_penalty(responses, overall)
    risk_score = calculate_risk_score(responses)
    maturity = get_maturity_level(adjusted)

    return {
        "answers_count": len(responses),
        "overall_score": overall,
        "adjusted_score": adjusted,
        "maturity": maturity,
        "risk_score": risk_score,
    }


def render_framework_comparison_section(actor, company, lang):
    if not actor:
        st.error("Utilizator neautentificat.")
        return

    session = get_session()
    assessment_service = AssessmentService(session)
    answer_service = AnswerService(session)

    try:
        assessments = assessment_service.list_for_company(actor, company.id)

        st.subheader("Framework Comparison")

        if not assessments:
            st.info("Nu exista evaluari pentru aceasta companie.")
            return

        framework_options = sorted(
            {getattr(item, "framework_name", "") or "" for item in assessments if getattr(item, "framework_name", None)}
        )
        selected_framework = st.selectbox(
            "Filtru framework",
            options=["Toate"] + framework_options,
            index=0,
            key=f"framework_compare_filter_{company.id}",
        )

        only_unlocked = st.checkbox(
            "Arata doar evaluari nelocate",
            value=False,
            key=f"framework_compare_unlocked_{company.id}",
        )

        sort_by = st.selectbox(
            "Sortare dupa",
            options=["Updated", "Adjusted Score", "Overall Score", "Risk Score", "Name"],
            index=0,
            key=f"framework_compare_sort_{company.id}",
        )

        reverse_sort = st.checkbox(
            "Sortare descrescatoare",
            value=True,
            key=f"framework_compare_reverse_{company.id}",
        )

        filtered = []
        for item in assessments:
            if selected_framework != "Toate" and (getattr(item, "framework_name", "") or "") != selected_framework:
                continue
            if only_unlocked and bool(getattr(item, "is_locked", False)):
                continue
            filtered.append(item)

        if not filtered:
            st.info("Nu exista evaluari care corespund filtrelor selectate.")
            return

        rows = []
        for item in filtered:
            metrics = _build_assessment_metrics(answer_service, actor, item.id)

            rows.append(
                {
                    "ID": item.id,
                    "Name": item.name,
                    "Framework": item.framework_name,
                    "Code": item.framework_code,
                    "Version": getattr(item, "framework_version", "") or "",
                    "Status": getattr(item, "status", "") or "",
                    "Locked": "Yes" if getattr(item, "is_locked", False) else "No",
                    "Answers": metrics["answers_count"],
                    "Overall Score": metrics["overall_score"],
                    "Adjusted Score": metrics["adjusted_score"],
                    "Maturity": metrics["maturity"],
                    "Risk Score": metrics["risk_score"],
                    "Updated": item.updated_at.strftime("%Y-%m-%d %H:%M") if getattr(item, "updated_at", None) else "",
                    "_updated_raw": getattr(item, "updated_at", None),
                }
            )

        if sort_by == "Updated":
            rows.sort(key=lambda x: x["_updated_raw"] or 0, reverse=reverse_sort)
        elif sort_by == "Adjusted Score":
            rows.sort(key=lambda x: x["Adjusted Score"] if x["Adjusted Score"] is not None else -1, reverse=reverse_sort)
        elif sort_by == "Overall Score":
            rows.sort(key=lambda x: x["Overall Score"] if x["Overall Score"] is not None else -1, reverse=reverse_sort)
        elif sort_by == "Risk Score":
            rows.sort(key=lambda x: x["Risk Score"] if x["Risk Score"] is not None else -1, reverse=reverse_sort)
        elif sort_by == "Name":
            rows.sort(key=lambda x: x["Name"] or "", reverse=reverse_sort)

        clean_rows = []
        for row in rows:
            clean_rows.append(
                {
                    "ID": row["ID"],
                    "Name": row["Name"],
                    "Framework": row["Framework"],
                    "Code": row["Code"],
                    "Version": row["Version"],
                    "Status": row["Status"],
                    "Locked": row["Locked"],
                    "Answers": row["Answers"],
                    "Overall Score": "" if row["Overall Score"] is None else f"{row['Overall Score']:.1f}",
                    "Adjusted Score": "" if row["Adjusted Score"] is None else f"{row['Adjusted Score']:.1f}",
                    "Maturity": row["Maturity"],
                    "Risk Score": "" if row["Risk Score"] is None else f"{row['Risk Score']:.1f}",
                    "Updated": row["Updated"],
                }
            )

        st.dataframe(clean_rows, use_container_width=True)

        scored_rows = [r for r in rows if r["Adjusted Score"] is not None]
        if scored_rows:
            st.write("### Rezumat comparativ")

            best = max(scored_rows, key=lambda x: x["Adjusted Score"])
            weakest = min(scored_rows, key=lambda x: x["Adjusted Score"])
            highest_risk = max(scored_rows, key=lambda x: x["Risk Score"] if x["Risk Score"] is not None else -1)

            c1, c2, c3 = st.columns(3)
            c1.metric("Cel mai bun scor", f"{best['Adjusted Score']:.1f}", best["Name"])
            c2.metric("Cel mai slab scor", f"{weakest['Adjusted Score']:.1f}", weakest["Name"])
            c3.metric("Cel mai mare risc", f"{highest_risk['Risk Score']:.1f}", highest_risk["Name"])

            st.write("### Comparatie rapida")
            summary_rows = []
            for row in scored_rows:
                summary_rows.append(
                    {
                        "Assessment": row["Name"],
                        "Framework": row["Framework"],
                        "Adjusted Score": row["Adjusted Score"],
                        "Maturity": row["Maturity"],
                        "Risk Score": row["Risk Score"],
                    }
                )
            st.dataframe(summary_rows, use_container_width=True)

    except Exception as exc:
        st.error(str(exc))
    finally:
        session.close()