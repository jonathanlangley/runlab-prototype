from __future__ import annotations


def determine_focus(metrics: dict, signals: list[dict]) -> dict:
    """
    Decide the runner's primary training focus based on structured signals.

    Returns a structured focus object that can be used by:
    - the Streamlit UI
    - the AI explanation layer
    - future API / agent workflows
    """
    high_priority_titles = [s["title"] for s in signals if s["priority"] == "high"]
    medium_priority_titles = [s["title"] for s in signals if s["priority"] == "medium"]

    if "Low consistency" in high_priority_titles:
        return {
            "headline": "Increase weekly run frequency",
            "detail": "Aim to build a consistent routine before adding more volume or intensity.",
            "priority": "high",
            "reason": "Low consistency detected",
            "supporting_signals": ["Low consistency"],
            "prescription": [
                "Run at least 5 times per week",
                "Keep most runs easy while building consistency",
                "Space runs evenly across the week",
                "Avoid adding more intensity until frequency is stable",
            ],
            "timeframe": "2-3 weeks",
        }

    if "No threshold work detected" in high_priority_titles:
        return {
            "headline": "Reintroduce threshold training",
            "detail": "Start with one threshold session per week and make it a regular part of the training pattern.",
            "priority": "high",
            "reason": "No threshold sessions detected in the last 28 days",
            "supporting_signals": ["No threshold work detected"],
            "prescription": [
                "Add 1 threshold session per week",
                "Keep the rest of the week controlled and aerobic",
                "Use repeatable threshold formats rather than very hard sessions",
                "Keep the session in place for several weeks before progressing it",
            ],
            "timeframe": "3-4 weeks",
        }

    if "No long run stimulus" in high_priority_titles:
        return {
            "headline": "Rebuild long run stimulus",
            "detail": "Reintroduce a regular long run to strengthen endurance and support overall progression.",
            "priority": "high",
            "reason": "No long runs detected in the last 28 days",
            "supporting_signals": ["No long run stimulus"],
            "prescription": [
                "Schedule 1 long run each week",
                "Keep the long run comfortably aerobic",
                "Build duration gradually rather than jumping too quickly",
                "Keep the long run consistent before adding extra quality elsewhere",
            ],
            "timeframe": "3-4 weeks",
        }

    if "Declining volume" in high_priority_titles:
        return {
            "headline": "Stabilise training load",
            "detail": "Recent volume has dropped, so the immediate goal is to rebuild a sustainable training rhythm before pushing harder.",
            "priority": "high",
            "reason": "Recent weekly distance is declining",
            "supporting_signals": ["Declining volume"],
            "prescription": [
                "Re-establish a repeatable weekly pattern",
                "Bring volume back gradually rather than forcing a sharp increase",
                "Protect consistency before adding harder sessions",
                "Let volume stabilise for a couple of weeks before progressing again",
            ],
            "timeframe": "2-3 weeks",
        }

    if "Moderate consistency" in medium_priority_titles:
        return {
            "headline": "Tighten training consistency",
            "detail": "The training pattern is reasonable, but more regular frequency would improve adaptation and make progression more reliable.",
            "priority": "medium",
            "reason": "Consistency is moderate rather than strong",
            "supporting_signals": ["Moderate consistency"],
            "prescription": [
                "Add one extra easy run each week if recovery allows",
                "Reduce large gaps between run days",
                "Keep the overall structure predictable",
                "Use consistency as the main goal before chasing harder progression",
            ],
            "timeframe": "2-3 weeks",
        }

    if "Limited threshold stimulus" in medium_priority_titles:
        return {
            "headline": "Strengthen threshold support",
            "detail": "Threshold work is present but limited. Keeping one regular session each week would make the training pattern more complete.",
            "priority": "medium",
            "reason": "Threshold stimulus is present but under-supported",
            "supporting_signals": ["Limited threshold stimulus"],
            "prescription": [
                "Keep 1 threshold session in the weekly pattern",
                "Make the session repeatable rather than maximal",
                "Support it with enough easy running around it",
                "Judge progress by consistency over several weeks",
            ],
            "timeframe": "3-4 weeks",
        }

    if "Minimal long run stimulus" in medium_priority_titles:
        return {
            "headline": "Make the long run more regular",
            "detail": "Endurance work is present but inconsistent. A more regular long run would improve durability and support overall development.",
            "priority": "medium",
            "reason": "Long run stimulus is present but limited",
            "supporting_signals": ["Minimal long run stimulus"],
            "prescription": [
                "Keep one long run in the week more consistently",
                "Aim for a predictable slot each week",
                "Keep it aerobic and controlled",
                "Build regularity before extending it much further",
            ],
            "timeframe": "3-4 weeks",
        }

    if metrics.get("volume_trend") == "flat":
        return {
            "headline": "Progress training load carefully",
            "detail": "The current pattern looks stable, but a small increase in volume or quality may be needed to keep progress moving.",
            "priority": "medium",
            "reason": "Volume trend is flat",
            "supporting_signals": ["Volume plateau"],
            "prescription": [
                "Choose one lever to progress: volume or quality, not both",
                "Make the increase small and controlled",
                "Hold the new level long enough to absorb it",
                "Reassess before progressing again",
            ],
            "timeframe": "2-4 weeks",
        }

    return {
        "headline": "Maintain consistency and progress gradually",
        "detail": "The current pattern looks broadly healthy. Keep the routine stable and build step by step.",
        "priority": "low",
        "reason": "No major limiting signal identified",
        "supporting_signals": [],
        "prescription": [
            "Keep the current weekly rhythm stable",
            "Progress gradually rather than making abrupt changes",
            "Protect consistency while nudging volume or quality upward",
            "Reassess after another block of consistent training",
        ],
        "timeframe": "2-4 weeks",
    }