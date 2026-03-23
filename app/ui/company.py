from __future__ import annotations

import streamlit as st

from app.db.session import get_session
from app.frameworks.loader import get_framework_options
from app.services.assessments import AssessmentService
from app.services.companies import CompanyService


def render_company_section(user, lang):
    if not user:
        st.error("Authentication required")
        return None

    session = get_session()
    company_service = CompanyService(session)
    assessment_service = AssessmentService(session)

    try:
        st.sidebar.subheader("Company / Assessment")

        companies = company_service.list_companies(user)

        if not companies:
            st.sidebar.info("Nu exista companii. Creeaza prima companie.")
        company_names = [c.name for c in companies]

        selected_company = None
        if company_names:
            selected_company_name = st.sidebar.selectbox(
                "Company",
                options=company_names,
                key="selected_company_name",
            )
            selected_company = next((c for c in companies if c.name == selected_company_name), None)

        with st.sidebar.expander("Create company", expanded=False):
            new_company_name = st.text_input("Company name", key="new_company_name")
            new_company_industry = st.text_input("Industry", key="new_company_industry")
            new_company_country = st.text_input("Country", key="new_company_country")
            new_company_size = st.selectbox(
                "Size",
                options=["", "Small", "Medium", "Large", "Enterprise"],
                key="new_company_size",
            )

            if st.button("Create company", key="btn_create_company"):
                try:
                    company_service.create_company(
                        user,
                        name=new_company_name.strip(),
                        industry=new_company_industry.strip(),
                        country=new_company_country.strip(),
                        size=new_company_size.strip(),
                    )
                    st.success("Company created")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        if not selected_company:
            return None

        assessments = assessment_service.list_for_company(user, selected_company.id)

        selected_assessment = None
        if assessments:
            assessment_labels = [
                f"{a.name} | {a.framework_name} | {a.status}"
                for a in assessments
            ]
            selected_assessment_label = st.sidebar.selectbox(
                "Assessment",
                options=assessment_labels,
                key="selected_assessment_label",
            )
            selected_assessment = assessments[assessment_labels.index(selected_assessment_label)]

        frameworks = get_framework_options()

        with st.sidebar.expander("Create assessment", expanded=False):
            new_assessment_name = st.text_input("Assessment name", key="new_assessment_name")

            selected_framework_code = st.selectbox(
                "Framework / Project Type",
                options=list(frameworks.keys()),
                format_func=lambda x: frameworks[x]["name"],
                key="selected_framework_code",
            )

            if st.button("Create assessment", key="btn_create_assessment"):
                try:
                    if not new_assessment_name.strip():
                        raise ValueError("Assessment name este obligatoriu.")

                    framework_code = selected_framework_code
                    selected_framework_name = frameworks[selected_framework_code]["name"]

                    assessment_service.create_assessment(
                        user,
                        company_id=selected_company.id,
                        name=new_assessment_name.strip(),
                        framework_code=framework_code,
                        framework_name=selected_framework_name,
                    )
                    st.success("Assessment created")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        if not selected_assessment:
            st.sidebar.info("Creeaza sau selecteaza o evaluare.")
            return None

        return {
            "company": selected_company,
            "assessment": selected_assessment,
        }

    finally:
        session.close()