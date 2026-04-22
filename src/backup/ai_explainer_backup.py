from __future__ import annotations

from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL


def format_frequency(count: int) -> str:
    """Convert session counts into coach-friendly wording."""
    if count == 0:
        return "none"
    if count == 1:
        return "1 session in the last 4 weeks (very limited)"
    if count == 2:
        return "2 sessions in the last 4 weeks (around once every 2 weeks)"
    if count == 3:
        return "3 sessions in the last 4 weeks (slightly inconsistent)"
    if count <= 6:
        return f"{count} sessions in the last 4 weeks (reasonably consistent)"
    return f"{count} sessions in the last 4 weeks (frequent)"


def build_structured_summary(metrics: dict) -> dict:
    threshold_sessions = int(metrics.get("threshold_sessions_last_28", 0) or 0)
    interval_sessions = int(metrics.get("interval_sessions_last_28", 0) or 0)
    long_runs = int(metrics.get("long_runs_last_28", 0) or 0)
    easy_runs = int(metrics.get("easy_runs_last_28", 0) or 0)
    days_with_run_last_28 = int(metrics.get("days_with_run_last_28", 0) or 0)

    return {
        "weeks_of_data": metrics.get("weeks_of_data", "Unknown"),
        "progression_confidence": metrics.get("progression_confidence", "Unknown"),
        "days_with_run_last_28": days_with_run_last_28,
        "run_days_per_week": round(days_with_run_last_28 / 4.0, 2),
        "consistency_label": metrics.get("consistency_label", "Unknown"),
        "total_distance_last_28": metrics.get("total_distance_last_28", 0),
        "avg_distance_per_run": metrics.get("avg_distance_per_run", 0),
        "longest_run_km": metrics.get("longest_run_km", 0),
        "long_run_ratio_to_weekly_volume": metrics.get("long_run_ratio_to_weekly_volume", "Unknown"),
        "recent_avg_weekly_km": metrics.get("recent_avg_weekly_km", 0),
        "prior_avg_weekly_km": metrics.get("prior_avg_weekly_km", 0),
        "volume_trend": metrics.get("volume_trend", "Unknown"),
        "volume_pattern": metrics.get("volume_pattern", "Unknown"),
        "volume_pattern_detail": metrics.get("volume_pattern_detail", "Unknown"),
        "threshold_sessions_last_28": threshold_sessions,
        "interval_sessions_last_28": interval_sessions,
        "long_runs_last_28": long_runs,
        "easy_runs_last_28": easy_runs,
        "quality_runs_last_28": metrics.get("quality_runs_last_28", 0),
        "easy_run_pct": int(metrics.get("easy_run_pct", 0) * 100),
        "quality_run_pct": int(metrics.get("quality_run_pct", 0) * 100),
        "threshold_trend": metrics.get("threshold_trend", "Unknown"),
        "interval_trend": metrics.get("interval_trend", "Unknown"),
        "long_run_trend": metrics.get("long_run_trend", "Unknown"),
        "progression_flat_count": metrics.get("progression_flat_count", "Unknown"),
        "progression_rising_count": metrics.get("progression_rising_count", "Unknown"),
        "vo2_present": interval_sessions > 0,
        "threshold_present": threshold_sessions > 0,
        "long_run_present": long_runs > 0,
        "threshold_freq_text": format_frequency(threshold_sessions),
        "interval_freq_text": format_frequency(interval_sessions),
        "long_run_freq_text": format_frequency(long_runs),
    }


def build_prompt(metrics: dict, signals: list[dict], focus: dict) -> str:
    summary = build_structured_summary(metrics)

    signal_lines = "\n".join(
        [f"- {s['title']} ({s['priority']}): {s['detail']}" for s in signals]
    ) or "- None"

    supporting_signals = ", ".join(focus.get("supporting_signals", [])) or "None"
    prescription_lines = "\n".join(
        [f"- {step}" for step in focus.get("prescription", [])]
    ) or "- None provided"

    timeframe = focus.get("timeframe", "Not specified")

    return f"""
You are an experienced endurance running coach explaining a structured training diagnosis.

Your role is not to re-analyse raw data from scratch.
Your role is to explain the system output clearly, conservatively, and accurately.

You must only use the facts provided below.
Do not guess.
Do not invent race results, physiology, heart-rate trends, or missing training history.
Do not say a session type is absent if its count is above zero.
If a session type is present but not frequent enough, describe it as limited, light, or inconsistent.

FACTS

Training summary:
- Weeks of data: {summary["weeks_of_data"]}
- Progression confidence: {summary["progression_confidence"]}
- Run days in the last 28 days: {summary["days_with_run_last_28"]}
- Average run days per week: {summary["run_days_per_week"]}
- Consistency: {summary["consistency_label"]}
- Total distance in last 28 days: {summary["total_distance_last_28"]} km
- Average distance per run: {summary["avg_distance_per_run"]} km
- Longest run: {summary["longest_run_km"]} km
- Long run ratio to weekly volume: {summary["long_run_ratio_to_weekly_volume"]}
- Recent weekly average: {summary["recent_avg_weekly_km"]} km
- Previous weekly average: {summary["prior_avg_weekly_km"]} km
- Volume trend: {summary["volume_trend"]}
- Volume pattern: {summary["volume_pattern"]}
- Volume pattern detail: {summary["volume_pattern_detail"]}

Training stimulus breakdown in the last 28 days:
- Threshold work: {summary["threshold_freq_text"]}
- Interval / VO2 work: {summary["interval_freq_text"]}
- Long runs: {summary["long_run_freq_text"]}
- Easy runs: {summary["easy_runs_last_28"]}
- Quality runs: {summary["quality_runs_last_28"]}
- Easy run percentage: {summary["easy_run_pct"]}%
- Quality run percentage: {summary["quality_run_pct"]}%
- VO2 present: {summary["vo2_present"]}
- Threshold present: {summary["threshold_present"]}
- Long run present: {summary["long_run_present"]}

Progression trends:
- Threshold trend: {summary["threshold_trend"]}
- Interval trend: {summary["interval_trend"]}
- Long run trend: {summary["long_run_trend"]}
- Flat progression count: {summary["progression_flat_count"]}
- Rising progression count: {summary["progression_rising_count"]}

Signals:
{signal_lines}

System-identified focus:
- Headline: {focus.get("headline", "Unknown")}
- Detail: {focus.get("detail", "Unknown")}
- Priority: {focus.get("priority", "Unknown")}
- Reason: {focus.get("reason", "Unknown")}
- Supporting signals: {supporting_signals}
- Timeframe: {timeframe}

Suggested prescription:
{prescription_lines}

INTERPRETATION RULES

- Always acknowledge all major training stimuli that are present: threshold, VO2, and long run.
- If interval / VO2 sessions are present, mention them explicitly.
- Do not present VO2 as the limiter unless interval session count is zero or the focus clearly says so.
- If VO2 is present but overall volume is low, describe VO2 as supportive rather than primary.
- Do not simply list session types. Explain their relative importance in the current training pattern.
- Clearly distinguish between:
  1. the primary limiter (what matters most)
  2. secondary constraints (what is underdeveloped)
  3. supportive stimuli (what is present but not limiting progress)
- Always describe training in this hierarchy, not as a list.
- Refer to consistency using run days, not total run entries, because some runners may log warm-ups, cool-downs, or short additional runs separately.
- Use session frequency wording that runners can understand naturally, for example "2 sessions in the last 4 weeks" rather than decimal sessions per week.

WRITING TASK

Write exactly 3 short paragraphs.

Paragraph 1 — Diagnosis
Describe the current training pattern using the structured facts.
Acknowledge threshold, interval / VO2, and long-run work if the count is above zero.

Paragraph 2 — Hierarchy
State the single primary limiter first.
Then briefly describe any secondary constraints.
Then briefly mention supportive stimuli that are present but not currently limiting progress.

Paragraph 3 — Action
Give a practical next step aligned with the prescription.
Do not repeat the focus headline verbatim as the opening sentence.
Make the recommendation decisive and specific.

STYLE RULES
- Be direct
- Be conservative
- Be specific
- No fluff
- No hype
- No motivational language
- No em dashes
- Sound like a coach reviewing a training log
""".strip()


def fallback_explanation(metrics: dict, signals: list[dict], focus: dict) -> str:
    summary = build_structured_summary(metrics)

    prescription = " ".join(focus.get("prescription", [])[:2]).strip()
    if not prescription:
        prescription = "Maintain a repeatable weekly structure and progress the main limiter gradually."

    primary_limiter = focus.get("headline", "current training focus")
    secondary_constraints = []

    if summary["threshold_present"] and summary["threshold_sessions_last_28"] <= 2:
        secondary_constraints.append(f"threshold work is present but limited, with {summary['threshold_freq_text']}")
    elif not summary["threshold_present"]:
        secondary_constraints.append("threshold work is absent")

    if summary["long_run_present"] and summary["long_runs_last_28"] <= 2:
        secondary_constraints.append(f"long runs are present but inconsistent, with {summary['long_run_freq_text']}")
    elif not summary["long_run_present"]:
        secondary_constraints.append("long runs are absent")

    supportive = []
    if summary["vo2_present"]:
        supportive.append(f"VO2 / interval work is present, with {summary['interval_freq_text']}")

    diagnosis = (
        f"Recent training shows {summary['consistency_label'].lower()} consistency, "
        f"with running on {summary['days_with_run_last_28']} of the last 28 days "
        f"({summary['run_days_per_week']} run days per week) and {summary['recent_avg_weekly_km']} km per week recently. "
        f"Threshold work is {summary['threshold_freq_text']}, interval / VO2 work is {summary['interval_freq_text']}, "
        f"and long runs are {summary['long_run_freq_text']}."
    )

    hierarchy_parts = [f"The primary limiter is {primary_limiter.lower()}."]
    if secondary_constraints:
        hierarchy_parts.append("Secondary constraints: " + "; ".join(secondary_constraints) + ".")
    if supportive:
        hierarchy_parts.append("Supportive stimuli: " + "; ".join(supportive) + ".")

    action = f"Next step: {prescription}"

    return f"{diagnosis}\n\n{' '.join(hierarchy_parts)}\n\n{action}"


def generate_ai_explanation(metrics: dict, signals: list[dict], focus: dict) -> tuple[str, bool]:
    if not OPENAI_API_KEY:
        return fallback_explanation(metrics, signals, focus), False

    prompt = build_prompt(metrics, signals, focus)

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You explain structured running training analysis conservatively. "
                        "You must stay grounded in the supplied facts and never contradict explicit counts."
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