from __future__ import annotations

from typing import Any

import pandas as pd

from src.ai_explainer import generate_ai_explanation
from src.balance import (
    build_balance_comparison_df,
    build_balance_interpretation,
    build_detailed_balance_df,
)
from src.data_loader import clean_data
from src.focus import determine_focus
from src.hierarchy import build_training_hierarchy
from src.metrics import overall_metrics, weekly_summary
from src.signals import derive_signals
from src.structure import (
    build_structure_gaps,
    build_weekly_structure,
    get_target_weekly_structure,
)
from src.ui_text import (
    build_focus_diagnosis,
    build_supporting_metrics,
    build_why_this_matters,
)


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

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

CATEGORY_ORDER = [
    "consistency",
    "volume",
    "balance",
    "structure",
    "quality",
    "progression",
    "other",
]


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _format_km(value: Any) -> str:
    return str(int(round(_num(value))))


def get_signal_category(signal: dict[str, Any]) -> str:
    rule_id = str(signal.get("rule_id", "")).lower()
    return SIGNAL_CATEGORY_BY_RULE_ID.get(rule_id, "other")


def build_top_signals(
    signals: list[dict[str, Any]],
    limit: int = 3,
) -> list[dict[str, Any]]:
    if not signals:
        return []

    sorted_signals = sorted(
        signals,
        key=lambda signal: (
            PRIORITY_RANK.get(str(signal.get("priority", "low")).lower(), 9),
            str(signal.get("title", "")),
        ),
    )

    selected: list[dict[str, Any]] = []
    used_ids: set[int] = set()

    for category in CATEGORY_ORDER:
        matches = [
            signal
            for signal in sorted_signals
            if get_signal_category(signal) == category
            and id(signal) not in used_ids
        ]

        if matches:
            selected.append(matches[0])
            used_ids.add(id(matches[0]))

        if len(selected) >= limit:
            return selected

    for signal in sorted_signals:
        if id(signal) not in used_ids:
            selected.append(signal)
            used_ids.add(id(signal))

        if len(selected) >= limit:
            break

    return selected


def build_summary_line(metrics: dict[str, Any], focus: dict[str, Any]) -> str:
    title, summary = build_focus_diagnosis(focus, metrics)
    return f"{title}. {summary}"


def build_decision(
    focus: dict[str, Any],
    hierarchy: dict[str, Any],
) -> dict[str, str]:
    secondary = focus.get("secondary_focus") or "Keep every other lever stable"
    supportive = hierarchy.get("supportive", [])
    maintain = supportive[0]["label"] if supportive else "Current healthy elements"

    plan = focus.get("next_week_plan", {})
    avoid = plan.get("avoid", "changing several levers at once")

    return {
        "primary_focus": focus.get("headline", "Maintain consistency"),
        "secondary_focus": secondary,
        "maintain": maintain,
        "avoid": avoid,
    }


def build_next_week_rows(
    metrics: dict[str, Any],
    focus: dict[str, Any],
) -> list[dict[str, str]]:
    plan = focus.get("next_week_plan", {})

    target_km_range = plan.get("target_km_range", (0, 0))
    if isinstance(target_km_range, (list, tuple)) and len(target_km_range) >= 2:
        km_low, km_high = target_km_range[0], target_km_range[1]
    else:
        km_low, km_high = 0, 0

    current_run_days = round(_num(metrics.get("days_with_run_last_28")) / 4.0, 1)
    current_quality = round(_num(metrics.get("quality_runs_last_28")) / 4.0, 1)
    current_long = round(_num(metrics.get("long_runs_last_28")) / 4.0, 1)

    long_next = (
        "1 most weeks"
        if plan.get("long_run") == "weekly"
        else str(plan.get("long_run", "maintain"))
    )

    return [
        {
            "Element": "Run days",
            "Current": f"{current_run_days}/week",
            "Next week": f"{plan.get('run_days', 'n/a')}/week",
        },
        {
            "Element": "Weekly distance",
            "Current": f"{_format_km(metrics.get('recent_avg_weekly_km'))} km",
            "Next week": f"{km_low}-{km_high} km",
        },
        {
            "Element": "Quality",
            "Current": f"{current_quality}/week",
            "Next week": f"{plan.get('quality_sessions', 'n/a')}/week",
        },
        {
            "Element": "Long run",
            "Current": f"{current_long}/week",
            "Next week": long_next,
        },
    ]


def unpack_balance_result(result: Any) -> tuple[pd.DataFrame, int]:
    """
    Handles both old and newer balance return shapes.

    Expected:
    - old/new stable shape: (balance_df, total_run_days)
    - possible expanded shape: (balance_df, total_run_days, ...)
    """
    if isinstance(result, tuple) and len(result) >= 2:
        balance_df = result[0]
        total_run_days = int(result[1] or 0)
        return balance_df, total_run_days

    raise ValueError(
        "build_balance_comparison_df must return at least "
        "(balance_df, total_run_days)."
    )


def generate_runlab_report(df_raw: pd.DataFrame) -> dict[str, Any]:
    df = clean_data(df_raw)

    weekly = weekly_summary(df)
    metrics = overall_metrics(df, weekly)
    signals = derive_signals(metrics)

    focus = determine_focus(metrics, signals)
    hierarchy = build_training_hierarchy(metrics, focus)
    top_signals = build_top_signals(signals)

    balance_result = build_balance_comparison_df(df, focus)
    balance_df, total_run_days = unpack_balance_result(balance_result)

    detailed_balance_df = build_detailed_balance_df(df, focus)
    balance_note = build_balance_interpretation(balance_df, focus, total_run_days)

    weekly_structure = build_weekly_structure(metrics)
    target_structure = get_target_weekly_structure(focus, total_run_days)
    structure_gaps = build_structure_gaps(metrics, focus, total_run_days)

    diagnosis_title, diagnosis_summary = build_focus_diagnosis(focus, metrics)
    why_points = build_why_this_matters(metrics, top_signals, focus)
    supporting_metrics = build_supporting_metrics(metrics)

    ai_text = generate_ai_explanation(metrics, signals, focus)
    used_ai = True

    return {
        "df": df,
        "weekly": weekly,
        "metrics": metrics,
        "signals": signals,
        "top_signals": top_signals,
        "focus": focus,
        "hierarchy": hierarchy,
        "decision": build_decision(focus, hierarchy),
        "summary_line": build_summary_line(metrics, focus),
        "diagnosis_title": diagnosis_title,
        "diagnosis_summary": diagnosis_summary,
        "why_points": why_points,
        "supporting_metrics": supporting_metrics,
        "ai_text": ai_text,
        "used_ai": used_ai,
        "balance_df": balance_df,
        "detailed_balance_df": detailed_balance_df,
        "balance_note": balance_note,
        "total_run_days": total_run_days,
        "weekly_structure": weekly_structure,
        "target_weekly_structure": target_structure,
        "structure_gaps": structure_gaps,
        "next_week_rows": build_next_week_rows(metrics, focus),
    }