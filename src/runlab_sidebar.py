from __future__ import annotations

import pandas as pd
import streamlit as st

from src.runlab_data import CLASSIFIER_AVAILABLE, build_pace_bands
from src.runlab_utils import parse_time_to_seconds, seconds_to_pace_str


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
            help="Only fills missing or unknown workout types. Existing valid labels are preserved.",
        )

        current_5k_time = st.text_input("Current 5K time", value="17:40").strip()
        current_hm_time = st.text_input("Current HM time (optional)", value="").strip()
        current_marathon_time = st.text_input("Current marathon time (optional)", value="").strip()

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
