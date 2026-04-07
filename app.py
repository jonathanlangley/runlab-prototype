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
    padding-top: 1rem;
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
</style>
""", unsafe_allow_html=True)

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

df_raw = None

if uploaded_file is not None:
    df_raw = pd.read_csv(uploaded_file)
elif use_sample:
    df_raw = pd.read_csv("data/sample_runs.csv")

if df_raw is None:
    st.title("RunLab Prototype")
    st.caption("Structured training insights with a lightweight AI explanation layer")
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

# Top section: intro + metrics on left, chart on right
top_left, top_right = st.columns([0.9, 1.1], gap="large")

with top_left:
    st.title("RunLab Prototype")
    st.caption("Structured training insights with a lightweight AI explanation layer")

    st.markdown("""
This prototype shows how training data can be turned into:
- clear weekly metrics
- structured training signals
- a primary training focus
- AI-assisted explanation

The goal is to support better decision-making, not replace coaching.
""")

    metric_row_1 = st.columns(2)
    metric_row_1[0].metric("28-day distance", f"{metrics['total_distance_last_28']} km")
    metric_row_1[1].metric("Run days (28d)", metrics["days_with_run_last_28"])

    metric_row_2 = st.columns(2)
    metric_row_2[0].metric("Consistency", metrics["consistency_label"].title())
    metric_row_2[1].metric("Volume trend", metrics["volume_trend"].title())

    st.markdown(
        f"<div class='small-muted'><strong>Volume pattern:</strong> "
        f"{metrics['volume_pattern'].replace('_', ' ').title()} — "
        f"{metrics['volume_pattern_detail']}</div>",
        unsafe_allow_html=True,
    )

with top_right:
    st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <h3 style="margin-top: 8px; margin-bottom: 10px;">
        Weekly training trend
    </h3>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(5.6, 2.2), dpi=120)

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

    st.pyplot(fig, use_container_width=False)
    
st.divider()

# Lower section: 3-panel layout
panel1, panel2, panel3 = st.columns([1.0, 1.05, 1.15], gap="large")

with panel1:
    st.subheader("Structured signals")
    for signal in signals:
        priority_icon = {
            "high": "🔴",
            "medium": "🟠",
            "low": "🟢",
        }.get(signal["priority"], "⚪")
        st.markdown(f"**{priority_icon} {signal['title']}**")
        st.write(signal["detail"])

with panel2:
    st.subheader("🎯 Primary focus")
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
    st.subheader("AI-assisted insight (beta)")
    if used_ai:
        st.caption("🟢 OpenAI active")
    else:
        st.caption("🟠 Fallback mode")

    st.write(ai_text)

st.divider()

st.subheader("Weekly summary")
st.dataframe(
    weekly.assign(
        avg_hr=weekly["avg_hr"].round(1)
    ),
    use_container_width=True,
)

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