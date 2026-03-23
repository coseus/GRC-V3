from __future__ import annotations

import streamlit as st

from app.db.session import get_session
from app.services.users import UserService


def render_admin_user_section(current_user):
    session = get_session()
    service = UserService(session)

    try:
        with st.sidebar.expander("User management", expanded=False):
            st.subheader("Utilizatori")

            users = service.list_users(current_user)
            for u in users:
                label = f"{u.username} ({u.role}) - {'Active' if u.is_active else 'Inactive'}"
                st.caption(label)

            st.write("---")
            st.subheader("Creeaza utilizator")

            username = st.text_input("New username", key="new_username")
            password = st.text_input("New password", type="password", key="new_password")
            role = st.selectbox("New role", ["admin", "auditor", "viewer"], key="new_role")

            if st.button("Create user", key="btn_create_user"):
                try:
                    service.create_user(current_user, username, password, role)
                    st.success("User created")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

            if users:
                st.write("---")
                st.subheader("Modifica utilizator")

                selected_username = st.selectbox(
                    "Select user",
                    options=[u.username for u in users],
                    key="selected_user_admin",
                )
                selected_user = next(u for u in users if u.username == selected_username)

                edited_username = st.text_input(
                    "Edit username",
                    value=selected_user.username,
                    key="edit_username",
                )
                edited_role = st.selectbox(
                    "Edit role",
                    ["admin", "auditor", "viewer"],
                    index=["admin", "auditor", "viewer"].index(selected_user.role),
                    key="edit_role",
                )
                edited_active = st.checkbox(
                    "Active",
                    value=selected_user.is_active,
                    key="edit_active",
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Save user", key="btn_save_user"):
                        try:
                            service.update_user(
                                current_user,
                                selected_user.id,
                                edited_username,
                                edited_role,
                                edited_active,
                            )
                            st.success("User updated")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))

                with col2:
                    if st.button("Delete user", key="btn_delete_user"):
                        try:
                            service.delete_user(current_user, selected_user.id)
                            st.success("User deleted")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))

                st.write("---")
                st.subheader("Schimba parola")

                new_password_for_user = st.text_input(
                    "New password for selected user",
                    type="password",
                    key="admin_reset_password",
                )

                if st.button("Change password", key="btn_change_password"):
                    try:
                        service.change_password(
                            current_user,
                            selected_user.id,
                            new_password_for_user,
                        )
                        st.success("Password changed")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

    finally:
        session.close()