# Metrics Reference

Metrics are computed in `src/metrics.py` from the cleaned activity DataFrame and weekly summary.

**Analysis window:** most limiter-relevant counts use the **last 28 days** ending on the latest activity date.

**Weekly trends:** recent 4 weeks vs prior 4 weeks (when ≥ 8 weeks of data exist).

## Weekly summary (`weekly_summary`)

Per `week_start` (Monday):

| Column | Aggregation |
|--------|-------------|
| `total_distance_km` | Sum of `distance_km` |
| `total_duration_min` | Sum of `duration_min` |
| `run_count` | Count of activities |
| `avg_hr` | Mean `avg_hr` |
| `threshold_sessions` | Count where `workout_type == "threshold"` |
| `vo2_sessions` | Count where `workout_type == "vo2"` |
| `race_sessions` | Count where `workout_type == "race"` |
| `long_runs` | Count where `workout_type == "long run"` |
| `easy_runs` | Count where `workout_type == "easy"` |
| `interval_sessions` | `vo2_sessions + race_sessions` |

## Overall metrics (`overall_metrics`)

### Volume and frequency

| Key | Description |
|-----|-------------|
| `days_with_run_last_28` | Unique calendar days with ≥1 run in last 28 days |
| `consistency_label` | Derived from run days/week — see below |
| `recent_avg_weekly_km` | Mean weekly km, last 4 weeks |
| `prior_avg_weekly_km` | Mean weekly km, weeks 5–8 back |
| `volume_change_pct` | % change recent vs prior weekly km |
| `volume_trend` | `rising` / `flat` / `declining` (±8% threshold) |
| `volume_pattern` | `plateau`, `ramping_up`, `declining`, `volatile`, `peaked_then_dipped`, `insufficient_data` |
| `volume_pattern_detail` | Human-readable pattern explanation |
| `total_distance_last_28` | Total km in last 28 days |
| `total_runs_last_28` | Activity count in last 28 days |
| `avg_runs_per_week` | Mean runs/week over last 4 weeks |
| `avg_distance_per_run` | Mean distance per run (all data) |
| `longest_run_km` | Max single-run distance (all data) |
| `long_run_ratio_to_weekly_volume` | Longest run / recent weekly km |

### Consistency label (`classify_consistency`)

Based on `days_with_run_last_28 / 4` (approx run days per week):

| Run days/week | Label |
|---------------|-------|
| ≥ 6 | `high` |
| ≥ 5 | `moderate` |
| ≥ 3 | `low` |
| < 3 | `very low` |

**Naming note:** `high` means physically high frequency, not "high priority issue."

### Session type counts (last 28 days)

| Key | Counts rows where `workout_type` equals |
|-----|----------------------------------------|
| `threshold_sessions_last_28` | `threshold` |
| `vo2_sessions_last_28` | `vo2` |
| `race_sessions_last_28` | `race` |
| `long_runs_last_28` | `long run` only |
| `easy_runs_last_28` | `easy` |
| `interval_sessions_last_28` | vo2 + race |
| `quality_runs_last_28` | threshold + vo2 + race |

**Critical:** `long` and `interval` labels are **not counted**. See [canonical-schema.md](canonical-schema.md).

### Per-week rates (last 28 days ÷ 4)

| Key | Description |
|-----|-------------|
| `threshold_sessions_per_week` | Threshold sessions / 4 |
| `vo2_sessions_per_week` | VO2 sessions / 4 |
| `long_runs_per_week` | Long runs / 4 |

### Balance metrics (last 28 days)

| Key | Formula |
|-----|---------|
| `easy_run_pct` | easy runs / total runs |
| `quality_run_pct` | quality runs / total runs |

Used by aerobic support hard gate (`quality_pct >= 0.35` and `easy_pct < 0.70`).

### Component trends

Compare recent 4-week session averages vs prior 4 weeks:

| Key | Values |
|-----|--------|
| `threshold_trend` | `rising` / `flat` / `declining` |
| `vo2_trend` | same |
| `long_run_trend` | same |
| `interval_trend` | mirrors vo2_trend |

Threshold: ±25% relative change for `rising` / `declining`.

### Progression helpers

| Key | Description |
|-----|-------------|
| `weeks_of_data` | Distinct week_start count |
| `progression_confidence` | `high` (≥8 weeks), `medium` (≥6), `low` |
| `progression_flat_count` | Number of flat trends among volume, threshold, vo2, long run |
| `progression_rising_count` | Number of rising trends among same |

## Metrics → limiter relationship (summary)

| Metric pattern | Often drives |
|----------------|--------------|
| Run days/week < 4 | `consistency` hard gate |
| Weekly km < 50 | `volume` hard gate |
| Quality % high, easy % low, km < 70 | `aerobic_support` hard gate |
| Volume declining, km ≥ 50 | `load_stability` hard gate |
| `long_runs_last_28 == 0` | `long_run` hard gate |
| No threshold, quality ≤ 2 | `threshold` hard gate |
| No quality, km ≥ 50 | `quality` hard gate |
| Plateau + adequate structure | `progression` via scores |

Full decision logic: [focus-rules.md](focus-rules.md).

## Tolerance guidance for validation tests

When asserting metrics in automated tests, use approximate tolerances:

| Metric | Tolerance |
|--------|-----------|
| `recent_avg_weekly_km` | ±3 km |
| `days_with_run_last_28` | ±1 day |
| Session counts (28d) | exact match expected after label normalisation |

Record actual values from engine runs in scenario specs when tightening tests.
