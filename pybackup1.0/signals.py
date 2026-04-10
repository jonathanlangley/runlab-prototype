from __future__ import annotations


def derive_signals(metrics: dict) -> list[dict]:
    signals: list[dict] = []

    consistency = metrics["consistency_label"]
    if consistency == "low":
        signals.append(
            {
                "title": "Low consistency",
                "detail": "Training frequency over the last 28 days is low. Building consistency is likely the highest priority.",
                "priority": "high",
            }
        )
    elif consistency == "moderate":
        signals.append(
            {
                "title": "Moderate consistency",
                "detail": "There is a reasonable training rhythm, but more regular frequency would likely improve adaptation.",
                "priority": "medium",
            }
        )
    else:
        signals.append(
            {
                "title": "Strong consistency",
                "detail": "Training frequency is solid. This creates a good base for progression.",
                "priority": "low",
            }
        )

    if metrics["volume_trend"] == "flat":
        signals.append(
            {
                "title": "Volume plateau",
                "detail": "Average weekly distance is broadly flat. This may indicate a plateau unless stimulus changes elsewhere.",
                "priority": "medium",
            }
        )
    elif metrics["volume_trend"] == "declining":
        signals.append(
            {
                "title": "Declining volume",
                "detail": "Recent weekly distance is lower than the previous block. This could reduce aerobic progression.",
                "priority": "high",
            }
        )
    else:
        signals.append(
            {
                "title": "Volume progressing",
                "detail": "Recent weekly distance is moving upward, which may support continued aerobic development if tolerated well.",
                "priority": "low",
            }
        )

    if metrics["threshold_sessions_last_28"] == 0:
        signals.append(
            {
                "title": "No threshold work detected",
                "detail": "No threshold sessions were identified in the last 28 days. This may limit sustained pace development.",
                "priority": "high",
            }
        )
    elif metrics["threshold_sessions_last_28"] == 1:
        signals.append(
            {
                "title": "Limited threshold stimulus",
                "detail": "Only one threshold session was detected in the last 28 days. Threshold development may be under-supported.",
                "priority": "medium",
            }
        )

    if metrics["long_runs_last_28"] == 0:
        signals.append(
            {
                "title": "No long run stimulus",
                "detail": "No long runs were detected in the last 28 days. This may limit endurance progression.",
                "priority": "high",
            }
        )
    elif metrics["long_runs_last_28"] == 1:
        signals.append(
            {
                "title": "Minimal long run stimulus",
                "detail": "Only one long run was detected in the last 28 days. Endurance support may be limited.",
                "priority": "medium",
            }
        )
    if metrics["volume_pattern"] == "peaked_then_dipped":
        signals.append(
            {
                "title": "Recent dip after peak volume",
                "detail": metrics["volume_pattern_detail"],
                "priority": "medium",
            }
        )
    elif metrics["volume_pattern"] == "volatile":
        signals.append(
            {
                "title": "Volatile weekly volume",
                "detail": metrics["volume_pattern_detail"],
                "priority": "medium",
            }
        )
    return signals