# V2 — Low Aerobic Volume

## Purpose

Validate that a runner with **moderate consistency** but **weekly km below 50** receives the **volume** (aerobic volume) limiter.

## Data file

| Field | Value |
|-------|-------|
| **Path** | `data/sample_runs.csv` |
| **App label** | Baseline runner (mixed stimulus) |
| **Rows** | 28 |
| **Date range** | ~2026-02-02 to 2026-03-22 |

**Note:** This file serves dual purpose today — UI demo and V2 validation. A dedicated `data/low_aerobic_volume.csv` may be created later for clearer isolation.

## Training pattern (design intent)

- ~4 run days/week (borderline consistency)
- ~40 km/week — below performance band
- Mixed easy, threshold, interval, long sessions
- Not a catastrophe pattern — volume is the clearest gap

## Workout types in file

`easy`, `threshold`, `long`, `interval` — **long/interval need alias normalisation**.

## Expected primary limiter

| Field | Expected |
|-------|----------|
| `primary_key` | `volume` |
| `limiter` | Aerobic volume |
| `headline` | Your training is limited by aerobic volume, not intensity |

## Expected metrics (approximate)

| Metric | Expected range | Observed (engine run) |
|--------|----------------|----------------------|
| `days_with_run_last_28` | 14–18 | 16 |
| Run days/week | 3.5–4.5 | 4.0 |
| `consistency_label` | `low` | low |
| `recent_avg_weekly_km` | 38–45 | 40.1 |
| `threshold_sessions_last_28` | 3–5 | 4 |
| `long_runs_last_28` | 3–5 (after alias fix) | **0** (bug: `long` not counted) |
| `volume_trend` | `flat` | flat |

## Expected supporting signals

| Signal title | Priority | Required |
|--------------|----------|----------|
| Low volume | high | **Yes** |
| Low consistency | high | Possible (4 days/week = low label) |
| No long run stimulus | high | **Only if alias bug present** — should clear after fix |

## Expected prescription theme

- Increase volume via **easy running** (target ~48–52 km)
- **One** controlled threshold session
- No second hard session
- All other runs easy

## Explanation logic

Weekly kilometres are below the band that supports stronger aerobic development. The next gain comes from easy volume, not more intensity.

## Confidence

Expect **High confidence** when volume gate fires (`km < 50`).

## Pass/fail criteria

| Result | Condition |
|--------|-----------|
| **PASS** | `primary_key == "volume"` + Low volume signal present |
| **FAIL** | `long_run` or other limiter driven by label bug |
| **WARN** | Primary correct but "No long run stimulus" still high after alias fix — investigate counts |

## Current validation status

**PASS** (primary limiter only) — `volume` selected correctly despite long-run count bug.

## Notes

- Borderline for consistency gate: 4.0 run days/week is **not** < 4, so volume gate applies.
- After alias fix, verify `long_runs_last_28 > 0` and limiter remains `volume`.
- Consider demoting this scenario to UI-only if a cleaner V2 CSV is added.
