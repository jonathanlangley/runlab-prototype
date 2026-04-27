from __future__ import annotations


def _format_km(value: float) -> str:
    return str(int(round(float(value))))


def recommend_volume_target(current_km: float) -> tuple[int, int]:
    current_km = float(current_km or 0)

    if current_km < 30:
        return int(round(current_km + 10)), int(round(current_km + 20))
    if current_km < 50:
        return int(round(current_km + 10)), int(round(current_km + 15))
    if current_km < 70:
        return int(round(current_km + 5)), int(round(current_km + 10))
    return int(round(current_km + 5)), int(round(current_km + 8))


def recommend_run_days_target(current_run_days_per_week: float) -> int:
    if current_run_days_per_week < 4:
        return 5
    if current_run_days_per_week < 5:
        return 6
    return 6


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
        "target_volume_range": None,
        "target_run_days_per_week": None,
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
        "headline": "Build a stronger base to support your current intensity",
        "detail": "High-intensity work is present, but the supporting volume and consistency are not yet strong enough to make it as effective as it could be.",
        "priority": "high",
        "reason": "Training intensity is under-supported by the current base",
        "prescription": [
            "Increase weekly distance gradually through easy running",
            "Add 1-2 additional easy run days if recovery allows",
            "Keep 1 quality session per week, but avoid adding extra intensity",
            "Introduce or stabilise a weekly long run",
        ],
        "timeframe": "3-6 weeks",
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
        "detail": "The training pattern is very aerobic at the moment. A clearer dose of threshold or VO2 work may be needed.",
        "priority": "medium",
        "reason": "Very little quality work detected",
        "prescription": [
            "Introduce one quality session each week",
            "Start with threshold before adding more aggressive VO2 work",
            "Keep the rest of the week controlled",
            "Review the response after a few weeks",
        ],
        "timeframe": "3-4 weeks",
    },
    "VO2-heavy relative to threshold": {
        "headline": "Support VO2 work with a stronger aerobic and threshold base",
        "detail": "VO2 work is showing up more often than threshold work. The issue is less about removing intensity altogether, and more about giving it better support underneath.",
        "priority": "medium",
        "reason": "VO2 sessions are outnumbering threshold sessions",
        "prescription": [
            "Hold VO2 to a manageable dose rather than adding more top-end intensity",
            "Make threshold work the more repeatable weekly quality session",
            "Support the quality work with enough easy volume",
            "Reassess after a few weeks of a more balanced structure",
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


def _build_volume_guidance(metrics: dict) -> tuple[str, tuple[int, int], int]:
    current_km = float(metrics.get("recent_avg_weekly_km", 0) or 0)
    current_run_days_per_week = float((metrics.get("days_with_run_last_28", 0) or 0) / 4.0)

    low_target, high_target = recommend_volume_target(current_km)
    target_run_days = recommend_run_days_target(current_run_days_per_week)

    volume_line = (
        f"Increase weekly volume from about {_format_km(current_km)} km to {low_target}-{high_target} km"
    )
    return volume_line, (low_target, high_target), target_run_days


def _augment_focus(base_focus: dict, metrics: dict) -> dict:
    focus = dict(base_focus)
    volume_line, volume_range, target_run_days = _build_volume_guidance(metrics)
    headline_lower = str(focus.get("headline", "")).lower()

    current_km = float(metrics.get("recent_avg_weekly_km", 0) or 0)
    current_run_days_per_week = round(float((metrics.get("days_with_run_last_28", 0) or 0) / 4.0), 1)

    focus["target_volume_range"] = volume_range
    focus["target_run_days_per_week"] = target_run_days

    if (
        "base to support your current intensity" in headline_lower
        or "support vo2 work with a stronger aerobic and threshold base" in headline_lower
    ):
        focus["detail"] = (
            f"You are already doing some higher-intensity work, but the supporting base looks too thin at the moment. "
            f"Recent volume is about {_format_km(current_km)} km per week across roughly {current_run_days_per_week} run days, "
            f"so the immediate goal is to make the harder work better supported rather than simply adding more of it."
        )
        focus["prescription"] = [
            volume_line,
            f"Build toward {target_run_days} run days per week, mainly through easy running",
            "Keep 1 quality session per week, but avoid adding extra VO2 load for now",
            "Introduce or stabilise a weekly long run",
        ]
        focus["timeframe"] = "3-6 weeks"

    elif "build aerobic volume" in headline_lower:
        focus["prescription"] = [
            volume_line,
            f"Build toward {target_run_days} run days per week if recovery allows",
            "Use easy running to build volume rather than adding extra intensity",
            "Keep the weekly structure repeatable and controlled",
        ]

    elif "progress volume carefully" in headline_lower:
        focus["prescription"] = [
            volume_line,
            f"Build toward {target_run_days} run days per week if practical",
            "Avoid progressing both volume and intensity at the same time",
            "Reassess after a stable block",
        ]

    elif "increase weekly run frequency" in headline_lower or "tighten training consistency" in headline_lower:
        focus["prescription"] = [
            f"Build toward {target_run_days} run days per week",
            volume_line,
            "Keep most added running easy",
            "Avoid adding more intensity until the weekly rhythm is stable",
        ]

    elif "stabilise training load" in headline_lower:
        focus["prescription"] = [
            "Re-establish a repeatable weekly pattern",
            volume_line,
            f"Build toward {target_run_days} run days per week if recovery allows",
            "Let volume stabilise before progressing harder sessions again",
        ]

    return focus


def determine_focus(metrics: dict, signals: list[dict]) -> dict:
    if not signals:
        return _augment_focus(_default_focus(), metrics)

    for priority in ["high", "medium", "low"]:
        priority_signals = [s for s in signals if s.get("priority") == priority]
        for signal in priority_signals:
            signal_title = signal.get("title", "")
            if signal_title in FOCUS_LIBRARY:
                selected = dict(FOCUS_LIBRARY[signal_title])
                selected["supporting_signals"] = [s.get("title", "") for s in priority_signals[:3] if s.get("title")]
                return _augment_focus(selected, metrics)

    return _augment_focus(_default_focus(), metrics)