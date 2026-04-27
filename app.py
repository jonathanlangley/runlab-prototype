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


def apply_auto_classification(df: pd.DataFrame, enabled: bool, profile: dict) -> tuple[pd.DataFrame, str | None]:
    if not enabled:
        return df, None
    if not CLASSIFIER_AVAILABLE or classify_dataframe is None:
        return df, "Classifier module is not available."
    try:
        return classify_dataframe(df, profile), None
    except Exception as exc:
        return df, f"Auto-classification failed, so the uploaded workout_type values were used instead. Details: {exc}"


def render_css() -> None:
    st.markdown(
        dedent(
            """
            <style>
            .block-container {max-width: 1120px; padding-top: 1.6rem; padding-bottom: 1.5rem;}
            .hero-card, .section-card, .metric-card, .action-card {border: 1px solid #e5e7eb; border-radius: 14px; background: #ffffff; padding: 1rem; margin-bottom: 1rem;}
            .hero-card {background: #f9fafb;}
            .action-card {background: #ecfdf5; border-color: #a7f3d0;}
            .kicker {font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; color: #6b7280; font-weight: 700; margin-bottom: 0.35rem;}
            .headline {font-size: 1.45rem; line-height: 1.25; font-weight: 750; color: #111827; margin-bottom: 0.45rem;}
            .body-copy {font-size: 1rem; line-height: 1.5; color: #374151;}
            .section-title {font-size: 1.05rem; font-weight: 750; color: #111827; margin-bottom: 0.55rem;}
            .why-box, .step-box, .support-box {border: 1px solid #e5e7eb; border-radius: 11px; padding: 0.82rem 0.9rem; margin-bottom: 0.6rem; color: #374151; line-height: 1.45; background: #ffffff;}
            .step-box {border-color: #a7f3d0; background: rgba(255,255,255,0.95);}
            .support-box {background: #f9fafb;}
            .metric-label {font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; color: #6b7280; font-weight: 700; margin-bottom: 0.25rem;}
            .metric-value {font-size: 1rem; color: #111827; font-weight: 650;}
            .small-note {font-size: 0.9rem; color: #6b7280; line-height: 1.45;}
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def card(title: str, body: str, kicker: str | None = None) -> None:
    kicker_html = f"<div class='kicker'>{kicker}</div>" if kicker else ""
    st.markdown(
        f"<div class='hero-card'>{kicker_html}<div class='headline'>{title}</div><div class='body-copy'>{body}</div></div>",
        unsafe_allow_html=True,
    )


def render_metric_cards(items: list[tuple[str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        with col:
            st.markdown(
                f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div></div>",
                unsafe_allow_html=True,
            )


def render_action_steps(focus: dict) -> None:
    st.markdown("<div class='action-card'><div class='section-title'>What to do next</div>", unsafe_allow_html=True)
    for step in focus.get("prescription", [])[:4]:
        st.markdown(f"<div class='step-box'>{step}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='support-box'><strong>{focus.get('confidence_label', 'Confidence')}:</strong> {focus.get('confidence_note', '')}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='support-box'><strong>Suggested timeframe:</strong> {focus.get('timeframe', '2-4 weeks')}</div></div>",
        unsafe_allow_html=True,
    )


def render_why(points: list[str]) -> None:
    st.markdown("<div class='section-card'><div class='section-title'>Why it matters</div>", unsafe_allow_html=True)
    for point in points[:3]:
        st.markdown(f"<div class='why-box'>{point}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_structure(report: dict) -> None:
    st.markdown("<div class='section-card'><div class='section-title'>Weekly structure check</div>", unsafe_allow_html=True)
    for gap in report.get("structure_gaps", []):
        st.markdown(
            f"<div class='support-box'><strong>{gap['label']}:</strong> {gap['status']}<br>{gap['detail']}</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_ai_explanation(report: dict) -> None:
    label = "AI-assisted explanation" if report.get("used_ai") else "Coach-style explanation"
    st.markdown(f"<div class='section-card'><div class='section-title'>{label}</div>", unsafe_allow_html=True)
    for para in str(report.get("ai_text", "")).split("\n\n"):
        if para.strip():
            st.markdown(f"<div class='body-copy'>{para.strip()}</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-note'>The recommendation above is generated by deterministic RunLab logic. The explanation layer adds context, but does not override the decision engine.</div></div>", unsafe_allow_html=True)


def render_report(report: dict) -> None:
    focus = report["focus"]
    metrics = report["metrics"]

    card(report["diagnosis_title"], report["diagnosis_summary"], "Summary")
    render_metric_cards(report.get("supporting_metrics", []))

    left, right = st.columns([1.05, 0.95])
    with left:
        render_why(report.get("why_points", []))
        render_action_steps(focus)
    with right:
        st.markdown("<div class='section-card'><div class='section-title'>Decision hierarchy</div>", unsafe_allow_html=True)
        decision = report.get("decision", {})
        st.markdown(f"<div class='support-box'><strong>Primary focus:</strong> {decision.get('primary_focus')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='support-box'><strong>Secondary:</strong> {decision.get('secondary_focus')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='support-box'><strong>Avoid:</strong> {decision.get('avoid')}</div></div>", unsafe_allow_html=True)
        render_structure(report)

    st.subheader("Supporting analysis")
    st.pyplot(build_weekly_distance_chart(report["df"]))

    st.markdown("<div class='section-card'><div class='section-title'>Training balance</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='small-note'>{report.get('balance_note', '')}</div>", unsafe_allow_html=True)
    st.pyplot(plot_training_balance_with_counts(report["balance_df"]))
    with st.expander("Show detailed threshold / VO2 split"):
        st.dataframe(report["detailed_balance_df"], hide_index=True, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    render_ai_explanation(report)

    with st.expander("Debug view: metrics and signals"):
        st.json(metrics)
        st.dataframe(pd.DataFrame(report.get("signals", [])), use_container_width=True)


def render_sidebar() -> tuple:
    with st.sidebar:
        st.header("Data input")
        uploaded_file = st.file_uploader("Upload running data (CSV)", type=["csv"])
        st.markdown(
            "`date, distance_km, duration_min, avg_hr, activity_type, workout_type, title, description`"
        )

        st.markdown("### Auto-classification beta")
        enable_auto = st.checkbox("Enable auto-classification for uploads", value=False)
        current_5k_time = st.text_input("Current 5K time", value="17:40").strip()
        current_hm_time = st.text_input("Current HM time (optional)", value="").strip()
        current_marathon_time = st.text_input("Current marathon time (optional)", value="").strip()

        profile = {
            "current_5k_time": current_5k_time,
            "current_hm_time": current_hm_time or None,
            "current_marathon_time": current_marathon_time or None,
        }

        if CLASSIFIER_AVAILABLE and build_pace_bands and parse_time_to_seconds(current_5k_time):
            bands = build_pace_bands(profile)
            pace_df = pd.DataFrame({
                "Band": ["Very fast", "VO2", "Threshold", "Steady", "Easy", "Recovery"],
                "Pace": [
                    f"< {seconds_to_pace_str(bands.get('very_fast_upper'))}",
                    f"{seconds_to_pace_str(bands.get('vo2_lower'))} to {seconds_to_pace_str(bands.get('vo2_upper'))}",
                    f"{seconds_to_pace_str(bands.get('threshold_lower'))} to {seconds_to_pace_str(bands.get('threshold_upper'))}",
                    f"{seconds_to_pace_str(bands.get('steady_lower'))} to {seconds_to_pace_str(bands.get('steady_upper'))}",
                    f"> {seconds_to_pace_str(bands.get('easy_lower'))}",
                    f"> {seconds_to_pace_str(bands.get('recovery_lower'))}",
                ],
            })
            st.dataframe(pace_df, hide_index=True, use_container_width=True)

    return uploaded_file, enable_auto, profile


def main() -> None:
    st.set_page_config(page_title="RunLab Prototype", page_icon="🏃", layout="wide")
    render_css()

    uploaded_file, enable_auto, profile = render_sidebar()

    st.title("RunLab Prototype")
    st.caption("Decision-focused training analysis with an AI-assisted explanation layer")
    st.markdown("RunLab turns recent training into a clear next focus: training data → metrics → signals → decision.")

    mode = st.radio("How would you like to use RunLab?", APP_MODES, horizontal=True)
    sample_option = st.selectbox("Choose a demo scenario", list(DEMO_FILES.keys()), disabled=mode != "Try demo scenarios")

    if mode == "Upload your own data":
        invite_code = st.text_input("Private beta code", type="password").strip()
        if invite_code not in VALID_BETA_CODES:
            st.info("Uploads are currently private beta only. You can still explore the demo scenarios.")
            st.link_button("Join the beta list", BETA_SIGNUP_URL)
            return
        if uploaded_file is None:
            st.info("Upload a CSV to generate a RunLab report.")
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

    render_report(report)


if __name__ == "__main__":
    main()
