from __future__ import annotations

from html import escape
from pathlib import Path
from textwrap import dedent

import pandas as pd
import streamlit as st
import base64
import streamlit.components.v1 as components

from src.charts import build_weekly_distance_chart, plot_training_balance_with_counts
from src.pdf_generator import generate_runlab_pdf_bytes
from src.report_engine import generate_runlab_report

try:
    from src.runlab_classifier_v1 import build_pace_bands, classify_dataframe

    CLASSIFIER_AVAILABLE = True
except Exception:
    build_pace_bands = None
    classify_dataframe = None
    CLASSIFIER_AVAILABLE = False


APP_MODES = ["Try demo scenarios", "Upload your own data"]
VALID_BETA_CODES = {"RUNLAB-BETA1"}
BETA_SIGNUP_URL = "https://runlab.ai/#beta"

DEMO_FILES = {
    "Baseline runner (mixed stimulus)": "data/sample_runs.csv",
    "Near-optimal but plateauing": "data/near_optimal_but_plateauing.csv",
    "Consistent plateau": "data/consistent_plateau.csv",
    "Inconsistent training": "data/inconsistent_training.csv",
    "High volume, low quality": "data/high_volume_no_quality.csv",
    "Too much intensity": "data/too_much_intensity.csv",
}

DEMO_DESCRIPTIONS = {
    "Baseline runner (mixed stimulus)": "A typical mixed pattern with no single obvious disaster, useful for seeing the full report flow.",
    "Near-optimal but plateauing": "A strong pattern that may need one clearer progression signal.",
    "Consistent plateau": "Good rhythm, but several training levers have become static.",
    "Inconsistent training": "Irregular frequency and gaps between runs.",
    "High volume, low quality": "Good mileage, but limited structured quality.",
    "Too much intensity": "Hard work appears before the aerobic support is strong enough.",
}


def html_text(value: object) -> str:
    return escape(str(value or ""))


def safe_get(item: object, key: str, default: object = "") -> object:
    if isinstance(item, dict):
        return item.get(key, default)
    return default


def normalise_label_value(item: object) -> tuple[str, str]:
    if isinstance(item, dict):
        return str(item.get("label", item.get("title", "Metric"))), str(
            item.get("value", item.get("detail", ""))
        )

    if isinstance(item, (list, tuple)) and len(item) >= 2:
        return str(item[0]), str(item[1])

    return "Metric", str(item)


def normalise_signal(item: object) -> dict:
    if isinstance(item, dict):
        return {
            "title": str(item.get("title", item.get("label", "Signal"))),
            "detail": str(item.get("detail", item.get("value", ""))),
            "priority": str(item.get("priority", "")),
        }

    if isinstance(item, (list, tuple)):
        title = str(item[0]) if len(item) > 0 else "Signal"
        detail = str(item[1]) if len(item) > 1 else ""
        priority = str(item[2]) if len(item) > 2 else ""
        return {"title": title, "detail": detail, "priority": priority}

    return {"title": "Signal", "detail": str(item), "priority": ""}


def parse_time_to_seconds(value: str) -> int | None:
    try:
        parts = value.strip().split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except Exception:
        return None

    return None


def seconds_to_pace_str(seconds_per_km: float | None) -> str:
    if seconds_per_km is None:
        return "N/A"

    seconds = int(round(seconds_per_km))
    return f"{seconds // 60}:{seconds % 60:02d}/km"


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

def read_input_data(mode: str, uploaded_file, sample_option: str) -> pd.DataFrame | None:
    if mode == "Upload your own data" and uploaded_file is not None:
        return pd.read_csv(uploaded_file)

    demo_path = Path(DEMO_FILES[sample_option])
    if demo_path.exists():
        return pd.read_csv(demo_path)

    fallback = Path(__file__).parent / DEMO_FILES[sample_option]
    if fallback.exists():
        return pd.read_csv(fallback)

    st.error(f"Demo file not found: {DEMO_FILES[sample_option]}")
    return None


def apply_auto_classification(
    df: pd.DataFrame,
    enabled: bool,
    profile: dict,
) -> tuple[pd.DataFrame, str | None]:
    if not enabled:
        return df, None

    if not CLASSIFIER_AVAILABLE or classify_dataframe is None:
        return df, "Classifier module is not available."

    try:
        return classify_dataframe(df, profile), None
    except Exception as exc:
        return (
            df,
            "Auto-classification failed, so uploaded workout_type values were used instead. "
            f"Details: {exc}",
        )


def render_css() -> None:
    st.markdown(
        dedent(
            """
            <style>
            .block-container {
                max-width: 1120px;
                padding-top: 1.5rem;
                padding-bottom: 1.5rem;
            }

            .hero-card,
            .report-card,
            .action-card,
            .metric-card,
            .signal-card,
            .section-card,
            .locked-card {
                border: 1px solid #e5e7eb;
                border-radius: 16px;
                background: #ffffff;
                padding: 1rem;
                margin-bottom: 1rem;
            }

            .hero-card {
                background: #f8fafc;
                padding: 1.25rem;
            }

            .action-card {
                background: #ecfdf5;
                border-color: #a7f3d0;
            }

            .locked-card {
                background: #fffbeb;
                border-color: #fcd34d;
            }

            .kicker {
                font-size: 0.76rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: #6b7280;
                font-weight: 750;
                margin-bottom: 0.35rem;
            }

            .hero-title {
                font-size: 1.65rem;
                line-height: 1.22;
                font-weight: 820;
                color: #111827;
                margin-bottom: 0.45rem;
            }

            .section-title {
                font-size: 1.08rem;
                font-weight: 760;
                color: #111827;
                margin-bottom: 0.65rem;
            }

            .body-copy {
                font-size: 1rem;
                line-height: 1.5;
                color: #374151;
                margin-bottom: 0.75rem;
            }

            .small-note {
                font-size: 0.9rem;
                color: #6b7280;
                line-height: 1.45;
            }

            .step-box,
            .why-box,
            .support-box {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 0.82rem 0.9rem;
                margin-bottom: 0.6rem;
                color: #374151;
                line-height: 1.45;
                background: #ffffff;
            }

            .step-box {
                border-color: #a7f3d0;
                background: rgba(255,255,255,0.96);
                font-weight: 650;
                color: #064e3b;
            }

            .support-box {
                background: #f9fafb;
            }

            .metric-label {
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.04em;
                color: #6b7280;
                font-weight: 700;
                margin-bottom: 0.25rem;
            }

            .metric-value {
                font-size: 1rem;
                color: #111827;
                font-weight: 650;
            }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


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

    metrics = report.get("metrics", {})
    render_metric_cards(
        [
            ("Run days", f"{round((metrics.get('days_with_run_last_28', 0) or 0) / 4.0, 1)}/week"),
            ("Weekly volume", f"{round(float(metrics.get('recent_avg_weekly_km', 0) or 0), 1)} km"),
            ("Quality sessions", f"{round(float(metrics.get('quality_runs_last_28', 0) or 0) / 4.0, 1)}/week"),
            ("Long runs", f"{int(metrics.get('long_runs_last_28', 0) or 0)} in 28 days"),
        ]
    )

    st.markdown(
        f"""
        <div class='report-card'>
            <div class='section-title'>Current training overview</div>
            <div class='body-copy'>{html_text(product.get("current_overview"))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    key_signal = product.get("key_signal", {}) or {}
    st.markdown(
        f"""
        <div class='report-card'>
            <div class='section-title'>Key signal</div>
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

    why_points = product.get("why_points", []) or []
    if why_points:
        st.markdown(
            "<div class='report-card'><div class='section-title'>Why this matters</div>",
            unsafe_allow_html=True,
        )

        for point in why_points[:3]:
            st.markdown(
                f"<div class='why-box'>{html_text(point)}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    coach_text = str(product.get("coach_explanation", "") or "").strip()
    if coach_text:
        paragraphs = [p.strip() for p in coach_text.split("\n\n") if p.strip()]

        st.markdown(
            "<div class='report-card'><div class='section-title'>Coach-style explanation</div>",
            unsafe_allow_html=True,
        )

        for para in paragraphs[:2]:
            st.markdown(
                f"<div class='body-copy'>{html_text(para)}</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div class='small-note'>
                RunLab uses deterministic rules to choose the recommendation.
                The AI layer explains the decision in plain English.
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    pdf_bytes = generate_runlab_pdf_bytes(report)

    st.download_button(
        label="Download your personalised RunLab Performance Report (PDF)",
        data=pdf_bytes,
        file_name="runlab_performance_report.pdf",
        mime="application/pdf",
    )

    supporting = product.get("supporting_signals", []) or []
    if supporting:
        with st.expander("Supporting signals", expanded=False):
            for raw_signal in supporting[:3]:
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


def render_next_week_table(report: dict, unlocked: bool = True) -> None:
    if not unlocked:
        return

    rows = report.get("next_week_rows", [])
    if not rows:
        return

    with st.expander("Current vs next week detail", expanded=False):
        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            use_container_width=True,
        )
        st.caption(
            "This stays intentionally simple. RunLab recommends changing the main limiter first and keeping other levers stable."
        )


def render_supporting_analysis(report: dict) -> None:
    supporting_metrics = report.get("supporting_metrics", [])
    if supporting_metrics:
        metric_items = [normalise_label_value(item) for item in supporting_metrics[:4]]
        render_metric_cards(metric_items)

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


def render_report(report: dict, unlocked: bool = True) -> None:
    render_product_report(report, unlocked=unlocked)
    render_next_week_table(report, unlocked=unlocked)

    if unlocked:
        with st.expander("Supporting analysis", expanded=False):
            render_supporting_analysis(report)


def render_sidebar() -> tuple:
    with st.sidebar:
        st.header("Data input")

        uploaded_file = st.file_uploader(
            "Upload running data (CSV)",
            type=["csv"],
        )

        st.markdown(
            "`date, distance_km, duration_min, avg_hr, activity_type, workout_type, title, description`"
        )

        st.markdown("### Auto-classification beta")

        enable_auto = st.checkbox(
            "Enable auto-classification for uploads",
            value=False,
        )

        current_5k_time = st.text_input("Current 5K time", value="17:40").strip()
        current_hm_time = st.text_input("Current HM time (optional)", value="").strip()
        current_marathon_time = st.text_input("Current marathon time (optional)", value="").strip()

        profile = {
            "current_5k_time": current_5k_time,
            "current_hm_time": current_hm_time or None,
            "current_marathon_time": current_marathon_time or None,
        }

        valid_5k_time = parse_time_to_seconds(current_5k_time)

        if CLASSIFIER_AVAILABLE and build_pace_bands and valid_5k_time:
            bands = build_pace_bands(profile)

            pace_df = pd.DataFrame(
                {
                    "Band": [
                        "Very fast",
                        "VO2",
                        "Threshold",
                        "Steady",
                        "Easy",
                        "Recovery",
                    ],
                    "Pace": [
                        f"< {seconds_to_pace_str(bands.get('very_fast_upper'))}",
                        f"{seconds_to_pace_str(bands.get('vo2_lower'))} to {seconds_to_pace_str(bands.get('vo2_upper'))}",
                        f"{seconds_to_pace_str(bands.get('threshold_lower'))} to {seconds_to_pace_str(bands.get('threshold_upper'))}",
                        f"{seconds_to_pace_str(bands.get('steady_lower'))} to {seconds_to_pace_str(bands.get('steady_upper'))}",
                        f"> {seconds_to_pace_str(bands.get('easy_lower'))}",
                        f"> {seconds_to_pace_str(bands.get('recovery_lower'))}",
                    ],
                }
            )

            st.dataframe(
                pace_df,
                hide_index=True,
                use_container_width=True,
            )

    return uploaded_file, enable_auto, profile


def main() -> None:
    st.set_page_config(
        page_title="RunLab Beta",
        page_icon="🏃",
        layout="wide",
    )

    render_css()

    uploaded_file, enable_auto, profile = render_sidebar()

    st.title("RunLab Beta")
    st.caption("Performance-focused training analysis for runners aiming to improve.")

    st.markdown(
        "RunLab turns recent training into one clear decision: "
        "training data → metrics → signals → recommendation."
    )

    mode = st.radio(
        "How would you like to use RunLab?",
        APP_MODES,
        horizontal=True,
    )

    sample_option = st.selectbox(
        "Choose a demo scenario",
        list(DEMO_FILES.keys()),
        disabled=mode != "Try demo scenarios",
    )

    valid_beta_code = False

    if mode == "Upload your own data":
        invite_code = st.text_input(
            "Private beta code",
            placeholder="Enter beta access code",
        ).strip()
        valid_beta_code = invite_code in VALID_BETA_CODES

        if invite_code and valid_beta_code:
            st.success("Beta code accepted. Your full report will unlock after upload.")
        elif invite_code and not valid_beta_code:
            st.warning("Beta code not recognised. You can still preview the headline insight.")

        if uploaded_file is None:
            st.info("Upload a CSV to generate a RunLab Performance Report.")
            return
    else:
        st.caption(DEMO_DESCRIPTIONS[sample_option])

    df_raw = read_input_data(mode, uploaded_file, sample_option)

    if df_raw is None:
        return

    df_input, classification_error = apply_auto_classification(
        df_raw,
        enabled=(mode == "Upload your own data" and enable_auto),
        profile=profile,
    )

    if classification_error:
        st.warning(classification_error)

    try:
        report = generate_runlab_report(df_input)
    except Exception as exc:
        st.error(f"RunLab could not generate a report: {exc}")
        return

    has_paid = False
    unlocked = mode == "Try demo scenarios" or valid_beta_code or has_paid

    if mode == "Upload your own data" and not unlocked:
        st.info(
            "Upload preview mode: your headline insight is shown below. "
            "Request beta access to unlock the full report."
        )
        st.link_button("Join the beta list", BETA_SIGNUP_URL)

    render_report(report, unlocked=unlocked)


if __name__ == "__main__":
    main()
