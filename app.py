from __future__ import annotations

import pandas as pd
import streamlit as st

from src.report_engine import EmptyDataError, generate_runlab_report
from src.runlab_config import APP_MODES, BETA_SIGNUP_URL, DEMO_DESCRIPTIONS, DEMO_FILES, VALID_BETA_CODES
from src.runlab_data import apply_auto_classification, read_input_data
from src.runlab_sidebar import render_sidebar
from src.ui_info_sections import (
    render_app_intro,
    render_exploring_next,
    render_how_runlab_thinks,
    render_strava_coming_soon,
    render_trust_and_explainability,
)
from src.ui_report_sections import render_report
from src.ui_styles import render_css


def main() -> None:
    st.set_page_config(
        page_title="RunLab Beta",
        page_icon="🏃",
        layout="wide",
    )

    render_css()

    uploaded_file, enable_auto, profile = render_sidebar()

    st.title("RunLab Beta")
    render_app_intro()
    render_how_runlab_thinks()

    st.markdown("---")
    st.markdown("### Choose your data source")

    mode = st.radio(
        "How would you like to use RunLab?",
        APP_MODES,
        horizontal=True,
    )

    if mode == "Strava Sync (Coming Soon)":
        render_strava_coming_soon()
        render_trust_and_explainability()
        render_exploring_next()
        return

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
    except EmptyDataError as exc:
        st.error(str(exc))
        st.info(
            "RunLab analyses running activities. Make sure your CSV contains rows where "
            "`activity_type` is set to `run` or similar, with positive `distance_km` and "
            "`duration_min` values."
        )
        return
    except ValueError as exc:
        st.error(f"Your CSV could not be read: {exc}")
        st.info(
            "RunLab expects at minimum: `date`, `distance_km`, `duration_min`. "
            "Optional: `avg_hr`, `activity_type`, `workout_type`, `title`, `description`."
        )
        return
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

    render_trust_and_explainability()
    render_exploring_next()


if __name__ == "__main__":
    main()
