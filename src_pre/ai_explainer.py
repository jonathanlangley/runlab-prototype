from __future__ import annotations

from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL


def format_frequency(count: int) -> str:
    if count == 0:
        return "none"
    if count == 1:
        return "1 session in the last 4 weeks"
    if count <= 3:
        return f"{count} sessions in the last 4 weeks"
    return f"{count} sessions in the last 4 weeks"


def build_structured_summary(metrics: dict) -> dict:
    threshold_sessions = int(metrics.get("threshold_sessions_last_28", 0) or 0)
    vo2_sessions = int(
        metrics.get("vo2_sessions_last_28", metrics.get("interval_sessions_last_28", 0)) or 0
    )
    long_runs = int(metrics.get("long_runs_last_28", 0) or 0)
    days_with_run_last_28 = int(metrics.get("days_with_run_last_28", 0) or 0)

    return {
        "run_days_per_week": round(days_with_run_last_28 / 4.0, 2),
        "recent_avg_weekly_km": metrics.get("recent_avg_weekly_km", 0),
        "volume_trend": metrics.get("volume_trend", "Unknown"),
        "threshold_freq_text": format_frequency(threshold_sessions),
        "vo2_freq_text": format_frequency(vo2_sessions),
        "long_run_freq_text": format_frequency(long_runs),
        "threshold_present": threshold_sessions > 0,
        "vo2_present": vo2_sessions > 0,
        "long_run_present": long_runs > 0,
    }


def build_prompt(metrics: dict, signals: list[dict], focus: dict) -> str:
    summary = build_structured_summary(metrics)

    top_signal_lines = "\n".join(
        [f"- {s['title']}: {s['detail']}" for s in signals[:2]]
    ) or "- None"

    target_volume_range = focus.get("target_volume_range")
    target_volume_text = (
        f"{target_volume_range[0]}-{target_volume_range[1]} km per week"
        if target_volume_range
        else "not specified"
    )

    return f"""
You are an experienced endurance running coach reviewing a short block of training.

The UI already shows:
- the diagnosis
- the recommendation
- the action steps
- the key metrics

Your job is NOT to repeat those.

Your job is to add deeper coaching context.

Write exactly TWO short paragraphs.

Paragraph 1:
- Explain what the current training pattern suggests
- Highlight what is working and what is limiting progress
- Explain interaction between volume, intensity, and long runs

Paragraph 2:
- Explain WHY the recommendation makes sense from a training perspective
- Make it clear why increasing volume and reducing reliance on intensity can improve 5K performance
- Refer to aerobic development, fatigue cost, and ability to sustain pace
- Explain why adding more intensity at this stage would be less effective
- Explicitly connect the recommendation to improving 5K speed
- Include one practical caution for the next block

FACTS

Primary focus:
{focus.get("headline", "Unknown")}

Recent pattern:
- Run days per week: {summary["run_days_per_week"]}
- Weekly volume: {summary["recent_avg_weekly_km"]}
- Volume trend: {summary["volume_trend"]}
- Threshold work: {summary["threshold_freq_text"]}
- VO2 work: {summary["vo2_freq_text"]}
- Long runs: {summary["long_run_freq_text"]}

Supporting signals:
{top_signal_lines}

Target volume:
{target_volume_text}

STYLE RULES:
- No repetition of the diagnosis or action steps
- No bullet points
- No quotes
- No named references
- No em dashes
- Be clear and practical
- Keep total length between 120 and 200 words
""".strip()


def fallback_explanation(metrics: dict, signals: list[dict], focus: dict) -> str:
    summary = build_structured_summary(metrics)

    base_text = (
        f"The current pattern shows some useful elements in place, but the overall structure is not yet strong enough to fully support consistent progression. "
        f"With weekly volume around {summary['recent_avg_weekly_km']} km and a relatively modest run frequency, the supporting aerobic base is likely limiting how effective the harder sessions can be."
    )

    rationale_text = (
        "From a training perspective, building a stronger aerobic base improves durability, recovery between sessions, and the ability to absorb quality work. "
        "The key risk in the short term is adding more intensity without increasing overall support, which can lead to fatigue without meaningful adaptation. "
        "Keeping the structure controlled while gradually building volume should allow the current work to become more productive."
    )

    return f"{base_text}\n\n{rationale_text}"


def generate_ai_explanation(metrics: dict, signals: list[dict], focus: dict) -> tuple[str, bool]:
    if not OPENAI_API_KEY:
        return fallback_explanation(metrics, signals, focus), False

    prompt = build_prompt(metrics, signals, focus)

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a pragmatic endurance coach. "
                        "You explain training patterns clearly and concisely. "
                        "You do not repeat obvious information. "
                        "You focus on interpretation and reasoning."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        return response.choices[0].message.content.strip(), True
    except Exception as e:
        print(f"OpenAI error: {e}")
        return fallback_explanation(metrics, signals, focus), False