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

st.set_page_config(
    page_title="RunLab Prototype",
    page_icon="🏃",
    layout="wide",
)

st.markdown("""
<style>
.block-container {
    padding-top: 2.2rem;
    padding-bottom: 1rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}

[data-testid="stMetricValue"] {
    font-size: 1.9rem;
}

[data-testid="stMetricLabel"] {
    font-size: 0.9rem;
}

h1 {
    margin-bottom: 0.2rem;
}

h2, h3 {
    margin-bottom: 0.35rem;
}

.small-muted {
    color: #6b7280;
    font-size: 0.92rem;
}

.panel-note {
    color: #6b7280;
    font-size: 0.88rem;
    margin-top: -0.25rem;
    margin-bottom: 0.75rem;
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

with st.sidebar:
    st.header("Data input")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    use_sample = st.checkbox("Use sample data", value=uploaded_file is None)

    st.markdown("""
<div style="
    background-color: #f5f5f5;
    padding: 10px;
    border-radius: 6px;
    font-family: monospace;
    font-size: 0.9rem;
    white-space: normal;
">
date, distance_km, duration_min, avg_hr, activity_type, workout_type
</div>
""", unsafe_allow_html=True)

sample_options = [
    "Baseline runner (mixed stimulus)",
    "Near-optimal but plateauing",
    "Consistent plateau",
    "Inconsistent training",
    "High volume, low quality",
    "Too much intensity",
]

# Determine chosen sample before running the pipeline
sample_option = st.session_state.get("sample_option", "Baseline runner (mixed stimulus)")
if sample_option not in sample_options:
    sample_option = "Baseline runner (mixed stimulus)"

df_raw = None

if uploaded_file is not None:
    df_raw = pd.read_csv(uploaded_file)
elif use_sample:
    df_raw = pd.read_csv(file_map[sample_option])

if df_raw is None:
    st.title("RunLab Prototype")
    st.caption("Structured training analysis with an AI-assisted coaching explanation layer")
    st.info("Upload a CSV file or tick 'Use sample data' in the sidebar to begin.")
    st.stop()

try:
    df = clean_data(df_raw)
except Exception as exc:
    st.error(f"Data error: {exc}")
    st.stop()

weekly = weekly_summary(df)
metrics = overall_metrics(df, weekly)
signals = derive_signals(metrics)
focus = determine_focus(metrics, signals)
ai_text, used_ai = generate_ai_explanation(metrics, signals, focus)

# Top row: intro + chart
top_left, top_right = st.columns([0.9, 1.1], gap="large")

with top_left:
    st.title("RunLab Prototype")
    st.caption("Structured training analysis with an AI-assisted coaching explanation layer")

    st.markdown("""
RunLab analyses recent training, identifies the main limiter, and highlights the most important next focus, with an AI-assisted coaching summary layered on top of the rule-based engine.

The goal is to support better decision-making for self-coached runners, not replace coaching.
""")

with top_right:
    if use_sample and uploaded_file is None:
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='scenario-label'>Explore training scenarios</div>", unsafe_allow_html=True)

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

        if selected != sample_option:
            st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    st.subheader("Recent training trend")

    fig, ax = plt.subplots(figsize=(6.2, 2.5), dpi=120)

    ax.plot(
        weekly["week_start"],
        weekly["total_distance_km"],
        marker="o",
        linewidth=1.8,
        markersize=4.5,
    )

    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))

    ax.set_title("Weekly distance", fontsize=10, pad=10)
    ax.set_xlabel("Week", fontsize=8, labelpad=4)
    ax.set_ylabel("Distance (km)", fontsize=8, labelpad=4)

    ax.tick_params(axis="x", labelsize=6)
    ax.tick_params(axis="y", labelsize=7)

    plt.setp(ax.get_xticklabels(), rotation=15, ha="right")

    ax.grid(True, alpha=0.2)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    plt.tight_layout()

    st.pyplot(fig, use_container_width=True)

# Full-width metrics strip
st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

metric_row_1 = st.columns(6)
metric_row_1[0].metric("28-day distance", f"{metrics['total_distance_last_28']} km")
metric_row_1[1].metric("Run days (28d)", metrics["days_with_run_last_28"])
metric_row_1[2].metric("Consistency", metrics["consistency_label"].title())
metric_row_1[3].metric("Volume trend", metrics["volume_trend"].title())
metric_row_1[4].metric("Threshold / week", metrics.get("threshold_sessions_per_week", "N/A"))
metric_row_1[5].metric("Quality ratio", f"{int(metrics.get('quality_run_pct', 0) * 100)}%")

metric_row_2 = st.columns(3)
metric_row_2[0].metric(
    "Progression confidence",
    str(metrics.get("progression_confidence", "Unknown")).title()
)
metric_row_2[1].metric("Weeks of data", metrics.get("weeks_of_data", "N/A"))
metric_row_2[2].markdown(
    f"<div class='small-muted' style='padding-top: 0.55rem;'><strong>Volume pattern:</strong> "
    f"{metrics['volume_pattern'].replace('_', ' ').title()} — "
    f"{metrics['volume_pattern_detail']}</div>",
    unsafe_allow_html=True,
)

st.divider()

# Lower section: 3-panel layout
panel1, panel2, panel3 = st.columns([1.0, 1.05, 1.15], gap="large")

with panel1:
    st.subheader("Key signals")
    st.markdown(
        "<div class='panel-note'>Structured signals detected from the recent training pattern.</div>",
        unsafe_allow_html=True,
    )

    visible_signals = signals[:4]
    extra_signals = signals[4:]

    for signal in visible_signals:
        priority_icon = {
            "high": "🔴",
            "medium": "🟠",
            "low": "🟢",
        }.get(signal["priority"], "⚪")
        st.markdown(f"**{priority_icon} {signal['title']}**")
        st.write(signal["detail"])

    if extra_signals:
        with st.expander("Show all signals"):
            for signal in extra_signals:
                priority_icon = {
                    "high": "🔴",
                    "medium": "🟠",
                    "low": "🟢",
                }.get(signal["priority"], "⚪")
                st.markdown(f"**{priority_icon} {signal['title']}**")
                st.write(signal["detail"])

with panel2:
    st.subheader("Recommended next focus")
    st.markdown(
        "<div class='panel-note'>Primary coaching direction based on the structured rule engine.</div>",
        unsafe_allow_html=True,
    )

    st.success(focus["headline"])
    st.write(focus["detail"])
    st.caption(f"Reason: {focus['reason']}")

    if focus.get("supporting_signals"):
        st.caption("Driven by: " + ", ".join(focus["supporting_signals"]))

    if focus.get("timeframe"):
        st.caption(f"Suggested timeframe: {focus['timeframe']}")

    if focus.get("prescription"):
        st.markdown("### 📋 What to do next")
        for step in focus["prescription"]:
            st.write(f"- {step}")

with panel3:
    st.subheader("AI coaching summary")
    st.markdown(
        "<div class='panel-note'>AI-generated explanation built on top of the structured metrics, signals, and focus.</div>",
        unsafe_allow_html=True,
    )

    if used_ai:
        st.caption("🟢 OpenAI active")
    else:
        st.caption("🟠 Fallback mode")

    st.write(ai_text)

st.divider()

st.subheader("Weekly summary")

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

st.dataframe(
    weekly_display,
    use_container_width=True,
)

with st.expander("Debug: metrics / signals / focus"):
    st.write("Metrics")
    st.json(metrics)

    st.write("Signals")
    st.json(signals)

    st.write("Focus")
    st.json(focus)

with st.expander("View cleaned data"):
    st.dataframe(df, use_container_width=True)

with st.expander("Download outputs"):
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