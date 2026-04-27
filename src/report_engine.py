from __future__ import annotations

from typing import Any

import pandas as pd

from src.ai_explainer import generate_ai_explanation
from src.balance import build_balance_comparison_df, build_balance_interpretation, build_detailed_balance_df
from src.data_loader import clean_data
from src.focus import determine_focus
from src.hierarchy import build_training_hierarchy
from src.metrics import overall_metrics, weekly_summary
from src.signals import derive_signals
from src.structure import build_structure_gaps, build_weekly_structure, get_target_weekly_structure
from src.ui_text import build_focus_diagnosis, build_supporting_metrics, build_why_this_matters

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
CATEGORY_ORDER = ["consistency", "volume", "balance", "structure", "quality", "progression", "other"]


def get_signal_category(signal: dict[str, Any]) -> str:
    return SIGNAL_CATEGORY_BY_RULE_ID.get(str(signal.get("rule_id", "")).lower(), "other")


def build_top_signals(signals: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    if not signals:
        return []

    sorted_signals = sorted(
        signals,
        key=lambda s: (PRIORITY_RANK.get(str(s.get("priority", "low")).lower(), 9), str(s.get("title", ""))),
    )

    selected: list[dict[str, Any]] = []
    used_ids: set[int] = set()
    for category in CATEGORY_ORDER:
        matches = [s for s in sorted_signals if get_signal_category(s) == category and id(s) not in used_ids]
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


def get_recommendation_confidence(metrics: dict[str, Any], signals: list[dict[str, Any]], focus: dict[str, Any]) -> tuple[str, str]:
    weeks = int(metrics.get("weeks_of_data", 0) or 0)
    primary_priority = str(focus.get("priority", "low")).lower()
    high_signals = sum(1 for s in signals if s.get("priority") == "high")
    medium_signals = sum(1 for s in signals if s.get("priority") == "medium")

    if weeks >= 4 and primary_priority == "high" and high_signals >= 1:
        return "High confidence", "The recommendation is supported by recent training data and at least one strong limiting signal."
    if weeks >= 3 and (primary_priority in {"high", "medium"} or medium_signals >= 2):
        return "Medium confidence", "This is the clearest current recommendation, but it should be reviewed after another short block."
    return "Lower confidence", "Treat this as a sensible nudge rather than a major correction because the pattern is either healthy or data is limited."


def _soften_step(step: str, prefix: str) -> str:
    text = str(step or "").strip()
    if not text:
        return text
    lower = text.lower()
    if lower.startswith(("aim", "consider", "keep", "avoid", "use", "hold", "review", "protect", "move")):
        return text
    return f"{prefix} {text[0].lower()}{text[1:]}"


def add_recommendation_confidence(metrics: dict[str, Any], signals: list[dict[str, Any]], focus: dict[str, Any]) -> dict[str, Any]:
    confidence_label, confidence_note = get_recommendation_confidence(metrics, signals, focus)
    updated = dict(focus)
    steps = list(updated.get("prescription", []) or [])
    if confidence_label == "Medium confidence":
        steps = [_soften_step(step, "Aim to") for step in steps]
    elif confidence_label == "Lower confidence":
        steps = [_soften_step(step, "Consider") for step in steps]
    updated["prescription"] = steps[:4]
    updated["confidence_label"] = confidence_label
    updated["confidence_note"] = confidence_note
    return updated


def build_summary_line(metrics: dict[str, Any], focus: dict[str, Any]) -> str:
    diagnosis_title, diagnosis_summary = build_focus_diagnosis(focus, metrics)
    return f"{diagnosis_title}. {diagnosis_summary}"


def build_decision(focus: dict[str, Any], hierarchy: dict[str, Any]) -> dict[str, str]:
    primary = focus.get("headline", "Maintain consistency and progress gradually")
    secondary = focus.get("secondary_focus") or "Keep the rest of the week stable"
    supportive = hierarchy.get("supportive", [])
    maintain = supportive[0]["label"] if supportive else "Current healthy elements"
    primary_key = str(focus.get("primary_key", ""))
    avoid = "Adding more intensity" if primary_key in {"volume", "balance", "consistency"} else "Changing multiple levers at once"
    return {"primary_focus": primary, "secondary_focus": secondary, "maintain": maintain, "avoid": avoid}


def generate_runlab_report(df_raw: pd.DataFrame) -> dict[str, Any]:
    df = clean_data(df_raw)
    weekly = weekly_summary(df)
    metrics = overall_metrics(df, weekly)
    signals = derive_signals(metrics)
    focus = add_recommendation_confidence(metrics, signals, determine_focus(metrics, signals))
    hierarchy = build_training_hierarchy(metrics, focus)
    top_signals = build_top_signals(signals)

    balance_df, total_run_days = build_balance_comparison_df(df, focus)
    detailed_balance_df = build_detailed_balance_df(df, focus)
    balance_note = build_balance_interpretation(balance_df, focus, total_run_days)
    weekly_structure = build_weekly_structure(metrics)
    target_structure = get_target_weekly_structure(focus, total_run_days)
    structure_gaps = build_structure_gaps(metrics, focus, total_run_days)
    diagnosis_title, diagnosis_summary = build_focus_diagnosis(focus, metrics)
    why_points = build_why_this_matters(metrics, top_signals, focus)
    supporting_metrics = build_supporting_metrics(metrics)
    ai_text, used_ai = generate_ai_explanation(metrics, signals, focus)

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
    }
