from __future__ import annotations

from openai import OpenAI

from src.config import OPENAI_API_KEY, OPENAI_MODEL


client = OpenAI(
    api_key=OPENAI_API_KEY,
    timeout=6.0,
)


def format_frequency(count: int) -> str:
    if count == 0:
        return "none"
    if count == 1:
        return "1 session in the last 4 weeks"
    return f"{count} sessions in the last 4 weeks"


def build_structured_summary(metrics: dict) -> dict:
    threshold_sessions = int(metrics.get("threshold_sessions_last_28", 0) or 0)
    vo2_sessions = int(metrics.get("vo2_sessions_last_28", 0) or 0)
    long_runs = int(metrics.get("long_runs_last_28", 0) or 0)
    days_with_run_last_28 = int(metrics.get("days_with_run_last_28", 0) or 0)

    return {
        "run_days_per_week": round(days_with_run_last_28 / 4.0, 2),
        "recent_avg_weekly_km": metrics.get("recent_avg_weekly_km", 0),
        "volume_trend": metrics.get("volume_trend", "Unknown"),
        "threshold_freq_text": format_frequency(threshold_sessions),
        "vo2_freq_text": format_frequency(vo2_sessions),
        "long_run_freq_text": format_frequency(long_runs),
    }


def build_prompt(metrics: dict, signals: list[dict], focus: dict) -> str:
    summary = build_structured_summary(metrics)

    prompt = f"""
You are an experienced endurance running coach.

The RunLab decision engine has already identified the correct training focus.
Your job is to explain WHY this is the right decision.

Write exactly TWO short paragraphs.

PARAGRAPH 1:
- Describe the current training pattern
- Identify the main limiter
- Explain how volume, intensity, and long-run structure are interacting

PARAGRAPH 2:
- Explain why THIS recommendation is correct right now
- Explicitly explain why NOT:
  - adding more intensity
  - changing multiple training levers at once
  - chasing short-term fitness gains
- Link this to aerobic development and fatigue cost
- Explain how this improves 5K performance
- Include one practical caution

DATA:
Run days/week: {summary["run_days_per_week"]}
Weekly km: {summary["recent_avg_weekly_km"]}
Volume trend: {summary["volume_trend"]}
Threshold: {summary["threshold_freq_text"]}
VO2: {summary["vo2_freq_text"]}
Long runs: {summary["long_run_freq_text"]}

FOCUS:
{focus.get("headline", "")}

RULES:
- No bullet points
- No fluff
- Be specific and practical
- Avoid repeating the recommendation word-for-word
- Do not override the RunLab decision
- No named references
- No em dashes
- 120-180 words total
"""
    return prompt.strip()


def fallback_explanation(metrics: dict, signals: list[dict], focus: dict) -> str:
    summary = build_structured_summary(metrics)
    focus_text = focus.get("headline", "the current recommendation")

    return (
        "The current pattern shows some useful training structure, but the main limiter is still "
        "how well the aerobic base supports the harder work. "
        f"With around {summary['recent_avg_weekly_km']} km per week and "
        f"{summary['run_days_per_week']} run days, the system is pointing toward "
        f"{focus_text.lower()}. That means the next gain is more likely to come from better support "
        "around the quality sessions than from simply making the hard work harder.\n\n"
        "Adding more intensity now would probably increase fatigue faster than fitness. Changing too many "
        "levers at once would also make it harder to know what is actually working. A more controlled block "
        "builds aerobic capacity, improves recovery between sessions, and helps you sustain faster pace for "
        "longer, which is directly relevant to 5K performance. Keep the next step gradual and reassess after "
        "a stable block."
    )


def generate_ai_explanation(metrics: dict, signals: list[dict], focus: dict) -> str:
    """
    Safe AI explanation pattern.

    The deterministic RunLab decision engine decides the recommendation.
    This function only explains that recommendation.

    Behaviour:
    1. Build a fallback explanation first
    2. Try the OpenAI call with a short timeout
    3. If the API fails or is slow, return the fallback
    """

    explanation = fallback_explanation(metrics, signals, focus)

    if not OPENAI_API_KEY:
        return explanation

    try:
        prompt = build_prompt(metrics, signals, focus)

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=260,
            temperature=0.4,
        )

        ai_text = response.choices[0].message.content

        if ai_text and ai_text.strip():
            explanation = ai_text.strip()

    except Exception:
        pass

    return explanation