from __future__ import annotations

from typing import Any


FOCUS_RULES: dict[str, dict[str, Any]] = {
    "consistency": {
        "headline": "Build a repeatable running rhythm first",
        "limiter": "Consistency",
        "detail": "Training frequency is the main limiter. The next block should make the week more repeatable before adding extra volume or intensity.",
        "timeframe": "2-3 weeks",
    },
    "volume": {
        "headline": "Build aerobic volume before adding more intensity",
        "limiter": "Aerobic volume",
        "detail": "Weekly volume is the clearest limiter. The next gain is more likely to come from easy aerobic running than from another hard session.",
        "timeframe": "3-4 weeks",
    },
    "aerobic_support": {
        "headline": "Support your quality work with more easy volume",
        "limiter": "Aerobic support",
        "detail": "Harder running is already present, but it needs more easy running underneath it. The priority is to make the quality work better supported, not harder.",
        "timeframe": "3-6 weeks",
    },
    "load_stability": {
        "headline": "Stabilise your training load",
        "limiter": "Training load stability",
        "detail": "Recent volume has dipped or become too variable. Rebuild a predictable week before pushing fitness harder.",
        "timeframe": "2-3 weeks",
    },
    "long_run": {
        "headline": "Make the long run a weekly anchor",
        "limiter": "Long run stimulus",
        "detail": "The long run is missing or inconsistent. A regular comfortable long run will improve durability and support the rest of the week.",
        "timeframe": "3-4 weeks",
    },
    "threshold": {
        "headline": "Add a controlled threshold stimulus",
        "limiter": "Threshold support",
        "detail": "Threshold work is missing or too irregular. A controlled threshold session will improve sustained pace without the fatigue cost of another race-level effort.",
        "timeframe": "3-4 weeks",
    },
    "quality": {
        "headline": "Add one clear quality stimulus",
        "limiter": "Quality stimulus",
        "detail": "The base is present, but the week needs one purposeful faster session to create a clearer performance signal.",
        "timeframe": "3-4 weeks",
    },
    "progression": {
        "headline": "Create one clear progression signal",
        "limiter": "Progression",
        "detail": "The pattern is broadly sound, but too many levers are static. The next block should progress one thing only.",
        "timeframe": "2-4 weeks",
    },
    "maintenance": {
        "headline": "Maintain the current rhythm and progress carefully",
        "limiter": "No major limiter",
        "detail": "The pattern is broadly healthy. The next step is small, controlled progression rather than a major correction.",
        "timeframe": "2-4 weeks",
    },
}


PRIMARY_ORDER = [
    "consistency",
    "aerobic_support",
    "volume",
    "load_stability",
    "long_run",
    "threshold",
    "quality",
    "progression",
    "maintenance",
]


SIGNAL_TO_DOMAIN = {
    "consistency": "consistency",
    "volume": "volume",
    "volume_trend": "load_stability",
    "volume_pattern": "load_stability",
    "long_run": "long_run",
    "threshold": "threshold",
    "balance": "aerobic_support",
    "progression": "progression",
}


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int = 0) -> int:
    return int(round(_num(value, default)))


def recommend_volume_target(current_km: float) -> tuple[int, int]:
    current_km = float(current_km or 0)

    if current_km < 30:
        return max(20, int(round(current_km + 8))), int(round(current_km + 15))
    if current_km < 50:
        return int(round(current_km + 8)), int(round(current_km + 12))
    if current_km < 70:
        return int(round(current_km + 5)), int(round(current_km + 8))

    return int(round(current_km + 3)), int(round(current_km + 6))


def recommend_run_days_target(current_run_days_per_week: float) -> int:
    if current_run_days_per_week < 4:
        return 5
    if current_run_days_per_week < 5.5:
        return 6
    return int(round(current_run_days_per_week))


def build_limiter_scores(metrics: dict[str, Any]) -> dict[str, int]:
    run_days = _num(metrics.get("days_with_run_last_28")) / 4.0
    weekly_km = _num(metrics.get("recent_avg_weekly_km"))

    threshold_sessions = _int(metrics.get("threshold_sessions_last_28"))
    vo2_sessions = _int(metrics.get("vo2_sessions_last_28")) + _int(metrics.get("race_sessions_last_28"))
    quality_sessions = threshold_sessions + vo2_sessions

    long_runs = _int(metrics.get("long_runs_last_28"))
    quality_pct = _num(metrics.get("quality_run_pct"))
    easy_pct = _num(metrics.get("easy_run_pct"))

    volume_trend = str(metrics.get("volume_trend", "flat")).lower()
    volume_pattern = str(metrics.get("volume_pattern", "plateau")).lower()

    if run_days < 3:
        consistency = 95
    elif run_days < 4:
        consistency = 82
    elif run_days < 5:
        consistency = 60
    elif run_days < 6:
        consistency = 35
    else:
        consistency = 10

    if weekly_km < 30:
        volume = 92
    elif weekly_km < 50:
        volume = 78
    elif weekly_km < 70:
        volume = 50
    elif weekly_km < 90:
        volume = 25
    else:
        volume = 10

    long_run = 90 if long_runs == 0 else 55 if long_runs <= 2 else 18
    threshold = 85 if threshold_sessions == 0 else 55 if threshold_sessions <= 2 else 15
    quality = 80 if quality_sessions == 0 else 30 if quality_sessions <= 2 else 10

    if quality_pct >= 0.40 and easy_pct < 0.70:
        intensity_balance = 90
    elif quality_pct >= 0.30 and weekly_km < 60:
        intensity_balance = 75
    elif vo2_sessions > threshold_sessions + 1 and weekly_km < 70:
        intensity_balance = 65
    else:
        intensity_balance = 20

    if volume_trend == "declining":
        load_stability = 80
    elif volume_pattern in {"volatile", "peaked_then_dipped"}:
        load_stability = 65
    elif volume_trend == "flat":
        load_stability = 45
    else:
        load_stability = 20

    progression = (
        55
        if volume_pattern == "plateau" and weekly_km >= 60 and quality_sessions >= 3
        else 20
    )

    return {
        "consistency": int(consistency),
        "volume": int(volume),
        "aerobic_support": int(
            max(
                intensity_balance,
                min(volume, 70) if quality_sessions >= 2 and weekly_km < 60 else 0,
            )
        ),
        "load_stability": int(load_stability),
        "long_run": int(long_run),
        "threshold": int(threshold),
        "quality": int(quality),
        "progression": int(progression),
    }


def choose_primary_limiter(metrics: dict[str, Any], scores: dict[str, int]) -> str:
    run_days = _num(metrics.get("days_with_run_last_28")) / 4.0
    weekly_km = _num(metrics.get("recent_avg_weekly_km"))
    quality_pct = _num(metrics.get("quality_run_pct"))
    easy_pct = _num(metrics.get("easy_run_pct"))

    quality_sessions = _int(metrics.get("quality_runs_last_28"))
    long_runs = _int(metrics.get("long_runs_last_28"))
    threshold_sessions = _int(metrics.get("threshold_sessions_last_28"))

    volume_trend = str(metrics.get("volume_trend", "flat")).lower()

    if run_days < 4:
        return "consistency"
    if quality_pct >= 0.35 and easy_pct < 0.70 and weekly_km < 70:
        return "aerobic_support"
    if weekly_km < 50:
        return "volume"
    if volume_trend == "declining" and weekly_km >= 50:
        return "load_stability"
    if long_runs == 0:
        return "long_run"
    if threshold_sessions == 0 and quality_sessions <= 2:
        return "threshold"
    if quality_sessions == 0 and weekly_km >= 50:
        return "quality"

    ranked = sorted(
        scores.items(),
        key=lambda item: (
            -item[1],
            PRIMARY_ORDER.index(item[0]) if item[0] in PRIMARY_ORDER else 99,
        ),
    )

    primary, score = ranked[0]
    return primary if score >= 55 else "maintenance"


def choose_secondary_limiter(primary: str, scores: dict[str, int]) -> str | None:
    allowed_by_primary = {
        "consistency": {"volume", "long_run"},
        "volume": {"long_run", "threshold"},
        "aerobic_support": {"volume", "long_run", "threshold"},
        "load_stability": {"volume", "long_run"},
        "long_run": {"volume", "threshold"},
        "threshold": {"volume", "long_run"},
        "quality": {"long_run", "volume"},
        "progression": {"volume", "threshold", "long_run"},
        "maintenance": set(),
    }

    allowed = allowed_by_primary.get(primary, set())
    candidates = [
        (key, value)
        for key, value in scores.items()
        if key in allowed and key != primary and value >= 55
    ]

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (
            -item[1],
            PRIMARY_ORDER.index(item[0]) if item[0] in PRIMARY_ORDER else 99,
        )
    )

    return candidates[0][0]


def build_next_week_plan(
    metrics: dict[str, Any],
    primary: str,
    secondary: str | None = None,
) -> dict[str, Any]:
    current_km = _num(metrics.get("recent_avg_weekly_km"))
    current_run_days = _num(metrics.get("days_with_run_last_28")) / 4.0
    current_quality = _num(metrics.get("quality_runs_last_28")) / 4.0
    current_long_runs = _num(metrics.get("long_runs_last_28")) / 4.0

    target_km = recommend_volume_target(current_km)
    target_days = recommend_run_days_target(current_run_days)

    if primary == "consistency":
        target_km = (
            (int(round(current_km)), int(round(current_km + 5)))
            if current_km >= 30
            else recommend_volume_target(current_km)
        )
        quality_target = 0 if current_run_days < 3 else 1
    elif primary in {"volume", "aerobic_support", "threshold", "quality"}:
        quality_target = 1
    elif primary == "long_run":
        quality_target = max(1, int(round(current_quality))) if current_quality > 0 else 1
    else:
        quality_target = max(1, min(2, int(round(current_quality)) or 1))

    if primary == "load_stability":
        target_km = (
            max(0, int(round(current_km * 0.95))),
            int(round(current_km * 1.05)),
        )
        quality_target = max(1, min(2, int(round(current_quality)) or 1))

    long_run_target = (
        "weekly"
        if primary in {"volume", "aerobic_support", "long_run", "threshold"}
        or current_long_runs < 0.75
        else "maintain"
    )

    return {
        "run_days": target_days,
        "target_km_range": target_km,
        "quality_sessions": quality_target,
        "long_run": long_run_target,
        "easy_volume": "increase"
        if primary in {"volume", "aerobic_support", "consistency"}
        else "maintain",
        "avoid": "adding another hard session"
        if primary in {"volume", "aerobic_support", "consistency"}
        else "changing several levers at once",
    }


def build_prescription(metrics: dict[str, Any], focus: dict[str, Any]) -> list[str]:
    plan = focus["next_week_plan"]
    km_low, km_high = plan["target_km_range"]
    primary = focus.get("primary_key")

    if primary == "consistency":
        return [
            f"Run {plan['run_days']} days if recovery allows.",
            f"Keep total volume controlled at around {km_low}-{km_high} km.",
        ]

    if primary == "volume":
        return [
            f"Build toward {km_low}-{km_high} km, mostly through easy running.",
            "Keep intensity stable while the aerobic base improves.",
        ]

    if primary == "aerobic_support":
        return [
            f"Build toward {km_low}-{km_high} km with more easy running.",
            "Keep one quality session, but do not add another hard day yet.",
        ]

    if primary == "load_stability":
        return [
            f"Keep next week within roughly {km_low}-{km_high} km.",
            "Prioritise a repeatable week over a bigger training stimulus.",
        ]

    if primary == "long_run":
        return [
            "Include one comfortable long run this week.",
            "Keep the long run controlled rather than turning it into another hard effort.",
        ]

    if primary == "threshold":
        return [
            "Add one controlled threshold session.",
            "Keep it comfortably hard, not race effort.",
        ]

    if primary == "quality":
        return [
            "Add one purposeful faster session.",
            "Keep the rest of the week easy enough to absorb it.",
        ]

    if primary == "progression":
        return [
            "Progress one lever only this week.",
            "Avoid increasing volume, intensity and long-run load at the same time.",
        ]

    return [
        "Maintain the current rhythm.",
        "Make only one small progression if recovery feels good.",
    ]


def build_decision_confidence(
    metrics: dict[str, Any],
    scores: dict[str, int],
    primary: str,
    secondary: str | None,
) -> tuple[str, str, int]:
    weeks = _int(metrics.get("weeks_of_data"))
    primary_score = scores.get(primary, 0)
    second_score = scores.get(secondary, 0) if secondary else 0
    separation = primary_score - second_score

    data_score = 20 if weeks >= 6 else 12 if weeks >= 4 else 6
    score = min(100, max(0, primary_score + data_score + max(0, separation // 2) - 20))

    if score >= 75:
        return (
            "High confidence",
            "The main limiter is clear and supported by enough recent training data.",
            score,
        )
    if score >= 55:
        return (
            "Medium confidence",
            "This is the clearest next focus, but it should be reviewed after another short block.",
            score,
        )

    return (
        "Lower confidence",
        "The pattern is either broadly healthy or the data is limited, so treat this as a gentle nudge.",
        score,
    )


def determine_focus(metrics: dict[str, Any], signals: list[dict[str, Any]]) -> dict[str, Any]:
    scores = build_limiter_scores(metrics)
    primary = choose_primary_limiter(metrics, scores)
    secondary = choose_secondary_limiter(primary, scores)
    template = FOCUS_RULES[primary]

    focus = dict(template)
    focus["primary_key"] = primary
    focus["secondary_key"] = secondary
    focus["primary_limiter"] = template["limiter"]
    focus["secondary_focus"] = FOCUS_RULES[secondary]["headline"] if secondary else None
    focus["priority"] = (
        "low"
        if primary == "maintenance"
        else "high"
        if scores.get(primary, 0) >= 75
        else "medium"
    )
    focus["reason"] = template["detail"]
    focus["decision_scores"] = scores
    focus["target_volume_range"] = (
        recommend_volume_target(_num(metrics.get("recent_avg_weekly_km")))
        if primary in {"volume", "aerobic_support", "consistency", "long_run", "threshold"}
        else None
    )
    focus["target_run_days_per_week"] = (
        recommend_run_days_target(_num(metrics.get("days_with_run_last_28")) / 4.0)
        if primary in {"consistency", "volume", "aerobic_support"}
        else None
    )
    focus["next_week_plan"] = build_next_week_plan(metrics, primary, secondary)
    focus["prescription"] = build_prescription(metrics, focus)

    confidence_label, confidence_note, confidence_score = build_decision_confidence(
        metrics,
        scores,
        primary,
        secondary,
    )

    focus["confidence_label"] = confidence_label
    focus["confidence_note"] = confidence_note
    focus["confidence_score"] = confidence_score

    relevant = {primary, secondary}
    focus["supporting_signals"] = [
        signal
        for signal in signals
        if SIGNAL_TO_DOMAIN.get(str(signal.get("rule_id", ""))) in relevant
    ]

    return focus