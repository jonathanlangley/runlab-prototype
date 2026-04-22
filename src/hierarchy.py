def build_training_hierarchy(metrics: dict, focus: dict) -> dict:
    primary = {
        "label": focus.get("headline", "Primary limiter"),
        "detail": focus.get("detail", ""),
    }

    secondary = []
    supportive = []

    threshold_count = int(metrics.get("threshold_sessions_last_28", 0) or 0)
    vo2_count = int(metrics.get("vo2_sessions_last_28", 0) or 0)
    race_count = int(metrics.get("race_sessions_last_28", 0) or 0)
    long_run_count = int(metrics.get("long_runs_last_28", 0) or 0)

    if threshold_count > 0:
        if threshold_count <= 2:
            secondary.append(
                {
                    "label": "Threshold work",
                    "detail": f"Present but limited, with {threshold_count} session(s) in the last 4 weeks.",
                }
            )
        else:
            supportive.append(
                {
                    "label": "Threshold work",
                    "detail": f"Present, with {threshold_count} session(s) in the last 4 weeks.",
                }
            )
    else:
        secondary.append(
            {
                "label": "Threshold work",
                "detail": "Absent in the last 4 weeks.",
            }
        )

    if long_run_count > 0:
        if long_run_count <= 2:
            secondary.append(
                {
                    "label": "Long run stimulus",
                    "detail": f"Present but inconsistent, with {long_run_count} long run(s) in the last 4 weeks.",
                }
            )
        else:
            supportive.append(
                {
                    "label": "Long run stimulus",
                    "detail": f"Present, with {long_run_count} long run(s) in the last 4 weeks.",
                }
            )
    else:
        secondary.append(
            {
                "label": "Long run stimulus",
                "detail": "Absent in the last 4 weeks.",
            }
        )

    if vo2_count > 0:
        supportive.append(
            {
                "label": "VO2 work",
                "detail": f"Present, with {vo2_count} session(s) in the last 4 weeks.",
            }
        )

    if race_count > 0:
        supportive.append(
            {
                "label": "Race efforts",
                "detail": f"Present, with {race_count} race effort(s) in the last 4 weeks.",
            }
        )

    return {
        "primary": primary,
        "secondary": secondary,
        "supportive": supportive,
    }