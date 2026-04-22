from __future__ import annotations
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from src.data_loader import clean_data
from src.metrics import weekly_summary, overall_metrics
from src.signals import derive_signals
from src.focus import determine_focus
from src.ai_explainer import generate_ai_explanation

try:
    from src.runlab_classifier_v1 import classify_dataframe, build_pace_bands
    CLASSIFIER_AVAILABLE = True
except Exception:
    classify_dataframe = None
    build_pace_bands = None
    CLASSIFIER_AVAILABLE = False

# -------------------------------
# Training hierarchy helper
# -------------------------------

def build_training_hierarchy(metrics: dict, focus: dict) -> dict:
    primary = {
        "label": focus.get("headline", "Primary limiter"),
        "detail": focus.get("detail", ""),
    }

    secondary = []
    supportive = []

    threshold_count = metrics.get("threshold_sessions_last_28", 0)
    interval_count = metrics.get("interval_sessions_last_28", 0)
    long_run_count = metrics.get("long_runs_last_28", 0)

    # Threshold
    if threshold_count > 0:
        if threshold_count <= 2:
            secondary.append({
                "label": "Threshold work",
                "detail": f"Present but limited, with {threshold_count} session(s) in the last 4 weeks.",
            })
        else:
            supportive.append({
                "label": "Threshold work",
                "detail": f"Present, with {threshold_count} session(s) in the last 4 weeks.",
            })
    else:
        secondary.append({
            "label": "Threshold work",
            "detail": "Absent in the last 4 weeks.",
        })

    # Long runs
    if long_run_count > 0:
        if long_run_count <= 2:
            secondary.append({
                "label": "Long run stimulus",
                "detail": f"Present but inconsistent, with {long_run_count} long run(s) in the last 4 weeks.",
            })
        else:
            supportive.append({
                "label": "Long run stimulus",
                "detail": f"Present, with {long_run_count} long run(s) in the last 4 weeks.",
            })
    else:
        secondary.append({
            "label": "Long run stimulus",
            "detail": "Absent in the last 4 weeks.",
        })

    # VO2
    if interval_count > 0:
        supportive.append({
            "label": "VO2 / interval work",
            "detail": f"Present, with {interval_count} session(s) in the last 4 weeks.",
        })

    return {
        "primary": primary,
        "secondary": secondary,
        "supportive": supportive,
    }

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


st.set_page_config(
    page_title="RunLab Prototype",
    page_icon="🏃",
    layout="wide",
)

st.markdown("""
<style>
.block-container {
    padding-top: 2.2rem;
    padding-bottom: 1.25rem;
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

h1 {
    margin-bottom: 0.15rem;
}

h2, h3 {
    margin-bottom: 0.35rem;
}

.small-muted {
    color: #6b7280;
    font-size: 0.92rem;
}

.section-note {
    color: #6b7280;
    font-size: 0.9rem;
    margin-top: -0.2rem;
    margin-bottom: 0.9rem;
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

.report-kicker {
    color: #6b7280;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.35rem;
}

.limiter-box {
    background-color: #f3f4f6;
    border-left: 4px solid #111827;
    padding: 0.85rem 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}

.focus-box {
    background-color: #ecfdf5;
    border: 1px solid #a7f3d0;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.ai-box {
    background-color: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

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

sample_options = [
    "Baseline runner (mixed stimulus)",
    "Near-optimal but plateauing",
    "Consistent plateau",
    "Inconsistent training",
    "High volume, low quality",
    "Too much intensity",
]

APP_MODES = ["Try demo scenarios", "Upload your own data"]
VALID_BETA_CODES = {"RUNLAB-BETA1"}  # replace with your real code(s)
BETA_SIGNUP_URL = "https://runlab.ai/#beta"  # replace with your real Formspree/landing-page beta link

with st.sidebar:
    st.header("Data input")
    uploaded_file = st.file_uploader("Upload running data (CSV)", type=["csv"])

    st.markdown("""
<div style="
    background-color: #f5f5f5;
    padding: 10px;
    border-radius: 6px;
    font-family: monospace;
    font-size: 0.9rem;
    white-space: normal;
">
date, distance_km, duration_min, avg_hr, activity_type, workout_type, title, description
</div>
""", unsafe_allow_html=True)

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
    current_hm_time_sec = parse_mmss_to_seconds(current_hm_time) if current_hm_time else None
    current_marathon_time_sec = parse_mmss_to_seconds(current_marathon_time) if current_marathon_time else None

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
        st.dataframe(
            pace_df,
            hide_index=True,
            use_container_width=True,
        )
        st.caption("Very fast and VO2 scale from 5K pace. Threshold scales from HM pace. Steady and easy scale from marathon pace.")
    elif current_5k_time and not CLASSIFIER_AVAILABLE:
        st.caption("Classifier module not available. Save the updated classifier inside src to show scalable pace bands.")
    elif current_5k_time:
        st.caption("Enter times as mm:ss or h:mm:ss, for example 17:40 or 1:19:00.")

    if enable_auto_classification and not CLASSIFIER_AVAILABLE:
        st.warning("Classifier module not available. Save runlab_classifier_v1.py inside src to use this feature.")

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

if app_mode == "Upload your own data":
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
else:
    df_raw = pd.read_csv(file_map[sample_option])

st.title("RunLab Prototype")
st.caption("Structured training analysis with an AI-assisted coaching explanation layer")

st.markdown("""
RunLab analyses recent training, identifies the main limiter, and highlights the most important next focus, with an AI-assisted coaching summary layered on top of the rule-based engine.
""")

st.caption("RunLab can be explored in demo mode, or used with your own running data in private beta.")

st.markdown("<div class='report-card'>", unsafe_allow_html=True)
st.markdown(
    "<div class='scenario-label'>How would you like to use RunLab?</div>",
    unsafe_allow_html=True,
)

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

    st.markdown(
        f"<div class='scenario-help'>{descriptions[selected]}</div>",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if selected != sample_option:
        st.rerun()

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

if df_raw is None and app_mode == "Try demo scenarios":
    st.info("Choose a demo scenario to begin.")
    st.stop()

if df_raw is None and app_mode == "Upload your own data":
    if beta_access_granted:
        st.info("Upload your running data CSV in the sidebar to begin.")
    else:
        st.info("Enter a valid beta invite code to unlock uploads, or use demo mode to explore RunLab.")
    st.stop()

try:
    df = clean_data(df_raw)
except Exception as exc:
    st.error(f"Data error: {exc}")
    st.stop()

if app_mode == "Upload your own data" and enable_auto_classification:
    if auto_classification_error:
        st.warning(f"Auto-classification was skipped: {auto_classification_error}")
    elif auto_classified_df is not None:
        st.success("Auto-classification applied to uploaded data.")

weekly = weekly_summary(df)
metrics = overall_metrics(df, weekly)
signals = derive_signals(metrics)
focus = determine_focus(metrics, signals)
ai_text, used_ai = generate_ai_explanation(metrics, signals, focus)
hierarchy = build_training_hierarchy(metrics, focus)

metric_row = st.columns(4)
metric_row[0].metric("28-day distance", f"{metrics['total_distance_last_28']} km")
metric_row[1].metric("Run days (28d)", metrics["days_with_run_last_28"])
metric_row[2].metric("Consistency", metrics["consistency_label"].title())
metric_row[3].metric("Volume trend", metrics["volume_trend"].title())

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

st.markdown('<div class="report-kicker">Primary limiter</div>', unsafe_allow_html=True)
st.markdown(
    f"""
<div class="limiter-box">
    <div style="font-size: 1.35rem; font-weight: 700; color: #111827;">{focus["headline"]}</div>
    <div style="margin-top: 0.35rem; color: #374151;">{focus["detail"]}</div>
</div>
""",
    unsafe_allow_html=True,
)

st.caption(
    f"Based on the last {metrics.get('weeks_of_data', 'N/A')} weeks of training. "
    f"Progression confidence: {str(metrics.get('progression_confidence', 'Unknown')).title()}."
)

st.divider()

st.markdown("## Diagnosis")
st.markdown(
    '<div class="section-note">The current training pattern ranked by what matters most.</div>',
    unsafe_allow_html=True,
)

st.markdown("### Primary limiter")
st.markdown(f"**{hierarchy['primary']['label']}**")
st.write(hierarchy["primary"]["detail"])

if hierarchy["secondary"]:
    st.markdown("### Secondary constraints")
    for item in hierarchy["secondary"]:
        st.markdown(f"**{item['label']}**")
        st.write(item["detail"])

if hierarchy["supportive"]:
    st.markdown("### Supportive stimuli")
    for item in hierarchy["supportive"]:
        st.markdown(f"**{item['label']}**")
        st.write(item["detail"])

st.divider()

st.markdown("## What to do next")
st.markdown(
    f"""
<div class="focus-box">
    <div style="font-size: 1.1rem; font-weight: 700; color: #065f46; margin-bottom: 0.5rem;">
        Recommended next focus
    </div>
    <div style="color: #111827; margin-bottom: 0.5rem;">{focus["headline"]}</div>
    <div style="color: #374151; margin-bottom: 0.85rem;">{focus["detail"]}</div>
    <div style="font-size: 0.9rem; color: #374151;"><strong>Suggested timeframe:</strong> {focus.get("timeframe", "N/A")}</div>
</div>
""",
    unsafe_allow_html=True,
)

if focus.get("prescription"):
    for step in focus["prescription"]:
        st.markdown(f"- {step}")

if focus.get("supporting_signals"):
    st.caption("Driven by: " + ", ".join(focus["supporting_signals"]))

st.divider()

st.markdown("## Why this recommendation")
st.markdown(
    f"""
<div class="ai-box">
    <div style="font-size: 1.05rem; font-weight: 700; color: #1d4ed8; margin-bottom: 0.5rem;">
        AI coaching summary
    </div>
    <div style="font-size: 0.88rem; color: #6b7280; margin-bottom: 0.75rem;">
        {"OpenAI active" if used_ai else "Fallback mode"}
    </div>
    <div style="color: #111827;">{ai_text}</div>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

st.markdown("## Supporting metrics")
metric_row_2 = st.columns(4)
metric_row_2[0].metric("Threshold / week", metrics.get("threshold_sessions_per_week", "N/A"))
metric_row_2[1].metric("Quality ratio", f"{int(metrics.get('quality_run_pct', 0) * 100)}%")
metric_row_2[2].metric("Weeks of data", metrics.get("weeks_of_data", "N/A"))
metric_row_2[3].metric(
    "Progression confidence",
    str(metrics.get("progression_confidence", "Unknown")).title()
)

st.markdown(
    f"<div class='small-muted'><strong>Volume pattern:</strong> "
    f"{metrics['volume_pattern'].replace('_', ' ').title()} — "
    f"{metrics['volume_pattern_detail']}</div>",
    unsafe_allow_html=True,
)

st.divider()

with st.expander("View training chart", expanded=False):
    fig, ax = plt.subplots(figsize=(8, 3.2), dpi=120)

    ax.plot(
        weekly["week_start"],
        weekly["total_distance_km"],
        marker="o",
        linewidth=1.8,
        markersize=4.5,
    )

    if len(weekly) > 8:
        xticks = weekly["week_start"][::2]
    else:
        xticks = weekly["week_start"]

    ax.set_xticks(xticks)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("w/c %d %b"))

    latest_week = weekly.iloc[-1]
    ax.scatter(
        latest_week["week_start"],
        latest_week["total_distance_km"],
        s=55,
        zorder=5,
    )
    ax.annotate(
        "Latest",
        xy=(latest_week["week_start"], latest_week["total_distance_km"]),
        xytext=(0, 10),
        textcoords="offset points",
        ha="center",
        fontsize=8,
    )

    ax.set_title("Weekly distance", fontsize=10, pad=10)
    ax.set_xlabel("Week", fontsize=8, labelpad=4)
    ax.set_ylabel("Distance (km)", fontsize=8, labelpad=4)

    ax.tick_params(axis="x", labelsize=7)
    ax.tick_params(axis="y", labelsize=8)

    plt.setp(ax.get_xticklabels(), rotation=15, ha="right")

    ax.grid(True, alpha=0.2)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

with st.expander("View weekly summary", expanded=False):
    weekly_display = weekly.copy()
    weekly_display = weekly_display.rename(columns={
        "week_start": "Week",
        "total_distance_km": "Distance (km)",
        "total_duration_min": "Duration (min)",
        "run_count": "Runs",
        "avg_hr": "Avg HR",
        "threshold_sessions": "Threshold",
        "interval_sessions": "Intervals",
        "long_runs": "Long runs",
        "easy_runs": "Easy runs",
    })

    weekly_display["Distance (km)"] = weekly_display["Distance (km)"].round(1)
    weekly_display["Duration (min)"] = weekly_display["Duration (min)"].round(1)
    weekly_display["Avg HR"] = weekly_display["Avg HR"].round(1)

    st.dataframe(weekly_display, use_container_width=True)

if app_mode == "Upload your own data" and auto_classified_df is not None:
    with st.expander("View auto-classified upload", expanded=False):
        st.dataframe(auto_classified_df, use_container_width=True)

        if "confidence" in auto_classified_df.columns:
            low_conf = auto_classified_df[auto_classified_df["confidence"] == "low"]
            st.write(f"Low confidence rows: {len(low_conf)}")
            if not low_conf.empty:
                st.dataframe(low_conf, use_container_width=True)

with st.expander("View cleaned data", expanded=False):
    st.dataframe(df, use_container_width=True)

with st.expander("Debug: metrics / signals / focus", expanded=False):
    st.write("Metrics")
    st.json(metrics)

    st.write("Signals")
    st.json(signals)

    st.write("Focus")
    st.json(focus)

with st.expander("Download outputs", expanded=False):
    cleaned_csv = df.to_csv(index=False).encode("utf-8")
    weekly_csv = weekly.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download cleaned data",
        data=cleaned_csv,
        file_name="cleaned_runs.csv",
        mime="text/csv",
    )

    st.download_button(
        "Download weekly summary",
        data=weekly_csv,
        file_name="weekly_summary.csv",
        mime="text/csv",
    )

    if auto_classified_df is not None:
        classified_csv = auto_classified_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download auto-classified upload",
            data=classified_csv,
            file_name="auto_classified_runs.csv",
            mime="text/csv",
        )
