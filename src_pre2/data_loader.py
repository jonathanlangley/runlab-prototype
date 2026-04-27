from __future__ import annotations

import pandas as pd

COLUMN_MAPPING = {
    "date": "date",
    "activity_date": "date",
    "start_date": "date",
    "distance": "distance_km",
    "distance_km": "distance_km",
    "distance_(km)": "distance_km",
    "duration": "duration_min",
    "duration_min": "duration_min",
    "moving_time": "duration_min",
    "elapsed_time": "duration_min",
    "average_heartrate": "avg_hr",
    "average_heart_rate": "avg_hr",
    "avg_hr": "avg_hr",
    "type": "activity_type",
    "activity_type": "activity_type",
    "workout_type": "workout_type",
    "session_type": "workout_type",
    "name": "activity_name",
    "activity_name": "activity_name",
}


def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        col.strip().lower().replace(" ", "_").replace("-", "_")
        for col in df.columns
    ]
    rename_dict = {col: COLUMN_MAPPING[col] for col in df.columns if col in COLUMN_MAPPING}
    return df.rename(columns=rename_dict)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = standardise_columns(df)

    required_defaults = {
        "activity_type": "run",
        "workout_type": "easy",
    }
    for col, default in required_defaults.items():
        if col not in df.columns:
            df[col] = default

    if "date" not in df.columns:
        raise ValueError("CSV must contain a date column.")

    if "distance_km" not in df.columns or "duration_min" not in df.columns:
        raise ValueError("CSV must contain distance_km and duration_min columns.")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce")
    df["duration_min"] = pd.to_numeric(df["duration_min"], errors="coerce")

    if "avg_hr" in df.columns:
        df["avg_hr"] = pd.to_numeric(df["avg_hr"], errors="coerce")
    else:
        df["avg_hr"] = None

    df["activity_type"] = df["activity_type"].astype(str).str.lower().str.strip()
    df["workout_type"] = df["workout_type"].astype(str).str.lower().str.strip()

    run_keywords = {"run", "running", "trail run", "treadmill run"}
    df = df[df["activity_type"].isin(run_keywords)]

    df = df.dropna(subset=["date", "distance_km", "duration_min"])
    df = df[df["distance_km"] > 0]
    df = df[df["duration_min"] > 0]

    df["pace_min_per_km"] = df["duration_min"] / df["distance_km"]

    # Monday-start training weeks
    df["week_start"] = df["date"] - pd.to_timedelta(df["date"].dt.weekday, unit="D")
    df["week_start"] = df["week_start"].dt.normalize()

    return df.sort_values("date").reset_index(drop=True)