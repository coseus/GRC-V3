from __future__ import annotations

import pandas as pd
import streamlit as st

from app.charts.dashboard import generate_bar_chart
from app.services.crosswalk_service import CrosswalkService
from app.services.risk_engine import (
    apply_risk_penalty,
    calculate_domain_maturity,
    calculate_overall_weighted_score,
    calculate_risk_score,
    calculate_vendor_risk_profile,
    calculate_weighted_domain_scores,
    get_maturity_level,
    get_top_gaps,
    normalize_responses,
)
from app.services.roadmap_service import RoadmapService


def _render_heatmap(responses):
    df = pd.DataFrame(responses)
    if df.empty:
        st.info("Nu exista date pentru heatmap.")
        return

    if "domain_name" not in df.columns and "domain" in df.columns:
        df["domain_name"] = df["domain"]
    if "risk" not in df.columns:
        df["risk"] = "Medium"

    heat = df.pivot_table(
        index="domain_name",
        columns="risk",
        values="score",
        aggfunc="mean",
    )

    if heat.empty:
        st.info("Nu exista suficiente scoruri pentru heatmap.")
        return

    order = [c for c in ["Low", "Medium", "High", "Critical"] if c in heat.columns]
    heat = heat[order]

    def color_score(value):
        if value == "" or pd.isna(value):
            return ""
        v = float(value)
        if v >= 85:
            return "background-color: #c6efce; color: #006100;"
        if v >= 70:
            return "background-color: #e2f0d9; color: #375623;"
        if v >= 50:
            return "background-color: #fff2cc; color: #7f6000;"
        if v >= 30:
            return "background-color: #fce4d6; color: #9c0006;"
        return "background-color: #ffc7ce; color: #9c0006;"

    styled = heat.style.format("{:.1f}").map(color_score)
    st.dataframe(styled, width="stretch")


def render_dashboard_section(data, lang, actor, company, assessment, assessment_state):
    if not actor:
        st.error("Authentication required")
        return

    st.header("Executive Dashboard")

    responses = normalize_responses((assessment_state or {}).get("responses_saved", []))
    if not responses:
        st.info("Nu exista raspunsuri salvate pentru aceasta evaluare.")
        return

    domain_scores = calculate_weighted_domain_scores(responses)
    domain_maturity = calculate_domain_maturity(responses)
    overall = calculate_overall_weighted_score(responses)
    adjusted = apply_risk_penalty(responses, overall)
    risk_score = calculate_risk_score(responses)
    maturity = get_maturity_level(adjusted)
    top_gaps = get_top_gaps(responses, limit=8)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Score", f"{overall:.1f}/100")
    c2.metric("Adjusted Score", f"{adjusted:.1f}/100")
    c3.metric("Maturity", maturity)
    c4.metric("Risk Score", f"{risk_score:.1f}")

    st.write("### Domain Scores")
    if domain_scores:
        st.image(generate_bar_chart(domain_scores), width="stretch")

    st.write("### Domain Maturity")
    maturity_rows = [
        {
            "Domain": domain,
            "Score": payload["score"],
            "Maturity Level": payload["maturity_level"],
            "Maturity Label": payload["maturity_label"],
        }
        for domain, payload in domain_maturity.items()
    ]
    st.dataframe(maturity_rows, width="stretch")

    st.write("### Top Gaps")
    if top_gaps:
        gap_rows = [
            {
                "Domain": item["domain"],
                "Question": item["question"],
                "Score": item["score"],
                "Risk": item["risk"],
                "Maturity": item["maturity_label"],
                "Weight": item["weight"],
                "Notes": item["notes"],
            }
            for item in top_gaps
        ]
        st.dataframe(gap_rows, width="stretch")
    else:
        st.info("Nu exista gap-uri semnificative.")

    st.write("### Risk Heatmap")
    _render_heatmap(responses)

    st.write("### Framework Crosswalk")
    crosswalk_rows = CrosswalkService().list_all()
    st.dataframe(crosswalk_rows, width="stretch")

    st.write("### Roadmap")
    roadmap = RoadmapService().build_roadmap(responses)

    cqw, cst = st.columns(2)
    with cqw:
        st.markdown("**Quick Wins**")
        if roadmap["quick_wins"]:
            st.dataframe(roadmap["quick_wins"], width="stretch")
        else:
            st.info("Nu exista quick wins identificate.")

    with cst:
        st.markdown("**Strategic Initiatives**")
        if roadmap["strategic"]:
            st.dataframe(roadmap["strategic"], width="stretch")
        else:
            st.info("Nu exista initiative strategice identificate.")

    if str(getattr(assessment, "framework_code", "")).lower().startswith("tprm"):
        st.write("### TPRM Vendor Risk Profile")

        colv1, colv2, colv3 = st.columns(3)
        with colv1:
            vendor_criticality = st.selectbox(
                "Vendor Criticality",
                ["low", "medium", "high", "critical"],
                index=2,
                key=f"vendor_criticality_{assessment.id}",
            )
        with colv2:
            internet_exposed = st.checkbox(
                "Internet Exposed Service",
                value=True,
                key=f"internet_exposed_{assessment.id}",
            )
        with colv3:
            privileged_access = st.checkbox(
                "Privileged Access",
                value=False,
                key=f"privileged_access_{assessment.id}",
            )

        personal_data_access = st.checkbox(
            "Personal Data Access",
            value=True,
            key=f"personal_data_access_{assessment.id}",
        )

        vendor_profile = calculate_vendor_risk_profile(
            responses,
            vendor_criticality=vendor_criticality,
            internet_exposed=internet_exposed,
            privileged_access=privileged_access,
            personal_data_access=personal_data_access,
        )

        cv1, cv2, cv3 = st.columns(3)
        cv1.metric("Vendor Tier", vendor_profile["vendor_tier"])
        cv2.metric("Inherent Vendor Risk", f"{vendor_profile['inherent_vendor_risk']:.1f}")
        cv3.metric("TPRM Maturity", vendor_profile["maturity"])
