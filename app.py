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


# -------------------------------
# Helpers
# -------------------------------
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


# -------------------------------
# Page config + styles
# -------------------------------
st.set_page_config(page_title="RunLab Prototype", page_icon="🏃", layout="wide")

st.markdown(
    dedent(
        """
        <style>
        .block-container {
            padding-top: 2.0rem;
            padding-bottom: 1.2rem;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
            max-width: 1100px;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.9rem;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.9rem;
        }

        .small-muted {
            color: #6b7280;
            font-size: 0.92rem;
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
            border-radius: 10px;
            padding: 1rem 1rem 0.85rem 1rem;
            margin-bottom: 1rem;
        }

        .hero-card,
        .focus-box,
        .ai-box,
        .signal-card,
        .mini-card {
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid #e5e7eb;
        }

        .hero-card {
            background: #f9fafb;
        }

        .signal-card,
        .mini-card {
            background: #ffffff;
        }

        .focus-box {
            background: #ecfdf5;
            border-color: #a7f3d0;
        }

        .ai-box {
            background: #eff6ff;
            border-color: #bfdbfe;
        }

        .hero-kicker {
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #6b7280;
            margin-bottom: 0.35rem;
        }

        .hero-headline {
            font-size: 1.35rem;
            font-weight: 700;
            line-height: 1.25;
            color: #111827;
            margin-bottom: 0.45rem;
        }

        .hero-summary {
            font-size: 0.98rem;
            color: #374151;
            margin-bottom: 0.9rem;
        }

        .impact-note {
            font-size: 0.92rem;
            color: #374151;
            background: #f3f4f6;
            border-radius: 10px;
            padding: 0.75rem 0.9rem;
            margin-top: 0.8rem;
        }

        .signal-title {
            font-size: 1rem;
            font-weight: 700;
            color: #111827;
            margin-bottom: 0.35rem;
        }

        .signal-detail {
            color: #374151;
            font-size: 0.95rem;
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
            font-size: 0.96rem;
            font-weight: 600;
            line-height: 1.35;
        }

        .balance-note {
            color: #4b5563;
            font-size: 0.92rem;
            margin-top: 0.5rem;
        }
        </style>
        """
    ),
    unsafe_allow_html=True,
)


# -------------------------------
# Demo data config
# -------------------------------
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


# -------------------------------
# Sidebar
# -------------------------------
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
        st.caption("Classifier module not available. Save the updated classifier inside src to show scalable pace bands.")
    elif current_5k_time:
        st.caption("Enter times as mm:ss or h:mm:ss, for example 17:40 or 1:19:00.")

    if enable_auto_classification and not CLASSIFIER_AVAILABLE:
        st.warning("Classifier module not available. Save runlab_classifier_v1.py inside src to use this feature.")


# -------------------------------
# Session state defaults
# -------------------------------
sample_option = st.session_state.get("sample_option", "Baseline runner (mixed stimulus)")
if sample_option not in sample_options:
    sample_option = "Baseline runner (mixed stimulus)"

app_mode = st.session_state.get("app_mode", "Try demo scenarios")
if app_mode not in APP_MODES:
    app_mode = "Try demo scenarios"

invite_code = st.session_state.get("invite_code", "").strip()
beta_access_granted = invite_code in VALID_BETA_CODES

auto_classified_df = None
auto_classification_error = None
df_raw = None


# -------------------------------
# Header + mode card
# -------------------------------
st.title("RunLab Prototype")
st.caption("Structured training analysis with an AI-assisted coaching explanation layer")

st.markdown(
    """
RunLab analyses recent training, identifies the main limiter, and highlights the most important next focus,
with an AI-assisted coaching summary layered on top of the rule-based engine.
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


# -------------------------------
# Guard rails
# -------------------------------
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


# -------------------------------
# Core report generation
# -------------------------------
try:
    report = generate_runlab_report(df_raw)
except Exception as exc:
    st.error(f"Data or report error: {exc}")
    st.stop()

df = report["df"]
metrics = report["metrics"]
top_signals = report["top_signals"]
focus = report["focus"]
ai_text = report["ai_text"]
used_ai = report["used_ai"]
decision = report["decision"]

hierarchy = report.get("hierarchy")
if hierarchy is None:
    hierarchy = build_training_hierarchy(metrics, focus)


# -------------------------------
# Top metrics
# -------------------------------
metric_row = st.columns(4)
metric_row[0].metric("28-day distance", f"{metrics['total_distance_last_28']} km")
metric_row[1].metric("Run days (28d)", metrics["days_with_run_last_28"])
metric_row[2].metric("Consistency", metrics["consistency_label"].title())
metric_row[3].metric("Volume trend", metrics["volume_trend"].title())

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)


# -------------------------------
# Hero section
# -------------------------------
st.markdown("## Your Current Focus")

diagnosis_headline, diagnosis_summary = build_focus_diagnosis(focus, metrics)
why_bullets = build_why_this_matters(metrics, top_signals)

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

hero_col_1, hero_col_2, hero_col_3 = st.columns(3)

with hero_col_1:
    st.markdown(
        dedent(
            f"""
            <div class="mini-card">
                <div class="mini-label">Primary focus</div>
                <div class="mini-value">{decision['primary_focus']}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

with hero_col_2:
    st.markdown(
        dedent(
            f"""
            <div class="mini-card">
                <div class="mini-label">Secondary</div>
                <div class="mini-value">{decision['secondary_focus']}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

with hero_col_3:
    st.markdown(
        dedent(
            f"""
            <div class="mini-card">
                <div class="mini-label">Maintain / Avoid</div>
                <div class="mini-value">Maintain: {decision['maintain']}<br>Avoid: {decision['avoid']}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

st.markdown(
    dedent(
        """
        <div class="impact-note">
            <strong>If unchanged:</strong> progress is likely to remain limited.<br>
            <strong>If addressed:</strong> this should give the training pattern a clearer platform for improvement.
        </div>
        """
    ),
    unsafe_allow_html=True,
)

st.caption(
    f"Based on the last {metrics.get('weeks_of_data', 'N/A')} weeks of training. "
    f"Progression confidence: {str(metrics.get('progression_confidence', 'Unknown')).title()}."
)

st.divider()


# -------------------------------
# Why this matters
# -------------------------------
st.markdown("## Why this matters")
for idx, bullet in enumerate(why_bullets, start=1):
    st.markdown(
        dedent(
            f"""
            <div class="signal-card">
                <div class="signal-title">Signal {idx}</div>
                <div class="signal-detail">{bullet}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

st.divider()


# -------------------------------
# What to do next
# -------------------------------
st.markdown("## What to do next")
st.markdown(
    dedent(
        f"""
        <div class="focus-box">
            <div style="font-size: 1.1rem; font-weight: 700; color: #065f46; margin-bottom: 0.5rem;">Recommended next focus</div>
            <div style="color: #111827; margin-bottom: 0.5rem; font-weight: 600;">{focus['headline']}</div>
            <div style="color: #374151; margin-bottom: 0.85rem;">{focus['detail']}</div>
            <div style="font-size: 0.9rem; color: #374151;"><strong>Expected impact:</strong> noticeable within {focus.get('timeframe', 'N/A')} if applied consistently</div>
        </div>
        """
    ),
    unsafe_allow_html=True,
)

if focus.get("prescription"):
    for step in focus["prescription"]:
        st.markdown(f"- {step}")

if focus.get("supporting_signals"):
    st.caption("Driven by: " + ", ".join(focus["supporting_signals"]))

st.divider()


# -------------------------------
# AI explanation
# -------------------------------
st.markdown("## What this means")
st.markdown(
    dedent(
        f"""
        <div class="ai-box">
            <div style="font-size: 1.05rem; font-weight: 700; color: #1d4ed8; margin-bottom: 0.5rem;">What this means</div>
            <div style="font-size: 0.88rem; color: #6b7280; margin-bottom: 0.75rem;">{'OpenAI active' if used_ai else 'Fallback mode'}</div>
            <div style="font-size: 0.88rem; color: #6b7280; margin-bottom: 0.75rem;">AI-assisted explanation of the rule-based recommendation</div>
            <div style="color: #111827;">{ai_text}</div>
        </div>
        """
    ),
    unsafe_allow_html=True,
)

st.divider()


# -------------------------------
# Training overview
# -------------------------------
st.markdown("## Training overview")
fig_overview = build_weekly_distance_chart(df)
st.pyplot(fig_overview, use_container_width=True)

st.divider()


# -------------------------------
# Supporting metrics
# -------------------------------
st.markdown("## Supporting metrics")
metric_row_2 = st.columns(4)
metric_row_2[0].metric("Threshold / week", metrics.get("threshold_sessions_per_week", "N/A"))
metric_row_2[1].metric("Quality ratio", f"{int(metrics.get('quality_run_pct', 0) * 100)}%")
metric_row_2[2].metric("Weeks of data", metrics.get("weeks_of_data", "N/A"))
metric_row_2[3].metric("Progression confidence", str(metrics.get("progression_confidence", "Unknown")).title())

st.markdown(
    f"<div class='small-muted'><strong>Volume pattern:</strong> {str(metrics['volume_pattern']).replace('_', ' ').title()} — {metrics['volume_pattern_detail']}</div>",
    unsafe_allow_html=True,
)

st.markdown("### Weekly structure")

current_struct = build_weekly_structure(metrics)
target_struct = get_target_weekly_structure(focus)

ws_col_1, ws_col_2, ws_col_3 = st.columns(3)
for i, label in enumerate(["Threshold", "VO2", "Long run"]):
    current_val = current_struct[label]
    target_val = target_struct[label]
    delta_val = round(current_val - target_val, 2)
    [ws_col_1, ws_col_2, ws_col_3][i].metric(
        f"{label} / week",
        f"{current_val}",
        f"{delta_val:+} vs target",
    )

st.caption("Target structure is framed as 2–3 key sessions per week, including the long run.")

st.markdown("### Training balance")
balance_df, total_run_days = build_balance_comparison_df(df, focus)

balance_chart_df = balance_df.copy()
balance_chart_df["ideal_pct"] = balance_chart_df["Ideal days"].apply(
    lambda x: round((x / total_run_days) * 100, 1) if total_run_days else 0.0
)

fig_balance = plot_training_balance_with_counts(balance_chart_df)
st.pyplot(fig_balance, use_container_width=True)

display_df = balance_df.copy()
display_df["Ideal %"] = balance_chart_df["ideal_pct"].map(lambda x: f"{x:.1f}%")
display_df["Current %"] = display_df["Current %"].map(lambda x: f"{x:.1f}%")
display_df["Gap"] = display_df["Gap"].map(lambda x: f"{x:+}")
st.dataframe(display_df, hide_index=True, use_container_width=True)

st.markdown(
    f"<div class='balance-note'>{build_balance_interpretation(balance_df, focus, total_run_days)}</div>",
    unsafe_allow_html=True,
)

st.caption("The current mix is based on distinct run days, not raw session count. The ideal mix is a heuristic target based on the current recommendation.")

st.divider()


# -------------------------------
# Expanders
# -------------------------------
with st.expander("View training hierarchy", expanded=False):
    st.markdown(f"**Primary**: {hierarchy['primary']['label']}")
    st.write(hierarchy["primary"]["detail"])

    if hierarchy["secondary"]:
        st.markdown("**Secondary constraints**")
        for item in hierarchy["secondary"]:
            st.markdown(f"- **{item['label']}**: {item['detail']}")

    if hierarchy["supportive"]:
        st.markdown("**Supportive stimuli**")
        for item in hierarchy["supportive"]:
            st.markdown(f"- **{item['label']}**: {item['detail']}")

with st.expander("View detailed metrics", expanded=False):
    metrics_df = pd.DataFrame([{"Metric": key, "Value": value} for key, value in metrics.items()])
    st.dataframe(metrics_df, hide_index=True, use_container_width=True)

if selected_mode == "Upload your own data" and auto_classified_df is not None:
    with st.expander("View classified uploaded data", expanded=False):
        preview_cols = [
            col for col in [
                "date",
                "title",
                "distance_km",
                "duration_min",
                "pace_min_per_km",
                "workout_type",
                "sub_type",
                "pace_band",
                "classification_notes",
            ]
            if col in auto_classified_df.columns
        ]
        if preview_cols:
            st.dataframe(auto_classified_df[preview_cols], use_container_width=True)
        else:
            st.dataframe(auto_classified_df, use_container_width=True)

with st.expander("View cleaned training data", expanded=False):
    st.dataframe(df, use_container_width=True)