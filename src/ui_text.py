from __future__ import annotations

from typing import Any


def _format_km(value: float) -> str:
    return str(int(round(float(value or 0))))


def build_focus_diagnosis(focus: dict[str, Any], metrics: dict[str, Any]) -> tuple[str, str]:
    headline = focus.get("headline", "Your current training pattern has a clear next focus")
    primary_key = str(focus.get("primary_key", ""))
    run_days = round((metrics.get("days_with_run_last_28", 0) or 0) / 4.0, 1)
    recent_km = round(float(metrics.get("recent_avg_weekly_km", 0) or 0), 1)
    target_volume_range = focus.get("target_volume_range")
    target_days = focus.get("target_run_days_per_week")

    if primary_key == "consistency":
        target = f"{target_days} days per week" if target_days else "5-6 days per week"
        return "Your main limiter is training frequency", f"You are currently running about {run_days} days per week. The clearest next step is to build toward {target} before adding more intensity."

    if primary_key == "volume":
        target = f" A sensible next range is {target_volume_range[0]}-{target_volume_range[1]} km per week." if target_volume_range else ""
        return "Your main limiter is aerobic volume", f"Your recent average is about {recent_km} km per week. That is likely limiting aerobic development and reducing the return from harder sessions.{target}"

    if primary_key == "balance":
        target = f" Aim to move toward {target_volume_range[0]}-{target_volume_range[1]} km per week mainly through easy running." if target_volume_range else ""
        return "Your harder sessions need more support", f"The issue is not simply needing more speed work. At about {recent_km} km per week and {run_days} run days, the quality work needs a stronger easy-running base underneath it.{target}"

    if primary_key == "long_run":
        return "Your endurance support is underdeveloped", "The long run is missing or too inconsistent, which limits durability and makes quality sessions harder to absorb."

    if primary_key == "threshold":
        return "Threshold support is underdeveloped", "Threshold work is missing or too irregular, which can limit your ability to sustain fast but controlled paces."

    if primary_key == "quality":
        return "You need a clearer quality stimulus", "The base is present, but the week needs one more purposeful threshold or VO2 stimulus to move performance forward."

    if primary_key == "volume_trend":
        return "Your training load needs stabilising", "Recent volume has dipped or become unstable. The immediate job is to rebuild a repeatable week before pushing harder."

    return headline, focus.get("detail", "Keep the pattern stable and progress gradually.")


def build_why_this_matters(metrics: dict[str, Any], top_signals: list[dict[str, Any]], focus: dict[str, Any] | None = None) -> list[str]:
    primary_key = str((focus or {}).get("primary_key", ""))

    if primary_key in {"volume", "balance"}:
        return [
            "For 5K performance, aerobic volume is not just marathon-style background work. It improves how much pace you can sustain before fatigue bites.",
            "More easy volume also lowers the relative cost of threshold and VO2 sessions, so the hard work becomes more productive rather than just more tiring.",
        ]

    if primary_key == "consistency":
        return [
            "Adaptation comes from repeated stimulus. More regular run days create a stronger training signal than occasional bigger sessions.",
            "Once frequency is stable, volume and quality become easier to progress without overloading single days.",
        ]

    if primary_key == "threshold":
        return [
            "Threshold work raises the speed you can hold without tipping into heavy fatigue, which is central to converting fitness into race pace.",
            "For a 5K runner, threshold is the bridge between easy volume and VO2 work. It makes top-end sessions more sustainable.",
        ]

    if primary_key == "long_run":
        return [
            "A regular long run builds durability, capillary development, and fatigue resistance, even for shorter races.",
            "It gives the rest of the week more aerobic support, so faster work is absorbed rather than simply survived.",
        ]

    if primary_key == "quality":
        return [
            "Once consistency and volume are in place, performance still needs a clear faster stimulus.",
            "A controlled weekly quality session gives the body a reason to adapt without turning the whole week into a recovery problem.",
        ]

    if top_signals:
        return [str(s.get("detail", "")).strip() for s in top_signals[:2] if str(s.get("detail", "")).strip()]

    return ["The current pattern is broadly healthy, so the best improvement is small, controlled progression."]


def build_supporting_metrics(metrics: dict[str, Any]) -> list[tuple[str, str]]:
    return [
        ("Run days", f"{round((metrics.get('days_with_run_last_28', 0) or 0) / 4.0, 1)} per week"),
        ("Weekly volume", f"{_format_km(metrics.get('recent_avg_weekly_km', 0))} km"),
        ("Quality", f"{metrics.get('quality_runs_last_28', 0)} sessions in 4 weeks"),
        ("Long runs", f"{metrics.get('long_runs_last_28', 0)} in 4 weeks"),
    ]
