from __future__ import annotations

from typing import Any

import pandas as pd

from src.ai_explainer import generate_ai_explanation
from src.data_loader import clean_data
from src.focus import determine_focus
from src.hierarchy import build_training_hierarchy
from src.metrics import overall_metrics, weekly_summary
from src.signals import derive_signals


SIGNAL_CATEGORY_BY_RULE_ID = {
    "consistency": "consistency",
    "volume": "volume",
    "volume_trend": "volume",
    "volume_pattern": "volume",
    "threshold": "quality",
    "long_run": "structure",
    "balance": "balance",
    "progression": "progression",
}

PRIORITY_RANK = {
    "high": 0,
    "medium": 1,
    "low": 2,
}


def get_signal_category(signal: dict[str, Any]) -> str:
    rule_id = str(signal.get("rule_id", "") or "").lower()
    return SIGNAL_CATEGORY_BY_RULE_ID.get(rule_id, "other")


def build_top_signals(signals: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    """
    Select a balanced set of top signals for the UI.

    This avoids showing three near-identical messages from the same area,
    such as low volume, volume plateau, and recent volume dip.
    """
    if not signals:
        return []

    selected: list[dict[str, Any]] = []
    selected_ids: set[int] = set()

    preferred_category_order = [
        "consistency",
        "volume",
        "quality",
        "structure",
        "balance",
        "progression",
        "other",
    ]

    sorted_signals = sorted(
        signals,
        key=lambda signal: (
            PRIORITY_RANK.get(str(signal.get("priority", "low")).lower(), 9),
            str(signal.get("title", "")),
        ),
    )

    for category in preferred_category_order:
        category_matches = [
            signal
            for signal in sorted_signals
            if get_signal_category(signal) == category and id(signal) not in selected_ids
        ]

        if category_matches:
            chosen = category_matches[0]
            selected.append(chosen)
            selected_ids.add(id(chosen))

        if len(selected) >= limit:
            return selected

    for signal in sorted_signals:
        if id(signal) in selected_ids:
            continue

        selected.append(signal)
        selected_ids.add(id(signal))

        if len(selected) >= limit:
            break

    return selected


def get_recommendation_confidence(
    metrics: dict[str, Any],
    signals: list[dict[str, Any]],
    focus: dict[str, Any],
) -> tuple[str, str]:
    """
    Add a plain-English confidence label to the recommendation.

    This is based on signal strength and data depth, not on model certainty.
    """
    high_count = sum(1 for signal in signals if signal.get("priority") == "high")
    medium_count = sum(1 for signal in signals if signal.get("priority") == "medium")
    focus_priority = str(focus.get("priority", "low")).lower()
    weeks_of_data = int(metrics.get("weeks_of_data", 0) or 0)

    if focus_priority == "high" and high_count >= 2 and weeks_of_data >= 4:
        return (
            "High confidence",
            "This recommendation is strongly supported by multiple recent training signals.",
        )

    if focus_priority in {"high", "medium"} or medium_count >= 2:
        return (
            "Medium confidence",
            "This is the clearest current recommendation, but it should be reviewed after another short block of data.",
        )

    return (
        "Lower confidence",
        "The pattern looks broadly healthy, so treat this as a gentle nudge rather than a major correction.",
    )


def _soften_step(step: str, prefix: str) -> str:
    text = str(step or "").strip()
    if not text:
        return text

    lower_text = text.lower()
    already_soft = (
        lower_text.startswith("aim ")
        or lower_text.startswith("aim to ")
        or lower_text.startswith("consider ")
        or lower_text.startswith("keep ")
        or lower_text.startswith("avoid ")
        or lower_text.startswith("reassess ")
        or lower_text.startswith("use ")
        or lower_text.startswith("hold ")
    )

    if already_soft:
        return text

    return f"{prefix} {text[0].lower()}{text[1:]}"


def adapt_prescription_for_confidence(focus: dict[str, Any], confidence_label: str) -> dict[str, Any]:
    """
    Adjust action wording so lower-confidence recommendations sound less absolute.
    """
    updated_focus = dict(focus)
    steps = list(updated_focus.get("prescription", []) or [])

    if confidence_label == "High confidence":
        adapted_steps = steps
    elif confidence_label == "Medium confidence":
        adapted_steps = [_soften_step(step, "Aim to") for step in steps]
    else:
        adapted_steps = [_soften_step(step, "Consider") for step in steps]

    updated_focus["prescription"] = adapted_steps
    return updated_focus


def add_recommendation_confidence(
    metrics: dict[str, Any],
    signals: list[dict[str, Any]],
    focus: dict[str, Any],
) -> dict[str, Any]:
    confidence_label, confidence_note = get_recommendation_confidence(metrics, signals, focus)
    updated_focus = adapt_prescription_for_confidence(focus, confidence_label)
    updated_focus["confidence_label"] = confidence_label
    updated_focus["confidence_note"] = confidence_note
    return updated_focus


def build_summary_line(metrics: dict[str, Any], focus: dict[str, Any]) -> str:
    consistency = str(metrics.get("consistency_label", "unknown")).replace("_", " ")
    weekly_km = int(round(float(metrics.get("recent_avg_weekly_km", 0) or 0)))
    target_volume_range = focus.get("target_volume_range")

    if target_volume_range:
        return (
            f"The current pattern suggests that the harder work is under-supported, "
            f"with {consistency} consistency, around {weekly_km} km per week recently, "
            f"and a better short-term target of roughly {target_volume_range[0]}-{target_volume_range[1]} km."
        )

    focus_text = str(focus.get("headline", "Maintain consistency and progress gradually"))
    return (
        f"Current pattern suggests {focus_text.lower()}, "
        f"with {consistency} consistency and around {weekly_km} km per week recently."
    )


def build_reasoning(metrics: dict[str, Any], signals: list[dict[str, Any]], limit: int = 4) -> list[str]:
    if signals:
        return [str(signal.get("detail", "")) for signal in signals[:limit] if signal.get("detail")]

    fallback_reasons = [
        f"Consistency: {str(metrics.get('consistency_label', 'unknown')).title()}",
        f"Recent weekly volume: {metrics.get('recent_avg_weekly_km', 'N/A')} km",
        f"Threshold sessions in last 28 days: {metrics.get('threshold_sessions_last_28', 'N/A')}",
        f"Long runs in last 28 days: {metrics.get('long_runs_last_28', 'N/A')}",
    ]
    return fallback_reasons[:limit]


def build_decision(
    metrics: dict[str, Any],
    focus: dict[str, Any],
    top_signals: list[dict[str, Any]],
    hierarchy: dict[str, Any],
) -> dict[str, str]:
    target_volume_range = focus.get("target_volume_range")
    primary_focus = focus.get("headline", "Maintain consistency and progress gradually")

    if target_volume_range:
        secondary_focus = f"Move weekly volume toward {target_volume_range[0]}-{target_volume_range[1]} km"
    elif len(top_signals) > 1:
        secondary_focus = top_signals[1].get("title", "Keep core structure stable")
    else:
        secondary_focus = "Keep core structure stable"

    maintain = hierarchy["supportive"][0]["label"] if hierarchy.get("supportive") else "Current healthy elements"

    avoid = (
        "Adding more intensity"
        if "support" in primary_focus.lower() or "vo2" in primary_focus.lower()
        else "Changing multiple levers at once"
    )

    return {
        "primary_focus": primary_focus,
        "secondary_focus": secondary_focus,
        "maintain": maintain,
        "avoid": avoid,
    }


def generate_runlab_report(df_raw: pd.DataFrame) -> dict[str, Any]:
    df = clean_data(df_raw)
    weekly = weekly_summary(df)
    metrics = overall_metrics(df, weekly)
    signals = derive_signals(metrics)

    focus = determine_focus(metrics, signals)
    focus = add_recommendation_confidence(metrics, signals, focus)

    ai_text, used_ai = generate_ai_explanation(metrics, signals, focus)
    hierarchy = build_training_hierarchy(metrics, focus)
    top_signals = build_top_signals(signals)

    return {
        "df": df,
        "weekly": weekly,
        "metrics": metrics,
        "signals": signals,
        "top_signals": top_signals,
        "focus": focus,
        "ai_text": ai_text,
        "used_ai": used_ai,
        "hierarchy": hierarchy,
        "summary_line": build_summary_line(metrics, focus),
        "reasoning": build_reasoning(metrics, signals),
        "decision": build_decision(metrics, focus, top_signals, hierarchy),
    }
