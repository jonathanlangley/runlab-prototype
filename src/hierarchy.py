from __future__ import annotations

from typing import Any


def _session_text(count: int, singular: str, plural: str) -> str:
    if count == 1:
        return f"1 {singular}"
    return f"{count} {plural}"


def build_training_hierarchy(metrics: dict[str, Any], focus: dict[str, Any]) -> dict[str, Any]:
    threshold_count = int(metrics.get("threshold_sessions_last_28", 0) or 0)
    vo2_count = int(metrics.get("vo2_sessions_last_28", 0) or 0) + int(metrics.get("race_sessions_last_28", 0) or 0)
    long_count = int(metrics.get("long_runs_last_28", 0) or 0)
    run_days = round((metrics.get("days_with_run_last_28", 0) or 0) / 4.0, 1)
    recent_km = round(float(metrics.get("recent_avg_weekly_km", 0) or 0), 1)

    primary = {
        "label": focus.get("primary_limiter", focus.get("headline", "Primary limiter")),
        "headline": focus.get("headline", "Maintain consistency"),
        "detail": focus.get("detail", ""),
    }

    secondary = []
    if focus.get("secondary_focus"):
        secondary.append({"label": "Secondary focus", "detail": focus["secondary_focus"]})

    supportive = [
        {"label": "Run frequency", "detail": f"About {run_days} run days per week in the last 4 weeks."},
        {"label": "Weekly volume", "detail": f"Recent average is about {recent_km} km per week."},
    ]

    if long_count > 0:
        supportive.append({"label": "Long run", "detail": f"{_session_text(long_count, 'long run', 'long runs')} in the last 4 weeks."})
    if threshold_count > 0:
        supportive.append({"label": "Threshold", "detail": f"{_session_text(threshold_count, 'threshold session', 'threshold sessions')} in the last 4 weeks."})
    if vo2_count > 0:
        supportive.append({"label": "VO2 / race stimulus", "detail": f"{_session_text(vo2_count, 'session', 'sessions')} in the last 4 weeks."})

    return {"primary": primary, "secondary": secondary[:2], "supportive": supportive[:5]}
