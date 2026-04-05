from __future__ import annotations
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL


def build_prompt(metrics: dict, signals: list[dict], focus: dict) -> str:
    signal_lines = "\n".join([f"- {s['title']}: {s['detail']}" for s in signals])
    supporting_signals = ", ".join(focus["supporting_signals"]) if focus["supporting_signals"] else "None"
    prescription_lines = "\n".join([f"- {step}" for step in focus.get("prescription", [])]) or "- None provided"
    timeframe = focus.get("timeframe", "Not specified")

    return f"""
You are an experienced endurance running coach analysing structured training data.

Your job is to interpret the data and make a clear, practical coaching call.

Avoid generic advice. Be specific, grounded, and decisive.
Focus on the highest priority signal when identifying the main limiter.

Metrics:
- Days with a run in the last 28 days: {metrics['days_with_run_last_28']}
- Consistency: {metrics['consistency_label']}
- Total distance (28 days): {metrics['total_distance_last_28']} km
- Average distance per run: {metrics['avg_distance_per_run']} km
- Longest run: {metrics['longest_run_km']} km
- Recent weekly average: {metrics['recent_avg_weekly_km']} km
- Previous weekly average: {metrics['prior_avg_weekly_km']} km
- Volume trend: {metrics['volume_trend']}
- Threshold sessions (28 days): {metrics['threshold_sessions_last_28']}
- Interval sessions (28 days): {metrics['interval_sessions_last_28']}
- Long runs (28 days): {metrics['long_runs_last_28']}

Signals:
{signal_lines}

System-identified focus:
- Headline: {focus['headline']}
- Detail: {focus['detail']}
- Priority: {focus['priority']}
- Reason: {focus['reason']}
- Supporting signals: {supporting_signals}
- Timeframe: {timeframe}

Suggested prescription:
{prescription_lines}

Write exactly 3 short paragraphs:

Paragraph 1 — Diagnosis
Clearly describe what the current training pattern indicates.

Paragraph 2 — Limitation
State the single biggest limiter in one clear sentence, then briefly explain it.

Paragraph 3 — Action
Do not repeat the focus headline verbatim as your opening sentence.
Give a clear, actionable next step aligned to the system-identified focus and prescription.
Where helpful, refer to the suggested timeframe.

Style rules:
- Be direct and decisive
- No fluff or motivational language
- No generic advice
- Keep sentences tight and practical
- Sound like a coach reviewing a training log
- Do not invent missing data
""".strip()


def fallback_explanation(metrics: dict, signals: list[dict], focus: dict) -> str:
    top_signals = ", ".join([s["title"] for s in signals[:3]]) if signals else "no major issues detected"
    prescription = " ".join(focus.get("prescription", [])[:2])

    return (
        f"The main signals are: {top_signals}. "
        f"Recent training shows {metrics['consistency_label']} consistency and a {metrics['volume_trend']} volume trend. "
        f"The main priority is {focus['headline'].lower()}. {focus['detail']} "
        f"Next step: {prescription}"
    )


def generate_ai_explanation(metrics: dict, signals: list[dict], focus: dict) -> tuple[str, bool]:
    if not OPENAI_API_KEY:
        return fallback_explanation(metrics, signals, focus), False

    prompt = build_prompt(metrics, signals, focus)

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.3,
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
        return response.choices[0].message.content.strip(), True
    except Exception as e:
        print(f"OpenAI error: {e}")
        return fallback_explanation(metrics, signals, focus), False