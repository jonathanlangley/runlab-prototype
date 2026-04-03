from __future__ import annotations
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL


def build_prompt(metrics: dict, signals: list[dict], focus: str) -> str:
    signal_lines = "\n".join([f"- {s['title']}: {s['detail']}" for s in signals])

    return f"""
You are an experienced running coach and data analyst.

Below is a structured training summary for a runner.

Metrics:
- Days with a run in the last 28 days: {metrics['days_with_run_last_28']}
- Consistency label: {metrics['consistency_label']}
- Total distance in the last 28 days: {metrics['total_distance_last_28']} km
- Total runs in the last 28 days: {metrics['total_runs_last_28']}
- Average distance per run: {metrics['avg_distance_per_run']} km
- Longest run: {metrics['longest_run_km']} km
- Recent average weekly distance: {metrics['recent_avg_weekly_km']} km
- Prior average weekly distance: {metrics['prior_avg_weekly_km']} km
- Volume change: {metrics['volume_change_pct']}%
- Volume trend: {metrics['volume_trend']}
- Threshold sessions in the last 28 days: {metrics['threshold_sessions_last_28']}
- Interval sessions in the last 28 days: {metrics['interval_sessions_last_28']}
- Long runs in the last 28 days: {metrics['long_runs_last_28']}

Signals:
{signal_lines}

Suggested focus:
- {focus}

Write a concise explanation in 3 short paragraphs:
1. What the current training pattern suggests
2. What may be limiting progress
3. What to focus on next

Keep it practical, grounded, and non-dramatic.
Do not invent missing data.
""".strip()


def fallback_explanation(metrics: dict, signals: list[dict], focus: str) -> str:
    top_signals = ", ".join([s["title"] for s in signals[:3]]) if signals else "no major issues detected"
    return (
        f"This prototype identified the following main signals: {top_signals}. "
        f"Recent training shows {metrics['consistency_label']} consistency and a {metrics['volume_trend']} volume trend. "
    )


def generate_ai_explanation(metrics: dict, signals: list[dict], focus: str) -> str:
    if not OPENAI_API_KEY:
        return fallback_explanation(metrics, signals, focus)

    prompt = build_prompt(metrics, signals, focus)

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.4,
            messages=[
                {
                    "role": "system",
                    "content": "You explain structured training analysis clearly and conservatively."
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return fallback_explanation(metrics, signals, focus)