from __future__ import annotations

from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def _clean_text(value: Any) -> str:
    text = str(value or "").strip()
    return (
        text.replace("—", "-")
        .replace("–", "-")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
    )


def _para(text: Any, style: ParagraphStyle) -> Paragraph:
    return Paragraph(_clean_text(text), style)


def _section_title(text: str, styles: dict[str, ParagraphStyle]) -> list:
    return [
        Spacer(1, 0.25 * cm),
        _para(text, styles["SectionTitle"]),
        Spacer(1, 0.12 * cm),
    ]


def _bullet_list(items: list[Any], styles: dict[str, ParagraphStyle]) -> list:
    flowables = []

    for item in items:
        flowables.append(
            Paragraph(
                f"• {_clean_text(item)}",
                styles["Body"],
            )
        )
        flowables.append(Spacer(1, 0.08 * cm))

    return flowables


def build_pdf_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()

    return {
        "Title": ParagraphStyle(
            "RunLabTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#111827"),
            spaceAfter=14,
            alignment=TA_LEFT,
        ),
        "Subtitle": ParagraphStyle(
            "RunLabSubtitle",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#6B7280"),
            spaceAfter=18,
        ),
        "Insight": ParagraphStyle(
            "RunLabInsight",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#111827"),
            spaceAfter=8,
        ),
        "SectionTitle": ParagraphStyle(
            "RunLabSectionTitle",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#111827"),
            spaceBefore=6,
            spaceAfter=5,
        ),
        "Body": ParagraphStyle(
            "RunLabBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#374151"),
            spaceAfter=6,
        ),
        "Small": ParagraphStyle(
            "RunLabSmall",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#6B7280"),
            spaceAfter=6,
        ),
    }


def build_metrics_table(metrics: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    run_days = round(float(metrics.get("days_with_run_last_28", 0) or 0) / 4.0, 1)
    weekly_km = round(float(metrics.get("recent_avg_weekly_km", 0) or 0), 1)
    quality = round(float(metrics.get("quality_runs_last_28", 0) or 0) / 4.0, 1)
    long_runs = int(metrics.get("long_runs_last_28", 0) or 0)

    data = [
        [
            _para("Run days", styles["Small"]),
            _para("Weekly volume", styles["Small"]),
            _para("Quality sessions", styles["Small"]),
            _para("Long runs", styles["Small"]),
        ],
        [
            _para(f"{run_days}/week", styles["Body"]),
            _para(f"{weekly_km} km", styles["Body"]),
            _para(f"{quality}/week", styles["Body"]),
            _para(f"{long_runs} in 28 days", styles["Body"]),
        ],
    ]

    table = Table(data, colWidths=[4.0 * cm, 4.0 * cm, 4.0 * cm, 4.0 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9FAFB")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    return table


def generate_runlab_pdf_bytes(report: dict[str, Any]) -> bytes:
    product = report.get("product_report", {}) or {}
    metrics = report.get("metrics", {}) or {}
    used_ai = bool(report.get("used_ai", False))
    styles = build_pdf_styles()

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
        title="RunLab Performance Report",
    )

    story = []

    # Title block
    story.append(_para("RunLab Performance Report", styles["Title"]))
    story.append(
        _para(
            "Performance-focused training analysis: data, signals, recommendation.",
            styles["Subtitle"],
        )
    )

    # SECTION 1: Your limiter
    story.extend(_section_title("Your limiter", styles))
    story.append(
        _para(
            product.get("primary_insight", "Your next training focus"),
            styles["Insight"],
        )
    )
    story.append(_para(product.get("primary_summary", ""), styles["Body"]))

    # SECTION 2: Why this is your limiter
    key_signal = product.get("key_signal", {}) or {}
    story.extend(_section_title("Why this is your limiter", styles))
    story.append(_para(key_signal.get("title", "Primary limiter"), styles["Body"]))
    story.append(_para(key_signal.get("detail", ""), styles["Body"]))

    # SECTION 3: What to do next
    actions = product.get("actions", []) or []
    story.extend(_section_title("What to do next (next 7 days)", styles))
    story.extend(_bullet_list(actions[:4], styles))

    # SECTION 4: Supporting evidence
    story.extend(_section_title("Supporting evidence", styles))
    story.append(build_metrics_table(metrics, styles))
    story.append(Spacer(1, 0.25 * cm))

    current_overview = product.get("current_overview", "")
    if current_overview:
        story.append(_para(current_overview, styles["Body"]))

    why_points = product.get("why_points", []) or []
    if why_points:
        story.extend(_bullet_list(why_points[:3], styles))

    # SECTION 5: Coach-style explanation
    coach_explanation = str(product.get("coach_explanation", "") or "").strip()
    if coach_explanation:
        story.extend(_section_title("Coach-style explanation", styles))
        paragraphs = [p.strip() for p in coach_explanation.split("\n\n") if p.strip()]

        for paragraph in paragraphs[:2]:
            story.append(_para(paragraph, styles["Body"]))

    # Footer note: reflects whether AI ran or fallback ran
    story.append(Spacer(1, 0.35 * cm))
    if used_ai:
        footer_text = (
            "RunLab uses deterministic rules to choose the recommendation. "
            "The AI layer explains the decision in plain English."
        )
    else:
        footer_text = (
            "RunLab uses deterministic rules to choose the recommendation. "
            "This explanation is generated from the same rules."
        )
    story.append(_para(footer_text, styles["Small"]))

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes