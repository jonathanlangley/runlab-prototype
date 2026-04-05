from __future__ import annotations
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

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

st.title("RunLab Prototype")
st.caption("Structured training insights with a lightweight AI explanation layer")
st.markdown("""
This prototype demonstrates how raw training data can be transformed into:

- clear weekly metrics
- structured training signals
- a primary training focus
- simple AI-assisted explanations

The goal is not to replace coaching, but to support better decision-making.
""")
st.info("Demo: using sample data. Upload your own CSV to analyse your training.")

with st.sidebar:
    st.header("Data input")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    use_sample = st.checkbox("Use sample data", value=uploaded_file is None)

    st.markdown("### Expected columns")
    st.code("date, distance_km, duration_min, avg_hr, activity_type, workout_type")

df_raw = None

if uploaded_file is not None:
    df_raw = pd.read_csv(uploaded_file)
elif use_sample:
    df_raw = pd.read_csv("data/sample_runs.csv")

if df_raw is None:
    st.info("Upload a CSV file or tick 'Use sample data' to begin.")
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

col1, col2, col3, col4 = st.columns(4)
col1.metric("28-day distance", f"{metrics['total_distance_last_28']} km")
col2.metric("Run days (28d)", metrics["days_with_run_last_28"])
col3.metric("Consistency", metrics["consistency_label"].title())
col4.metric("Volume trend", metrics["volume_trend"].title())

st.subheader("Weekly training trend")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(weekly["week_start"], weekly["total_distance_km"], marker="o")
ax.set_xlabel("Week")
ax.set_ylabel("Distance (km)")
ax.set_title("Weekly distance")
ax.grid(True, alpha=0.3)
st.pyplot(fig)

left, right = st.columns([1, 1])

with left:
    st.subheader("Structured signals")
    for signal in signals:
        priority_icon = {
            "high": "🔴",
            "medium": "🟠",
            "low": "🟢",
        }.get(signal["priority"], "⚪")
        st.markdown(f"**{priority_icon} {signal['title']}**")
        st.write(signal["detail"])

    st.markdown("### 🎯 Primary Focus")
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

with right:
    st.subheader("AI-assisted insight (beta)")

    if used_ai:
        st.caption("🟢 OpenAI active")
    else:
        st.caption("🟠 Fallback mode")

    st.write(ai_text)

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