from __future__ import annotations

from textwrap import dedent

import pandas as pd
import streamlit as st

from src.report_engine import generate_runlab_report
from src.balance import build_balance_comparison_df, build_balance_interpretation
from src.ui_text import build_focus_diagnosis, build_why_this_matters
from src.structure import build_weekly_structure, get_target_weekly_structure
from src.hierarchy import build_training_hierarchy
from src.charts import build_weekly_distance_chart, plot_training_balance_with_counts

try:
    from src.runlab_classifier_v1 import classify_dataframe, build_pace_bands
    CLASSIFIER_AVAILABLE = True
except Exception:
    classify_dataframe = None
    build_pace_bands = None
    CLASSIFIER_AVAILABLE = False


def parse_mmss_to_seconds(time_str: str):
    try:
        parts = time_str.strip().split(":")
        if len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + int(seconds)
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    except Exception:
        return None
    return None


def seconds_to_pace_str(seconds_per_km: float | None) -> str:
    if seconds_per_km is None:
        return "N/A"
    total_seconds = int(round(seconds_per_km))
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}/km"


def dedupe_list(items: list[str], limit: int | None = None) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()

    for item in items:
        if item is None:
            continue
        text = str(item).strip()
        if not text:
            continue
        if text in seen:
            continue
        seen.add(text)
        cleaned.append(text)

    if limit is not None:
        return cleaned[:limit]
    return cleaned


def safe_get(report: dict, key: str, default):
    value = report.get(key, default)
    return default if value is None else value


def render_info_card(label: str, value: str):
    st.markdown(
        dedent(
            f"""
            <div class="mini-card">
                <div class="mini-label">{label}</div>
                <div class="mini-value">{value}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def render_action_steps(
    steps: list[str],
    timeframe: str,
    confidence_label: str = "",
    confidence_note: str = "",
):
    st.markdown("<div class='action-card'>", unsafe_allow_html=True)

    for step in steps[:4]:
        st.markdown(
            f"<div class='action-step'>{step}</div>",
            unsafe_allow_html=True,
        )

    if confidence_label or confidence_note:
        confidence_text = (
            f"<strong>{confidence_label}:</strong> {confidence_note}"
            if confidence_label
            else confidence_note
        )
        st.markdown(
            f"<div class='support-note'>{confidence_text}</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        f"<div class='support-note'><strong>Suggested timeframe:</strong> {timeframe}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


st.set_page_config(page_title="RunLab Prototype", page_icon="🏃", layout="wide")

st.markdown(
    dedent(
        """
        <style>
        .block-container {
            padding-top: 1.7rem;
            padding-bottom: 1.4rem;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
            max-width: 1120px;
        }

        h2 {
            margin-top: 0.6rem;
            margin-bottom: 0.7rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.88rem;
        }

        .scenario-label {
            font-size: 0.95rem;
            font-weight: 600;
            color: #111827;
            margin-bottom: 0.35rem;
        }

        .scenario-help {
            color: #6b7280;
            font-size: 0.9rem;
            margin-top: 0.35rem;
            margin-bottom: 0.75rem;
        }

        .report-card {
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1rem 1rem 0.9rem 1rem;
            margin-bottom: 1rem;
        }

        .hero-card,
        .section-card,
        .action-card,
        .mini-card,
        .metric-shell {
            border-radius: 14px;
            border: 1px solid #e5e7eb;
            background: #ffffff;
        }

        .hero-card,
        .section-card,
        .mini-card,
        .metric-shell {
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .hero-card {
            background: #f9fafb;
            padding: 1.1rem 1.1rem 1rem 1.1rem;
        }

        .action-card {
            background: #ecfdf5;
            border-color: #a7f3d0;
            padding: 0.8rem;
            margin-bottom: 1rem;
        }

        .hero-kicker {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #6b7280;
            margin-bottom: 0.35rem;
            font-weight: 700;
        }

        .hero-headline {
            font-size: 1.45rem;
            font-weight: 700;
            line-height: 1.25;
            color: #111827;
            margin-bottom: 0.45rem;
        }

        .hero-summary {
            font-size: 1rem;
            color: #374151;
            margin-bottom: 0;
            line-height: 1.5;
        }

        .section-title {
            font-size: 1rem;
            font-weight: 700;
            color: #111827;
            margin-bottom: 0.6rem;
        }

        .mini-label {
            color: #6b7280;
            font-size: 0.74rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.3rem;
        }

        .mini-value {
            color: #111827;
            font-size: 0.98rem;
            font-weight: 600;
            line-height: 1.35;
        }

        .action-step {
            background: rgba(255,255,255,0.92);
            border: 1px solid rgba(167,243,208,0.95);
            border-radius: 11px;
            padding: 0.82rem 0.9rem;
            margin-bottom: 0.6rem;
            color: #1f2937;
            font-size: 0.96rem;
            line-height: 1.45;
        }

        .action-step:last-child {
            margin-bottom: 0;
        }

        .why-box {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 11px;
            padding: 0.85rem 0.95rem;
            margin-bottom: 0.65rem;
            color: #374151;
            font-size: 0.95rem;
            line-height: 1.45;
        }

        .support-note {
            font-size: 0.92rem;
            color: #4b5563;
            background: #f3f4f6;
            border-radius: 10px;
            padding: 0.75rem 0.9rem;
            margin-top: 0.25rem;
        }

        .chart-note {
            color: #4b5563;
            font-size: 0.92rem;
            margin-top: 0.45rem;
        }

        .subtle-caption {
            color: #6b7280;
            font-size: 0.9rem;
            margin-top: -0.2rem;
            margin-bottom: 0.8rem;
        }
        </style>
        """
    ),
    unsafe_allow_html=True,
)

file_map = {
    "Baseline runner (mixed stimulus)": "data/sample_runs.csv",
    "Near-optimal but plateauing": "data/near_optimal_but_plateauing.csv",
    "Consistent plateau": "data/consistent_plateau.csv",
    "Inconsistent training": "data/inconsistent_training.csv",
    "High volume, low quality": "data/high_volume_no_quality.csv",
    "Too much intensity": "data/too_much_intensity.csv",
}

descriptions = {
    "Baseline runner (mixed stimulus)": "A typical mixed training pattern with no single dominant issue.",
    "Near-optimal but plateauing": "A strong, balanced pattern that now looks too static and may need a new stimulus.",
    "Consistent plateau": "Steady training with good consistency, but limited progression in key areas.",
    "Inconsistent training": "An irregular training pattern with gaps and unstable weekly rhythm.",
    "High volume, low quality": "Strong mileage and consistency, but not enough structured quality work.",
    "Too much intensity": "A training pattern skewed too heavily toward hard sessions, with limited easy support.",
}

sample_options = list(file_map.keys())
APP_MODES = ["Try demo scenarios", "Upload your own data"]
VALID_BETA_CODES = {"RUNLAB-BETA1"}
BETA_SIGNUP_URL = "https://runlab.ai/#beta"

with st.sidebar:
    st.header("Data input")
    uploaded_file = st.file_uploader("Upload running data (CSV)", type=["csv"])

    st.markdown(
        dedent(
            """
            <div style="background-color:#f5f5f5;padding:10px;border-radius:6px;font-family:monospace;font-size:0.9rem;white-space:normal;">
            date, distance_km, duration_min, avg_hr, activity_type, workout_type, title, description
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    st.markdown("### Auto-classification (beta)")
    enable_auto_classification = st.checkbox(
        "Enable auto-classification for uploads",
        value=False,
        help="Adds calculated session classifications for uploaded CSVs using title, pace, and race-pace anchors.",
    )

    current_5k_time = st.text_input(
        "Current 5K time",
        value="17:40",
        help="Main speed anchor, for example 17:40.",
    ).strip()

    current_hm_time = st.text_input(
        "Current HM time (optional)",
        value="",
        help="Optional threshold anchor. Leave blank to estimate from 5K.",
    ).strip()

    current_marathon_time = st.text_input(
        "Current marathon time (optional)",
        value="",
        help="Optional steady/easy anchor. Leave blank to estimate from HM or 5K.",
    ).strip()

    current_5k_time_sec = parse_mmss_to_seconds(current_5k_time)

    if current_5k_time_sec and CLASSIFIER_AVAILABLE and build_pace_bands is not None:
        user_profile = {
            "current_5k_time": current_5k_time,
            "current_hm_time": current_hm_time or None,
            "current_marathon_time": current_marathon_time or None,
        }
        bands = build_pace_bands(user_profile)

        pace_df = pd.DataFrame(
            {
                "Band": ["Very fast", "VO2", "Threshold", "Steady", "Easy", "Recovery"],
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

        st.markdown("**Approx pace bands**")
        st.dataframe(pace_df, hide_index=True, use_container_width=True)
        st.caption("Very fast and VO2 scale from 5K pace. Threshold scales from HM pace. Steady and easy scale from marathon pace.")
    elif current_5k_time and not CLASSIFIER_AVAILABLE:
        st.caption("Classifier module not available.")
    elif current_5k_time:
        st.caption("Enter times as mm:ss or h:mm:ss, for example 17:40 or 1:19:00.")

sample_option = st.session_state.get("sample_option", sample_options[0])
if sample_option not in sample_options:
    sample_option = sample_options[0]

app_mode = st.session_state.get("app_mode", APP_MODES[0])
if app_mode not in APP_MODES:
    app_mode = APP_MODES[0]

invite_code = st.session_state.get("invite_code", "").strip()
beta_access_granted = invite_code in VALID_BETA_CODES

auto_classified_df = None
auto_classification_error = None
df_raw = None

st.title("RunLab Prototype")
st.caption("Structured training analysis with an AI-assisted coaching explanation layer")

st.markdown(
    """
RunLab analyses recent training, identifies the main limiter, and highlights the clearest next focus,
while keeping the deeper supporting analysis available below.
"""
)

st.caption("RunLab can be explored in demo mode, or used with your own running data in private beta.")

st.markdown("<div class='report-card'>", unsafe_allow_html=True)
st.markdown("<div class='scenario-label'>How would you like to use RunLab?</div>", unsafe_allow_html=True)

selected_mode = st.radio(
    "How would you like to use RunLab?",
    APP_MODES,
    index=APP_MODES.index(app_mode),
    horizontal=True,
    label_visibility="collapsed",
    key="app_mode",
)

if selected_mode == "Try demo scenarios":
    st.markdown(
        "<div class='scenario-help'>These demo scenarios are for illustration only. They show how the analysis behaves across different types of running data.</div>",
        unsafe_allow_html=True,
    )

    selected = st.selectbox(
        "Choose a training scenario",
        sample_options,
        index=sample_options.index(sample_option),
        label_visibility="collapsed",
        key="sample_option",
    )

    st.markdown(f"<div class='scenario-help'>{descriptions[selected]}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if selected != sample_option:
        st.rerun()

    df_raw = pd.read_csv(file_map[selected])

else:
    st.markdown(
        "<div class='scenario-help'>Upload your own running data to generate a personalised report. This feature is currently limited to beta users with an invite code.</div>",
        unsafe_allow_html=True,
    )

    entered_code = st.text_input(
        "Enter beta invite code",
        value=st.session_state.get("invite_code", ""),
        key="invite_code_input",
    ).strip()

    if entered_code != st.session_state.get("invite_code", ""):
        st.session_state["invite_code"] = entered_code
        st.rerun()

    beta_access_granted = entered_code in VALID_BETA_CODES

    if beta_access_granted:
        st.success("Beta access granted. You can now upload your own running data in the sidebar.")
    else:
        st.warning("Beta access is required to upload your own data.")
        st.markdown(f"[Join the beta here]({BETA_SIGNUP_URL})")

    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file is not None and beta_access_granted:
        df_raw = pd.read_csv(uploaded_file)

        if enable_auto_classification and CLASSIFIER_AVAILABLE:
            try:
                user_profile = {
                    "current_5k_time": current_5k_time,
                    "current_hm_time": current_hm_time or None,
                    "current_marathon_time": current_marathon_time or None,
                }
                auto_classified_df = classify_dataframe(df_raw.copy(), user_profile)
                df_raw = auto_classified_df.copy()
            except Exception as exc:
                auto_classification_error = str(exc)

if df_raw is None and selected_mode == "Try demo scenarios":
    st.info("Choose a demo scenario to begin.")
    st.stop()

if df_raw is None and selected_mode == "Upload your own data":
    if beta_access_granted:
        st.info("Upload your running data CSV in the sidebar to begin.")
    else:
        st.info("Enter a valid beta invite code to unlock uploads, or use demo mode to explore RunLab.")
    st.stop()

if selected_mode == "Upload your own data" and enable_auto_classification:
    if auto_classification_error:
        st.warning(f"Auto-classification was skipped: {auto_classification_error}")
    elif auto_classified_df is not None:
        st.success("Auto-classification applied to uploaded data.")

try:
    report = generate_runlab_report(df_raw)
except Exception as exc:
    st.error(f"Data or report error: {exc}")
    st.stop()

df = safe_get(report, "df", pd.DataFrame())
metrics = safe_get(report, "metrics", {})
signals = safe_get(report, "signals", [])
top_signals = safe_get(report, "top_signals", signals[:3] if signals else [])
focus = safe_get(report, "focus", {})
ai_text = safe_get(report, "ai_text", "")
used_ai = safe_get(report, "used_ai", False)

hierarchy = report.get("hierarchy")
if hierarchy is None:
    hierarchy = build_training_hierarchy(metrics, focus)

diagnosis_headline, diagnosis_summary = build_focus_diagnosis(focus, metrics)

why_bullets = dedupe_list(build_why_this_matters(metrics, top_signals, focus), limit=2)
balance_df, total_run_days = build_balance_comparison_df(df, focus)
balance_note = build_balance_interpretation(balance_df, focus, total_run_days)

weekly_structure = build_weekly_structure(metrics)
target_structure = get_target_weekly_structure(focus, total_run_days)

weekly_chart = build_weekly_distance_chart(df)
balance_chart = plot_training_balance_with_counts(balance_df)

# 1. Verdict
st.markdown("## Your current focus")
st.markdown(
    dedent(
        f"""
        <div class="hero-card">
            <div class="hero-kicker">Primary limiter</div>
            <div class="hero-headline">{diagnosis_headline}</div>
            <div class="hero-summary">{diagnosis_summary}</div>
        </div>
        """
    ),
    unsafe_allow_html=True,
)

# 2. Actions
st.markdown("## What to do next")
render_action_steps(
    focus.get("prescription", ["Keep the current pattern stable and reassess after another consistent block."]),
    focus.get("timeframe", "2-4 weeks"),
    focus.get("confidence_label", ""),
    focus.get("confidence_note", ""),
)

# 3. Evidence + fact panel
st.markdown("## Why this matters")
st.markdown("<div class='subtle-caption'>The key evidence behind the recommendation.</div>", unsafe_allow_html=True)

why_col_1, why_col_2 = st.columns([1.25, 0.75])

with why_col_1:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Key reasons</div>", unsafe_allow_html=True)

    if why_bullets:
        for reason in why_bullets:
            st.markdown(f"<div class='why-box'>{reason}</div>", unsafe_allow_html=True)
    else:
        st.write("No additional reasoning available.")

    st.markdown("</div>", unsafe_allow_html=True)

with why_col_2:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>At a glance</div>", unsafe_allow_html=True)

    run_days_per_week = round((metrics.get("days_with_run_last_28", 0) or 0) / 4.0, 1)
    recent_weekly_km = round(metrics.get("recent_avg_weekly_km", 0) or 0, 1)
    target_volume_range = focus.get("target_volume_range")

    render_info_card("Run frequency", f"{run_days_per_week} days/week")
    render_info_card("Weekly volume", f"{recent_weekly_km} km/week")
    if target_volume_range:
        render_info_card("Target volume", f"{target_volume_range[0]}-{target_volume_range[1]} km/week")

    st.markdown("</div>", unsafe_allow_html=True)

# 4. Summary metrics lower in the flow
st.markdown("## Summary metrics")
metrics_row = st.columns(4)
metrics_row[0].metric("28-day distance", f"{metrics.get('total_distance_last_28', 0)} km")
metrics_row[1].metric("Run days (28d)", metrics.get("days_with_run_last_28", 0))
metrics_row[2].metric("Consistency", str(metrics.get("consistency_label", "unknown")).title())
metrics_row[3].metric("Volume trend", str(metrics.get("volume_trend", "unknown")).title())

# 5. Visual validation
st.markdown("## Training pattern")

chart_col_1, chart_col_2 = st.columns(2)

with chart_col_1:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Weekly distance</div>", unsafe_allow_html=True)
    st.pyplot(weekly_chart, use_container_width=True)
    st.markdown(
        "<div class='chart-note'>Weekly volume over the last few weeks.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with chart_col_2:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Current vs ideal training mix</div>", unsafe_allow_html=True)
    st.pyplot(balance_chart, use_container_width=True)
    st.markdown(
        "<div class='chart-note'>Current run-day mix compared with the current target distribution.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# 6. Optional nuance
st.markdown("## Coaching interpretation")
with st.expander("Show AI-assisted explanation", expanded=False):
    if used_ai:
        st.caption("Generated using the AI explanation layer")
    else:
        st.caption("Using fallback explanation because no OpenAI key was available")
    st.write(ai_text)

# 7. Deep dive
st.markdown("## Deep dive")

with st.expander("Training hierarchy", expanded=False):
    primary = hierarchy.get("primary", {})
    secondary = hierarchy.get("secondary", [])
    supportive = hierarchy.get("supportive", [])

    st.markdown("**Primary**")
    st.write(primary.get("label", "N/A"))
    if primary.get("detail"):
        st.caption(primary.get("detail"))

    if secondary:
        st.markdown("**Secondary constraints**")
        for item in secondary:
            st.markdown(f"- **{item.get('label', 'N/A')}**: {item.get('detail', '')}")

    if supportive:
        st.markdown("**Supportive stimuli already in place**")
        for item in supportive:
            st.markdown(f"- **{item.get('label', 'N/A')}**: {item.get('detail', '')}")

with st.expander("All system signals", expanded=False):
    if not signals:
        st.write("No signals available.")
    else:
        for signal in signals:
            st.markdown(
                f"- **{signal.get('title', 'Untitled')}** "
                f"({signal.get('priority', 'unknown')}): {signal.get('detail', '')}"
            )

with st.expander("Weekly structure detail", expanded=False):
    structure_df = pd.DataFrame(
        {
            "Stimulus": ["Threshold", "VO2", "Long run"],
            "Current per week": [
                weekly_structure.get("Threshold", 0.0),
                weekly_structure.get("VO2", 0.0),
                weekly_structure.get("Long run", 0.0),
            ],
            "Target per week": [
                target_structure.get("Threshold", 0.0),
                target_structure.get("VO2", 0.0),
                target_structure.get("Long run", 0.0),
            ],
        }
    )
    st.dataframe(structure_df, hide_index=True, use_container_width=True)

with st.expander("Training balance detail", expanded=False):
    st.dataframe(balance_df, hide_index=True, use_container_width=True)
    st.caption(balance_note)

with st.expander("Key metrics", expanded=False):
    metric_export = {
        "Weeks of data": metrics.get("weeks_of_data"),
        "Progression confidence": metrics.get("progression_confidence"),
        "Run days in last 28 days": metrics.get("days_with_run_last_28"),
        "Recent avg weekly km": metrics.get("recent_avg_weekly_km"),
        "Prior avg weekly km": metrics.get("prior_avg_weekly_km"),
        "Volume trend": metrics.get("volume_trend"),
        "Volume pattern": metrics.get("volume_pattern"),
        "Threshold sessions last 28": metrics.get("threshold_sessions_last_28"),
        "VO2 sessions last 28": metrics.get("vo2_sessions_last_28"),
        "Race sessions last 28": metrics.get("race_sessions_last_28"),
        "Long runs last 28": metrics.get("long_runs_last_28"),
        "Easy runs last 28": metrics.get("easy_runs_last_28"),
        "Quality runs last 28": metrics.get("quality_runs_last_28"),
        "Easy run %": metrics.get("easy_run_pct"),
        "Quality run %": metrics.get("quality_run_pct"),
        "Threshold trend": metrics.get("threshold_trend"),
        "VO2 trend": metrics.get("vo2_trend", metrics.get("interval_trend")),
        "Long run trend": metrics.get("long_run_trend"),
    }

    metrics_df = pd.DataFrame(
        {"Metric": list(metric_export.keys()), "Value": list(metric_export.values())}
    )
    st.dataframe(metrics_df, hide_index=True, use_container_width=True)

with st.expander("Underlying cleaned data", expanded=False):
    st.dataframe(df, use_container_width=True)