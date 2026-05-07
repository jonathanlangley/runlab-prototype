from __future__ import annotations

import base64

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.charts import build_weekly_distance_chart, plot_training_balance_with_counts
from src.pdf_generator import generate_runlab_pdf_bytes
from src.runlab_utils import html_text, normalise_label_value, normalise_signal, safe_get


def render_pdf_preview(pdf_bytes: bytes, height: int = 760) -> None:
    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    pdf_display = f"""
    <iframe
        src="data:application/pdf;base64,{base64_pdf}"
        width="100%"
        height="{height}px"
        style="border: none;">
    </iframe>
    """

    components.html(pdf_display, height=height)


def render_metric_cards(items: list[tuple[str, str]]) -> None:
    if not items:
        return

    cols = st.columns(len(items))

    for col, (label, value) in zip(cols, items):
        with col:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>{html_text(label)}</div>
                    <div class='metric-value'>{html_text(value)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def get_product_report(report: dict) -> dict:
    if isinstance(report.get("product_report"), dict):
        return report["product_report"]

    return {
        "title": "RunLab Performance Report",
        "primary_insight": report.get("diagnosis_title", "Your next training focus"),
        "primary_summary": report.get("diagnosis_summary", ""),
        "current_overview": report.get("summary_line", ""),
        "key_signal": {
            "title": report.get("focus", {}).get("limiter", "Primary limiter"),
            "detail": report.get("focus", {}).get("detail", ""),
        },
        "actions": report.get("focus", {}).get("prescription", [])[:4],
        "why_points": report.get("why_points", [])[:3],
        "coach_explanation": report.get("ai_text", ""),
        "supporting_signals": report.get("top_signals", [])[:3],
        "focus": report.get("focus", {}),
    }


def render_locked_report_message() -> None:
    st.markdown(
        """
        <div class='locked-card'>
            <div class='section-title'>Unlock your full RunLab Performance Report</div>
            <div class='body-copy'>
                Your headline insight and key signal are shown above. Request beta access to view:
            </div>
            <div class='support-box'>Your specific next training actions</div>
            <div class='support-box'>The full coach-style explanation</div>
            <div class='support-box'>A downloadable personalised PDF report</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _build_ai_badge_and_footer(used_ai: bool) -> tuple[str, str]:
    if used_ai:
        ai_badge = (
            "<div style='"
            "display:inline-flex;"
            "align-items:center;"
            "gap:6px;"
            "padding:4px 10px;"
            "border-radius:999px;"
            "background:#ecfdf5;"
            "border:1px solid #a7f3d0;"
            "color:#065f46;"
            "font-size:0.78rem;"
            "font-weight:600;"
            "white-space:nowrap;"
            "'>"
            "<span>🟢</span>"
            "<span>OpenAI connected</span>"
            "</div>"
        )
        footer_note = (
            "Training signals and recommendations are generated using deterministic logic. "
            "OpenAI is used as an explanation layer to translate those signals into plain English."
        )
    else:
        ai_badge = (
            "<div style='"
            "display:inline-flex;"
            "align-items:center;"
            "gap:6px;"
            "padding:4px 10px;"
            "border-radius:999px;"
            "background:#f9fafb;"
            "border:1px solid #e5e7eb;"
            "color:#6b7280;"
            "font-size:0.78rem;"
            "font-weight:600;"
            "white-space:nowrap;"
            "'>"
            "<span>⚪</span>"
            "<span>Fallback mode</span>"
            "</div>"
        )
        footer_note = (
            "Training signals and recommendations are generated using deterministic logic. "
            "A local fallback explanation was used because the AI explanation layer was unavailable."
        )

    return ai_badge, footer_note


def render_coach_explanation(product: dict, report: dict) -> None:
    coach_text = str(product.get("coach_explanation", "") or "").strip()
    used_ai = bool(report.get("used_ai", False))

    if not coach_text:
        return

    paragraphs = [p.strip() for p in coach_text.split("\n\n") if p.strip()]
    ai_badge, footer_note = _build_ai_badge_and_footer(used_ai)

    coach_html = (
        "<div class='report-card'>"
        "<div style='"
        "display:flex;"
        "justify-content:space-between;"
        "align-items:center;"
        "margin-bottom:16px;"
        "gap:12px;"
        "flex-wrap:wrap;"
        "'>"
        "<div class='section-title' style='margin-bottom:0;'>Coach-style explanation</div>"
        f"{ai_badge}"
        "</div>"
    )

    for para in paragraphs[:2]:
        coach_html += f"<div class='body-copy'>{html_text(para)}</div>"

    coach_html += (
        f"<div class='small-note' style='margin-top:12px;'>{html_text(footer_note)}</div>"
        "</div>"
    )

    st.markdown(coach_html, unsafe_allow_html=True)


def render_product_report(report: dict, unlocked: bool = True) -> None:
    product = get_product_report(report)
    focus = product.get("focus", report.get("focus", {}))

    confidence_label = ""
    confidence_note = ""
    if isinstance(focus, dict):
        confidence_label = str(focus.get("confidence_label", ""))
        confidence_note = str(focus.get("confidence_note", ""))

    confidence_html = ""
    if confidence_label:
        confidence_html = (
            f"<div class='small-note'>"
            f"<strong>{html_text(confidence_label)}</strong>"
            f"{': ' + html_text(confidence_note) if confidence_note else ''}"
            f"</div>"
        )

    st.markdown(
        f"""
        <div class='hero-card'>
            <div class='kicker'>RunLab Performance Report</div>
            <div class='hero-title'>{html_text(product.get("primary_insight"))}</div>
            <div class='body-copy'>{html_text(product.get("primary_summary"))}</div>
            {confidence_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    key_signal = product.get("key_signal", {}) or {}
    st.markdown(
        f"""
        <div class='report-card'>
            <div class='section-title'>Why this is your limiter</div>
            <div class='body-copy'><strong>{html_text(safe_get(key_signal, "title", "Primary limiter"))}</strong></div>
            <div class='body-copy'>{html_text(safe_get(key_signal, "detail", ""))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not unlocked:
        render_locked_report_message()
        return

    actions = product.get("actions", []) or [
        "Keep the current structure stable.",
        "Make only one small change at a time.",
    ]

    st.markdown(
        "<div class='action-card'><div class='section-title'>What to do next</div>",
        unsafe_allow_html=True,
    )

    for action in actions[:4]:
        st.markdown(
            f"<div class='step-box'>{html_text(action)}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='report-card'><div class='section-title'>Supporting evidence</div>",
        unsafe_allow_html=True,
    )

    supporting_metrics = report.get("supporting_metrics", [])
    if supporting_metrics:
        metric_items = [normalise_label_value(item) for item in supporting_metrics[:4]]
        render_metric_cards(metric_items)
    else:
        metrics = report.get("metrics", {})
        render_metric_cards(
            [
                ("Run days", f"{round((metrics.get('days_with_run_last_28', 0) or 0) / 4.0, 1)}/week"),
                ("Weekly volume", f"{round(float(metrics.get('recent_avg_weekly_km', 0) or 0), 1)} km"),
                ("Quality sessions", f"{round(float(metrics.get('quality_runs_last_28', 0) or 0) / 4.0, 1)}/week"),
                ("Long runs", f"{int(metrics.get('long_runs_last_28', 0) or 0)} in 28 days"),
            ]
        )

    current_overview = product.get("current_overview", "")
    if current_overview:
        st.markdown(
            f"<div class='support-box'>{html_text(current_overview)}</div>",
            unsafe_allow_html=True,
        )

    why_points = product.get("why_points", []) or []
    for point in why_points[:3]:
        st.markdown(
            f"<div class='why-box'>{html_text(point)}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    render_coach_explanation(product, report)

    pdf_bytes = generate_runlab_pdf_bytes(report)

    st.download_button(
        label="Download your personalised RunLab Performance Report (PDF)",
        data=pdf_bytes,
        file_name="runlab_performance_report.pdf",
        mime="application/pdf",
    )


def render_supporting_signals(report: dict) -> None:
    product = get_product_report(report)
    supporting = product.get("supporting_signals", []) or []

    with st.expander("Supporting signals", expanded=False):
        if not supporting:
            st.info("No additional supporting signals were generated for this report.")
            return

        for raw_signal in supporting[:4]:
            signal = normalise_signal(raw_signal)

            st.markdown(
                f"""
                <div class='signal-card'>
                    <div class='section-title'>{html_text(signal["title"])}</div>
                    <div class='body-copy'>{html_text(signal["detail"])}</div>
                    <div class='small-note'>Priority: {html_text(signal["priority"])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_next_week_analysis(report: dict) -> None:
    rows = report.get("next_week_rows", [])

    with st.expander("Current vs next week detail", expanded=False):
        if not rows:
            st.info(
                "No next-week detail table is available for this report yet. "
                "The main recommendation above is still based on the current limiter and supporting signals."
            )
            return

        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            use_container_width=True,
        )

        st.caption(
            "RunLab recommends changing the primary limiter first while keeping the rest of the structure relatively stable."
        )


def render_supporting_analysis(report: dict) -> None:
    render_supporting_signals(report)
    render_next_week_analysis(report)

    st.markdown(
        "<div class='section-card'><div class='section-title'>Weekly distance trend</div>",
        unsafe_allow_html=True,
    )
    st.pyplot(build_weekly_distance_chart(report["df"]))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='section-card'><div class='section-title'>Training balance</div>",
        unsafe_allow_html=True,
    )

    if "balance_df" in report and isinstance(report["balance_df"], pd.DataFrame):
        st.pyplot(plot_training_balance_with_counts(report["balance_df"]))

        balance_note = report.get("balance_note", "")
        if balance_note:
            st.markdown(
                f"<div class='support-box'>{html_text(balance_note)}</div>",
                unsafe_allow_html=True,
            )

        st.dataframe(
            report["balance_df"],
            hide_index=True,
            use_container_width=True,
        )

    if "detailed_balance_df" in report and isinstance(report["detailed_balance_df"], pd.DataFrame):
        with st.expander("Show detailed threshold / VO2 split"):
            st.dataframe(
                report["detailed_balance_df"],
                hide_index=True,
                use_container_width=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

    structure_gaps = report.get("structure_gaps", [])
    if structure_gaps:
        st.markdown(
            "<div class='section-card'><div class='section-title'>Structure gaps</div>",
            unsafe_allow_html=True,
        )

        for raw_gap in structure_gaps[:4]:
            gap = normalise_signal(raw_gap)
            st.markdown(
                f"""
                <div class='support-box'>
                    <strong>{html_text(gap["title"])}:</strong>
                    {html_text(gap["detail"])}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Debug view: decision scores, metrics and signals"):
        focus = report.get("focus", {})
        if isinstance(focus, dict):
            st.json(focus.get("decision_scores", {}))
        st.json(report.get("metrics", {}))
        st.dataframe(
            pd.DataFrame(report.get("signals", [])),
            use_container_width=True,
        )
