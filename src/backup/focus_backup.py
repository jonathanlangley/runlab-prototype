from __future__ import annotations


def _default_focus() -> dict:
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


FOCUS_LIBRARY = {
    "Low consistency": {
        "headline": "Increase weekly run frequency",
        "detail": "Aim to build a more repeatable weekly routine before adding more volume or intensity.",
        "priority": "high",
        "reason": "Low consistency detected",
        "prescription": [
            "Run at least 5 times per week",
            "Keep most runs easy while building consistency",
            "Reduce large gaps between run days",
            "Avoid adding more intensity until frequency is stable",
        ],
        "timeframe": "2-3 weeks",
    },
    "Low volume": {
        "headline": "Build aerobic volume",
        "detail": "The current weekly mileage is likely too low to support stronger aerobic progression.",
        "priority": "high",
        "reason": "Average weekly volume is below target range",
        "prescription": [
            "Increase weekly distance gradually",
            "Use easy running to build volume rather than adding extra intensity",
            "Keep the weekly structure repeatable",
            "Only progress one lever at a time",
        ],
        "timeframe": "3-4 weeks",
    },
    "No threshold work detected": {
        "headline": "Reintroduce threshold training",
        "detail": "Threshold work is missing from the current pattern, which may limit sustained pace development.",
        "priority": "high",
        "reason": "No threshold sessions detected in the last 28 days",
        "prescription": [
            "Add 1 threshold session per week",
            "Use repeatable threshold formats rather than very hard sessions",
            "Support the session with enough easy running",
            "Keep the pattern in place for several weeks before progressing it",
        ],
        "timeframe": "3-4 weeks",
    },
    "No long run stimulus": {
        "headline": "Rebuild long run stimulus",
        "detail": "A regular long run is missing, which may limit endurance development and durability.",
        "priority": "high",
        "reason": "No long runs detected in the last 28 days",
        "prescription": [
            "Schedule 1 long run each week",
            "Keep the long run comfortably aerobic",
            "Build duration gradually rather than jumping too quickly",
            "Keep the long run consistent before adding more quality elsewhere",
        ],
        "timeframe": "3-4 weeks",
    },
    "Intensity imbalance": {
        "headline": "Rebalance the training mix",
        "detail": "The current pattern appears too intensity-heavy. More easy running may improve adaptation and reduce unnecessary fatigue.",
        "priority": "high",
        "reason": "Training balance is skewed toward quality sessions",
        "prescription": [
            "Reduce the density of hard sessions",
            "Protect at least one threshold or interval session, not both at high frequency",
            "Increase the proportion of easy running",
            "Stabilise the weekly rhythm before progressing again",
        ],
        "timeframe": "2-3 weeks",
    },
    "Declining volume": {
        "headline": "Stabilise training load",
        "detail": "Recent volume has dropped, so the immediate goal is to rebuild a sustainable training rhythm before pushing harder.",
        "priority": "high",
        "reason": "Recent weekly distance is declining",
        "prescription": [
            "Re-establish a repeatable weekly pattern",
            "Bring volume back gradually rather than forcing a sharp increase",
            "Protect consistency before adding harder sessions",
            "Let volume stabilise before progressing again",
        ],
        "timeframe": "2-3 weeks",
    },
    "Moderate consistency": {
        "headline": "Tighten training consistency",
        "detail": "The overall pattern is reasonable, but more regular frequency would improve adaptation and make progression more reliable.",
        "priority": "medium",
        "reason": "Consistency is moderate rather than strong",
        "prescription": [
            "Add one extra easy run each week if recovery allows",
            "Reduce large gaps between run days",
            "Keep the overall structure predictable",
            "Use consistency as the immediate goal before pushing harder",
        ],
        "timeframe": "2-3 weeks",
    },
    "Moderate volume": {
        "headline": "Progress volume carefully",
        "detail": "Volume is reasonable, but there may be scope for a small increase if recovery and consistency are stable.",
        "priority": "medium",
        "reason": "Weekly mileage is adequate but not yet strong",
        "prescription": [
            "Increase weekly distance slightly rather than sharply",
            "Keep the increase sustainable",
            "Avoid progressing both volume and intensity at the same time",
            "Reassess after a stable block",
        ],
        "timeframe": "2-4 weeks",
    },
    "Limited threshold stimulus": {
        "headline": "Strengthen threshold support",
        "detail": "Threshold work is present but limited. Making it a more regular part of the week would strengthen the training pattern.",
        "priority": "medium",
        "reason": "Threshold stimulus is present but under-supported",
        "prescription": [
            "Keep 1 threshold session in the weekly pattern",
            "Make the session repeatable rather than maximal",
            "Support it with enough easy running around it",
            "Judge progress by consistency over several weeks",
        ],
        "timeframe": "3-4 weeks",
    },
    "Minimal long run stimulus": {
        "headline": "Make the long run more regular",
        "detail": "Endurance work is present but inconsistent. A more regular long run would improve durability and support overall development.",
        "priority": "medium",
        "reason": "Long run stimulus is present but limited",
        "prescription": [
            "Keep one long run in the week more consistently",
            "Aim for a predictable slot each week",
            "Keep it aerobic and controlled",
            "Build regularity before extending it much further",
        ],
        "timeframe": "3-4 weeks",
    },
    "Low quality density": {
        "headline": "Add a clearer quality stimulus",
        "detail": "The training pattern is very aerobic at the moment. A clearer dose of threshold or interval work may be needed.",
        "priority": "medium",
        "reason": "Very little quality work detected",
        "prescription": [
            "Introduce one quality session each week",
            "Start with threshold before adding more aggressive intensity",
            "Keep the rest of the week controlled",
            "Review the response after a few weeks",
        ],
        "timeframe": "3-4 weeks",
    },
    "Volume plateau": {
        "headline": "Progress training load carefully",
        "detail": "The current pattern looks stable, but a small increase in volume or quality may be needed to keep progress moving.",
        "priority": "medium",
        "reason": "Volume trend is flat",
        "prescription": [
            "Choose one lever to progress: volume or quality, not both",
            "Make the increase small and controlled",
            "Hold the new level long enough to absorb it",
            "Reassess before progressing again",
        ],
        "timeframe": "2-4 weeks",
    },
    "Well-structured but static": {
        "headline": "Change the stimulus rather than repeating the same block",
        "detail": "The training pattern is broadly solid, but the main levers are no longer progressing. Continuing with the same structure is unlikely to drive further improvement.",
        "priority": "medium",
        "reason": "Training is well structured but static",
        "prescription": [
            "Choose one main lever to change over the next block",
            "Progress threshold volume, long run stimulus, or overall volume in a controlled way",
            "Avoid changing everything at once",
            "Reassess after 3-4 weeks to see whether the new stimulus is working",
        ],
        "timeframe": "3-4 weeks",
    },
    "Limited progression across key levers": {
        "headline": "Create a clearer progression signal",
        "detail": "Several important components are currently flat. A more deliberate progression in one key area is likely needed.",
        "priority": "medium",
        "reason": "Key training levers are static across recent blocks",
        "prescription": [
            "Pick one primary lever to progress",
            "Keep the rest of the week stable while that change beds in",
            "Prefer a small, sustainable increase over a sharp jump",
            "Review the pattern after a few weeks before progressing again",
        ],
        "timeframe": "2-4 weeks",
    },
}


def determine_focus(metrics: dict, signals: list[dict]) -> dict:
    if not signals:
        return _default_focus()

    for priority in ["high", "medium", "low"]:
        priority_signals = [s for s in signals if s["priority"] == priority]

        for signal in priority_signals:
            signal_title = signal["title"]

            if signal_title in FOCUS_LIBRARY:
                focus_template = FOCUS_LIBRARY[signal_title]
                supporting = [s["title"] for s in priority_signals if s["title"] != signal_title]

                return {
                    "headline": focus_template["headline"],
                    "detail": focus_template["detail"],
                    "priority": focus_template["priority"],
                    "reason": focus_template["reason"],
                    "supporting_signals": supporting,
                    "prescription": focus_template["prescription"],
                    "timeframe": focus_template["timeframe"],
                }

    return _default_focus()