"""Tests for workout-type alias normalisation in data_loader."""

from __future__ import annotations

import pandas as pd

from src.data_loader import clean_data


def test_workout_type_aliases_normalised() -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08"],
            "distance_km": [10, 10, 10, 10],
            "duration_min": [50, 50, 50, 50],
            "activity_type": ["run", "run", "run", "run"],
            "workout_type": ["long", "interval", "intervals", "tempo"],
        }
    )
    cleaned = clean_data(df)
    assert cleaned["workout_type"].tolist() == ["long run", "vo2", "vo2", "threshold"]


def test_canonical_workout_types_unchanged() -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-01-05", "2026-01-06"],
            "distance_km": [10, 10],
            "duration_min": [50, 50],
            "activity_type": ["run", "run"],
            "workout_type": ["easy", "long run"],
        }
    )
    cleaned = clean_data(df)
    assert cleaned["workout_type"].tolist() == ["easy", "long run"]
