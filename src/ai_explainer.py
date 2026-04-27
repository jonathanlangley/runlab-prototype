from __future__ import annotations

from typing import Any

from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL


def _format_frequency(count: int, label: str) -> str:
    if count == 0:
        return f"no {label}"
    if count == 1:
        return f"1 {label} in the last 4 weeks"
    return f"{count} {label}s in the last 4 weeks"


def build_structured_summary(metrics: dict[str, Any]) -> dict[str, Any]:
    threshold = int(metrics.get("threshold_sessions_last_28", 0) or 0)
    vo2 = int(metrics.get("vo2_sessions_last_28", 0) or 0) + int(metrics.get("race_sessions_last_28", 0) or 0)
    long_runs = int(metrics.get("long_runs_last_28", 0) or 0)
    run_days = int(metrics.get("days_with_run_last_28", 0) or 0)
    return {
        "run_days_per_week": round(run_days / 4.0, 2),
        "recent_avg_weekly_km": metrics.get("recent_avg_weekly_km", 0),
        "volume_trend": metrics.get("volume_trend", "unknown"),
        "threshold_text": _format_frequency(threshold, "threshold session"),
        "vo2_text": _format_frequency(vo2, "VO2/race session"),
        "long_run_text": _format_frequency(long_runs, "long run"),
    }


def build_prompt(metrics: dict[str, Any], signals: list[dict[str, Any]], focus: dict[str, Any]) -> str:
    summary = build_structured_summary(metrics)
    primary_key = focus.get("primary_key", "unknown")
    target = focus.get("target_volume_range")
    target_text = f"{target[0]}-{target[1]} km per week" if target else "not specified"
    signal_lines = "\n".join(f"- {s.get('title')}: {s.get('detail')}" for s in signals[:3]) or "- None"

    return f"""
You are an experienced endurance running coach writing the explanation layer for RunLab.ai.

RunLab's deterministic engine has already chosen the recommendation. Do not change it. Your job is to explain why it makes sense.

Write exactly two short paragraphs, 130-210 words total.

Paragraph 1:
- Explain what the pattern suggests about the runner's current limiter.
- Mention the interaction between easy volume, long run support, threshold work and VO2/race work.
- Be specific to the facts below.

Paragraph 2:
- Explain why this recommendation can improve 5K performance.
- Explain that 5K speed is not only top-end speed. It also depends on aerobic support, fatigue resistance, threshold strength and the ability to repeat quality sessions.
- Include one practical caution for the next block.

Facts:
Primary recommendation: {focus.get('headline')}
Primary limiter: {focus.get('primary_limiter')}
Primary key: {primary_key}
Secondary focus: {focus.get('secondary_focus') or 'none'}
Run days per week: {summary['run_days_per_week']}
Weekly volume: {summary['recent_avg_weekly_km']} km
Volume trend: {summary['volume_trend']}
Threshold: {summary['threshold_text']}
VO2/race: {summary['vo2_text']}
Long runs: {summary['long_run_text']}
Target volume: {target_text}
Supporting signals:
{signal_lines}

Style rules:
- No bullets.
- No named references.
- No em dashes.
- No generic motivational language.
- Do not repeat the action steps.
- Do not introduce a different recommendation.
""".strip()


def fallback_explanation(metrics: dict[str, Any], signals: list[dict[str, Any]], focus: dict[str, Any]) -> str:
    summary = build_structured_summary(metrics)
    primary_key = str(focus.get("primary_key", ""))
    volume = summary["recent_avg_weekly_km"]
    run_days = summary["run_days_per_week"]

    if primary_key in {"volume", "balance"}:
        return (
            f"The current pattern suggests that the faster work needs more aerobic support underneath it. With about {volume} km per week and {run_days} run days, the priority is not simply to add another hard session. Easy volume and a stable long run improve durability, recovery between sessions and the ability to turn threshold and VO2 work into repeatable adaptation.\n\n"
            "That matters for 5K performance because 5K speed is not only about top-end pace. A stronger aerobic base helps you sustain a high percentage of your speed for longer, delays fatigue and makes quality sessions more productive. The caution is to build the next block gradually, keeping quality controlled while volume becomes more consistent."
        )

    if primary_key == "threshold":
        return (
            "The current pattern lacks a regular threshold stimulus, which leaves a gap between easy running and harder VO2 or race-style efforts. Threshold work improves the speed you can hold while staying controlled, and it usually carries less fatigue cost than repeated very hard sessions.\n\n"
            "For 5K performance, this helps bridge aerobic fitness and top-end speed. It supports the ability to sustain pace rather than simply hit fast reps in isolation. The caution is to keep threshold sessions repeatable and avoid turning them into races."
        )

    if primary_key == "consistency":
        return (
            f"The main pattern is frequency rather than fitness. At about {run_days} run days per week, the body is not yet getting a frequent enough signal to adapt reliably, so bigger individual sessions are less useful than a more repeatable week.\n\n"
            "For 5K improvement, consistency creates the base that allows volume, threshold and VO2 work to stack together. The caution is to add easy days first, not extra intensity, so the new rhythm feels sustainable rather than forced."
        )

    return (
        "The current pattern has enough useful work to build from, but the next block needs one clear priority rather than several competing changes. Keeping most of the week stable makes it easier to see whether the chosen stimulus is actually working.\n\n"
        "For 5K performance, the goal is to combine aerobic support, threshold strength and controlled speed work in a way that can be repeated. The caution is to progress one lever at a time and avoid making the week harder in several places at once."
    )


def generate_ai_explanation(metrics: dict[str, Any], signals: list[dict[str, Any]], focus: dict[str, Any]) -> tuple[str, bool]:
    if not OPENAI_API_KEY:
        return fallback_explanation(metrics, signals, focus), False

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You write concise, practical endurance coaching explanations. You do not override deterministic product logic."},
                {"role": "user", "content": build_prompt(metrics, signals, focus)},
            ],
            temperature=0.4,
        )
        content = response.choices[0].message.content or ""
        return content.strip() or fallback_explanation(metrics, signals, focus), True
    except Exception:
        return fallback_explanation(metrics, signals, focus), False
