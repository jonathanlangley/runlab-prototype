from __future__ import annotations

from typing import Any

import pandas as pd

from src.ai_explainer import generate_ai_explanation
from src.data_loader import clean_data
from src.focus import determine_focus
from src.metrics import overall_metrics, weekly_summary
from src.signals import derive_signals


def build_training_hierarchy(metrics: dict[str, Any], focus: dict[str, Any]) -> dict[str, Any]:
    """Create a simple primary / secondary / supportive hierarchy for UI display."""
    primary = {
        "label": focus.get("headline", "Primary limiter"),
        "detail": focus.get("detail", ""),
    }

    secondary: list[dict[str, str]] = []
    supportive: list[dict[str, str]] = []

    threshold_count = int(metrics.get("threshold_sessions_last_28", 0) or 0)
    interval_count = int(metrics.get("interval_sessions_last_28", 0) or 0)
    long_run_count = int(metrics.get("long_runs_last_28", 0) or 0)
    consistency_label = str(metrics.get("consistency_label", "unknown") or "unknown")

    if threshold_count == 0:
        secondary.append(
            {
                "label": "Threshold work",
                "detail": "Absent in the last 4 weeks.",
            }
        )
    elif threshold_count <= 2:
        secondary.append(
            {
                "label": "Threshold work",
                "detail": f"Present but limited, with {threshold_count} session(s) in the last 4 weeks.",
            }
        )
    else:
        supportive.append(
            {
                "label": "Threshold work",
                "detail": f"Present, with {threshold_count} session(s) in the last 4 weeks.",
            }
        )

    if long_run_count == 0:
        secondary.append(
            {
                "label": "Long run stimulus",
                "detail": "Absent in the last 4 weeks.",
            }
        )
    elif long_run_count <= 2:
        secondary.append(
            {
                "label": "Long run stimulus",
                "detail": f"Present but inconsistent, with {long_run_count} long run(s) in the last 4 weeks.",
            }
        )
    else:
        supportive.append(
            {
                "label": "Long run stimulus",
                "detail": f"Present, with {long_run_count} long run(s) in the last 4 weeks.",
            }
        )

    if interval_count > 0:
        supportive.append(
            {
                "label": "VO2 / interval work",
                "detail": f"Present, with {interval_count} session(s) in the last 4 weeks.",
            }
        )

    if consistency_label in {"low", "very low"}:
        secondary.insert(
            0,
            {
                "label": "Weekly rhythm",
                "detail": f"Consistency is currently {consistency_label.replace('_', ' ')}.",
            },
        )

    return {
        "primary": primary,
        "secondary": secondary,
        "supportive": supportive,
    }


def build_top_signals(signals: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    """Return the most important signals for compact UI display."""
    return signals[:limit] if signals else []


def build_summary_line(metrics: dict[str, Any], focus: dict[str, Any]) -> str:
    """Create a short one-line summary for the hero section."""
    focus_text = str(focus.get("headline", "Maintain consistency and progress gradually"))
    consistency = str(metrics.get("consistency_label", "unknown")).replace("_", " ")
    weekly_km = metrics.get("recent_avg_weekly_km", 0)
    return (
        f"Current pattern suggests {focus_text.lower()}, "
        f"with {consistency} consistency and around {weekly_km} km per week recently."
    )


def build_reasoning(metrics: dict[str, Any], signals: list[dict[str, Any]], limit: int = 4) -> list[str]:
    """Turn top signals into UI-friendly reasoning bullets."""
    if signals:
        return [str(signal.get("detail", "")) for signal in signals[:limit] if signal.get("detail")]

    fallback_reasons = [
        f"Consistency: {str(metrics.get('consistency_label', 'unknown')).title()}",
        f"Recent weekly volume: {metrics.get('recent_avg_weekly_km', 'N/A')} km",
        f"Threshold sessions in last 28 days: {metrics.get('threshold_sessions_last_28', 'N/A')}",
        f"Long runs in last 28 days: {metrics.get('long_runs_last_28', 'N/A')}",
    ]
    return fallback_reasons[:limit]


def generate_runlab_report(df_raw: pd.DataFrame) -> dict[str, Any]:
    """
    Run the core RunLab pipeline.

    This is intentionally UI-agnostic so Streamlit becomes a thin display layer.
    Input: raw uploaded or demo dataframe.
    Output: structured report dict for cards, charts, explanation and downloads.
    """
    df = clean_data(df_raw)
    weekly = weekly_summary(df)
    metrics = overall_metrics(df, weekly)
    signals = derive_signals(metrics)
    focus = determine_focus(metrics, signals)
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
        "decision": {
            "primary_focus": focus.get("headline", "Maintain consistency and progress gradually"),
            "secondary_focus": top_signals[1]["title"] if len(top_signals) > 1 else "Keep core structure stable",
            "maintain": hierarchy["supportive"][0]["label"] if hierarchy["supportive"] else "Current healthy elements",
            "avoid": "Adding more intensity" if focus.get("reason") == "Training balance is skewed toward quality sessions" else "Changing multiple levers at once",
        },
    }
