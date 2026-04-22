import pandas as pd


def build_ideal_targets(focus: dict) -> dict[str, int]:
    headline = focus.get("headline", "").lower()

    targets = {
        "Easy": 14,
        "Threshold": 3,
        "VO2": 1,
        "Long run": 4,
    }

    if "threshold" in headline:
        targets["Threshold"] = 4
    elif "volume" in headline or "aerobic" in headline:
        targets["Easy"] = 15
        targets["VO2"] = 0
    elif "intensity" in headline or "vo2" in headline or "rebalance" in headline:
        targets["VO2"] = 0

    return targets


def build_balance_comparison_df(df: pd.DataFrame, focus: dict) -> tuple[pd.DataFrame, int]:
    """
    Build training balance from distinct run days, not raw session counts.
    Each day is assigned its dominant stimulus:
    Long run > VO2/race > Threshold > Easy
    """
    if df.empty or "date" not in df.columns or "workout_type" not in df.columns:
        empty_df = pd.DataFrame(
            {
                "Session type": ["Easy", "Threshold", "VO2", "Long run"],
                "Current days": [0, 0, 0, 0],
                "Ideal days": [
                    build_ideal_targets(focus)["Easy"],
                    build_ideal_targets(focus)["Threshold"],
                    build_ideal_targets(focus)["VO2"],
                    build_ideal_targets(focus)["Long run"],
                ],
                "Gap": [0, 0, 0, 0],
                "Current %": [0.0, 0.0, 0.0, 0.0],
            }
        )
        return empty_df, 0

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

    ideal_counts = build_ideal_targets(focus)

    rows = []
    for session_type in ["Easy", "Threshold", "VO2", "Long run"]:
        current_days = current_counts.get(session_type, 0)
        ideal_days = ideal_counts.get(session_type, 0)
        rows.append(
            {
                "Session type": session_type,
                "Current days": current_days,
                "Ideal days": ideal_days,
                "Gap": current_days - ideal_days,
                "Current %": round(current_days / total_run_days * 100, 1) if total_run_days else 0.0,
            }
        )

    return pd.DataFrame(rows), total_run_days


def build_balance_interpretation(balance_df: pd.DataFrame, focus: dict, total_run_days: int) -> str:
    if balance_df.empty:
        return "No training balance insight available."

    headline = focus.get("headline", "").lower()

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
        return prefix + (
            f"The pattern supports a more aerobic approach. "
            f"{gap_text('Easy')} and {gap_text('VO2')}."
        )

    if "threshold" in headline:
        return prefix + f"This recommendation is supported by the current mix. {gap_text('Threshold')}."

    if "long run" in headline or "endurance" in headline:
        return prefix + f"The endurance gap shows up clearly in the session mix. {gap_text('Long run')}."

    if "rebalance" in headline or "intensity" in headline or "recovery" in headline or "vo2" in headline:
        return prefix + (
            f"The current pattern looks too intensity-heavy. "
            f"{gap_text('VO2')} and {gap_text('Easy')}."
        )

    return prefix + (
        f"Compared with the current target mix, {gap_text('Easy')}, {gap_text('Threshold')}, "
        f"{gap_text('VO2')}, and {gap_text('Long run')}."
    )