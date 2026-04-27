from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pandas as pd
import streamlit as st

from src.charts import build_weekly_distance_chart, plot_training_balance_with_counts
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


def read_input_data(
    mode: str,
    uploaded_file,
    sample_option: str,
) -> pd.DataFrame | None:
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

            .decision-card,
            .section-card,
            .metric-card,
            .action-card {
                border: 1px solid #e5e7eb;
                border-radius: 16px;
                background: #ffffff;
                padding: 1rem;
                margin-bottom: 1rem;
            }

            .decision-card {
                background: #f8fafc;
                padding: 1.15rem;
            }

            .action-card {
                background: #ecfdf5;
                border-color: #a7f3d0;
            }

            .kicker {
                font-size: 0.76rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: #6b7280;
                font-weight: 750;
                margin-bottom: 0.35rem;
            }

            .decision-title {
                font-size: 1.55rem;
                line-height: 1.22;
                font-weight: 800;
                color: #111827;
                margin-bottom: 0.45rem;
            }

            .body-copy {
                font-size: 1rem;
                line-height: 1.5;
                color: #374151;
                margin-bottom: 0.75rem;
            }

            .section-title {
                font-size: 1.05rem;
                font-weight: 760;
                color: #111827;
                margin-bottom: 0.6rem;
            }

            .step-box,
            .support-box,
            .why-box {
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
                font-weight: 600;
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

            .small-note {
                font-size: 0.9rem;
                color: #6b7280;
                line-height: 1.45;
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
                    <div class='metric-label'>{label}</div>
                    <div class='metric-value'>{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_decision_header(report: dict) -> None:
    st.markdown(
        f"""
        <div class='decision-card'>
            <div class='kicker'>Your next training focus</div>
            <div class='decision-title'>{report['diagnosis_title']}</div>
            <div class='body-copy'>{report['diagnosis_summary']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_next_week_plan(report: dict) -> None:
    focus = report["focus"]

    st.markdown(
        "<div class='action-card'><div class='section-title'>What to change this week</div>",
        unsafe_allow_html=True,
    )

    for step in focus.get("prescription", [])[:4]:
        st.markdown(
            f"<div class='step-box'>{step}</div>",
            unsafe_allow_html=True,
        )

    confidence_label = focus.get("confidence_label", "")
    confidence_note = focus.get("confidence_note", "")

    if confidence_label or confidence_note:
        st.markdown(
            f"<div class='support-box'><strong>{confidence_label}:</strong> {confidence_note}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='section-card'><div class='section-title'>Current vs next week</div>",
        unsafe_allow_html=True,
    )

    st.dataframe(
        pd.DataFrame(report.get("next_week_rows", [])),
        hide_index=True,
        use_container_width=True,
    )

    st.markdown(
        """
        <div class='small-note'>
            This is intentionally simple. RunLab recommends changing the main limiter first
            and keeping other levers stable.
        </div></div>
        """,
        unsafe_allow_html=True,
    )


def render_why(report: dict) -> None:
    st.markdown(
        "<div class='section-card'><div class='section-title'>Why this is the right sequence</div>",
        unsafe_allow_html=True,
    )

    for point in report.get("why_points", [])[:3]:
        st.markdown(
            f"<div class='why-box'>{point}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_ai_explanation(report: dict, compact: bool = False) -> None:
    label = "AI-assisted coach reasoning" if report.get("used_ai") else "Coach-style reasoning"

    paragraphs = [
        para.strip()
        for para in str(report.get("ai_text", "")).split("\n\n")
        if para.strip()
    ]

    if compact:
        first_para = (
            paragraphs[0]
            if paragraphs
            else "RunLab uses AI to explain the deterministic training recommendation in plain English."
        )

        st.markdown(
            f"""
            <div class='section-card'>
                <div class='kicker'>AI-assisted explanation</div>
                <div class='body-copy'>{first_para}</div>
                <div class='small-note'>
                    RunLab does not ask AI to choose the recommendation. The deterministic
                    decision engine identifies the limiter first, then the AI layer explains why
                    this approach is preferable to alternatives such as adding more intensity,
                    changing multiple levers at once, or chasing short-term fitness.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"<div class='section-card'><div class='section-title'>{label}</div>",
        unsafe_allow_html=True,
    )

    for para in paragraphs:
        st.markdown(
            f"<div class='body-copy'>{para}</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class='small-note'>
            The recommendation comes from deterministic RunLab logic. The AI layer explains
            the reasoning and contrasts it with less suitable approaches, but it does not
            override the decision.
        </div></div>
        """,
        unsafe_allow_html=True,
    )


def render_supporting_analysis(report: dict) -> None:
    render_metric_cards(report.get("supporting_metrics", []))

    left, right = st.columns([1, 1])

    with left:
        st.markdown(
            "<div class='section-card'><div class='section-title'>Decision hierarchy</div>",
            unsafe_allow_html=True,
        )

        decision = report.get("decision", {})

        st.markdown(
            f"<div class='support-box'><strong>Primary:</strong> {decision.get('primary_focus')}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='support-box'><strong>Secondary:</strong> {decision.get('secondary_focus')}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='support-box'><strong>Avoid:</strong> {decision.get('avoid')}</div>",
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            "<div class='section-card'><div class='section-title'>Weekly structure check</div>",
            unsafe_allow_html=True,
        )

        for gap in report.get("structure_gaps", []):
            st.markdown(
                f"""
                <div class='support-box'>
                    <strong>{gap['label']}:</strong> {gap['status']}<br>
                    {gap['detail']}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.pyplot(build_weekly_distance_chart(report["df"]))

    st.markdown(
        "<div class='section-card'><div class='section-title'>Training balance</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div class='small-note'>{report.get('balance_note', '')}</div>",
        unsafe_allow_html=True,
    )

    st.pyplot(plot_training_balance_with_counts(report["balance_df"]))

    with st.expander("Show detailed threshold / VO2 split"):
        st.dataframe(
            report["detailed_balance_df"],
            hide_index=True,
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Debug view: decision scores, metrics and signals"):
        st.json(report["focus"].get("decision_scores", {}))
        st.json(report["metrics"])
        st.dataframe(
            pd.DataFrame(report.get("signals", [])),
            use_container_width=True,
        )


def render_report(report: dict) -> None:
    render_decision_header(report)
    render_next_week_plan(report)

    render_ai_explanation(report, compact=True)

    with st.expander("Full coaching reasoning", expanded=False):
        render_why(report)
        render_ai_explanation(report)

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

        current_5k_time = st.text_input(
            "Current 5K time",
            value="17:40",
        ).strip()

        current_hm_time = st.text_input(
            "Current HM time (optional)",
            value="",
        ).strip()

        current_marathon_time = st.text_input(
            "Current marathon time (optional)",
            value="",
        ).strip()

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
        page_title="RunLab Prototype",
        page_icon="🏃",
        layout="wide",
    )

    render_css()

    uploaded_file, enable_auto, profile = render_sidebar()

    st.title("RunLab Prototype")
    st.caption("Decision-focused training analysis with an AI-assisted explanation layer")

    st.markdown(
        "RunLab turns recent training into one clear next focus: "
        "training data → metrics → signals → decision."
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

    if mode == "Upload your own data":
        invite_code = st.text_input(
            "Private beta code",
            type="password",
        ).strip()

        if invite_code not in VALID_BETA_CODES:
            st.info(
                "Uploads are currently private beta only. "
                "You can still explore the demo scenarios."
            )
            st.link_button("Join the beta list", BETA_SIGNUP_URL)
            return

        if uploaded_file is None:
            st.info("Upload a CSV to generate a RunLab report.")
            return
    else:
        st.caption(DEMO_DESCRIPTIONS[sample_option])

    df_raw = read_input_data(
        mode,
        uploaded_file,
        sample_option,
    )

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

    render_report(report)


if __name__ == "__main__":
    main()