from __future__ import annotations

from typing import Any

PRIORITY_SCORE = {"high": 3, "medium": 2, "low": 1}

FOCUS_RULES: dict[str, dict[str, Any]] = {
    "consistency": {
        "headline": "Increase weekly run frequency",
        "limiter": "Consistency",
        "detail": "The training rhythm is not yet repeatable enough to support reliable progression.",
        "timeframe": "2-3 weeks",
        "prescription": [
            "Run more frequently before adding extra intensity",
            "Use short easy runs to close large gaps between training days",
            "Aim for a repeatable weekly rhythm first",
            "Review the pattern after 2-3 consistent weeks",
        ],
    },
    "volume": {
        "headline": "Build aerobic volume",
        "limiter": "Aerobic volume",
        "detail": "Weekly volume is the clearest limiter, so the next block should be built around more easy aerobic running.",
        "timeframe": "3-4 weeks",
        "prescription": [
            "Increase weekly distance gradually through easy running",
            "Keep quality controlled while volume catches up",
            "Protect one regular long run each week",
            "Avoid progressing volume and intensity at the same time",
        ],
    },
    "volume_trend": {
        "headline": "Stabilise training load",
        "limiter": "Training load stability",
        "detail": "Recent volume has dipped or become unstable, so the priority is to rebuild a sustainable rhythm.",
        "timeframe": "2-3 weeks",
        "prescription": [
            "Re-establish a repeatable weekly pattern",
            "Bring volume back gradually rather than forcing a sharp jump",
            "Keep hard sessions controlled while load stabilises",
            "Use consistency as the success measure for this block",
        ],
    },
    "long_run": {
        "headline": "Rebuild long run stimulus",
        "limiter": "Long run stimulus",
        "detail": "The endurance support is too light or inconsistent, which limits durability and aerobic development.",
        "timeframe": "3-4 weeks",
        "prescription": [
            "Schedule one comfortable long run each week",
            "Build the long run gradually rather than jumping distance",
            "Keep the long run aerobic and controlled",
            "Stabilise this before adding more hard work",
        ],
    },
    "threshold": {
        "headline": "Strengthen threshold support",
        "limiter": "Threshold stimulus",
        "detail": "Threshold work is missing or too irregular to strongly support sustained pace development.",
        "timeframe": "3-4 weeks",
        "prescription": [
            "Add one repeatable threshold session each week",
            "Use controlled efforts rather than maximal sessions",
            "Keep easy running around the session genuinely easy",
            "Hold this pattern for several weeks before progressing it",
        ],
    },
    "balance": {
        "headline": "Support quality with a stronger aerobic base",
        "limiter": "Training balance",
        "detail": "The harder work is present, but the supporting easy volume and structure are not strong enough yet.",
        "timeframe": "3-6 weeks",
        "prescription": [
            "Keep one quality session each week but avoid adding more intensity",
            "Add easy volume around the quality work if recovery allows",
            "Make the long run a stable part of the week",
            "Use the next block to make hard sessions better supported",
        ],
    },
    "quality": {
        "headline": "Add a clearer quality stimulus",
        "limiter": "Quality stimulus",
        "detail": "The base is present, but the training week needs one clearer dose of threshold or VO2 work.",
        "timeframe": "3-4 weeks",
        "prescription": [
            "Introduce one controlled quality session each week",
            "Start with threshold before adding more aggressive VO2 work",
            "Keep the rest of the week easy and repeatable",
            "Review after 3-4 weeks before adding a second quality day",
        ],
    },
    "progression": {
        "headline": "Create a clearer progression signal",
        "limiter": "Progression",
        "detail": "The pattern is broadly sound, but too many key levers are static.",
        "timeframe": "2-4 weeks",
        "prescription": [
            "Choose one lever to progress in the next block",
            "Keep the rest of the week stable while that change beds in",
            "Prefer a small sustainable increase over a sharp jump",
            "Reassess once the new stimulus has had time to show up",
        ],
    },
    "maintenance": {
        "headline": "Maintain consistency and progress gradually",
        "limiter": "No major limiter",
        "detail": "The current pattern is broadly healthy, so the best next step is controlled progression rather than a major change.",
        "timeframe": "2-4 weeks",
        "prescription": [
            "Keep the current weekly rhythm stable",
            "Progress only one training lever at a time",
            "Protect recovery around harder sessions",
            "Reassess after another consistent block",
        ],
    },
}

PRIMARY_RULE_ORDER = [
    "consistency",
    "volume_trend",
    "volume",
    "balance",
    "long_run",
    "threshold",
    "quality",
    "progression",
]

RULE_ID_TO_FOCUS_KEY = {
    "consistency": "consistency",
    "volume": "volume",
    "volume_trend": "volume_trend",
    "volume_pattern": "volume_trend",
    "long_run": "long_run",
    "threshold": "threshold",
    "balance": "balance",
    "progression": "progression",
}


def recommend_volume_target(current_km: float) -> tuple[int, int]:
    current_km = float(current_km or 0)
    if current_km < 30:
        return int(round(current_km + 10)), int(round(current_km + 20))
    if current_km < 50:
        return int(round(current_km + 10)), int(round(current_km + 15))
    if current_km < 70:
        return int(round(current_km + 5)), int(round(current_km + 10))
    return int(round(current_km + 5)), int(round(current_km + 8))


def recommend_run_days_target(current_run_days_per_week: float) -> int:
    if current_run_days_per_week < 4:
        return 5
    if current_run_days_per_week < 5:
        return 6
    return 6


def _format_km(value: float) -> str:
    return str(int(round(float(value or 0))))


def _signal_score(signal: dict[str, Any]) -> int:
    return PRIORITY_SCORE.get(str(signal.get("priority", "low")).lower(), 1)


def _best_signal_by_focus(signals: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for signal in signals:
        focus_key = RULE_ID_TO_FOCUS_KEY.get(str(signal.get("rule_id", "")))
        if not focus_key:
            continue
        if focus_key not in grouped or _signal_score(signal) > _signal_score(grouped[focus_key]):
            grouped[focus_key] = signal
    return grouped


def _quality_absent(metrics: dict[str, Any]) -> bool:
    return int(metrics.get("quality_runs_last_28", 0) or 0) == 0


def _choose_primary_key(metrics: dict[str, Any], signals: list[dict[str, Any]]) -> str:
    grouped = _best_signal_by_focus(signals)

    if grouped.get("consistency") and _signal_score(grouped["consistency"]) >= 3:
        return "consistency"

    if grouped.get("volume_trend") and _signal_score(grouped["volume_trend"]) >= 3:
        return "volume_trend"

    recent_km = float(metrics.get("recent_avg_weekly_km", 0) or 0)
    quality_pct = float(metrics.get("quality_run_pct", 0) or 0)
    easy_pct = float(metrics.get("easy_run_pct", 0) or 0)

    if quality_pct > 0.40 and easy_pct < 0.70:
        return "balance"

    if recent_km < 50:
        return "volume"

    if int(metrics.get("long_runs_last_28", 0) or 0) == 0:
        return "long_run"

    if int(metrics.get("threshold_sessions_last_28", 0) or 0) == 0:
        return "threshold"

    if recent_km < 70 and grouped.get("volume") and _signal_score(grouped["volume"]) >= 2:
        return "volume"

    if _quality_absent(metrics):
        return "quality"

    for key in PRIMARY_RULE_ORDER:
        signal = grouped.get(key)
        if signal and _signal_score(signal) >= 2:
            return key

    return "maintenance"


def _choose_secondary_key(primary_key: str, metrics: dict[str, Any], signals: list[dict[str, Any]]) -> str | None:
    grouped = _best_signal_by_focus(signals)
    candidates = [key for key in PRIMARY_RULE_ORDER if key != primary_key]

    # Avoid diluting the decision. Secondary focus should support the primary, not compete with it.
    if primary_key in {"consistency", "volume_trend"}:
        allowed = {"volume", "long_run"}
    elif primary_key == "volume":
        allowed = {"long_run", "threshold"}
    elif primary_key == "balance":
        allowed = {"volume", "long_run", "threshold"}
    elif primary_key == "long_run":
        allowed = {"volume", "threshold"}
    elif primary_key == "threshold":
        allowed = {"volume", "long_run"}
    else:
        allowed = set(candidates)

    ranked = []
    for key in candidates:
        if key not in allowed:
            continue
        signal = grouped.get(key)
        if not signal:
            continue
        score = _signal_score(signal)
        if score >= 2:
            ranked.append((score, -PRIMARY_RULE_ORDER.index(key), key))

    if not ranked:
        return None

    ranked.sort(reverse=True)
    return ranked[0][2]


def _target_fields(primary_key: str, metrics: dict[str, Any]) -> dict[str, Any]:
    current_km = float(metrics.get("recent_avg_weekly_km", 0) or 0)
    run_days = float(metrics.get("days_with_run_last_28", 0) or 0) / 4.0
    volume_range = recommend_volume_target(current_km)
    run_days_target = recommend_run_days_target(run_days)

    target_fields: dict[str, Any] = {
        "target_volume_range": None,
        "target_run_days_per_week": None,
    }

    if primary_key in {"consistency", "volume", "balance", "long_run", "threshold"}:
        target_fields["target_volume_range"] = volume_range
    if primary_key in {"consistency", "volume", "balance"}:
        target_fields["target_run_days_per_week"] = run_days_target

    return target_fields


def _augment_prescription(focus: dict[str, Any], primary_key: str, metrics: dict[str, Any]) -> list[str]:
    steps = list(focus.get("prescription", []))
    current_km = float(metrics.get("recent_avg_weekly_km", 0) or 0)
    volume_range = focus.get("target_volume_range")
    run_days_target = focus.get("target_run_days_per_week")

    if volume_range and primary_key in {"volume", "balance", "consistency"}:
        steps.insert(0, f"Move from about {_format_km(current_km)} km toward {volume_range[0]}-{volume_range[1]} km per week")
    if run_days_target and primary_key == "consistency":
        steps.insert(0, f"Build toward {run_days_target} run days per week")

    cleaned: list[str] = []
    seen: set[str] = set()
    for step in steps:
        text = str(step).strip()
        if text and text not in seen:
            cleaned.append(text)
            seen.add(text)
    return cleaned[:4]


def determine_focus(metrics: dict[str, Any], signals: list[dict[str, Any]]) -> dict[str, Any]:
    primary_key = _choose_primary_key(metrics, signals)
    secondary_key = _choose_secondary_key(primary_key, metrics, signals)

    template = FOCUS_RULES[primary_key]
    focus = dict(template)
    focus["primary_key"] = primary_key
    focus["secondary_key"] = secondary_key
    focus["primary_limiter"] = template["limiter"]
    focus["secondary_focus"] = FOCUS_RULES[secondary_key]["headline"] if secondary_key else None
    focus["priority"] = "low" if primary_key == "maintenance" else "high" if primary_key in {"consistency", "volume", "balance", "volume_trend"} else "medium"
    focus["reason"] = template["detail"]
    focus["supporting_signals"] = [s for s in signals if RULE_ID_TO_FOCUS_KEY.get(str(s.get("rule_id", ""))) in {primary_key, secondary_key}]
    focus.update(_target_fields(primary_key, metrics))
    focus["prescription"] = _augment_prescription(focus, primary_key, metrics)
    return focus
