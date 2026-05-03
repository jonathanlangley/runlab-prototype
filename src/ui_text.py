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

    if primary_key == "consistency":
        return (
            headline,
            f"You are running about {run_days} days per week. The priority is to make training more repeatable before increasing load.",
        )

    if primary_key == "volume":
        return (
            headline,
            f"You are averaging about {recent_km} km per week, which is below the level usually needed to support consistent threshold or race-level work.",
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
    weekly_km = round(float(metrics.get("recent_avg_weekly_km", 0) or 0), 1)

    if primary_key == "volume":
        return [
            f"At around {weekly_km} km per week, much of the benefit from hard sessions may be lost because the aerobic base is not strong enough to fully support them.",
            "Adding another hard session now would increase fatigue without fixing the main limiter.",
            "The correct sequence is to build easy volume first, then layer quality on top.",
        ]

    if primary_key == "aerobic_support":
        return [
            "The current training includes hard efforts, but not enough easy running to support them.",
            "This means sessions can become isolated hard efforts rather than repeatable training stimulus.",
            "The correct sequence is to support the hard work first, then sharpen intensity later.",
        ]

    if primary_key == "consistency":
        return [
            "The current pattern is not repeatable enough yet, which limits long-term progress.",
            "Inconsistent training reduces the cumulative effect of all sessions.",
            "The correct sequence is consistency first, then progression.",
        ]

    if primary_key == "long_run":
        return [
            "The long run is the key endurance stimulus missing from the week.",
            "Without it, fatigue resistance and durability remain limited.",
            "The correct sequence is to establish the long run before increasing intensity.",
        ]

    if primary_key == "threshold":
        return [
            "The current week lacks enough sustained aerobic pressure.",
            "Threshold work improves the pace you can hold without excessive fatigue.",
            "The correct sequence is controlled threshold before harder intensity.",
        ]

    if primary_key == "quality":
        return [
            "The base is present, but there is no clear performance stimulus.",
            "Without it, fitness may plateau despite consistent training.",
            "The correct sequence is one clear quality session, then review the response.",
        ]

    if primary_key == "progression":
        return [
            "The current structure is sound, but stimulus is static.",
            "Without progression, adaptation slows or stops.",
            "The correct sequence is to move one lever clearly, not many at once.",
        ]

    if primary_key == "load_stability":
        return [
            "The recent load is too variable to progress confidently.",
            "A more stable week makes the training response easier to interpret.",
            "The correct sequence is stable load first, then progression.",
        ]

    if primary_key == "maintenance":
        return [
            "The current pattern is broadly healthy, so the main risk is over-correcting something that is already working.",
            "Small progressions are safer and easier to interpret than sudden changes to volume or intensity.",
            "The correct sequence is to protect the rhythm and progress carefully.",
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
