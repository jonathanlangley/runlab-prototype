
from __future__ import annotations


def rule_consistency(metrics: dict) -> list[dict]:
    consistency = metrics["consistency_label"]

    if consistency in {"very low", "low"}:
        return [
            {
                "title": "Low consistency",
                "detail": "Training frequency over the last 28 days is low. Building consistency is likely the highest priority.",
                "priority": "high",
                "rule_id": "consistency",
            }
        ]

    if consistency == "moderate":
        return [
            {
                "title": "Moderate consistency",
                "detail": "There is a reasonable training rhythm, but more regular frequency would likely improve adaptation.",
                "priority": "medium",
                "rule_id": "consistency",
            }
        ]

    return [
        {
            "title": "Strong consistency",
            "detail": "Training frequency is solid. This creates a good base for progression.",
            "priority": "low",
            "rule_id": "consistency",
        }
    ]


def rule_volume(metrics: dict) -> list[dict]:
    recent_km = metrics["recent_avg_weekly_km"]
    volume_trend = metrics["volume_trend"]
    volume_pattern = metrics["volume_pattern"]
    signals: list[dict] = []

    if recent_km < 50:
        signals.append(
            {
                "title": "Low volume",
                "detail": "Average weekly volume is likely too low to support stronger aerobic development for a performance-focused runner.",
                "priority": "high",
                "rule_id": "volume",
            }
        )
    elif recent_km < 70:
        signals.append(
            {
                "title": "Moderate volume",
                "detail": "Weekly volume is reasonable, but there may be room to increase it if the goal is further performance development.",
                "priority": "medium",
                "rule_id": "volume",
            }
        )
    else:
        signals.append(
            {
                "title": "Solid volume base",
                "detail": "Weekly volume is in a broadly supportive range for continued development.",
                "priority": "low",
                "rule_id": "volume",
            }
        )

    if volume_trend == "flat":
        signals.append(
            {
                "title": "Volume plateau",
                "detail": "Average weekly distance is broadly flat. This may indicate a plateau unless stimulus changes elsewhere.",
                "priority": "medium",
                "rule_id": "volume_trend",
            }
        )
    elif volume_trend == "declining":
        signals.append(
            {
                "title": "Declining volume",
                "detail": "Recent weekly distance is lower than the previous block. This could reduce aerobic progression.",
                "priority": "high",
                "rule_id": "volume_trend",
            }
        )
    else:
        signals.append(
            {
                "title": "Volume progressing",
                "detail": "Recent weekly distance is moving upward, which may support continued aerobic development if tolerated well.",
                "priority": "low",
                "rule_id": "volume_trend",
            }
        )

    if volume_pattern == "peaked_then_dipped":
        signals.append(
            {
                "title": "Recent dip after peak volume",
                "detail": metrics["volume_pattern_detail"],
                "priority": "medium",
                "rule_id": "volume_pattern",
            }
        )
    elif volume_pattern == "volatile":
        signals.append(
            {
                "title": "Volatile weekly volume",
                "detail": metrics["volume_pattern_detail"],
                "priority": "medium",
                "rule_id": "volume_pattern",
            }
        )

    return signals


def rule_threshold(metrics: dict) -> list[dict]:
    threshold_count = metrics["threshold_sessions_last_28"]
    threshold_per_week = metrics["threshold_sessions_per_week"]

    if threshold_count == 0:
        return [
            {
                "title": "No threshold work detected",
                "detail": "No threshold sessions were identified in the last 28 days. This may limit sustained pace development.",
                "priority": "high",
                "rule_id": "threshold",
            }
        ]

    if threshold_per_week < 1.0:
        return [
            {
                "title": "Limited threshold stimulus",
                "detail": "Threshold work is present but not yet regular enough to strongly support sustained pace development.",
                "priority": "medium",
                "rule_id": "threshold",
            }
        ]

    return [
        {
            "title": "Threshold support in place",
            "detail": "Threshold work is showing up regularly enough to support continued development.",
            "priority": "low",
            "rule_id": "threshold",
        }
    ]


def rule_long_run(metrics: dict) -> list[dict]:
    long_runs_last_28 = metrics["long_runs_last_28"]

    if long_runs_last_28 == 0:
        return [
            {
                "title": "No long run stimulus",
                "detail": "No long runs were detected in the last 28 days. This may limit endurance progression.",
                "priority": "high",
                "rule_id": "long_run",
            }
        ]

    if long_runs_last_28 < 3:
        return [
            {
                "title": "Minimal long run stimulus",
                "detail": "Long run stimulus is present but inconsistent. This may limit endurance and overall durability.",
                "priority": "medium",
                "rule_id": "long_run",
            }
        ]

    return [
        {
            "title": "Long run support in place",
            "detail": "A regular long run pattern is present, which supports endurance development.",
            "priority": "low",
            "rule_id": "long_run",
        }
    ]


def rule_balance(metrics: dict) -> list[dict]:
    quality_pct = metrics["quality_run_pct"]
    easy_pct = metrics["easy_run_pct"]
    vo2_per_week = metrics.get("vo2_sessions_per_week", metrics.get("interval_sessions_per_week", 0))
    threshold_per_week = metrics.get("threshold_sessions_per_week", 0)

    signals: list[dict] = []

    if quality_pct > 0.40 and easy_pct < 0.70:
        signals.append(
            {
                "title": "Intensity imbalance",
                "detail": "A large share of runs are quality sessions. The training mix may be too intensity-heavy to maximise adaptation.",
                "priority": "high",
                "rule_id": "balance",
            }
        )

    if quality_pct < 0.10:
        signals.append(
            {
                "title": "Low quality density",
                "detail": "There is very little threshold or VO2 work in the current training mix.",
                "priority": "medium",
                "rule_id": "balance",
            }
        )

    if vo2_per_week >= 1.0 and threshold_per_week < 0.75:
        signals.append(
            {
                "title": "VO2-heavy relative to threshold",
                "detail": "VO2 work is showing up more often than threshold work. The pattern may be leaning too hard toward top-end intensity without enough threshold support underneath.",
                "priority": "medium",
                "rule_id": "balance",
            }
        )

    if not signals:
        signals.append(
            {
                "title": "Training balance broadly healthy",
                "detail": "The current mix of easy and quality running looks broadly supportive.",
                "priority": "low",
                "rule_id": "balance",
            }
        )

    return signals


def rule_progression(metrics: dict) -> list[dict]:
    confidence = metrics["progression_confidence"]
    consistency = metrics["consistency_label"]
    recent_km = metrics["recent_avg_weekly_km"]

    strong_structure = (
        consistency == "high"
        and recent_km >= 50
        and metrics["threshold_sessions_per_week"] >= 1.0
        and metrics["long_runs_last_28"] >= 3
    )

    if strong_structure and confidence == "low":
        return [
            {
                "title": "Well-structured but static",
                "detail": "The training pattern looks broadly sound, but several key levers now appear flat rather than progressing.",
                "priority": "medium",
                "rule_id": "progression",
            }
        ]

    flat_count = int(metrics.get("progression_flat_count", 0) or 0)
    if flat_count >= 2:
        return [
            {
                "title": "Limited progression across key levers",
                "detail": "More than one important training component is currently flat. A clearer progression signal may be needed.",
                "priority": "medium",
                "rule_id": "progression",
            }
        ]

    return [
        {
            "title": "Progression signals acceptable",
            "detail": "The current pattern still shows enough movement across key training components.",
            "priority": "low",
            "rule_id": "progression",
        }
    ]


def derive_signals(metrics: dict) -> list[dict]:
    all_signals: list[dict] = []
    all_signals.extend(rule_consistency(metrics))
    all_signals.extend(rule_volume(metrics))
    all_signals.extend(rule_threshold(metrics))
    all_signals.extend(rule_long_run(metrics))
    all_signals.extend(rule_balance(metrics))
    all_signals.extend(rule_progression(metrics))

    priority_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(
        all_signals,
        key=lambda s: (priority_order.get(s["priority"], 9), s["title"])
    )
