from __future__ import annotations

from typing import Any


def _format_km(value: float) -> str:
    return str(int(round(float(value or 0))))


def build_focus_diagnosis(
    focus: dict[str, Any],
    metrics: dict[str, Any],
) -> tuple[str, str]:
    primary_key = str(focus.get("primary_key", ""))
    headline = focus.get("headline", "Your next training focus")
    detail = focus.get("detail", "Keep the pattern stable and progress gradually.")

    run_days = round((metrics.get("days_with_run_last_28", 0) or 0) / 4.0, 1)
    recent_km = round(float(metrics.get("recent_avg_weekly_km", 0) or 0), 1)

    threshold = int(metrics.get("threshold_sessions_last_28", 0) or 0)
    vo2 = int(metrics.get("vo2_sessions_last_28", 0) or 0)
    races = int(metrics.get("race_sessions_last_28", 0) or 0)
    long_runs = int(metrics.get("long_runs_last_28", 0) or 0)

    plan = focus.get("next_week_plan", {})
    km_low, km_high = plan.get("target_km_range", (None, None))

    if primary_key == "consistency":
        return (
            headline,
            f"You are running about {run_days} days per week. The priority is to make training more repeatable before increasing load.",
        )

    if primary_key == "volume":
        return (
            headline,
            f"Your recent average is about {recent_km} km per week. The next useful step is {km_low}-{km_high} km, mostly through easy running.",
        )

    if primary_key == "aerobic_support":
        return (
            headline,
            f"RunLab detected {threshold + vo2 + races} quality or race-level efforts in the last 28 days, but only {recent_km} km per week. The hard work needs more easy running underneath it.",
        )

    if primary_key == "load_stability":
        return (
            headline,
            "Recent volume has dipped or become variable. Stabilise the week before pushing a new training stimulus.",
        )

    if primary_key == "long_run":
        return (
            headline,
            f"RunLab detected {long_runs} long runs in the last 28 days. Make the long run a reliable weekly anchor before chasing extra speed.",
        )

    if primary_key == "threshold":
        return (
            headline,
            f"RunLab detected {threshold} threshold sessions in the last 28 days. Add one controlled threshold stimulus rather than another all-out hard day.",
        )

    if primary_key == "quality":
        return (
            headline,
            "The base is present, but the week needs one purposeful faster stimulus to move performance forward.",
        )

    if primary_key == "progression":
        return (
            headline,
            "The pattern is broadly sound, but it needs one clear progression signal rather than more of everything.",
        )

    if primary_key == "maintenance":
        return (
            headline,
            "The current pattern is broadly healthy. The best next step is to protect the rhythm and progress carefully.",
        )

    return headline, detail


def build_why_this_matters(
    metrics: dict[str, Any],
    top_signals: list[dict[str, Any]],
    focus: dict[str, Any] | None = None,
) -> list[str]:
    primary_key = str((focus or {}).get("primary_key", ""))

    if primary_key == "consistency":
        return [
            "Performance improves from repeated stimulus. A reliable weekly rhythm usually beats occasional bigger weeks.",
            "Once frequency is stable, volume and quality can be added without making single sessions carry too much load.",
        ]

    if primary_key == "volume":
        return [
            "Aerobic volume increases the amount of fast running you can support before fatigue takes over.",
            "Easy mileage also makes quality sessions more productive because they sit on top of a stronger base.",
            "Adding more intensity now would probably increase fatigue faster than fitness.",
        ]

    if primary_key == "aerobic_support":
        return [
            "Quality work only produces its full benefit when there is enough easy volume underneath it.",
            "More easy running improves recovery between hard efforts and helps threshold or VO2 sessions become repeatable.",
            "The better sequence is to support the hard work first, then sharpen intensity once the base can absorb it.",
        ]

    if primary_key == "load_stability":
        return [
            "Fitness responds best to a repeatable load. If weekly volume is bouncing around, it becomes harder to know whether the body is adapting or just coping.",
            "Stabilising the week makes the next progression safer and easier to interpret.",
        ]

    if primary_key == "long_run":
        return [
            "A regular long run improves durability and fatigue resistance, even for shorter races.",
            "It gives the rest of the week more aerobic support, so faster work is absorbed rather than just survived.",
        ]

    if primary_key == "threshold":
        return [
            "Threshold training improves the fastest pace you can sustain while staying controlled.",
            "It bridges easy volume and harder interval work, making performance gains more repeatable.",
            "The aim is controlled discomfort, not another race effort.",
        ]

    if primary_key == "quality":
        return [
            "Once consistency and volume are in place, performance still needs a clear faster stimulus.",
            "One controlled quality session gives the body a reason to adapt without turning the whole week into a recovery problem.",
        ]

    if primary_key == "progression":
        return [
            "When the structure is already solid, improvement usually comes from progressing one lever clearly.",
            "Changing too many things at once makes it harder to know what is actually working.",
        ]

    if primary_key == "maintenance":
        return [
            "When training is broadly healthy, the highest-value move is often to protect consistency.",
            "Small progressions are safer and easier to interpret than big changes to volume or intensity.",
        ]

    if top_signals:
        return [
            str(signal.get("detail", "")).strip()
            for signal in top_signals[:2]
            if str(signal.get("detail", "")).strip()
        ]

    return [
        "The current pattern is broadly healthy, so the best improvement is small, controlled progression."
    ]


def build_supporting_metrics(metrics: dict[str, Any]) -> list[tuple[str, str]]:
    return [
        (
            "Run days",
            f"{round((metrics.get('days_with_run_last_28', 0) or 0) / 4.0, 1)} / week",
        ),
        (
            "Weekly volume",
            f"{_format_km(metrics.get('recent_avg_weekly_km', 0))} km",
        ),
        (
            "Quality",
            f"{metrics.get('quality_runs_last_28', 0)} in 4 weeks",
        ),
        (
            "Long runs",
            f"{metrics.get('long_runs_last_28', 0)} in 4 weeks",
        ),
    ]