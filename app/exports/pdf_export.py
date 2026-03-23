from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _safe_logo(logo_path: str | None, max_width=5 * cm, max_height=2 * cm):
    if not logo_path:
        return None

    p = Path(logo_path)
    if not p.exists() or not p.is_file():
        return None

    try:
        img = Image(str(p))
        img._restrictSize(max_width, max_height)
        return img
    except Exception:
        return None


def _section_title(text, styles):
    return Paragraph(f"<b>{text}</b>", styles["Heading2"])


def _criticality_color(value: str):
    value = str(value or "").strip().title()
    return {
        "Critical": colors.HexColor("#c00000"),
        "High": colors.HexColor("#e26b0a"),
        "Medium": colors.HexColor("#bf9000"),
        "Low": colors.HexColor("#38761d"),
    }.get(value, colors.HexColor("#1F1F1F"))


def _make_chart(domain_scores: dict):
    if not domain_scores:
        return None

    labels = list(domain_scores.keys())
    values = list(domain_scores.values())

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(labels, values)
    ax.set_title("Domain Scores")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def _build_cover_metadata_table(company_name, assessment_name, framework_name, auditor_name, report_version, report_date):
    rows = [
        ["Company", company_name],
        ["Assessment", assessment_name],
        ["Framework", framework_name],
        ["Auditor", auditor_name or "-"],
        ["Report Version", report_version or "1.0"],
        ["Report Date", report_date or datetime.now().strftime("%Y-%m-%d")],
    ]
    table = Table(rows, colWidths=[4.5 * cm, 10 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#D9E2F3")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def generate_pdf_report(
    *,
    company_name: str,
    assessment_name: str,
    framework_name: str,
    responses,
    domain_scores,
    executive_summary=None,
    recommendations=None,
    findings=None,
    logo_path: str | None = None,
    include_annex: bool = True,
    auditor_name: str | None = None,
    report_version: str | None = None,
    report_date: str | None = None,
):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#1F4E78"),
            spaceAfter=12,
        )
    )

    story = []

    logo = _safe_logo(logo_path)
    if logo:
        story.append(logo)
        story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("GRC Assessment Report", styles["CoverTitle"]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(
        _build_cover_metadata_table(
            company_name,
            assessment_name,
            framework_name,
            auditor_name,
            report_version,
            report_date,
        )
    )
    story.append(Spacer(1, 0.8 * cm))
    story.append(
        Paragraph(
            "This report provides an executive overview of assessment performance, domain scores, findings, recommendations, and a detailed annex of evaluated controls.",
            styles["BodyText"],
        )
    )
    story.append(PageBreak())

    story.append(_section_title("Domain Scores", styles))
    if domain_scores:
        table_data = [["Domain", "Score"]]
        for domain_name, score in domain_scores.items():
            table_data.append([str(domain_name), f"{score:.1f}" if isinstance(score, (int, float)) else str(score)])

        table = Table(table_data, colWidths=[10.5 * cm, 3.2 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#F7F9FC")]),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 0.35 * cm))

        chart_buf = _make_chart(domain_scores)
        if chart_buf:
            chart = Image(chart_buf, width=16 * cm, height=7.2 * cm)
            story.append(chart)
    else:
        story.append(Paragraph("No domain scores available.", styles["Normal"]))

    story.append(Spacer(1, 0.5 * cm))
    story.append(_section_title("Executive Summary", styles))
    if executive_summary:
        for label, value in [
            ("Summary", getattr(executive_summary, "summary_text", "") or ""),
            ("Strengths", getattr(executive_summary, "strengths_text", "") or ""),
            ("Gaps", getattr(executive_summary, "gaps_text", "") or ""),
            ("Management Recommendations", getattr(executive_summary, "recommendations_text", "") or ""),
        ]:
            if value:
                story.append(Paragraph(f"<b>{label}</b>", styles["Heading3"]))
                story.append(Paragraph(value.replace("\n", "<br/>"), styles["BodyText"]))
                story.append(Spacer(1, 0.2 * cm))
    else:
        story.append(Paragraph("No executive summary available.", styles["Normal"]))

    story.append(Spacer(1, 0.5 * cm))
    story.append(_section_title("Findings by Criticality", styles))
    if findings:
        grouped = defaultdict(list)
        for item in findings:
            grouped[str(item.get("criticality", "Medium")).title()].append(item)

        for criticality in ["Critical", "High", "Medium", "Low"]:
            items = grouped.get(criticality, [])
            if not items:
                continue

            story.append(
                Paragraph(
                    f"<font color='{_criticality_color(criticality).hexval()}'><b>{criticality}</b></font>",
                    styles["Heading3"],
                )
            )

            rows = [["ID", "Title", "Domain", "Score", "Notes"]]
            for idx, item in enumerate(items[:50], start=1):
                finding_id = f"{criticality[:1].upper()}-{idx:03d}"
                rows.append(
                    [
                        finding_id,
                        item.get("title", ""),
                        item.get("domain", ""),
                        "" if item.get("score") is None else str(item.get("score")),
                        item.get("notes", ""),
                    ]
                )

            t = Table(rows, colWidths=[1.2 * cm, 5.0 * cm, 2.8 * cm, 1.4 * cm, 4.6 * cm])
            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), _criticality_color(criticality)),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            story.append(t)
            story.append(Spacer(1, 0.25 * cm))
    else:
        story.append(Paragraph("No findings included.", styles["Normal"]))

    story.append(Spacer(1, 0.5 * cm))
    story.append(_section_title("Recommendations", styles))
    if recommendations:
        rows = [["Priority", "Title", "Description", "Domain"]]
        for rec in recommendations:
            rows.append(
                [
                    str(getattr(rec, "priority", "") or ""),
                    str(getattr(rec, "title", "") or ""),
                    str(getattr(rec, "description", "") or ""),
                    str(getattr(rec, "domain_name", "") or ""),
                ]
            )

        rec_table = Table(rows, colWidths=[2 * cm, 4.5 * cm, 6.0 * cm, 2.2 * cm])
        rec_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(rec_table)
    else:
        story.append(Paragraph("No recommendations available.", styles["Normal"]))

    if include_annex:
        story.append(PageBreak())
        story.append(_section_title("Annex - Detailed Controls and Scores", styles))

        if responses:
            rows = [["Domain", "Question ID", "Question", "Answer", "Score", "Risk", "Weight"]]
            for row in responses:
                rows.append(
                    [
                        str(row.get("domain_name") or row.get("domain") or ""),
                        str(row.get("question_id") or row.get("question_code") or ""),
                        str(row.get("question_text") or row.get("question") or ""),
                        str(row.get("answer_value") or row.get("selected_value") or ""),
                        "" if row.get("score") is None else str(row.get("score")),
                        str(row.get("risk") or ""),
                        str(row.get("weight") or ""),
                    ]
                )

            annex_table = Table(rows, colWidths=[2.8 * cm, 1.9 * cm, 6.2 * cm, 1.8 * cm, 1.2 * cm, 1.7 * cm, 1.2 * cm])
            annex_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            story.append(annex_table)
        else:
            story.append(Paragraph("No annex data available.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()