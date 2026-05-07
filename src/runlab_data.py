from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.runlab_config import DEMO_FILES

try:
    from src.runlab_classifier_v1 import build_pace_bands, fill_missing_workout_types

    CLASSIFIER_AVAILABLE = True
except Exception:
    build_pace_bands = None
    fill_missing_workout_types = None
    CLASSIFIER_AVAILABLE = False


def read_input_data(mode: str, uploaded_file, sample_option: str) -> pd.DataFrame | None:
    if mode == "Upload your own data" and uploaded_file is not None:
        return pd.read_csv(uploaded_file)

    demo_path = Path(DEMO_FILES[sample_option])
    if demo_path.exists():
        return pd.read_csv(demo_path)

    fallback = Path(__file__).resolve().parents[1] / DEMO_FILES[sample_option]
    if fallback.exists():
        return pd.read_csv(fallback)

    st.error(f"Demo file not found: {DEMO_FILES[sample_option]}")
    return None


def apply_auto_classification(
    df: pd.DataFrame,
    enabled: bool,
    profile: dict,
) -> tuple[pd.DataFrame, str | None]:
    if not enabled:
        return df, None

    if not CLASSIFIER_AVAILABLE or fill_missing_workout_types is None:
        return df, "Classifier module is not available."

    try:
        return fill_missing_workout_types(df, profile), None
    except Exception as exc:
        return (
            df,
            "Auto-classification failed, so uploaded workout_type values were used instead. "
            f"Details: {exc}",
        )
