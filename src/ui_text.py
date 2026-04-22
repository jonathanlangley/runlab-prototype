from __future__ import annotations


def _format_km(value: float) -> str:
    return str(int(round(float(value or 0))))


def build_focus_diagnosis(focus: dict, metrics: dict) -> tuple[str, str]:
    headline = focus.get("headline", "")
    detail = focus.get("detail", "")

    run_days_per_week = round((metrics.get("days_with_run_last_28", 0) or 0) / 4.0, 1)
    recent_km = round(metrics.get("recent_avg_weekly_km", 0) or 0, 1)
    long_runs_last_28 = int(metrics.get("long_runs_last_28", 0) or 0)
    target_volume_range = focus.get("target_volume_range")
    target_run_days = focus.get("target_run_days_per_week")

    headline_lower = str(headline).lower()

    # Frequency / consistency limiter
    if "frequency" in headline_lower or "consistency" in headline_lower:
        title = "Your current frequency is limiting progression"
        summary = (
            f"You are currently running about {run_days_per_week} days per week. "
            f"For stronger progression, this likely needs to move closer to {target_run_days or 5}-6 consistent runs."
        )
        return title, summary

    # Volume / aerobic limiter
    if "volume" in headline_lower or "aerobic" in headline_lower:
        target_text = ""
        if target_volume_range:
            target_text = f" A sensible next range would be around {target_volume_range[0]}-{target_volume_range[1]} km per week."

        title = "Your current volume is limiting aerobic development"
        summary = (
            f"Your recent weekly average is about {recent_km} km. "
            f"That is likely limiting aerobic development and reducing the impact of harder sessions.{target_text}"
        )
        return title, summary

    # Threshold limiter
    if "threshold" in headline_lower:
        title = "Threshold support is currently underdeveloped"
        summary = (
            "Threshold work appears under-supported at the moment, which is likely limiting sustained pace development."
        )
        return title, summary

    # Long run / endurance limiter
    if "long run" in headline_lower or "endurance" in headline_lower:
        title = "Your endurance support is currently underdeveloped"
        if long_runs_last_28 == 0:
            summary = (
                "No long runs were detected in the last 28 days, which is likely limiting durability and endurance progression."
            )
        else:
            summary = (
                "The long run stimulus is present but too inconsistent to fully support durability and endurance progression."
            )
        return title, summary

    # Intensity support limiter
    if "support your current intensity" in headline_lower or "support vo2 work" in headline_lower:
        target_text = ""
        if target_volume_range:
            target_text = (
                f" The priority is to move weekly volume from about {_format_km(recent_km)} km "
                f"toward {target_volume_range[0]}-{target_volume_range[1]} km."
            )

        title = "Your harder sessions are not yet well supported by the current base"
        summary = (
            f"You are already doing some useful quality work, but at about {recent_km} km per week "
            f"and {run_days_per_week} run days per week, the supporting base looks too thin for that work to be fully effective.{target_text}"
        )
        return title, summary

    # Default fallback
    return headline or "Your current training pattern has a clear next focus", detail


def build_why_this_matters(metrics: dict, top_signals: list[dict], focus: dict | None = None) -> list[str]:
    bullets: list[str] = []

    recent_km = round(metrics.get("recent_avg_weekly_km", 0) or 0, 1)
    long_runs_last_28 = int(metrics.get("long_runs_last_28", 0) or 0)

    target_volume_range = focus.get("target_volume_range") if focus else None
    headline_lower = str(focus.get("headline", "")).lower() if focus else ""

    # --- INTENSITY SUPPORT CASE ---
    if "support your current intensity" in headline_lower or "support vo2 work" in headline_lower:

        bullets.append(
            "The current structure includes some quality work, but overall support is not strong enough for that work to translate into consistent progression."
        )

        if long_runs_last_28 == 0:
            bullets.append(
                "There is no consistent long run in the pattern, so endurance and durability are not being developed."
            )
        elif long_runs_last_28 < 3:
            bullets.append(
                "The long run is inconsistent, which limits durability and reduces your ability to sustain pace over time."
            )
        else:
            bullets.append(
                "The long run is present, but the overall structure still needs more support to make the quality work fully effective."
            )

        return bullets[:2]

    # --- VOLUME / AEROBIC CASE (UPDATED - NO METRIC DUPLICATION) ---
    if "volume" in headline_lower or "aerobic" in headline_lower:

        bullets.append(
            "The current weekly volume is not high enough to support consistent aerobic adaptation, which limits how much benefit you get from harder sessions."
        )

        if long_runs_last_28 == 0:
            bullets.append(
                "There is no consistent long run in the pattern, so endurance and durability are not being developed."
            )
        elif long_runs_last_28 < 3:
            bullets.append(
                "The long run is inconsistent, which limits durability and reduces your ability to sustain pace over time."
            )
        else:
            bullets.append(
                "The long run is present, but the overall structure still needs more support to build endurance effectively."
            )

        return bullets[:2]

    # --- FALLBACK: USE SIGNALS ---
    for signal in top_signals[:2]:
        detail = signal.get("detail", "")
        if detail:
            bullets.append(detail)

    # Deduplicate
    deduped: list[str] = []
    seen: set[str] = set()
    for bullet in bullets:
        if bullet not in seen:
            deduped.append(bullet)
            seen.add(bullet)

    return deduped[:2]