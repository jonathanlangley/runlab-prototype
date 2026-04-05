from __future__ import annotations
import pandas as pd
from src.utils import safe_mean, classify_consistency, classify_volume_trend

def classify_volume_pattern(weekly: pd.DataFrame) -> dict:
    distances = weekly["total_distance_km"].tolist()

    if len(distances) < 4:
        return {
            "volume_pattern": "insufficient_data",
            "volume_pattern_detail": "Not enough weekly data to classify the volume pattern reliably.",
        }

    recent = distances[-6:] if len(distances) >= 6 else distances[:]
    max_value = max(recent)
    max_index = recent.index(max_value)

    last_week = recent[-1]
    prev_week = recent[-2]

    week_changes = [recent[i] - recent[i - 1] for i in range(1, len(recent))]
    avg_abs_change = sum(abs(x) for x in week_changes) / len(week_changes) if week_changes else 0.0

    recent_avg = safe_mean(pd.Series(recent[-3:]))
    prior_avg = safe_mean(pd.Series(recent[:-3])) if len(recent) > 3 else recent_avg

    if max_index <= len(recent) - 3 and last_week < max_value * 0.9 and prev_week < max_value * 0.95:
        return {
            "volume_pattern": "peaked_then_dipped",
            "volume_pattern_detail": "Training volume built to a recent peak and has dropped over the last couple of weeks.",
        }

    if avg_abs_change >= 8:
        return {
            "volume_pattern": "volatile",
            "volume_pattern_detail": "Weekly volume is moving around quite a lot from week to week, which makes the overall pattern less stable.",
        }

    if prior_avg > 0:
        change_pct = ((recent_avg - prior_avg) / prior_avg) * 100
    else:
        change_pct = 0.0

    if change_pct >= 8:
        return {
            "volume_pattern": "ramping_up",
            "volume_pattern_detail": "Weekly volume is still trending upward overall.",
        }

    if change_pct <= -8:
        return {
            "volume_pattern": "declining",
            "volume_pattern_detail": "Weekly volume is trending downward overall.",
        }

    return {
        "volume_pattern": "plateau",
        "volume_pattern_detail": "Weekly volume looks broadly stable rather than clearly rising or falling.",
    }

def weekly_summary(df: pd.DataFrame) -> pd.DataFrame:
    weekly = (
        df.groupby("week_start", as_index=False)
        .agg(
            total_distance_km=("distance_km", "sum"),
            total_duration_min=("duration_min", "sum"),
            run_count=("date", "count"),
            avg_hr=("avg_hr", "mean"),
            threshold_sessions=("workout_type", lambda s: (s == "threshold").sum()),
            interval_sessions=("workout_type", lambda s: (s == "interval").sum()),
            long_runs=("workout_type", lambda s: (s == "long").sum()),
        )
        .sort_values("week_start")
        .reset_index(drop=True)
    )
    return weekly


def overall_metrics(df: pd.DataFrame, weekly: pd.DataFrame) -> dict:
    latest_date = df["date"].max()
    last_28_cutoff = latest_date - pd.Timedelta(days=27)
    last_28 = df[df["date"] >= last_28_cutoff]

    unique_run_days = last_28["date"].dt.date.nunique()
    consistency_label = classify_consistency(unique_run_days)

    total_distance_last_28 = float(last_28["distance_km"].sum())
    total_runs_last_28 = int(len(last_28))
    avg_distance = safe_mean(df["distance_km"])
    longest_run = float(df["distance_km"].max())

    recent_weeks = weekly.tail(4)
    prior_weeks = weekly.iloc[-8:-4] if len(weekly) >= 8 else weekly.head(max(len(weekly) - 4, 0))

    recent_avg = safe_mean(recent_weeks["total_distance_km"])
    prior_avg = safe_mean(prior_weeks["total_distance_km"])

    if prior_avg > 0:
        volume_change_pct = ((recent_avg - prior_avg) / prior_avg) * 100
    else:
        volume_change_pct = 0.0

    volume_trend = classify_volume_trend(volume_change_pct)

    volume_pattern_info = classify_volume_pattern(weekly)

    threshold_last_28 = int((last_28["workout_type"] == "threshold").sum())
    interval_last_28 = int((last_28["workout_type"] == "interval").sum())
    long_runs_last_28 = int((last_28["workout_type"] == "long").sum())

    return {
        "latest_date": latest_date,
        "days_with_run_last_28": unique_run_days,
        "consistency_label": consistency_label,
        "total_distance_last_28": round(total_distance_last_28, 1),
        "total_runs_last_28": total_runs_last_28,
        "avg_distance_per_run": round(avg_distance, 1),
        "longest_run_km": round(longest_run, 1),
        "recent_avg_weekly_km": round(recent_avg, 1),
        "prior_avg_weekly_km": round(prior_avg, 1),
        "volume_change_pct": round(volume_change_pct, 1),
        "volume_trend": volume_trend,
        "volume_pattern": volume_pattern_info["volume_pattern"],
        "volume_pattern_detail": volume_pattern_info["volume_pattern_detail"],
        "threshold_sessions_last_28": threshold_last_28,
        "interval_sessions_last_28": interval_last_28,
        "long_runs_last_28": long_runs_last_28,
    }