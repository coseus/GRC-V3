from __future__ import annotations

from datetime import datetime

import streamlit as st

from app.charts.scoring import calculate_scores
from app.config import settings
from app.db.session import get_session
from app.services.backup_service import BackupService
from app.services.executive import ExecutiveService
from app.services.export_service import ExportService
from app.services.recommendations import RecommendationService


def render_import_export_section(data, lang, user, company, assessment, assessment_state):
    if not user:
        st.error("Authentication required")
        return

    st.header("Import / Export")

    session = get_session()
    executive_service = ExecutiveService(session)
    export_service = ExportService(session)
    recommendation_service = RecommendationService(session)
    backup_service = BackupService(session)

    try:
        responses = (assessment_state or {}).get("responses_saved", [])
        domain_scores = calculate_scores(responses)

        summary = executive_service.get(user, assessment.id)
        recommendations = recommendation_service.list_for_assessment(user, assessment.id)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Generate Recommendations from Assessment", key=f"gen_reco_{assessment.id}"):
                try:
                    recommendation_service.regenerate_from_responses(
                        user,
                        assessment.id,
                        responses,
                        framework_code=getattr(assessment, "framework_code", None),
                    )
                    st.success("Recommendations generated.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        with col2:
            st.caption(f"Recommendations: {len(recommendations)}")

        st.write("### Add Recommendation")

        domain_options = sorted(
            {str(r.get("domain_name") or r.get("domain") or "General") for r in responses if isinstance(r, dict)}
        )
        if not domain_options:
            domain_options = ["General"]

        with st.form(key=f"manual_recommendation_form_{assessment.id}"):
            selected_domain = st.selectbox(
                "Domain",
                options=domain_options,
                key=f"manual_reco_domain_{assessment.id}",
            )

            manual_recommendation = st.text_area(
                "Recommendation",
                key=f"manual_reco_text_{assessment.id}",
                height=120,
            )

            risk_value = st.selectbox(
                "Risk",
                options=["Low", "Medium", "High", "Critical"],
                index=0,
                key=f"manual_reco_risk_{assessment.id}",
            )

            responsible = st.text_input(
                "Responsible",
                key=f"manual_reco_responsible_{assessment.id}",
            )

            deadline = st.text_input(
                "Deadline",
                value="YYYY/MM/DD",
                key=f"manual_reco_deadline_{assessment.id}",
            )

            status_value = st.selectbox(
                "Status",
                options=["Open", "In Progress", "Mitigated", "Closed"],
                index=0,
                key=f"manual_reco_status_{assessment.id}",
            )

            submitted_manual_reco = st.form_submit_button("Add Recommendation")

        if submitted_manual_reco:
            try:
                title = f"{selected_domain} - {manual_recommendation[:80].strip()}" if manual_recommendation.strip() else ""
                description_parts = [
                    manual_recommendation.strip(),
                    f"Responsible: {responsible.strip()}" if responsible.strip() else "",
                    f"Deadline: {deadline.strip()}" if deadline.strip() and deadline.strip() != "YYYY/MM/DD" else "",
                    f"Status: {status_value}",
                ]
                description = "\n".join([p for p in description_parts if p])

                priority_map = {
                    "Critical": "high",
                    "High": "high",
                    "Medium": "medium",
                    "Low": "low",
                }

                if not manual_recommendation.strip():
                    st.warning("Completeaza textul recomandarii.")
                else:
                    recommendation_service.create_manual(
                        user,
                        assessment_id=assessment.id,
                        title=title,
                        description=description,
                        priority=priority_map.get(risk_value, "medium"),
                        domain_name=selected_domain,
                        domain_code=selected_domain,
                        question_code=None,
                        score=None,
                    )
                    st.success("Recommendation added.")
                    st.rerun()
            except Exception as exc:
                st.error(str(exc))

        st.write("### Recommendation Table")
        recommendations = recommendation_service.list_for_assessment(user, assessment.id)

        if recommendations:
            recommendation_rows = []
            for rec in recommendations:
                recommendation_rows.append(
                    {
                        "Priority": getattr(rec, "priority", "") or "",
                        "Domain": getattr(rec, "domain_name", "") or "",
                        "Title": getattr(rec, "title", "") or "",
                        "Description": getattr(rec, "description", "") or "",
                        "Status": getattr(rec, "status", "") or "",
                        "Score": getattr(rec, "score", None),
                        "Source": getattr(rec, "source", "") or "",
                    }
                )
            st.dataframe(recommendation_rows, use_container_width=True)
        else:
            st.info("Nu exista recomandari disponibile.")

        st.write("### Export Options")

        include_findings = st.checkbox(
            "Include findings grouped by criticality",
            value=True,
            key=f"include_findings_{assessment.id}",
        )

        include_annex = st.checkbox(
            "Include detailed annex with all controls and scores",
            value=True,
            key=f"include_annex_{assessment.id}",
        )

        logo_path = st.text_input(
            "Logo path for PDF / Word",
            value=getattr(settings, "company_logo_path", "") or "",
            key=f"logo_path_{assessment.id}",
            help="Exemplu: uploads/logo.png",
        )

        auditor_name_default = getattr(user, "username", "") or ""
        auditor_name = st.text_input(
            "Auditor name",
            value=auditor_name_default,
            key=f"auditor_name_{assessment.id}",
        )

        report_version = st.text_input(
            "Report version",
            value=getattr(settings, "default_report_version", "1.0") or "1.0",
            key=f"report_version_{assessment.id}",
        )

        report_date = st.text_input(
            "Report date",
            value=datetime.now().strftime("%Y-%m-%d"),
            key=f"report_date_{assessment.id}",
        )

        st.write("### Current domain scores")
        if domain_scores:
            st.json(domain_scores)
        else:
            st.info("Nu exista suficiente raspunsuri pentru calculul scorurilor.")

        st.write("### Executive summary preview")
        if summary:
            st.text_area(
                "Summary",
                value=summary.summary_text or "",
                height=120,
                disabled=True,
                key=f"summary_preview_{assessment.id}",
            )
            st.text_area(
                "Strengths",
                value=summary.strengths_text or "",
                height=100,
                disabled=True,
                key=f"strengths_preview_{assessment.id}",
            )
            st.text_area(
                "Gaps",
                value=summary.gaps_text or "",
                height=100,
                disabled=True,
                key=f"gaps_preview_{assessment.id}",
            )
            st.text_area(
                "Recommendations",
                value=summary.recommendations_text or "",
                height=120,
                disabled=True,
                key=f"recs_preview_{assessment.id}",
            )
        else:
            st.info("Nu exista executive summary salvat.")

        st.write("### Generated recommendations")
        if recommendations:
            for rec in recommendations:
                st.markdown(f"**[{str(getattr(rec, 'priority', '')).upper()}] {getattr(rec, 'title', '')}**")
                if getattr(rec, "description", ""):
                    st.write(getattr(rec, "description", ""))
        else:
            st.info("Nu exista recomandari generate.")

        st.write("### Descarcare export")
        pdf_bytes = export_service.export_pdf(
            user,
            company=company,
            assessment=assessment,
            responses=responses,
            domain_scores=domain_scores,
            executive_summary=summary,
            recommendations=recommendations,
            include_findings=include_findings,
            include_annex=include_annex,
            logo_path=logo_path,
            auditor_name=auditor_name,
            report_version=report_version,
            report_date=report_date,
        )
        word_bytes = export_service.export_word(
            user,
            company=company,
            assessment=assessment,
            responses=responses,
            domain_scores=domain_scores,
            executive_summary=summary,
            recommendations=recommendations,
            include_findings=include_findings,
            include_annex=include_annex,
            logo_path=logo_path,
            auditor_name=auditor_name,
            report_version=report_version,
            report_date=report_date,
        )
        excel_bytes = export_service.export_excel(
            user,
            company=company,
            assessment=assessment,
            responses=responses,
            domain_scores=domain_scores,
            executive_summary=summary,
            recommendations=recommendations,
        )

        c_pdf, c_word, c_excel = st.columns(3)
        with c_pdf:
            st.download_button(
                label="Descarca PDF",
                data=pdf_bytes,
                file_name=f"{company.name}_{assessment.name}.pdf".replace(" ", "_"),
                mime="application/pdf",
                key=f"download_pdf_{assessment.id}",
                use_container_width=True,
            )
        with c_word:
            st.download_button(
                label="Descarca Word",
                data=word_bytes,
                file_name=f"{company.name}_{assessment.name}.docx".replace(" ", "_"),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"download_word_{assessment.id}",
                use_container_width=True,
            )
        with c_excel:
            st.download_button(
                label="Descarca Excel",
                data=excel_bytes,
                file_name=f"{company.name}_{assessment.name}.xlsx".replace(" ", "_"),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download_excel_{assessment.id}",
                use_container_width=True,
            )

        st.write("### Import Excel in evaluarea curenta")
        uploaded_excel = st.file_uploader(
            "Incarca fisier Excel exportat anterior",
            type=["xlsx"],
            key=f"upload_excel_{assessment.id}",
        )

        if uploaded_excel is not None:
            excel_content = uploaded_excel.getvalue()

            try:
                validation = backup_service.validate_assessment_excel(
                    user,
                    assessment=assessment,
                    excel_bytes=excel_content,
                )

                st.info(
                    f"Randuri totale: {validation['total_rows']} | "
                    f"Valide: {validation['valid_rows']} | "
                    f"Invalide: {validation['invalid_rows']}"
                )

                if validation["errors"]:
                    st.warning("Exista randuri invalide in fisier.")
                    st.dataframe(validation["errors"], use_container_width=True)
                else:
                    st.success("Fisierul Excel a trecut validarea.")

                overwrite = st.checkbox(
                    "Overwrite complet pentru evaluarea curenta",
                    value=False,
                    key=f"overwrite_excel_{assessment.id}",
                )

                if st.button("Importa Excel", key=f"btn_import_excel_{assessment.id}"):
                    updated_count = backup_service.import_assessment_excel(
                        user,
                        company=company,
                        assessment=assessment,
                        excel_bytes=excel_content,
                        overwrite=overwrite,
                    )
                    if overwrite:
                        st.success(
                            f"Import complet realizat. Au fost scrise {updated_count} raspunsuri in baza de date."
                        )
                    else:
                        st.success(
                            f"Import incremental realizat. Au fost actualizate {updated_count} raspunsuri in baza de date."
                        )
                    st.rerun()

            except Exception as exc:
                st.error(str(exc))

        st.write("### Export / Import JSON evaluare")
        json_bytes = backup_service.export_assessment_json(user, company, assessment)
        st.download_button(
            label="Descarca JSON evaluare",
            data=json_bytes,
            file_name=f"{company.name}_{assessment.name}.json".replace(" ", "_"),
            mime="application/json",
            key=f"download_json_{assessment.id}",
            use_container_width=True,
        )

        uploaded_json = st.file_uploader(
            "Importa JSON in evaluarea curenta",
            type=["json"],
            key=f"upload_json_{assessment.id}",
        )
        if uploaded_json is not None:
            if st.button("Importa JSON", key=f"btn_import_json_{assessment.id}"):
                try:
                    backup_service.import_assessment_json(
                        user,
                        company=company,
                        assessment=assessment,
                        json_bytes=uploaded_json.read(),
                    )
                    st.success("JSON importat cu succes.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        if getattr(user, "role", "") == "admin":
            st.write("### Backup / Restore baza de date")
            db_bytes = backup_service.export_sqlite_db(user)
            st.download_button(
                label="Descarca backup DB",
                data=db_bytes,
                file_name="assessment.db",
                mime="application/octet-stream",
                key="download_db_backup",
                use_container_width=True,
            )

            uploaded_db = st.file_uploader(
                "Restore DB SQLite",
                type=["db", "sqlite", "sqlite3"],
                key="upload_db_restore",
            )
            if uploaded_db is not None:
                if st.button("Restore DB", key="btn_restore_db"):
                    try:
                        backup_service.import_sqlite_db(user, uploaded_db.read())
                        st.success("DB restaurata. Reincarca aplicatia.")
                    except Exception as exc:
                        st.error(str(exc))

    finally:
        session.close()