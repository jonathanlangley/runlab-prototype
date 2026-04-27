from __future__ import annotations

from typing import Any

from src.balance import build_ideal_targets, split_quality_targets


def build_weekly_structure(metrics: dict[str, Any]) -> dict[str, float]:
    weeks = 4.0
    quality = (metrics.get("threshold_sessions_last_28", 0) or 0) + (metrics.get("vo2_sessions_last_28", 0) or 0) + (metrics.get("race_sessions_last_28", 0) or 0)
    return {
        "Quality": round(quality / weeks, 2),
        "Threshold": round((metrics.get("threshold_sessions_last_28", 0) or 0) / weeks, 2),
        "VO2": round(((metrics.get("vo2_sessions_last_28", 0) or 0) + (metrics.get("race_sessions_last_28", 0) or 0)) / weeks, 2),
        "Long run": round((metrics.get("long_runs_last_28", 0) or 0) / weeks, 2),
        "Run days": round((metrics.get("days_with_run_last_28", 0) or 0) / weeks, 2),
    }


def get_target_weekly_structure(focus: dict[str, Any], total_run_days: int, weeks: float = 4.0) -> dict[str, float]:
    if weeks <= 0:
        return {"Quality": 0.0, "Threshold": 0.0, "VO2": 0.0, "Long run": 0.0, "Run days": 0.0}

    ideal = build_ideal_targets(focus, total_run_days)
    quality = ideal.get("Quality", 0)
    split = split_quality_targets(quality, focus)
    return {
        "Quality": round(quality / weeks, 2),
        "Threshold": round(split["Threshold"] / weeks, 2),
        "VO2": round(split["VO2"] / weeks, 2),
        "Long run": round(ideal.get("Long run", 0) / weeks, 2),
        "Run days": round(total_run_days / weeks, 2),
    }


def build_structure_gaps(metrics: dict[str, Any], focus: dict[str, Any], total_run_days: int) -> list[dict[str, str]]:
    current = build_weekly_structure(metrics)
    target = get_target_weekly_structure(focus, total_run_days)
    gaps: list[dict[str, str]] = []

    if current["Run days"] < 5:
        gaps.append({"label": "Run frequency", "status": "Needs attention", "detail": f"Currently about {current['Run days']} run days per week. Build toward 5-6 before layering in more intensity."})

    if current["Long run"] < 0.75:
        gaps.append({"label": "Long run", "status": "Missing or inconsistent", "detail": "Aim for one comfortable long run most weeks to improve durability and aerobic support."})

    if current["Quality"] < max(0.75, target["Quality"] - 0.25):
        gaps.append({"label": "Quality stimulus", "status": "Light", "detail": "Use one controlled threshold or VO2 session each week once the base is stable."})
    elif current["Quality"] > target["Quality"] + 0.75:
        gaps.append({"label": "Quality stimulus", "status": "Heavy", "detail": "Quality looks high for the current structure. More easy support is likely more useful than another hard session."})

    if not gaps:
        gaps.append({"label": "Weekly structure", "status": "Broadly aligned", "detail": "The main components are present. Progress one lever at a time rather than changing the whole week."})

    return gaps[:3]
