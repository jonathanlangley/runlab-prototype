def build_focus_diagnosis(focus: dict, metrics: dict) -> tuple[str, str]:
    headline = focus.get("headline", "")
    detail = focus.get("detail", "")

    run_days_per_week = round((metrics.get("days_with_run_last_28", 0) or 0) / 4.0, 1)
    recent_km = round(metrics.get("recent_avg_weekly_km", 0) or 0, 1)
    long_runs_last_28 = int(metrics.get("long_runs_last_28", 0) or 0)

    headline_lower = headline.lower()

    if "frequency" in headline_lower or "consistency" in headline_lower:
        title = "Your current frequency is limiting progression"
        summary = (
            f"You are currently running about {run_days_per_week} days per week. "
            f"For stronger progression, this likely needs to move closer to 5–6 consistent runs."
        )
        return title, summary

    if "volume" in headline_lower or "aerobic" in headline_lower:
        title = "Your current volume is limiting aerobic development"
        summary = (
            f"Your recent weekly average is about {recent_km} km. "
            f"That is likely limiting aerobic development and reducing the impact of harder sessions."
        )
        return title, summary

    if "threshold" in headline_lower:
        title = "Threshold support is currently underdeveloped"
        summary = "Threshold work appears under-supported at the moment, which is likely limiting sustained pace development."
        return title, summary

    if "long run" in headline_lower or "endurance" in headline_lower:
        title = "Your endurance support is currently underdeveloped"
        if long_runs_last_28 == 0:
            summary = "No long runs were detected in the last 28 days, which is likely limiting durability and endurance progression."
        else:
            summary = "The long run stimulus is present but too inconsistent to fully support durability and endurance progression."
        return title, summary

    if "recovery" in headline_lower or "rebalance" in headline_lower or "intensity" in headline_lower or "vo2" in headline_lower:
        title = "Your training mix is currently too intensity-heavy"
        summary = "The pattern suggests you may be carrying too much hard work relative to your easy and threshold support, which can blunt adaptation."
        return title, summary

    return headline or "Your current training pattern has a clear next focus", detail


def build_why_this_matters(metrics: dict, top_signals: list[dict]) -> list[str]:
    bullets = []

    run_days_per_week = round((metrics.get("days_with_run_last_28", 0) or 0) / 4.0, 1)
    recent_km = round(metrics.get("recent_avg_weekly_km", 0) or 0, 1)
    long_runs_last_28 = int(metrics.get("long_runs_last_28", 0) or 0)

    bullets.append(f"You are currently running about {run_days_per_week} days per week, which may be limiting adaptation.")
    bullets.append(f"Recent weekly volume is about {recent_km} km, which may be too low to support stronger aerobic development.")

    if long_runs_last_28 == 0:
        bullets.append("No long runs were detected in the last 28 days, which limits endurance support.")
    elif long_runs_last_28 < 3:
        bullets.append(f"Long run stimulus is present but inconsistent, with {long_runs_last_28} long run(s) in the last 28 days.")

    for signal in top_signals[:2]:
        detail = signal.get("detail", "")
        if detail and detail not in bullets:
            bullets.append(detail)

    return bullets[:4]