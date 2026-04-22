from __future__ import annotations

from src.balance import build_ideal_targets


def build_weekly_structure(metrics: dict) -> dict[str, float]:
    weeks = 4.0
    return {
        "Threshold": round((metrics.get("threshold_sessions_last_28", 0) or 0) / weeks, 2),
        "VO2": round(
            (
                (metrics.get("vo2_sessions_last_28", 0) or 0)
                + (metrics.get("race_sessions_last_28", 0) or 0)
            ) / weeks,
            2,
        ),
        "Long run": round((metrics.get("long_runs_last_28", 0) or 0) / weeks, 2),
    }


def get_target_weekly_structure(focus: dict, total_run_days: int, weeks: float = 4.0) -> dict[str, float]:
    """
    Derive weekly structure targets from the same ideal target logic used by the
    training balance chart, so both sections stay aligned.
    """
    ideal_counts = build_ideal_targets(focus, total_run_days)

    if weeks <= 0:
        return {
            "Threshold": 0.0,
            "VO2": 0.0,
            "Long run": 0.0,
        }

    return {
        "Threshold": round(ideal_counts["Threshold"] / weeks, 2),
        "VO2": round(ideal_counts["VO2"] / weeks, 2),
        "Long run": round(ideal_counts["Long run"] / weeks, 2),
    }