import pandas as pd


SESSION_ORDER = ["Easy", "Threshold", "VO2", "Long run"]


def allocate_targets_from_weights(total_run_days: int, weights: dict[str, float]) -> dict[str, int]:
    if total_run_days <= 0:
        return {session: 0 for session in SESSION_ORDER}

    raw = {session: weights.get(session, 0.0) * total_run_days for session in SESSION_ORDER}
    base = {session: int(raw[session]) for session in SESSION_ORDER}

    allocated = sum(base.values())
    remainder = total_run_days - allocated

    if remainder > 0:
        fractional_order = sorted(
            SESSION_ORDER,
            key=lambda s: raw[s] - base[s],
            reverse=True,
        )
        for i in range(remainder):
            base[fractional_order[i % len(fractional_order)]] += 1

    return base


def build_ideal_targets(focus: dict, total_run_days: int) -> dict[str, int]:
    headline = focus.get("headline", "").lower()

    weights = {
        "Easy": 0.70,
        "Threshold": 0.15,
        "VO2": 0.05,
        "Long run": 0.10,
    }

    if "threshold" in headline:
        weights = {
            "Easy": 0.65,
            "Threshold": 0.20,
            "VO2": 0.05,
            "Long run": 0.10,
        }
    elif "volume" in headline or "aerobic" in headline:
        weights = {
            "Easy": 0.70,
            "Threshold": 0.10,
            "VO2": 0.05,
            "Long run": 0.15,
        }
    elif "long run" in headline or "endurance" in headline:
        weights = {
            "Easy": 0.65,
            "Threshold": 0.10,
            "VO2": 0.05,
            "Long run": 0.20,
        }
    elif "support your current intensity" in headline or "support vo2 work" in headline:
        weights = {
            "Easy": 0.75,
            "Threshold": 0.10,
            "VO2": 0.05,
            "Long run": 0.10,
        }
    elif "frequency" in headline or "consistency" in headline:
        weights = {
            "Easy": 0.75,
            "Threshold": 0.10,
            "VO2": 0.05,
            "Long run": 0.10,
        }

    targets = allocate_targets_from_weights(total_run_days, weights)

    if total_run_days >= 5 and (
        "support your current intensity" in headline
        or "support vo2 work" in headline
        or "intensity" in headline
        or "vo2" in headline
    ):
        targets["VO2"] = max(1, targets["VO2"])
        total_assigned = sum(targets.values())
        if total_assigned > total_run_days:
            targets["Easy"] = max(0, targets["Easy"] - (total_assigned - total_run_days))

    return targets


def build_balance_comparison_df(df: pd.DataFrame, focus: dict) -> tuple[pd.DataFrame, int]:
    if df.empty or "date" not in df.columns or "workout_type" not in df.columns:
        empty_total = 0
        empty_targets = build_ideal_targets(focus, empty_total)
        empty_df = pd.DataFrame(
            {
                "Session type": SESSION_ORDER,
                "Current days": [0, 0, 0, 0],
                "Ideal days": [empty_targets[s] for s in SESSION_ORDER],
                "Gap": [0, 0, 0, 0],
                "Current %": [0.0, 0.0, 0.0, 0.0],
                "Ideal %": [0.0, 0.0, 0.0, 0.0],
            }
        )
        return empty_df, empty_total

    day_df = df.copy()
    day_df["run_date"] = pd.to_datetime(day_df["date"]).dt.date

    priority_map = {
        "easy": 1,
        "threshold": 2,
        "vo2": 3,
        "race": 3,
        "long run": 4,
    }

    label_map = {
        "easy": "Easy",
        "threshold": "Threshold",
        "vo2": "VO2",
        "race": "VO2",
        "long run": "Long run",
    }

    day_df["priority"] = day_df["workout_type"].map(priority_map).fillna(1)
    day_df["balance_label"] = day_df["workout_type"].map(label_map).fillna("Easy")

    dominant_by_day = (
        day_df.sort_values(["run_date", "priority"], ascending=[True, False])
        .drop_duplicates(subset=["run_date"], keep="first")
    )

    total_run_days = int(dominant_by_day["run_date"].nunique())

    current_counts = {
        "Easy": int((dominant_by_day["balance_label"] == "Easy").sum()),
        "Threshold": int((dominant_by_day["balance_label"] == "Threshold").sum()),
        "VO2": int((dominant_by_day["balance_label"] == "VO2").sum()),
        "Long run": int((dominant_by_day["balance_label"] == "Long run").sum()),
    }

    ideal_counts = build_ideal_targets(focus, total_run_days)

    rows = []
    for session_type in SESSION_ORDER:
        current_days = current_counts.get(session_type, 0)
        ideal_days = ideal_counts.get(session_type, 0)

        rows.append(
            {
                "Session type": session_type,
                "Current days": current_days,
                "Ideal days": ideal_days,
                "Gap": current_days - ideal_days,
                "Current %": round(current_days / total_run_days * 100, 1) if total_run_days else 0.0,
                "Ideal %": round(ideal_days / total_run_days * 100, 1) if total_run_days else 0.0,
            }
        )

    return pd.DataFrame(rows), total_run_days


def build_balance_interpretation(balance_df: pd.DataFrame, focus: dict, total_run_days: int) -> str:
    if balance_df.empty:
        return "No training balance insight available."

    headline = focus.get("headline", "").lower()
    target_volume_range = focus.get("target_volume_range")

    def gap_text(label: str) -> str:
        current_days = int(balance_df.loc[balance_df["Session type"] == label, "Current days"].iloc[0])
        ideal_days = int(balance_df.loc[balance_df["Session type"] == label, "Ideal days"].iloc[0])
        diff = current_days - ideal_days

        if diff > 0:
            return f"{label} is {abs(diff)} run day(s) above the current target"
        if diff < 0:
            return f"{label} is {abs(diff)} run day(s) below the current target"
        return f"{label} is in line with the current target"

    prefix = f"Based on {total_run_days} distinct run days. "

    if "frequency" in headline or "consistency" in headline:
        return prefix + (
            f"The main issue is still frequency rather than session mix. "
            f"{gap_text('Easy')}, but the bigger opportunity is simply getting more repeatable run days into the week."
        )

    if "volume" in headline or "aerobic" in headline:
        extra = ""
        if target_volume_range:
            extra = f" The short-term volume target is roughly {target_volume_range[0]}-{target_volume_range[1]} km per week."
        return prefix + (
            f"The pattern supports a more aerobic approach. "
            f"{gap_text('Easy')} and {gap_text('VO2')}.{extra}"
        )

    if "threshold" in headline:
        return prefix + (
            f"This recommendation is supported by the current mix. "
            f"{gap_text('Threshold')}."
        )

    if "long run" in headline or "endurance" in headline:
        return prefix + (
            f"The endurance gap shows up clearly in the session mix. "
            f"{gap_text('Long run')}."
        )

    if "support your current intensity" in headline or "support vo2 work" in headline:
        extra = ""
        if target_volume_range:
            extra = f" A sensible next volume range would be around {target_volume_range[0]}-{target_volume_range[1]} km per week."
        return prefix + (
            f"The current intensity is not the main problem on its own. "
            f"{gap_text('VO2')} and {gap_text('Easy')}. "
            f"The bigger opportunity is to give the harder work better aerobic support through more easy running and a more stable weekly structure.{extra}"
        )

    return prefix + (
        f"Compared with the current target mix, {gap_text('Easy')}, {gap_text('Threshold')}, "
        f"{gap_text('VO2')}, and {gap_text('Long run')}."
    )