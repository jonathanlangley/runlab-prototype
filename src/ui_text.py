from __future__ import annotations

from typing import Any


def _format_km(value: float) -> str:
    return str(int(round(float(value or 0))))


def build_focus_diagnosis(focus: dict[str, Any], metrics: dict[str, Any]) -> tuple[str, str]:
    primary_key = str(focus.get("primary_key", ""))
    headline = focus.get("headline", "Your next training focus")
    detail = focus.get("detail", "Keep the pattern stable and progress gradually.")
    run_days = round((metrics.get("days_with_run_last_28", 0) or 0) / 4.0, 1)
    recent_km = round(float(metrics.get("recent_avg_weekly_km", 0) or 0), 1)
    plan = focus.get("next_week_plan", {})
    km_low, km_high = plan.get("target_km_range", (None, None))

    if primary_key == "consistency":
        return headline, f"You are running about {run_days} days per week. Before adding more load, make the week more repeatable."
    if primary_key == "volume":
        return headline, f"Your recent average is about {recent_km} km per week. The next useful step is {km_low}-{km_high} km, mostly easy."
    if primary_key == "aerobic_support":
        return headline, f"The hard work is present, but at about {recent_km} km per week it needs more easy volume underneath it."
    if primary_key == "load_stability":
        return headline, "Recent volume has dipped or become variable. Stabilise the week before pushing a new training stimulus."
    if primary_key == "long_run":
        return headline, "The long run is missing or inconsistent. Make it a weekly anchor before chasing extra speed."
    if primary_key == "threshold":
        return headline, "Threshold work is missing or too irregular. Add one controlled session rather than another all-out hard day."
    if primary_key == "quality":
        return headline, "The base is present, but the week needs one purposeful faster stimulus to move performance forward."
    if primary_key == "progression":
        return headline, "The pattern is broadly sound, but it needs one clear progression signal rather than more analysis."
    return headline, detail


def build_why_this_matters(metrics: dict[str, Any], top_signals: list[dict[str, Any]], focus: dict[str, Any] | None = None) -> list[str]:
    primary_key = str((focus or {}).get("primary_key", ""))

    if primary_key in {"volume", "aerobic_support"}:
        return [
            "For 5K performance, aerobic volume is not just background mileage. It raises the amount of fast running you can sustain before fatigue takes over.",
            "More easy volume also makes threshold and VO2 sessions more productive because they sit on top of a stronger aerobic base instead of becoming isolated hard efforts.",
            "Adding more intensity now would probably increase fatigue faster than fitness. The better sequence is easy volume first, then sharper quality once the base can absorb it.",
        ]
    if primary_key == "consistency":
        return [
            "Adaptation comes from repeated stimulus. A reliable weekly rhythm usually beats occasional bigger sessions.",
            "Once frequency is stable, you can add volume or quality without making single days carry too much load.",
        ]
    if primary_key == "threshold":
        return [
            "Threshold training improves the fastest pace you can sustain while staying controlled, which matters directly for 5K and 10K performance.",
            "It also bridges easy volume and VO2 work. Without it, harder sessions can become too spiky and less repeatable.",
        ]
    if primary_key == "long_run":
        return [
            "A regular long run improves durability and fatigue resistance, even for shorter races.",
            "It gives the rest of the week more aerobic support, so faster work is absorbed rather than just survived.",
        ]
    if primary_key == "quality":
        return [
            "Once consistency and volume are in place, performance still needs a clear faster stimulus.",
            "One controlled quality session gives the body a reason to adapt without turning the whole week into a recovery problem.",
        ]
    if primary_key == "load_stability":
        return [
            "Fitness responds best to a repeatable load. If volume is bouncing around, it becomes harder to know whether the body is adapting or just coping.",
            "Stabilising the week makes the next progression safer and easier to interpret.",
        ]
    if top_signals:
        return [str(s.get("detail", "")).strip() for s in top_signals[:2] if str(s.get("detail", "")).strip()]
    return ["The current pattern is broadly healthy, so the best improvement is small, controlled progression."]


def build_supporting_metrics(metrics: dict[str, Any]) -> list[tuple[str, str]]:
    return [
        ("Run days", f"{round((metrics.get('days_with_run_last_28', 0) or 0) / 4.0, 1)} / week"),
        ("Weekly volume", f"{_format_km(metrics.get('recent_avg_weekly_km', 0))} km"),
        ("Quality", f"{metrics.get('quality_runs_last_28', 0)} in 4 weeks"),
        ("Long runs", f"{metrics.get('long_runs_last_28', 0)} in 4 weeks"),
    ]
