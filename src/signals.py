from __future__ import annotations


def rule_consistency(metrics: dict) -> list[dict]:
    consistency = metrics["consistency_label"]

    if consistency == "low":
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

    if quality_pct > 0.40 and easy_pct < 0.70:
        return [
            {
                "title": "Intensity imbalance",
                "detail": "A large share of runs are quality sessions. The training mix may be too intensity-heavy to maximise adaptation.",
                "priority": "high",
                "rule_id": "balance",
            }
        ]

    if quality_pct < 0.10:
        return [
            {
                "title": "Low quality density",
                "detail": "There is very little threshold or interval work in the current training mix.",
                "priority": "medium",
                "rule_id": "balance",
            }
        ]

    return [
        {
            "title": "Training balance broadly healthy",
            "detail": "The current mix of easy and quality running looks broadly supportive.",
            "priority": "low",
            "rule_id": "balance",
        }
    ]


def rule_progression(metrics: dict) -> list[dict]:
    confidence = metrics["progression_confidence"]
    consistency = metrics["consistency_label"]
    recent_km = metrics["recent_avg_weekly_km"]

    strong_structure = (
        consistency == "high"
        and recent_km >= 50
        and metrics["threshold_sessions_per_week"] >= 1.0
        and metrics["long_runs_last_28"] >= 3
        and metrics["quality_run_pct"] >= 0.10
        and metrics["quality_run_pct"] <= 0.40
    )

    flat_count = metrics["progression_flat_count"]
    rising_count = metrics["progression_rising_count"]

    if confidence == "low":
        return []

    if strong_structure and flat_count >= 3 and rising_count == 0:
        return [
            {
                "title": "Well-structured but static",
                "detail": "The overall training pattern looks solid, but the main training levers are not progressing. This suggests that the current stimulus may no longer be enough.",
                "priority": "medium",
                "rule_id": "progression",
            }
        ]

    if confidence in {"medium", "high"} and flat_count >= 3 and metrics["volume_trend"] == "flat":
        return [
            {
                "title": "Limited progression across key levers",
                "detail": "Several core training components are flat across recent blocks. Progress may stall unless one of the main levers is progressed.",
                "priority": "medium",
                "rule_id": "progression",
            }
        ]

    if rising_count >= 2:
        return [
            {
                "title": "Progression signals present",
                "detail": "Multiple training components are moving in the right direction, which supports continued development if the load remains sustainable.",
                "priority": "low",
                "rule_id": "progression",
            }
        ]

    return []


RULES = [
    rule_consistency,
    rule_volume,
    rule_threshold,
    rule_long_run,
    rule_balance,
    rule_progression,
]


def derive_signals(metrics: dict) -> list[dict]:
    signals: list[dict] = []

    for rule in RULES:
        rule_signals = rule(metrics)
        if rule_signals:
            signals.extend(rule_signals)

    priority_order = {"high": 0, "medium": 1, "low": 2}
    signals.sort(key=lambda s: (priority_order.get(s["priority"], 3), s["title"]))

    return signals