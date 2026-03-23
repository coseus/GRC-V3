from __future__ import annotations

import streamlit as st

from app.db.session import get_session
from app.services.executive import ExecutiveService
from app.services.risk_engine import (
    apply_risk_penalty,
    calculate_overall_weighted_score,
    calculate_risk_score,
    calculate_weighted_domain_scores,
    get_maturity_level,
    get_top_gaps,
    normalize_responses,
)


def _build_ai_summary(company, assessment, state):
    responses = normalize_responses((state or {}).get("responses_saved", []))
    domain_scores = calculate_weighted_domain_scores(responses)
    overall = calculate_overall_weighted_score(responses)
    adjusted = apply_risk_penalty(responses, overall)
    risk_score = calculate_risk_score(responses)
    maturity = get_maturity_level(adjusted)
    top_gaps = get_top_gaps(responses, limit=5)

    total_answers = len(responses)
    pass_count = sum(1 for r in responses if (r.get("score") or 0) >= 70)
    partial_count = sum(1 for r in responses if r.get("score") is not None and 0 < (r.get("score") or 0) < 70)
    fail_count = sum(1 for r in responses if (r.get("score") or 0) == 0)

    strongest_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    weakest_domains = sorted(domain_scores.items(), key=lambda x: x[1])[:3]

    summary_text = (
        f"Assessment '{assessment.name}' for company '{company.name}' contains {total_answers} evaluated controls. "
        f"The weighted overall score is {overall:.1f}/100, the adjusted score is {adjusted:.1f}/100, "
        f"the current maturity is '{maturity}', and the calculated risk score is {risk_score:.1f}. "
        f"The assessment indicates {pass_count} stronger controls, {partial_count} partially effective controls, "
        f"and {fail_count} controls with material gaps."
    )

    strengths_lines = []
    if strongest_domains:
        strengths_lines.append("Strong areas identified:")
        for domain, score in strongest_domains:
            strengths_lines.append(f"- {domain}: {score:.1f}/100")
    else:
        strengths_lines.append("- No significant strengths identified yet.")

    gaps_lines = []
    if weakest_domains:
        gaps_lines.append("Priority gaps identified:")
        for domain, score in weakest_domains:
            gaps_lines.append(f"- {domain}: {score:.1f}/100")
    else:
        gaps_lines.append("- No material gaps identified yet.")

    recommendations_lines = []
    if top_gaps:
        recommendations_lines.append("Recommended management actions:")
        for item in top_gaps:
            recommendations_lines.append(
                f"- Improve '{item['question']}' in domain '{item['domain']}' "
                f"(score {item['score']:.1f}, risk {item['risk']})."
            )
    else:
        recommendations_lines.append("- Maintain current posture and continue periodic control review.")

    return {
        "summary_text": summary_text,
        "strengths_text": "\n".join(strengths_lines),
        "gaps_text": "\n".join(gaps_lines),
        "recommendations_text": "\n".join(recommendations_lines),
    }


def render_executive_section(data, lang, actor, company, assessment, state):
    if not actor:
        st.error("Authentication required")
        return

    st.header("Executive Summary")

    session = get_session()
    service = ExecutiveService(session)

    try:
        existing = service.get(actor, assessment.id)

        if f"ai_exec_payload_{assessment.id}" not in st.session_state:
            st.session_state[f"ai_exec_payload_{assessment.id}"] = None

        current_summary = existing.summary_text if existing and existing.summary_text else ""
        current_strengths = existing.strengths_text if existing and existing.strengths_text else ""
        current_gaps = existing.gaps_text if existing and existing.gaps_text else ""
        current_recommendations = (
            existing.recommendations_text if existing and existing.recommendations_text else ""
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Generate AI Executive Summary", key=f"btn_exec_ai_{assessment.id}"):
                try:
                    ai_payload = _build_ai_summary(company, assessment, state)
                    st.session_state[f"ai_exec_payload_{assessment.id}"] = ai_payload
                    st.success("AI executive summary generated.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        with col2:
            if st.button("Aplica textul AI", key=f"btn_exec_apply_ai_{assessment.id}"):
                ai_payload = st.session_state.get(f"ai_exec_payload_{assessment.id}")
                if not ai_payload:
                    st.warning("Genereaza intai textul AI.")
                else:
                    st.session_state[f"exec_summary_{assessment.id}"] = ai_payload.get("summary_text", "")
                    st.session_state[f"exec_strengths_{assessment.id}"] = ai_payload.get("strengths_text", "")
                    st.session_state[f"exec_gaps_{assessment.id}"] = ai_payload.get("gaps_text", "")
                    st.session_state[f"exec_recommendations_{assessment.id}"] = ai_payload.get(
                        "recommendations_text", ""
                    )
                    st.success("Textul AI a fost aplicat in editor.")
                    st.rerun()

        ai_payload = st.session_state.get(f"ai_exec_payload_{assessment.id}")
        if ai_payload:
            st.write("### AI Preview")
            st.text_area(
                "AI Summary Preview",
                value=ai_payload.get("summary_text", ""),
                height=120,
                disabled=True,
                key=f"ai_preview_summary_{assessment.id}",
            )
            st.text_area(
                "AI Recommendations Preview",
                value=ai_payload.get("recommendations_text", ""),
                height=120,
                disabled=True,
                key=f"ai_preview_recs_{assessment.id}",
            )

        summary_text = st.text_area(
            "Summary",
            value=st.session_state.get(f"exec_summary_{assessment.id}", current_summary),
            height=180,
            key=f"exec_summary_{assessment.id}",
        )

        strengths_text = st.text_area(
            "Strengths",
            value=st.session_state.get(f"exec_strengths_{assessment.id}", current_strengths),
            height=140,
            key=f"exec_strengths_{assessment.id}",
        )

        gaps_text = st.text_area(
            "Gaps",
            value=st.session_state.get(f"exec_gaps_{assessment.id}", current_gaps),
            height=140,
            key=f"exec_gaps_{assessment.id}",
        )

        recommendations_text = st.text_area(
            "Recommendations",
            value=st.session_state.get(
                f"exec_recommendations_{assessment.id}",
                current_recommendations,
            ),
            height=180,
            key=f"exec_recommendations_{assessment.id}",
        )

        if st.button("Save executive summary", key=f"btn_exec_save_{assessment.id}"):
            try:
                service.save(
                    actor,
                    assessment.id,
                    summary_text=summary_text,
                    strengths_text=strengths_text,
                    gaps_text=gaps_text,
                    recommendations_text=recommendations_text,
                )
                st.success("Executive summary saved.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    except Exception as exc:
        st.error(str(exc))
    finally:
        session.close()