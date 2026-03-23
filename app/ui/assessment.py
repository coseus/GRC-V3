from __future__ import annotations

import streamlit as st

from app.db.session import get_session
from app.services.answers import AnswerService


SCORE_OPTIONS = ["Fail", "Partial", "Pass", "NotApplicable"]

SCORE_MAP = {
    "Fail": 0,
    "Partial": 50,
    "Pass": 100,
    "NotApplicable": None,
}

DB_TO_UI_SCORE = {
    "fail": "Fail",
    "partial": "Partial",
    "pass": "Pass",
    "notapplicable": "NotApplicable",
    "not_applicable": "NotApplicable",
    "n/a": "NotApplicable",
    "na": "NotApplicable",
    "yes": "Pass",
    "no": "Fail",
}


def localize(text_obj, lang):
    if isinstance(text_obj, dict):
        return text_obj.get(lang) or text_obj.get("en") or ""
    return str(text_obj)


def _qid(value):
    if value is None:
        return ""
    return str(value).strip()


def _normalize_saved_answers(answer_rows):
    result = {}

    for a in answer_rows:
        key = _qid(getattr(a, "question_id", None) or getattr(a, "question_code", None))
        if not key:
            continue

        raw_value = getattr(a, "answer_value", None) or getattr(a, "selected_value", None) or ""
        raw_value_normalized = str(raw_value).strip().lower()

        ui_value = DB_TO_UI_SCORE.get(raw_value_normalized, raw_value if raw_value in SCORE_OPTIONS else "Fail")

        result[key] = {
            "question_id": key,
            "domain_id": _qid(getattr(a, "domain_id", None) or getattr(a, "domain_code", None)),
            "domain_name": getattr(a, "domain_name", None),
            "question_text": getattr(a, "question_text", None),
            "answer_value": getattr(a, "answer_value", None) or getattr(a, "selected_value", None),
            "ui_score_label": ui_value,
            "score": getattr(a, "score", None),
            "notes": getattr(a, "notes", None) or getattr(a, "comment", None) or "",
            "proof": getattr(a, "proof", None) or getattr(a, "evidence", None) or "",
        }

    return result


def _question_status_badge(saved_item):
    if not saved_item:
        return "? Nesalvat"

    value = (saved_item.get("ui_score_label") or "").strip()

    if value == "Pass":
        return "?? Pass"
    if value == "Partial":
        return "?? Partial"
    if value == "Fail":
        return "?? Fail"
    if value == "NotApplicable":
        return "? NotApplicable"

    return "? Nesalvat"


def _domain_progress(questions, saved_answers):
    total = len(questions)
    answered = 0

    for q in questions:
        qid = _qid(q.get("id"))
        if qid in saved_answers:
            answered += 1

    return answered, total


def _save_single_answer(answer_service, user, assessment, domain, q, lang, score_label, notes, proof):
    q_id = _qid(q.get("id"))
    q_text = localize(q.get("text", ""), lang)

    answer_service.save_answer(
        user,
        assessment_id=assessment.id,
        domain_id=domain.get("id"),
        domain_name=localize(domain.get("name", ""), lang),
        question_id=q_id,
        question_text=q_text,
        answer_value=score_label,
        score=SCORE_MAP.get(score_label),
        notes=notes,
        proof=proof,
        weight=q.get("weight", 1),
    )


def render_assessment_section(data, lang, user, company, assessment, selected_applies, selected_scope):
    session = get_session()
    answer_service = AnswerService(session)

    try:
        st.header("Assessment")

        domains = data.get("domains", [])
        if not domains:
            st.info("Framework-ul selectat nu contine domenii.")
            return {"responses_saved": [], "filtered_domains": []}

        all_answers = answer_service.list_for_assessment(user, assessment.id)
        saved_answers = _normalize_saved_answers(all_answers)

        domain_names = [localize(d.get("name", ""), lang) for d in domains]
        selected_domain_name = st.selectbox(
            "Domain",
            domain_names,
            key=f"domain_select_{assessment.id}",
        )

        domain = next(
            d for d in domains
            if localize(d.get("name", ""), lang) == selected_domain_name
        )

        questions = domain.get("questions", [])
        if not questions:
            st.info("Domeniul selectat nu contine intrebari.")
            return {"responses_saved": [], "filtered_domains": domains}

        answered, total = _domain_progress(questions, saved_answers)
        st.caption(f"Progres domeniu: {answered}/{total} intrebari salvate")

        show_only_unsaved = st.checkbox(
            "Arata doar intrebarile nesalvate",
            value=False,
            key=f"only_unsaved_{assessment.id}_{domain.get('id')}",
        )

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button(
                "Save All pe domeniu",
                key=f"save_all_{assessment.id}_{domain.get('id')}",
                width="stretch",
            ):
                try:
                    visible_questions = []
                    for q in questions:
                        q_id = _qid(q.get("id"))
                        if show_only_unsaved and q_id in saved_answers:
                            continue
                        visible_questions.append(q)

                    for q in visible_questions:
                        q_id = _qid(q.get("id"))
                        score_key = f"score_{assessment.id}_{q_id}"
                        notes_key = f"notes_{assessment.id}_{q_id}"
                        proof_key = f"proof_{assessment.id}_{q_id}"

                        score_label = st.session_state.get(score_key, "Fail")
                        notes = st.session_state.get(notes_key, "")
                        proof = st.session_state.get(proof_key, "")

                        _save_single_answer(
                            answer_service,
                            user,
                            assessment,
                            domain,
                            q,
                            lang,
                            score_label,
                            notes,
                            proof,
                        )

                    st.success("Intrebarile vizibile din domeniu au fost salvate.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        with col_b:
            if st.button(
                "Seteaza NotApplicable pe tot domeniul",
                key=f"na_domain_{assessment.id}_{domain.get('id')}",
                width="stretch",
            ):
                try:
                    visible_questions = []
                    for q in questions:
                        q_id = _qid(q.get("id"))
                        if show_only_unsaved and q_id in saved_answers:
                            continue
                        visible_questions.append(q)

                    for q in visible_questions:
                        q_id = _qid(q.get("id"))
                        st.session_state[f"score_{assessment.id}_{q_id}"] = "NotApplicable"
                        st.session_state[f"notes_{assessment.id}_{q_id}"] = "Set automat pe tot domeniul."
                        st.session_state[f"proof_{assessment.id}_{q_id}"] = ""

                        _save_single_answer(
                            answer_service,
                            user,
                            assessment,
                            domain,
                            q,
                            lang,
                            "NotApplicable",
                            "Set automat pe tot domeniul.",
                            "",
                        )

                    st.success("Intrebarile vizibile au fost setate pe NotApplicable.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        st.write("---")

        visible_questions = []
        for q in questions:
            q_id = _qid(q.get("id"))
            is_saved = q_id in saved_answers

            if show_only_unsaved and is_saved:
                continue

            visible_questions.append(q)

        if not visible_questions:
            st.info("Nu exista intrebari nesalvate in acest domeniu.")
        else:
            for idx, q in enumerate(visible_questions, start=1):
                q_id = _qid(q.get("id"))
                q_text = localize(q.get("text", ""), lang)
                saved_item = saved_answers.get(q_id)

                default_score = "Fail"
                default_notes = ""
                default_proof = ""

                if saved_item:
                    default_score = saved_item.get("ui_score_label") or "Fail"
                    default_notes = saved_item.get("notes") or ""
                    default_proof = saved_item.get("proof") or ""

                if f"score_{assessment.id}_{q_id}" not in st.session_state:
                    st.session_state[f"score_{assessment.id}_{q_id}"] = default_score
                if f"notes_{assessment.id}_{q_id}" not in st.session_state:
                    st.session_state[f"notes_{assessment.id}_{q_id}"] = default_notes
                if f"proof_{assessment.id}_{q_id}" not in st.session_state:
                    st.session_state[f"proof_{assessment.id}_{q_id}"] = default_proof

                with st.container():
                    st.markdown(f"### {idx}. {q_text}")
                    st.caption(f"ID: {q_id} | Status: {_question_status_badge(saved_item)}")

                    if q.get("risk"):
                        st.caption(f"Risk: {q.get('risk')}")
                    if q.get("weight") is not None:
                        st.caption(f"Weight: {q.get('weight', 1)}")

                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.selectbox(
                            "Score",
                            SCORE_OPTIONS,
                            key=f"score_{assessment.id}_{q_id}",
                        )

                    with col2:
                        current_score = st.session_state.get(f"score_{assessment.id}_{q_id}", "Fail")
                        if current_score == "Pass":
                            st.success("Control implementat")
                        elif current_score == "Partial":
                            st.warning("Control partial implementat")
                        elif current_score == "Fail":
                            st.error("Control neimplementat")
                        else:
                            st.info("Not applicable")

                    st.text_area(
                        "Notes",
                        key=f"notes_{assessment.id}_{q_id}",
                        height=100,
                    )

                    st.text_input(
                        "Proof / Evidence",
                        key=f"proof_{assessment.id}_{q_id}",
                    )

                    if st.button(f"Salveaza {q_id}", key=f"save_{assessment.id}_{q_id}"):
                        try:
                            score_label = st.session_state.get(f"score_{assessment.id}_{q_id}", "Fail")
                            notes = st.session_state.get(f"notes_{assessment.id}_{q_id}", "")
                            proof = st.session_state.get(f"proof_{assessment.id}_{q_id}", "")

                            _save_single_answer(
                                answer_service,
                                user,
                                assessment,
                                domain,
                                q,
                                lang,
                                score_label,
                                notes,
                                proof,
                            )
                            st.success("Salvat")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))

                    st.write("---")

        refreshed_answers = answer_service.list_for_assessment(user, assessment.id)
        qmeta = {
            _qid(q.get("id")): q
            for d in domains
            for q in d.get("questions", [])
        }

        responses_saved = []
        for a in refreshed_answers:
            qid = _qid(a.question_id)
            q = qmeta.get(qid)
            if not q:
                continue

            responses_saved.append(
                {
                    "domain_id": _qid(a.domain_id),
                    "domain": a.domain_name,
                    "domain_name": a.domain_name,
                    "domain_code": _qid(a.domain_id),
                    "question_id": qid,
                    "question_code": qid,
                    "question": a.question_text,
                    "question_text": a.question_text,
                    "answer_value": a.answer_value,
                    "selected_value": a.answer_value,
                    "score": a.score,
                    "weight": q.get("weight", 1),
                    "risk": q.get("risk", "Medium"),
                    "notes": a.notes or "",
                    "comment": a.notes or "",
                    "proof": a.proof or "",
                    "evidence": a.proof or "",
                }
            )

        st.write("## Toate raspunsurile din evaluare")
        if responses_saved:
            table_rows = []
            for row in responses_saved:
                table_rows.append(
                    {
                        "Domain": row.get("domain_name") or row.get("domain"),
                        "Question ID": row.get("question_id"),
                        "Question": row.get("question_text") or row.get("question"),
                        "Answer": row.get("answer_value"),
                        "Score": row.get("score"),
                        "Weight": row.get("weight"),
                        "Risk": row.get("risk"),
                        "Notes": row.get("notes"),
                        "Proof": row.get("proof"),
                    }
                )
            st.dataframe(table_rows, width="stretch")
        else:
            st.info("Nu exista raspunsuri salvate in aceasta evaluare.")

        return {
            "responses_saved": responses_saved,
            "filtered_domains": domains,
        }

    finally:
        session.close()