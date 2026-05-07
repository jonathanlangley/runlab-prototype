import re
from typing import Any, Dict, Optional
import pandas as pd


VALID_WORKOUT_TYPES = {"easy", "threshold", "vo2", "long run", "race"}


def parse_time_to_seconds(time_value: Any) -> Optional[int]:
    if time_value is None or pd.isna(time_value):
        return None
    if isinstance(time_value, (int, float)):
        return int(time_value)
    if isinstance(time_value, str):
        parts = time_value.strip().split(":")
        try:
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        except ValueError:
            return None
    return None


def seconds_to_pace_str(seconds_per_km: Optional[float]) -> Optional[str]:
    if seconds_per_km is None:
        return None
    total_seconds = int(round(seconds_per_km))
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}/km"


def clean_text(*values: Any) -> str:
    text_parts = []
    for value in values:
        if value is not None and not pd.isna(value):
            text_parts.append(str(value).lower().strip())
    return re.sub(r"\s+", " ", " ".join(text_parts))


def pace_sec_per_km(distance_km: Any, duration_min: Any) -> Optional[float]:
    if distance_km is None or duration_min is None or pd.isna(distance_km) or pd.isna(duration_min):
        return None
    if float(distance_km) <= 0:
        return None
    return float(duration_min) * 60.0 / float(distance_km)


def riegel_predict_time(base_time_sec: float, base_distance_km: float, target_distance_km: float, exponent: float = 1.06) -> float:
    return float(base_time_sec) * (float(target_distance_km) / float(base_distance_km)) ** exponent


def build_pace_bands(user_profile: Dict[str, Any]) -> Dict[str, Optional[float]]:
    current_5k_time_sec = parse_time_to_seconds(user_profile.get("current_5k_time"))
    current_hm_time_sec = parse_time_to_seconds(user_profile.get("current_hm_time"))
    current_marathon_time_sec = parse_time_to_seconds(user_profile.get("current_marathon_time"))

    current_5k_pace_sec = current_5k_time_sec / 5.0 if current_5k_time_sec else None
    if current_hm_time_sec:
        current_hm_pace_sec = current_hm_time_sec / 21.0975
    elif current_5k_time_sec:
        current_hm_pace_sec = riegel_predict_time(current_5k_time_sec, 5.0, 21.0975) / 21.0975
    else:
        current_hm_pace_sec = None

    if current_marathon_time_sec:
        current_marathon_pace_sec = current_marathon_time_sec / 42.195
    elif current_hm_pace_sec is not None:
        current_marathon_pace_sec = current_hm_pace_sec + 15.0
    elif current_5k_time_sec:
        current_marathon_pace_sec = riegel_predict_time(current_5k_time_sec, 5.0, 42.195) / 42.195
    else:
        current_marathon_pace_sec = None

    bands = {
        "very_fast_upper": None,
        "vo2_lower": None,
        "vo2_upper": None,
        "threshold_lower": None,
        "threshold_upper": None,
        "steady_lower": None,
        "steady_upper": None,
        "easy_lower": None,
        "recovery_lower": None,
        "current_5k_pace_sec": current_5k_pace_sec,
        "current_hm_pace_sec": current_hm_pace_sec,
        "current_marathon_pace_sec": current_marathon_pace_sec,
    }

    if current_5k_pace_sec is not None:
        bands["very_fast_upper"] = current_5k_pace_sec - 12.0
        bands["vo2_lower"] = current_5k_pace_sec - 12.0
        bands["vo2_upper"] = current_5k_pace_sec + 3.0

    threshold_anchor_sec = None
    if current_hm_pace_sec is not None and current_5k_pace_sec is not None:
        threshold_anchor_sec = 0.7 * current_hm_pace_sec + 0.3 * (current_5k_pace_sec * 1.08)
    elif current_hm_pace_sec is not None:
        threshold_anchor_sec = current_hm_pace_sec
    elif current_5k_pace_sec is not None:
        threshold_anchor_sec = current_5k_pace_sec * 1.08

    if threshold_anchor_sec is not None:
        threshold_lower = threshold_anchor_sec - 8.0
        if bands["vo2_upper"] is not None:
            threshold_lower = max(threshold_lower, bands["vo2_upper"])
        bands["threshold_lower"] = threshold_lower
        bands["threshold_upper"] = threshold_anchor_sec + 7.0

    if current_marathon_pace_sec is not None:
        steady_lower = bands["threshold_upper"] if bands["threshold_upper"] is not None else current_marathon_pace_sec - 10.0
        steady_lower = max(steady_lower, current_marathon_pace_sec - 10.0)
        steady_upper = current_marathon_pace_sec + 30.0
        bands["steady_lower"] = steady_lower
        bands["steady_upper"] = steady_upper
        bands["easy_lower"] = steady_upper
        bands["recovery_lower"] = steady_upper + 20.0

    return bands


def classify_pace_band(pace_sec: Optional[float], bands: Dict[str, Optional[float]]) -> str:
    if pace_sec is None:
        return "unknown"
    if bands.get("very_fast_upper") is not None and pace_sec < bands["very_fast_upper"]:
        return "very_fast"
    if bands.get("very_fast_upper") is not None and bands.get("vo2_upper") is not None and bands["very_fast_upper"] <= pace_sec <= bands["vo2_upper"]:
        return "vo2"
    if bands.get("threshold_lower") is not None and bands.get("threshold_upper") is not None and bands["threshold_lower"] <= pace_sec <= bands["threshold_upper"]:
        return "threshold"
    if bands.get("threshold_upper") is not None and bands.get("steady_upper") is not None and bands["threshold_upper"] < pace_sec <= bands["steady_upper"]:
        return "steady"
    if bands.get("recovery_lower") is not None and pace_sec >= bands["recovery_lower"]:
        return "recovery"
    if bands.get("steady_upper") is not None and pace_sec > bands["steady_upper"]:
        return "easy"
    if bands.get("vo2_upper") is not None and pace_sec <= bands["vo2_upper"]:
        return "vo2"
    if bands.get("threshold_upper") is not None and pace_sec <= bands["threshold_upper"]:
        return "threshold"
    if bands.get("steady_upper") is not None and pace_sec <= bands["steady_upper"]:
        return "steady"
    return "easy"


def derive_helper_fields(row: pd.Series, user_profile: Dict[str, Any]) -> Dict[str, Any]:
    distance_km = row.get("distance_km")
    duration_min = row.get("duration_min")
    title = row.get("title", row.get("activity_name", ""))
    description = row.get("description", "")
    text = clean_text(title, description)
    pace = pace_sec_per_km(distance_km, duration_min)
    pace_bands = build_pace_bands(user_profile)
    current_5k_pace_sec = pace_bands.get("current_5k_pace_sec")
    pace_ratio_to_5k = pace / current_5k_pace_sec if pace is not None and current_5k_pace_sec else None
    rep_pattern = re.search(r"(\d+)\s*x\s*(200|300|400|600|800|1000|1200|1600|1k|2k|3k|5k)", text)
    rep_distance_m = None
    if rep_pattern:
        rep_raw = rep_pattern.group(2)
        rep_distance_m = 1000 if rep_raw == "1k" else 2000 if rep_raw == "2k" else 3000 if rep_raw == "3k" else 5000 if rep_raw == "5k" else int(rep_raw)
    return {
        "text": text,
        "pace_sec_per_km": pace,
        "pace_ratio_to_5k": pace_ratio_to_5k,
        "pace_band": classify_pace_band(pace, pace_bands),
        "has_tempo_keyword": any(k in text for k in ["tempo", "threshold", "cruise"]),
        "has_progressive_keyword": any(k in text for k in ["progressive", "prog", "steady to hard", "finish hard"]),
        "has_shakeout_keyword": any(k in text for k in ["shakeout", "shake out"]),
        "has_race_keyword": any(k in text for k in ["race", "parkrun", "park run", "xc", "cross country", "1500", "3000", "5k", "10k", "half marathon", "marathon"]),
        "has_hills_keyword": "hill" in text or "hills" in text,
        "has_stride_keyword": "stride" in text or "strides" in text,
        "has_reps_pattern": rep_pattern is not None,
        "rep_distance_m": rep_distance_m,
        "is_short_run": distance_km is not None and not pd.isna(distance_km) and float(distance_km) < 5,
        "is_medium_run": distance_km is not None and not pd.isna(distance_km) and 5 <= float(distance_km) < 12,
        "is_long_run_candidate": distance_km is not None and not pd.isna(distance_km) and float(distance_km) >= 12,
    }


def classify_workout_type(row: pd.Series, user_profile: Dict[str, Any]) -> Dict[str, Any]:
    helpers = derive_helper_fields(row, user_profile)
    workout_type = "easy"
    sub_type = "easy aerobic"
    notes = []

    if helpers["has_race_keyword"] and helpers["pace_band"] in {"very_fast", "vo2", "threshold"}:
        workout_type = "race"
        sub_type = "race effort"
        notes.append("Race keyword with hard pace")
    elif helpers["has_reps_pattern"]:
        if helpers["rep_distance_m"] is not None and helpers["rep_distance_m"] >= 1000:
            workout_type = "threshold"
            sub_type = "threshold intervals"
            notes.append("Longer reps pattern")
        else:
            workout_type = "vo2"
            sub_type = "vo2 reps"
            notes.append("Shorter reps pattern")
    elif helpers["pace_band"] == "very_fast":
        if helpers["is_short_run"]:
            workout_type = "race"
            sub_type = "short race effort"
            notes.append("Very fast over short distance")
        else:
            workout_type = "vo2"
            sub_type = "very fast aerobic power"
            notes.append("Very fast pace")
    elif helpers["pace_band"] == "vo2":
        workout_type = "vo2"
        sub_type = "vo2 effort"
        notes.append("VO2 pace band")
    elif helpers["pace_band"] == "threshold":
        workout_type = "threshold"
        if helpers["has_progressive_keyword"]:
            sub_type = "progressive threshold"
            notes.append("Progressive threshold clue")
        elif helpers["has_tempo_keyword"]:
            sub_type = "tempo threshold"
            notes.append("Tempo / threshold clue")
        else:
            sub_type = "threshold effort"
            notes.append("Threshold pace band")
    elif helpers["pace_band"] == "steady":
        if helpers["is_long_run_candidate"]:
            workout_type = "long run"
            sub_type = "steady long run"
            notes.append("Longer run at steady pace")
        elif helpers["has_progressive_keyword"] and helpers["is_medium_run"]:
            workout_type = "threshold"
            sub_type = "progressive steady to threshold"
            notes.append("Progressive medium run")
        else:
            workout_type = "easy"
            sub_type = "steady aerobic"
            notes.append("Steady aerobic support")
    elif helpers["pace_band"] in {"easy", "recovery"}:
        if helpers["is_long_run_candidate"]:
            workout_type = "long run"
            sub_type = "easy long run"
            notes.append("Longer run at easy pace")
        else:
            workout_type = "easy"
            sub_type = "easy aerobic"
            notes.append("Easy or recovery pace")

    if helpers["has_tempo_keyword"] and workout_type in {"easy", "vo2"}:
        workout_type = "threshold"
        sub_type = "tempo threshold"
        notes.append("Tempo keyword override")
    if helpers["has_hills_keyword"] and workout_type in {"easy", "threshold"}:
        workout_type = "vo2"
        sub_type = "hill reps"
        notes.append("Hill session override")
    if helpers["has_shakeout_keyword"]:
        workout_type = "easy"
        sub_type = "shakeout"
        notes.append("Shakeout override")
    if helpers["has_stride_keyword"] and workout_type == "easy":
        sub_type = "easy with strides"
        notes.append("Strides inside easy bucket")

    return {
        "workout_type": workout_type,
        "sub_type": sub_type,
        "pace_band": helpers["pace_band"],
        "pace_sec_per_km": helpers["pace_sec_per_km"],
        "pace_ratio_to_5k": helpers["pace_ratio_to_5k"],
        "classification_notes": " | ".join(notes),
    }


def _is_missing_workout_type(value: Any) -> bool:
    """A workout_type value is treated as missing if it is null, blank, or
    not one of the recognised RunLab labels."""
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except (TypeError, ValueError):
        pass
    text = str(value).strip().lower()
    if text in {"", "nan", "none", "unknown", "n/a"}:
        return True
    return text not in VALID_WORKOUT_TYPES


def fill_missing_workout_types(df: pd.DataFrame, user_profile: Dict[str, Any]) -> pd.DataFrame:
    """
    Fill in workout_type only for rows where it is missing or unknown.
    Existing valid workout_type values are preserved exactly.

    Guarantees:
    - Returns a DataFrame with exactly one column named 'workout_type'
    - Existing valid labels are not overwritten
    - Adds 'sub_type', 'pace_band' helper columns where they were derived
    """
    output = df.copy()

    if "title" not in output.columns and "activity_name" in output.columns:
        output["title"] = output["activity_name"]
    if "title" not in output.columns:
        output["title"] = ""
    if "description" not in output.columns:
        output["description"] = ""

    # Ensure a single workout_type column exists. If there are duplicate
    # workout_type columns (rare but possible from joins), collapse to the
    # first one.
    if "workout_type" not in output.columns:
        output["workout_type"] = pd.NA
    else:
        wt_locs = [i for i, col in enumerate(output.columns) if col == "workout_type"]
        if len(wt_locs) > 1:
            primary = output.iloc[:, wt_locs[0]]
            output = output.drop(columns=["workout_type"])
            output["workout_type"] = primary

    # Identify rows needing classification
    needs_fill_mask = output["workout_type"].apply(_is_missing_workout_type)

    if not needs_fill_mask.any():
        return output

    # Classify only the rows that need it
    rows_to_classify = output.loc[needs_fill_mask]
    classified_records = [
        classify_workout_type(row, user_profile) for _, row in rows_to_classify.iterrows()
    ]

    # Write back only into the missing rows, never overwriting valid values
    for idx, record in zip(rows_to_classify.index, classified_records):
        output.at[idx, "workout_type"] = record["workout_type"]

        # Helper columns: only write where they don't already exist for that row
        for helper_col in ("sub_type", "pace_band"):
            if helper_col not in output.columns:
                output[helper_col] = pd.NA
            if pd.isna(output.at[idx, helper_col]):
                output.at[idx, helper_col] = record.get(helper_col)

    return output


def classify_dataframe(df: pd.DataFrame, user_profile: Dict[str, Any]) -> pd.DataFrame:
    """
    Backward-compatible classifier: classifies every row regardless of
    existing workout_type. Prefer fill_missing_workout_types for the app
    path so user-provided labels are respected.

    Returns a DataFrame with exactly one 'workout_type' column.
    """
    output = df.copy()
    if "title" not in output.columns and "activity_name" in output.columns:
        output["title"] = output["activity_name"]
    if "title" not in output.columns:
        output["title"] = ""
    if "description" not in output.columns:
        output["description"] = ""

    classified_records = [classify_workout_type(row, user_profile) for _, row in output.iterrows()]
    classified_df = pd.DataFrame(classified_records, index=output.index)

    # Drop any pre-existing workout_type / sub_type / helper columns to avoid
    # duplicate-column collisions when concat'ing.
    columns_to_replace = [
        col for col in ("workout_type", "sub_type", "pace_band", "pace_sec_per_km",
                        "pace_ratio_to_5k", "classification_notes")
        if col in output.columns
    ]
    if columns_to_replace:
        output = output.drop(columns=columns_to_replace)

    result = pd.concat([output, classified_df], axis=1)
    result["primary_type"] = result["workout_type"]
    result["secondary_type"] = result["sub_type"]
    return result