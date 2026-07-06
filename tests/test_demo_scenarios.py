"""Regression tests for core validation scenarios (V1–V6)."""

from __future__ import annotations

import pandas as pd
import pytest

from src.report_engine import generate_runlab_report

VALIDATION_SCENARIOS = [
    pytest.param("data/inconsistent_training.csv", "consistency", id="V1-consistency"),
    pytest.param("data/sample_runs.csv", "volume", id="V2-volume"),
    pytest.param("data/too_much_intensity.csv", "aerobic_support", id="V3-aerobic-support"),
    pytest.param("data/high_volume_no_quality.csv", "quality", id="V4-quality"),
    pytest.param("data/near_optimal_but_plateauing.csv", "progression", id="V5-progression"),
    pytest.param("data/declining_load.csv", "load_stability", id="V6-load-stability"),
]


@pytest.mark.parametrize(("csv_path", "expected_primary"), VALIDATION_SCENARIOS)
def test_demo_scenario_primary_limiter(csv_path: str, expected_primary: str) -> None:
    df = pd.read_csv(csv_path)
    report = generate_runlab_report(df)
    assert report["focus"]["primary_key"] == expected_primary


def test_report_includes_engine_version() -> None:
    df = pd.read_csv("data/sample_runs.csv")
    report = generate_runlab_report(df)
    assert report["engine_version"]
    assert isinstance(report["engine_version"], str)
