from __future__ import annotations
import pandas as pd


def format_percentage(value: float) -> str:
    return f"{value:.0f}%"


def safe_mean(series: pd.Series) -> float:
    if series.empty:
        return 0.0
    return float(series.mean())

def classify_consistency(days_with_run_last_28: int) -> str:
    run_days_per_week = days_with_run_last_28 / 4.0

    if run_days_per_week >= 6:
        return "high"
    elif run_days_per_week >= 5:
        return "moderate"
    elif run_days_per_week >= 3:
        return "low"
    else:
        return "very low"
    
def classify_volume_trend(change_pct: float) -> str:
    if change_pct >= 8:
        return "rising"
    if change_pct <= -8:
        return "declining"
    return "flat"