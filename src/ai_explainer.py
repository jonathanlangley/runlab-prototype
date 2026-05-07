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
    race_sessions = int(metrics.get("race_sessions_last_28", 0) or 0)
    long_runs = int(metrics.get("long_runs_last_28", 0) or 0)
    days_with_run_last_28 = int(metrics.get("days_with_run_last_28", 0) or 0)

    return {
        "run_days_per_week": round(days_with_run_last_28 / 4.0, 2),
        "recent_avg_weekly_km": round(float(metrics.get("recent_avg_weekly_km", 0) or 0), 1),
        "volume_trend": metrics.get("volume_trend", "Unknown"),
        "threshold_freq_text": format_frequency(threshold_sessions),
        "vo2_freq_text": format_frequency(vo2_sessions + race_sessions),
        "long_run_freq_text": format_frequency(long_runs),
    }


def build_prompt(metrics: dict, signals: list[dict], focus: dict) -> str:
    summary = build_structured_summary(metrics)

    prompt = f"""
You are an experienced endurance running coach writing for RunLab.

The RunLab decision engine has already chosen the recommendation.
Your job is only to explain the decision in a clear, practical way.

Write exactly TWO short paragraphs.

PARAGRAPH 1:
- Describe the recent training pattern
- Explain the main limiter
- Keep it specific to the data

PARAGRAPH 2:
- Explain why the recommendation is the right next step
- Explain why adding more intensity or changing several things at once is not the best move
- Link the advice to aerobic development, fatigue cost, and sustainable performance improvement
- Include one practical caution

DATA:
Run days per week: {summary["run_days_per_week"]}
Weekly km: {summary["recent_avg_weekly_km"]}
Volume trend: {summary["volume_trend"]}
Threshold frequency: {summary["threshold_freq_text"]}
VO2 or race-level frequency: {summary["vo2_freq_text"]}
Long run frequency: {summary["long_run_freq_text"]}

RUNLAB FOCUS:
Headline: {focus.get("headline", "")}
Limiter: {focus.get("limiter", "")}
Detail: {focus.get("detail", "")}

RULES:
- No bullet points
- No hype
- No generic coaching cliches
- Do not say "as an AI"
- Do not override the RunLab decision
- Do not name athletes
- No em dashes
- 80-120 words total
"""
    return prompt.strip()


def fallback_explanation(metrics: dict, signals: list[dict], focus: dict) -> str:
    summary = build_structured_summary(metrics)
    primary_key = str(focus.get("primary_key", "")).lower()
    focus_text = focus.get("headline", "the current recommendation").lower()

    pattern = (
        f"The recent pattern is around {summary['run_days_per_week']} run days and "
        f"{summary['recent_avg_weekly_km']} km per week, with "
        f"{summary['threshold_freq_text']} of threshold work, "
        f"{summary['vo2_freq_text']} at VO2 or race-level effort, and "
        f"{summary['long_run_freq_text']}."
    )

    if primary_key in {"volume", "aerobic_support"}:
        return (
            f"{pattern} The main issue is not lack of effort, but lack of aerobic support. "
            "The hard sessions are present, but they need more easy running underneath them to become more productive.\n\n"
            "Over the next few weeks, increase easy volume while keeping quality controlled. "
            "This should improve durability, recovery between sessions, and the base that supports threshold and race pace work."
        )

    if primary_key == "threshold":
        return (
            f"{pattern} RunLab is pointing toward {focus_text} because sustained controlled work is the missing link between easy running and harder intervals.\n\n"
            "Another race-level effort would add stress, but it would not solve the main gap. A threshold session gives a repeatable stimulus with a lower fatigue cost, helping improve the pace that can be sustained without turning the whole week into a recovery problem."
        )

    if primary_key == "long_run":
        return (
            f"{pattern} RunLab is pointing toward {focus_text} because the endurance anchor is not yet reliable enough.\n\n"
            "The long run supports durability, aerobic development, and recovery from faster work. The caution is to keep it comfortable rather than chasing pace. The value comes from making it repeatable, not from making it another hard session."
        )

    if primary_key == "consistency":
        return (
            f"{pattern} RunLab is pointing toward {focus_text} because the week needs a more repeatable rhythm before load is increased.\n\n"
            "Bigger individual sessions are less useful if the weekly pattern is not stable. Build frequency first, keep the effort controlled, and only progress volume or intensity once the rhythm feels sustainable."
        )

    if primary_key == "load_stability":
        return (
            f"{pattern} RunLab is pointing toward {focus_text} because the recent load is not stable enough to interpret clearly.\n\n"
            "A predictable week makes adaptation easier to judge. Rather than pushing another stimulus, the better next step is to hold the load steady, protect recovery, and rebuild confidence in the rhythm."
        )

    if primary_key == "quality":
        return (
            f"{pattern} RunLab is pointing toward {focus_text} because the base is in place but the week lacks one clear performance stimulus.\n\n"
            "Adding several hard sessions at once would muddy the signal and raise fatigue. One controlled, purposeful faster session each week gives a clear adaptation cue while keeping the rest of the structure intact."
        )

    if primary_key == "progression":
        return (
            f"{pattern} RunLab is pointing toward {focus_text} because the structure is sound but progression has stalled across multiple levers.\n\n"
            "The right move is to progress one thing only over the next block, whether that is a small volume increase, a slightly longer long run, or a clearer quality stimulus. Changing several at once makes it impossible to read the response."
        )

    if primary_key == "maintenance":
        return (
            f"{pattern} RunLab is pointing toward {focus_text} because the current rhythm is broadly healthy.\n\n"
            "The bigger risk now is over-correcting something that is already working. Protect the current pattern, make small controlled progressions, and only adjust if a clear gap appears."
        )

    return (
        f"{pattern} RunLab is pointing toward {focus_text} because it is the clearest next lever in the recent training pattern.\n\n"
        "The aim is to change one thing at a time so the response is easy to judge. Adding more intensity or changing several levers at once would make it harder to know what is working and could raise fatigue unnecessarily."
    )


def generate_ai_explanation(
    metrics: dict,
    signals: list[dict],
    focus: dict,
) -> tuple[str, bool]:
    """
    Returns (explanation_text, used_ai).

    used_ai is True only when the OpenAI API was successfully called and
    returned non-empty content. Otherwise the deterministic fallback is
    used and used_ai is False.
    """
    explanation = fallback_explanation(metrics, signals, focus)

    if not OPENAI_API_KEY:
        return explanation, False

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
            max_tokens=240,
            temperature=0.35,
        )

        ai_text = response.choices[0].message.content

        if ai_text and ai_text.strip():
            return ai_text.strip(), True

    except Exception:
        return explanation, False

    return explanation, False