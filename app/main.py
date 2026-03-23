from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from app.config import settings
from app.db.init_db import init_db
from app.db.session import get_session
from app.frameworks.loader import load_framework_data
from app.repositories.users import UserRepository
from app.services.auth import authenticate
from app.ui.admin_users import render_admin_user_section
from app.ui.assessment import render_assessment_section
from app.ui.company import render_company_section
from app.ui.dashboard import render_dashboard_section
from app.ui.executive import render_executive_section
from app.ui.framework_comparison import render_framework_comparison_section
from app.ui.import_export import render_import_export_section


def login_sidebar():
    st.sidebar.title("Login")

    username = st.sidebar.text_input("Username", key="login_username")
    password = st.sidebar.text_input("Password", type="password", key="login_password")

    if st.sidebar.button("Login", key="btn_login"):
        session = get_session()
        try:
            user = authenticate(session, username, password)
            if user:
                st.session_state["user_id"] = user.id
                st.session_state["user_role"] = user.role
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials")
        finally:
            session.close()


def get_current_user():
    user_id = st.session_state.get("user_id")
    if not user_id:
        return None

    session = get_session()
    try:
        repo = UserRepository(session)
        return repo.get_by_id(user_id)
    finally:
        session.close()


def logout_button():
    if st.sidebar.button("Logout", key="btn_logout"):
        for key in ["user_id", "user_role", "assessment_id"]:
            st.session_state.pop(key, None)
        st.rerun()


def main():
    st.set_page_config(layout="wide", page_title=settings.app_name)

    if settings.auto_init_db:
        init_db()

    user = get_current_user()
    if not user:
        login_sidebar()
        st.stop()

    logout_button()

    lang = st.sidebar.selectbox("Language", ["ro", "en"], index=0)

    if user.role == "admin":
        render_admin_user_section(user)

    context = render_company_section(user, lang)
    if not context:
        st.title(settings.app_name)
        st.info("Selecteaza sau creeaza o companie si o evaluare.")
        st.stop()

    data = load_framework_data(context["assessment"].framework_code)

    st.title(settings.app_name)
    st.caption(
        f"Company: {context['company'].name} | "
        f"Assessment: {context['assessment'].name} | "
        f"Framework: {context['assessment'].framework_name}"
    )

    tabs = st.tabs(
        [
            "Assessment",
            "Executive Dashboard",
            "Executive Summary",
            "Import / Export",
            "Framework Comparison",
        ]
    )

    state = {"responses_saved": {}}

    with tabs[0]:
        result = render_assessment_section(
            data,
            lang,
            user,
            context["company"],
            context["assessment"],
            [],
            [],
        )
        if result is not None:
            state = result

    with tabs[1]:
        render_dashboard_section(
            data,
            lang,
            user,
            context["company"],
            context["assessment"],
            state,
        )

    with tabs[2]:
        render_executive_section(
            data,
            lang,
            user,
            context["company"],
            context["assessment"],
            state,
        )

    with tabs[3]:
        render_import_export_section(
            data,
            lang,
            user,
            context["company"],
            context["assessment"],
            state,
        )

    with tabs[4]:
        render_framework_comparison_section(
            user,
            context["company"],
            lang,
        )


if __name__ == "__main__":
    main()