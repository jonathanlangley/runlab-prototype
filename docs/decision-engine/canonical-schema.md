# Canonical Data Schema

RunLab expects activity data to conform to a **canonical schema** after `clean_data()` in `src/data_loader.py`. All metrics, signals, and focus rules operate on this shape.

## Required columns (after cleaning)

| Column | Type | Rule |
|--------|------|------|
| `date` | datetime | Activity start date |
| `distance_km` | float | Distance in kilometres; must be > 0 |
| `duration_min` | float | Duration in **minutes** (moving time preferred); must be > 0 |

## Optional columns

| Column | Type | Used for |
|--------|------|----------|
| `avg_hr` | float | Weekly average HR; supporting evidence |
| `activity_type` | string | Filter to running activities |
| `workout_type` | string | Session classification — **critical for limiter logic** |
| `activity_name` / `title` | string | Classifier keywords |
| `description` | string | Classifier keywords |

## Derived columns (added by cleaner)

| Column | Formula / rule |
|--------|----------------|
| `pace_min_per_km` | `duration_min / distance_km` |
| `week_start` | Monday of activity week |

## Activity type filter

After cleaning, only rows where `activity_type` is one of:

- `run`
- `running`
- `trail run`
- `treadmill run`

If `activity_type` is missing, it defaults to `run`.

**Note:** Strava labels such as `Virtual Run` or `Trail Run` are **not** currently mapped automatically. They will be dropped unless normalised by a future import adapter or manual preprocessing.

## Workout type — canonical vocabulary

The engine recognises exactly **five** workout types for metrics and classification:

| Canonical value | Meaning |
|-----------------|---------|
| `easy` | Easy aerobic running |
| `threshold` | Controlled threshold / tempo work |
| `vo2` | VO2 max intervals, reps, race-pace intervals |
| `long run` | Endurance long run (typically ≥ ~12 km or longest weekly session) |
| `race` | Race or race-effort session |

Counts in `metrics.py` use **exact string match** on these values:

```python
(s == "threshold").sum()
(s == "vo2").sum()
(s == "long run").sum()
```

If `workout_type` is missing, `clean_data()` defaults every row to `easy`.

## Known aliases (must be normalised)

Several demo CSV files and external exports use non-canonical labels. These **do not count correctly** in the engine today unless mapped.

| Alias (seen in data) | Should map to | Status |
|----------------------|---------------|--------|
| `long` | `long run` | **Not normalised in code yet** — known bug |
| `interval` | `vo2` | **Not normalised in code yet** — known bug |
| `intervals` | `vo2` | Documented; not implemented |
| `tempo` | `threshold` | Documented; not implemented |

**Validation impact:** demo files `sample_runs.csv`, `near_optimal_but_plateauing.csv`, `consistent_plateau.csv`, `high_volume_no_quality.csv`, and `too_much_intensity.csv` use `long` and/or `interval`. This causes `long_runs_last_28 = 0` and incorrect limiter selection.

**Planned fix:** add alias normalisation in `data_loader.py` during `clean_data()`. Demo CSV labels may also be updated separately.

## Classifier vocabulary

`src/runlab_classifier_v1.py` defines:

```python
VALID_WORKOUT_TYPES = {"easy", "threshold", "vo2", "long run", "race"}
```

The classifier fills **missing or unknown** `workout_type` values using pace bands and text keywords. It does **not** overwrite valid canonical labels.

Classifier-valid but non-canonical labels (e.g. `long`) are treated as **unknown** and may be reclassified on upload — but pre-labelled demo CSVs bypass the classifier in the demo path.

## Column aliases (input mapping)

`COLUMN_MAPPING` in `data_loader.py` maps common export headers:

| Input column | Canonical column |
|--------------|------------------|
| `activity_date`, `start_date` | `date` |
| `distance`, `distance_(km)` | `distance_km` |
| `duration`, `moving_time`, `elapsed_time` | `duration_min` |
| `average_heartrate`, `average_heart_rate` | `avg_hr` |
| `type` | `activity_type` |
| `session_type` | `workout_type` |
| `name` | `activity_name` |

**Unit warning:** `duration_min` must already be in minutes. Strava `Moving Time` as `HH:MM:SS` strings will **not** parse correctly without a source adapter.

## Quality session definition

For metrics:

```
quality_runs = threshold sessions + vo2 sessions + race sessions
quality_run_pct = quality_runs / total_runs  (last 28 days)
```

Sessions labelled `interval` instead of `vo2` are **not** counted as quality work.

## Minimum data for a report

- At least one running row with valid date, distance, duration
- Ideally **4+ weeks** of data for trend and confidence logic
- Ideally **28 days** with multiple sessions for limiter accuracy

Empty DataFrame after run filtering raises `EmptyDataError` in `report_engine.py`.

## Demo scenario files

| Validation ID | File | Registered in app |
|---------------|------|-------------------|
| V1 | `data/inconsistent_training.csv` | Yes |
| V2 | `data/sample_runs.csv` | Yes (as "Baseline runner") |
| V3 | `data/too_much_intensity.csv` | Yes |
| V4 | `data/high_volume_no_quality.csv` | Yes |
| V5 | `data/near_optimal_but_plateauing.csv` | Yes |
| V6 | `data/declining_load.csv` | **Not created yet** |
| V7 | TBD | No |

See [../validation/validation-pack.md](../validation/validation-pack.md).
