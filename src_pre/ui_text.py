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

    # --- Frequency / consistency limiter ---
    if "frequency" in headline_lower or "consistency" in headline_lower:

        if target_run_days:
            if target_run_days >= 6:
                target_text = "6 consistent runs"
            else:
                target_text = f"{target_run_days}-6 consistent runs"
        else:
            target_text = "5-6 consistent runs"

        title = "Your current frequency is limiting progression"
        summary = (
            f"You are currently running about {run_days_per_week} days per week. "
            f"For stronger progression, this likely needs to move closer to {target_text}."
        )
        return title, summary

    # --- Volume / aerobic limiter ---
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

    # --- Threshold limiter ---
    if "threshold" in headline_lower:
        title = "Threshold support is currently underdeveloped"
        summary = (
            "Threshold work appears under-supported at the moment, which is likely limiting sustained pace development."
        )
        return title, summary

    # --- Long run / endurance limiter ---
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

    # --- Intensity support limiter ---
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

    # --- Default fallback ---
    return headline or "Your current training pattern has a clear next focus", detail


def build_why_this_matters(metrics: dict, top_signals: list[dict], focus: dict | None = None) -> list[str]:
    """
    This section should NOT repeat the diagnosis.
    It should explain WHY it matters physiologically or structurally.
    """

    bullets: list[str] = []

    headline_lower = str(focus.get("headline", "")).lower() if focus else ""

    # --- INTENSITY SUPPORT CASE ---
    if "support your current intensity" in headline_lower or "support vo2 work" in headline_lower:

        bullets.append(
            "Higher intensity sessions carry a high fatigue cost, and without enough supporting volume they become less effective."
        )

        bullets.append(
            "A stronger aerobic base allows you to recover better and sustain faster paces, which ultimately improves 5K performance."
        )

        return bullets[:2]

    # --- VOLUME CASE ---
    if "volume" in headline_lower or "aerobic" in headline_lower:

        bullets.append(
            "Aerobic development depends heavily on total training volume, which builds endurance and efficiency over time."
        )

        bullets.append(
            "Without enough volume, harder sessions provide less long-term benefit and progression can stall."
        )

        return bullets[:2]

    # --- CONSISTENCY CASE ---
    if "consistency" in headline_lower or "frequency" in headline_lower:

        bullets.append(
            "Consistent training creates repeated stimulus, which is essential for adaptation and long-term progression."
        )

        bullets.append(
            "Large gaps between runs reduce the cumulative effect of training and limit overall development."
        )

        return bullets[:2]

    # --- DEFAULT FALLBACK (use signals but avoid duplication) ---
    if top_signals:
        for signal in top_signals[:2]:
            detail = str(signal.get("detail", "")).strip()
            if detail:
                bullets.append(detail)

    return bullets[:2]