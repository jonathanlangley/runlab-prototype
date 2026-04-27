from __future__ import annotations

from typing import Any

import pandas as pd

SESSION_ORDER = ["Easy", "Quality", "Long run"]
DETAILED_SESSION_ORDER = ["Easy", "Threshold", "VO2", "Long run"]


def _normalise_type(value: Any) -> str:
    text = str(value or "easy").strip().lower()
    if text == "race":
        return "vo2"
    if text not in {"easy", "threshold", "vo2", "long run"}:
        return "easy"
    return text


def _dominant_session_by_day(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["run_date", "balance_label", "detailed_label"])

    day_df = df.copy()
    day_df["run_date"] = pd.to_datetime(day_df["date"]).dt.date
    day_df["workout_type"] = day_df["workout_type"].apply(_normalise_type)

    priority_map = {"easy": 1, "threshold": 2, "vo2": 3, "long run": 4}
    detailed_map = {"easy": "Easy", "threshold": "Threshold", "vo2": "VO2", "long run": "Long run"}
    balance_map = {"easy": "Easy", "threshold": "Quality", "vo2": "Quality", "long run": "Long run"}

    day_df["priority"] = day_df["workout_type"].map(priority_map).fillna(1)
    day_df["detailed_label"] = day_df["workout_type"].map(detailed_map).fillna("Easy")
    day_df["balance_label"] = day_df["workout_type"].map(balance_map).fillna("Easy")

    return (
        day_df.sort_values(["run_date", "priority"], ascending=[True, False])
        .drop_duplicates(subset=["run_date"], keep="first")
        .reset_index(drop=True)
    )


def allocate_targets_from_weights(total_run_days: int, weights: dict[str, float], order: list[str] | None = None) -> dict[str, int]:
    order = order or SESSION_ORDER
    if total_run_days <= 0:
        return {session: 0 for session in order}

    raw = {session: weights.get(session, 0.0) * total_run_days for session in order}
    base = {session: int(raw[session]) for session in order}
    remainder = total_run_days - sum(base.values())

    for session in sorted(order, key=lambda s: raw[s] - base[s], reverse=True)[:remainder]:
        base[session] += 1

    return base


def target_weights_for_focus(focus: dict[str, Any]) -> dict[str, float]:
    primary_key = str(focus.get("primary_key", "")).lower()

    if primary_key == "consistency":
        return {"Easy": 0.78, "Quality": 0.10, "Long run": 0.12}
    if primary_key == "volume":
        return {"Easy": 0.72, "Quality": 0.12, "Long run": 0.16}
    if primary_key == "balance":
        return {"Easy": 0.76, "Quality": 0.10, "Long run": 0.14}
    if primary_key == "long_run":
        return {"Easy": 0.68, "Quality": 0.12, "Long run": 0.20}
    if primary_key == "threshold":
        return {"Easy": 0.68, "Quality": 0.20, "Long run": 0.12}
    if primary_key == "quality":
        return {"Easy": 0.68, "Quality": 0.20, "Long run": 0.12}
    return {"Easy": 0.70, "Quality": 0.15, "Long run": 0.15}


def build_ideal_targets(focus: dict[str, Any], total_run_days: int) -> dict[str, int]:
    targets = allocate_targets_from_weights(total_run_days, target_weights_for_focus(focus), SESSION_ORDER)

    # Avoid unrealistic targets when frequency is low. At 3-4 run days per week, combine quality into one bucket.
    if total_run_days < 16:
        targets["Quality"] = min(targets["Quality"], max(1, round(total_run_days / 7))) if total_run_days >= 8 else 0
        assigned = sum(targets.values())
        targets["Easy"] = max(0, targets["Easy"] + (total_run_days - assigned))

    return targets


def split_quality_targets(quality_days: int, focus: dict[str, Any]) -> dict[str, int]:
    primary_key = str(focus.get("primary_key", "")).lower()
    if quality_days <= 0:
        return {"Threshold": 0, "VO2": 0}
    if primary_key in {"threshold", "volume", "balance", "consistency"}:
        threshold = max(1, quality_days - 1)
        return {"Threshold": threshold, "VO2": quality_days - threshold}
    if primary_key == "quality" and quality_days >= 2:
        return {"Threshold": 1, "VO2": quality_days - 1}
    return {"Threshold": quality_days, "VO2": 0}


def build_balance_comparison_df(df: pd.DataFrame, focus: dict[str, Any]) -> tuple[pd.DataFrame, int]:
    required = {"date", "workout_type"}
    if df.empty or not required.issubset(df.columns):
        targets = build_ideal_targets(focus, 0)
        return pd.DataFrame({
            "Session type": SESSION_ORDER,
            "Current days": [0, 0, 0],
            "Ideal days": [targets[s] for s in SESSION_ORDER],
            "Gap": [0, 0, 0],
            "Current %": [0.0, 0.0, 0.0],
            "Ideal %": [0.0, 0.0, 0.0],
        }), 0

    dominant = _dominant_session_by_day(df)
    total_run_days = int(dominant["run_date"].nunique())
    current_counts = {session: int((dominant["balance_label"] == session).sum()) for session in SESSION_ORDER}
    ideal_counts = build_ideal_targets(focus, total_run_days)

    rows = []
    for session in SESSION_ORDER:
        current = current_counts.get(session, 0)
        ideal = ideal_counts.get(session, 0)
        rows.append({
            "Session type": session,
            "Current days": current,
            "Ideal days": ideal,
            "Gap": current - ideal,
            "Current %": round(current / total_run_days * 100, 1) if total_run_days else 0.0,
            "Ideal %": round(ideal / total_run_days * 100, 1) if total_run_days else 0.0,
        })

    return pd.DataFrame(rows), total_run_days


def build_detailed_balance_df(df: pd.DataFrame, focus: dict[str, Any]) -> pd.DataFrame:
    dominant = _dominant_session_by_day(df)
    total = int(dominant["run_date"].nunique()) if not dominant.empty else 0
    quality_target = build_ideal_targets(focus, total).get("Quality", 0)
    split = split_quality_targets(quality_target, focus)
    targets = {
        "Easy": build_ideal_targets(focus, total).get("Easy", 0),
        "Threshold": split["Threshold"],
        "VO2": split["VO2"],
        "Long run": build_ideal_targets(focus, total).get("Long run", 0),
    }

    rows = []
    for session in DETAILED_SESSION_ORDER:
        current = int((dominant["detailed_label"] == session).sum()) if not dominant.empty else 0
        ideal = targets.get(session, 0)
        rows.append({"Session type": session, "Current days": current, "Ideal days": ideal, "Gap": current - ideal})
    return pd.DataFrame(rows)


def _get_days(balance_df: pd.DataFrame, label: str, col: str) -> int:
    match = balance_df.loc[balance_df["Session type"] == label, col]
    if match.empty:
        return 0
    return int(match.iloc[0])


def build_balance_interpretation(balance_df: pd.DataFrame, focus: dict[str, Any], total_run_days: int) -> str:
    if balance_df.empty or total_run_days <= 0:
        return "No recent run-day mix is available yet."

    primary_key = str(focus.get("primary_key", ""))
    quality_current = _get_days(balance_df, "Quality", "Current days")
    quality_ideal = _get_days(balance_df, "Quality", "Ideal days")
    easy_current = _get_days(balance_df, "Easy", "Current days")
    easy_ideal = _get_days(balance_df, "Easy", "Ideal days")
    long_current = _get_days(balance_df, "Long run", "Current days")
    long_ideal = _get_days(balance_df, "Long run", "Ideal days")

    prefix = f"Based on {total_run_days} distinct run days in the last 4 weeks, "

    if primary_key == "balance":
        return prefix + (
            f"quality appears heavy relative to the support underneath. The next block should move closer to "
            f"{easy_ideal} easy days, {quality_ideal} quality day(s), and {long_ideal} long run day(s)."
        )
    if primary_key == "volume":
        return prefix + (
            f"the mix should favour easy volume. You currently have {easy_current} easy days against a target of about {easy_ideal}."
        )
    if primary_key == "long_run":
        return prefix + (
            f"the main gap is long-run regularity. You currently have {long_current} long run day(s), with a short-term target of about {long_ideal}."
        )
    if primary_key == "threshold":
        return prefix + (
            f"quality is best treated as one controlled weekly stimulus. You currently have {quality_current} quality day(s), against a target of about {quality_ideal}."
        )

    return prefix + (
        f"a realistic next mix is about {easy_ideal} easy days, {quality_ideal} quality day(s), and {long_ideal} long run day(s)."
    )
