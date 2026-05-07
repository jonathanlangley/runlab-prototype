from __future__ import annotations

import streamlit as st

from src.runlab_utils import html_text


def render_app_intro() -> None:
    st.markdown(
        """
        <div class='hero-card'>
            <div class='status-pill'>Current Status: Early Prototype / Active Development</div>
            <div class='kicker'>Decision intelligence for self-coached runners</div>
            <div class='hero-title'>Turn training data into clearer decisions.</div>
            <div class='body-copy'>
                RunLab focuses on interpretation rather than dashboard overload. It analyses recent training,
                identifies the current signal, and highlights the likely primary focus area with supporting evidence.
            </div>
            <div class='small-note'>
                Structured metrics and deterministic rules generate the signal. AI can then help explain the context
                in plain English, rather than acting as a black-box decision-maker.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_how_runlab_thinks() -> None:
    st.markdown("## How RunLab Thinks")
    st.markdown(
        """
        <div class='body-copy'>
            RunLab is designed as a decision-support system. The aim is to move from raw training history
            to a clear, explainable next focus.
        </div>
        """,
        unsafe_allow_html=True,
    )

    flow_items = [
        ("1", "Training Data", "Activities, consistency, workload, session types, titles and optional notes."),
        ("2", "Metrics", "Structured analysis of volume, frequency, intensity and recent training patterns."),
        ("3", "Signals", "Meaningful trends, imbalances, gaps, risks and potential limiters."),
        ("4", "Decision Support", "A clearer primary focus area, with supporting evidence and confidence-aware language."),
        ("5", "AI Explanation", "Plain-English context layered on top of the deterministic training logic."),
    ]

    cols = st.columns(5)
    for col, (step, title, detail) in zip(cols, flow_items):
        with col:
            st.markdown(
                f"""
                <div class='flow-card'>
                    <div class='flow-step'>Step {html_text(step)}</div>
                    <div class='flow-title'>{html_text(title)}</div>
                    <div class='small-note'>{html_text(detail)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_strava_coming_soon() -> None:
    st.markdown(
        """
        <div class='locked-card'>
            <div class='section-title'>Strava Sync is planned for a future beta release</div>
            <div class='body-copy'>
                The current prototype supports demo scenarios and CSV upload. Strava Sync is intended to reduce friction
                by importing recent activities directly once the integration, authentication and data controls are ready.
            </div>
            <div class='support-box'>Planned direction: connect Strava, import recent activities, normalise the data and generate RunLab signals automatically.</div>
            <div class='support-box'>Trust focus: data minimisation, user control, explainable outputs and careful handling of free-text activity notes.</div>
            <div class='small-note'>For now, please use demo scenarios or upload your own CSV to generate a RunLab report.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_trust_and_explainability() -> None:
    st.markdown("---")
    st.markdown(
        """
        <div class='trust-card'>
            <div class='section-title'>Built with Explainability in Mind</div>
            <div class='body-copy'>
                RunLab separates structured decision logic from AI-generated explanation. The training signal should come
                from measurable data such as consistency, workload, session balance and progression. AI can then help explain
                the context in plain English.
            </div>
            <div class='small-note'>
                The goal is to make outputs understandable, confidence-aware and useful for self-coached runners, without
                overstating what the data can safely conclude.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_exploring_next() -> None:
    st.markdown("---")
    st.markdown("## Exploring Next")
    st.markdown(
        """
        RunLab is being developed iteratively through practical experimentation, athlete feedback,
        and ongoing exploration of analytics and AI-assisted decision support.
        """
    )

    future_features = [
        "Strava sync and automated activity ingestion",
        "Smarter session classification",
        "Confidence-aware training signals",
        "Persona-driven athlete interpretation",
        "Longitudinal block analysis",
        "Explainable AI summaries",
        "Coach and squad comparison views",
    ]

    cols = st.columns(2)
    for index, feature in enumerate(future_features):
        with cols[index % 2]:
            st.markdown(
                f"<div class='coming-soon-item'>{html_text(feature)}</div>",
                unsafe_allow_html=True,
            )

    st.caption("Built as a practical exploration of analytics, AI, explainability, and decision-support systems.")
