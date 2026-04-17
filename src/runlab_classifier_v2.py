import re
from typing import Any, Dict, Optional

import pandas as pd


def parse_time_to_seconds(time_value: Any) -> Optional[int]:
    """Convert a time value into total seconds."""
    if time_value is None or pd.isna(time_value):
        return None
    if isinstance(time_value, (int, float)):
        return int(time_value)
    if isinstance(time_value, str):
        parts = time_value.strip().split(":")
        if not parts:
            return None
        try:
            if len(parts) == 2:
                minutes, seconds = parts
                return int(minutes) * 60 + int(seconds)
            if len(parts) == 3:
                hours, minutes, seconds = parts
                return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        except ValueError:
            return None
    return None


def seconds_to_pace_str(seconds_per_km: Optional[float]) -> Optional[str]:
    """Convert seconds per km into m:ss/km."""
    if seconds_per_km is None:
        return None
    total_seconds = int(round(seconds_per_km))
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}/km"


def clean_text(*values: Any) -> str:
    """Join free-text fields and normalize them for keyword matching."""
    text_parts = []
    for value in values:
        if value is not None and not pd.isna(value):
            text_parts.append(str(value).lower().strip())
    text = " ".join(text_parts)
    text = re.sub(r"\s+", " ", text)
    return text


def pace_sec_per_km(distance_km: Any, duration_min: Any) -> Optional[float]:
    """Convert distance + duration into seconds per km."""
    if distance_km is None or duration_min is None:
        return None
    if pd.isna(distance_km) or pd.isna(duration_min):
        return None
    if float(distance_km) <= 0:
        return None
    return float(duration_min) * 60.0 / float(distance_km)


def riegel_predict_time(base_time_sec: float, base_distance_km: float, target_distance_km: float, exponent: float = 1.06) -> float:
    """Simple Riegel prediction."""
    return float(base_time_sec) * (float(target_distance_km) / float(base_distance_km)) ** exponent


def build_pace_bands(user_profile: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """
    Build scalable pace bands.

    Design:
    - very_fast / VO2 anchored to current 5K pace
    - threshold anchored primarily to HM pace (explicit or estimated)
    - steady / easy anchored to marathon pace (explicit or estimated)
    """
    current_5k_time_sec = parse_time_to_seconds(user_profile.get("current_5k_time"))
    current_hm_time_sec = parse_time_to_seconds(user_profile.get("current_hm_time"))
    current_marathon_time_sec = parse_time_to_seconds(user_profile.get("current_marathon_time"))

    current_5k_pace_sec = None
    current_hm_pace_sec = None
    current_marathon_pace_sec = None

    if current_5k_time_sec:
        current_5k_pace_sec = current_5k_time_sec / 5.0

    if current_hm_time_sec:
        current_hm_pace_sec = current_hm_time_sec / 21.0975
    elif current_5k_time_sec:
        estimated_hm_time_sec = riegel_predict_time(current_5k_time_sec, 5.0, 21.0975)
        current_hm_pace_sec = estimated_hm_time_sec / 21.0975

    if current_marathon_time_sec:
        current_marathon_pace_sec = current_marathon_time_sec / 42.195
    elif current_hm_pace_sec is not None:
        # Pragmatic training anchor rather than a pure race equivalence.
        # This places marathon pace in a realistic training relationship to HM pace.
        current_marathon_pace_sec = current_hm_pace_sec + 15.0
    elif current_5k_time_sec:
        estimated_marathon_time_sec = riegel_predict_time(current_5k_time_sec, 5.0, 42.195)
        current_marathon_pace_sec = estimated_marathon_time_sec / 42.195

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

    if current_hm_pace_sec is not None:
        threshold_lower = current_hm_pace_sec - 8.0
        if bands["vo2_upper"] is not None:
            threshold_lower = max(threshold_lower, bands["vo2_upper"])
        bands["threshold_lower"] = threshold_lower
        bands["threshold_upper"] = current_hm_pace_sec + 7.0

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
    """Assign a pace band using the scalable pace zones."""
    if pace_sec is None:
        return "unknown"

    very_fast_upper = bands.get("very_fast_upper")
    vo2_upper = bands.get("vo2_upper")
    threshold_lower = bands.get("threshold_lower")
    threshold_upper = bands.get("threshold_upper")
    steady_upper = bands.get("steady_upper")
    recovery_lower = bands.get("recovery_lower")

    if very_fast_upper is not None and pace_sec < very_fast_upper:
        return "very_fast"
    if very_fast_upper is not None and vo2_upper is not None and very_fast_upper <= pace_sec <= vo2_upper:
        return "vo2"
    if threshold_lower is not None and threshold_upper is not None and threshold_lower <= pace_sec <= threshold_upper:
        return "threshold"
    if threshold_upper is not None and steady_upper is not None and threshold_upper < pace_sec <= steady_upper:
        return "steady"
    if recovery_lower is not None and pace_sec >= recovery_lower:
        return "recovery"
    if steady_upper is not None and pace_sec > steady_upper:
        return "easy"

    # Soft fallbacks when one or more anchors are missing
    if vo2_upper is not None and pace_sec <= vo2_upper:
        return "vo2"
    if threshold_upper is not None and pace_sec <= threshold_upper:
        return "threshold"
    if steady_upper is not None and pace_sec <= steady_upper:
        return "steady"
    return "easy"


def derive_helper_fields(row: pd.Series, user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create helper fields from raw input and user profile.

    Expected row fields:
    - date
    - distance_km
    - duration_min
    - title
    - optional description
    - optional avg_hr

    Expected user_profile:
    - current_5k_time (str like '17:40' or seconds)
    - optional current_hm_time
    - optional current_marathon_time
    """
    distance_km = row.get("distance_km")
    duration_min = row.get("duration_min")
    title = row.get("title", "")
    description = row.get("description", "")
    avg_hr = row.get("avg_hr")

    text = clean_text(title, description)
    pace = pace_sec_per_km(distance_km, duration_min)

    pace_bands = build_pace_bands(user_profile)
    current_5k_pace_sec = pace_bands.get("current_5k_pace_sec")

    pace_ratio_to_5k = None
    if pace is not None and current_5k_pace_sec:
        pace_ratio_to_5k = pace / current_5k_pace_sec

    has_tempo_keyword = any(k in text for k in ["tempo", "threshold", "cruise"])
    has_progressive_keyword = any(k in text for k in ["progressive", "prog", "steady to hard", "finish hard"])
    has_easy_keyword = any(k in text for k in ["easy", "recovery", "easy run", "easy mile"])
    has_shakeout_keyword = any(k in text for k in ["shakeout", "shake out"])
    has_race_keyword = any(k in text for k in ["race", "parkrun", "park run", "xc", "cross country", "1500", "3000", "5k"])
    has_hills_keyword = "hill" in text or "hills" in text
    has_stride_keyword = "stride" in text or "strides" in text
    has_warmup_keyword = any(k in text for k in ["wu", "warm up", "warmup"])
    has_cooldown_keyword = any(k in text for k in ["cd", "cool down", "cooldown"])

    rep_pattern = re.search(r"(\d+)\s*x\s*(200|300|400|600|800|1000|1200|1600|1k|2k|3k)", text)
    has_reps_pattern = rep_pattern is not None

    reps = None
    rep_distance_m = None
    if rep_pattern:
        reps = int(rep_pattern.group(1))
        rep_raw = rep_pattern.group(2)
        rep_distance_m = 1000 if rep_raw == "1k" else 2000 if rep_raw == "2k" else 3000 if rep_raw == "3k" else int(rep_raw)

    is_short_run = distance_km is not None and not pd.isna(distance_km) and float(distance_km) < 5
    is_medium_run = distance_km is not None and not pd.isna(distance_km) and 5 <= float(distance_km) < 12
    is_long_run_candidate = distance_km is not None and not pd.isna(distance_km) and float(distance_km) >= 12

    pace_band = classify_pace_band(pace, pace_bands)

    return {
        "text": text,
        "pace_sec_per_km": pace,
        "current_5k_time_sec": parse_time_to_seconds(user_profile.get("current_5k_time")),
        "current_hm_time_sec": parse_time_to_seconds(user_profile.get("current_hm_time")),
        "current_marathon_time_sec": parse_time_to_seconds(user_profile.get("current_marathon_time")),
        "current_5k_pace_sec": current_5k_pace_sec,
        "current_hm_pace_sec": pace_bands.get("current_hm_pace_sec"),
        "current_marathon_pace_sec": pace_bands.get("current_marathon_pace_sec"),
        "pace_ratio_to_5k": pace_ratio_to_5k,
        "pace_band": pace_band,
        "pace_bands": pace_bands,
        "avg_hr": avg_hr,
        "has_tempo_keyword": has_tempo_keyword,
        "has_progressive_keyword": has_progressive_keyword,
        "has_easy_keyword": has_easy_keyword,
        "has_shakeout_keyword": has_shakeout_keyword,
        "has_race_keyword": has_race_keyword,
        "has_hills_keyword": has_hills_keyword,
        "has_stride_keyword": has_stride_keyword,
        "has_warmup_keyword": has_warmup_keyword,
        "has_cooldown_keyword": has_cooldown_keyword,
        "has_reps_pattern": has_reps_pattern,
        "reps": reps,
        "rep_distance_m": rep_distance_m,
        "is_short_run": is_short_run,
        "is_medium_run": is_medium_run,
        "is_long_run_candidate": is_long_run_candidate,
    }


def classify_workout_type(row: pd.Series, user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decide the core workout classification from helper fields.

    Priority order:
    1. explicit structured reps
    2. pace-band-led classification
    3. distance / duration context
    4. title / description as supporting evidence
    """
    helpers = derive_helper_fields(row, user_profile)
    text = helpers["text"]

    workout_type = "easy"
    sub_type = None
    classification_notes = []

    if helpers["has_reps_pattern"]:
        workout_type = "intervals"

        if helpers["rep_distance_m"] is not None:
            if helpers["rep_distance_m"] <= 400:
                sub_type = "short reps"
            else:
                sub_type = "long reps"
        else:
            sub_type = "intervals"

        classification_notes.append("Structured reps pattern detected")

    elif helpers["pace_band"] == "very_fast":
        if helpers["is_short_run"]:
            workout_type = "race"
            sub_type = "race effort"
            classification_notes.append("Very fast pace over short distance suggests race effort")
        else:
            workout_type = "intervals"
            sub_type = "fast reps / hard effort"
            classification_notes.append("Very fast pace suggests interval-like or race effort")

    elif helpers["pace_band"] == "vo2":
        workout_type = "intervals"
        sub_type = "interval effort"
        classification_notes.append("Pace band suggests VO2 / interval stimulus")

    elif helpers["pace_band"] == "threshold":
        workout_type = "threshold"

        if helpers["has_progressive_keyword"]:
            sub_type = "progressive"
            classification_notes.append("Threshold pace with progressive clue")
        elif helpers["has_tempo_keyword"]:
            sub_type = "tempo"
            classification_notes.append("Threshold pace with tempo clue")
        else:
            sub_type = "threshold effort"
            classification_notes.append("Pace band suggests threshold-like continuous effort")

    elif helpers["pace_band"] == "steady":
        if helpers["is_long_run_candidate"]:
            workout_type = "long run"
            sub_type = "steady long run"
            classification_notes.append("Longer run at steady aerobic pace")
        else:
            workout_type = "steady"
            sub_type = "steady aerobic"
            classification_notes.append("Pace band suggests steady aerobic support")

    elif helpers["pace_band"] in {"easy", "recovery"}:
        if helpers["is_long_run_candidate"]:
            workout_type = "long run"
            sub_type = "easy long run" if helpers["pace_band"] == "easy" else "recovery long run"
            classification_notes.append("Longer run at easy or recovery pace")
        else:
            workout_type = "easy"
            sub_type = "recovery aerobic" if helpers["pace_band"] == "recovery" else "easy aerobic"
            classification_notes.append("Pace band suggests easy or recovery aerobic running")

    else:
        workout_type = "easy"
        sub_type = "easy aerobic"
        classification_notes.append("Fallback easy classification")

    if helpers["has_hills_keyword"] and workout_type in {"steady", "easy"}:
        workout_type = "intervals"
        sub_type = "hills"
        classification_notes.append("Hill session clue adjusted classification")

    if helpers["has_shakeout_keyword"]:
        workout_type = "easy"
        sub_type = "shakeout"
        classification_notes.append("Shakeout keyword adjusted classification")

    if helpers["has_race_keyword"] and workout_type in {"threshold", "intervals"}:
        if helpers["is_short_run"]:
            workout_type = "race"
            if "parkrun" in text or "park run" in text:
                sub_type = "parkrun"
            elif "xc" in text or "cross country" in text:
                sub_type = "XC race"
            elif "1500" in text:
                sub_type = "track 1500"
            elif "3000" in text or "3k" in text:
                sub_type = "track 3000"
            elif "5k" in text:
                sub_type = "road 5k"
            else:
                sub_type = "race"
            classification_notes.append("Race keyword adjusted classification")

    return {
        **helpers,
        "workout_type": workout_type,
        "sub_type": sub_type,
        "classification_notes": "; ".join(classification_notes),
    }


def assign_training_attributes(row: pd.Series, user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Map workout_type into the additional calculated fields."""
    classified = classify_workout_type(row, user_profile)
    workout_type = classified["workout_type"]
    sub_type = classified["sub_type"]
    text = classified["text"]

    energy_system_primary = "aerobic"
    stimulus_weight = 1
    session_purpose = "support"
    is_key_session = False
    fatigue_cost = 1

    if workout_type == "easy":
        energy_system_primary = "aerobic"
        stimulus_weight = 1
        is_key_session = False
        fatigue_cost = 1
        session_purpose = "recovery" if ("shakeout" in text or "recovery" in text or classified["pace_band"] == "recovery") else "support"

    elif workout_type == "steady":
        energy_system_primary = "aerobic"
        stimulus_weight = 2
        session_purpose = "support"
        is_key_session = False
        fatigue_cost = 2

    elif workout_type == "threshold":
        energy_system_primary = "threshold"
        stimulus_weight = 3
        session_purpose = "build"
        is_key_session = True
        fatigue_cost = 3

        if classified["is_short_run"] and not classified["has_tempo_keyword"] and not classified["has_progressive_keyword"]:
            stimulus_weight = 2
            is_key_session = False
            session_purpose = "support"
            fatigue_cost = 2

    elif workout_type == "intervals":
        energy_system_primary = "VO2"
        stimulus_weight = 3
        session_purpose = "build"
        is_key_session = True
        fatigue_cost = 3

        if sub_type == "short reps":
            stimulus_weight = 4
            fatigue_cost = 4
        elif sub_type == "fast reps / hard effort":
            stimulus_weight = 4
            fatigue_cost = 4

    elif workout_type == "long run":
        energy_system_primary = "aerobic"
        stimulus_weight = 2
        session_purpose = "build"
        is_key_session = True
        fatigue_cost = 3

    elif workout_type == "race":
        stimulus_weight = 4
        session_purpose = "race"
        is_key_session = True
        fatigue_cost = 5

        if sub_type in {"parkrun", "track 3000", "XC race", "road 5k", "race effort"}:
            energy_system_primary = "VO2"
            fatigue_cost = 4
        elif sub_type == "track 1500":
            energy_system_primary = "anaerobic"
        else:
            energy_system_primary = "VO2"
            fatigue_cost = 4

    return {
        **classified,
        "energy_system_primary": energy_system_primary,
        "stimulus_weight": stimulus_weight,
        "session_purpose": session_purpose,
        "is_key_session": is_key_session,
        "fatigue_cost": fatigue_cost,
    }


def assign_confidence(row: pd.Series, user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Assign confidence based on how many signals agree."""
    assigned = assign_training_attributes(row, user_profile)
    score = 0

    if assigned["has_reps_pattern"]:
        score += 3
    if assigned["has_tempo_keyword"] or assigned["has_progressive_keyword"]:
        score += 2
    if assigned["has_race_keyword"]:
        score += 3
    if assigned["has_easy_keyword"] or assigned["has_shakeout_keyword"]:
        score += 2
    if assigned["pace_band"] != "unknown":
        score += 2
    if assigned["sub_type"] is not None:
        score += 1

    vague_titles = {"run", "morning run", "evening run", "afternoon run"}
    if clean_text(row.get("title", "")) in vague_titles:
        score -= 2

    if score >= 5:
        confidence = "high"
    elif score >= 2:
        confidence = "medium"
    else:
        confidence = "low"

    return {**assigned, "confidence": confidence}


def classify_session(row: pd.Series, user_profile: Dict[str, Any]) -> pd.Series:
    """Wrapper function to classify a single pandas row."""
    result = assign_confidence(row, user_profile)
    pace_bands = result.get("pace_bands", {})

    return pd.Series({
        "workout_type": result["workout_type"],
        "sub_type": result["sub_type"],
        "energy_system_primary": result["energy_system_primary"],
        "stimulus_weight": result["stimulus_weight"],
        "session_purpose": result["session_purpose"],
        "is_key_session": result["is_key_session"],
        "fatigue_cost": result["fatigue_cost"],
        "confidence": result["confidence"],
        "classification_notes": result["classification_notes"],
        "pace_sec_per_km": result["pace_sec_per_km"],
        "pace_band": result["pace_band"],
        "pace_ratio_to_5k": result["pace_ratio_to_5k"],
        "very_fast_upper_pace": seconds_to_pace_str(pace_bands.get("very_fast_upper")),
        "vo2_range": (
            f"{seconds_to_pace_str(pace_bands.get('vo2_lower'))} to {seconds_to_pace_str(pace_bands.get('vo2_upper'))}"
            if pace_bands.get("vo2_lower") is not None and pace_bands.get("vo2_upper") is not None else None
        ),
        "threshold_range": (
            f"{seconds_to_pace_str(pace_bands.get('threshold_lower'))} to {seconds_to_pace_str(pace_bands.get('threshold_upper'))}"
            if pace_bands.get("threshold_lower") is not None and pace_bands.get("threshold_upper") is not None else None
        ),
        "steady_range": (
            f"{seconds_to_pace_str(pace_bands.get('steady_lower'))} to {seconds_to_pace_str(pace_bands.get('steady_upper'))}"
            if pace_bands.get("steady_lower") is not None and pace_bands.get("steady_upper") is not None else None
        ),
        "easy_lower_pace": seconds_to_pace_str(pace_bands.get("easy_lower")),
        "recovery_lower_pace": seconds_to_pace_str(pace_bands.get("recovery_lower")),
    })


def classify_dataframe(df: pd.DataFrame, user_profile: Dict[str, Any]) -> pd.DataFrame:
    """Classify all rows in a dataframe and append the output columns."""
    classified_cols = df.apply(lambda row: classify_session(row, user_profile), axis=1)
    return pd.concat([df.copy(), classified_cols], axis=1)


if __name__ == "__main__":
    sample_df = pd.DataFrame([
        {"date": "2026-04-15", "distance_km": 9.7, "duration_min": 40.73, "title": "WU 4M tempo CD"},
        {"date": "2026-04-14", "distance_km": 4.8, "duration_min": 19.77, "title": "Quick trot"},
        {"date": "2026-04-13", "distance_km": 4.6, "duration_min": 21.02, "title": "20 min shakeout with Ben"},
        {"date": "2026-04-11", "distance_km": 5.9, "duration_min": 21.42, "title": "Morning run"},
        {"date": "2026-04-08", "distance_km": 9.3, "duration_min": 46.9, "title": "WU 10x400 + 90 CD"},
    ])
    sample_profile = {
        "current_5k_time": "17:40",
        "current_hm_time": "1:19:00",
        "current_marathon_time": "2:49:00",
    }
    print(classify_dataframe(sample_df, sample_profile))
