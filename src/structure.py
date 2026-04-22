def build_weekly_structure(metrics: dict) -> dict[str, float]:
    weeks = 4.0
    return {
        "Threshold": round((metrics.get("threshold_sessions_last_28", 0) or 0) / weeks, 2),
        "VO2": round(
            (
                (metrics.get("vo2_sessions_last_28", 0) or 0)
                + (metrics.get("race_sessions_last_28", 0) or 0)
            ) / weeks,
            2,
        ),
        "Long run": round((metrics.get("long_runs_last_28", 0) or 0) / weeks, 2),
    }


def get_target_weekly_structure(focus: dict) -> dict[str, float]:
    headline = focus.get("headline", "").lower()

    targets = {
        "Threshold": 0.75,
        "VO2": 0.25,
        "Long run": 1.0,
    }

    if "threshold" in headline:
        targets["Threshold"] = 1.0
        targets["VO2"] = 0.25
    elif "volume" in headline or "aerobic" in headline:
        targets["Threshold"] = 0.75
        targets["VO2"] = 0.0
    elif "intensity" in headline or "vo2" in headline or "rebalance" in headline:
        targets["Threshold"] = 0.75
        targets["VO2"] = 0.0

    return targets