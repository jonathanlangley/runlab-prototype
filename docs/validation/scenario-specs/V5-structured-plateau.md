# V5 — Structured Plateau

## Purpose

Validate that a runner with **sound overall structure** but **flat progression across levers** receives the **progression** limiter.

## Data file

| Field | Value |
|-------|-------|
| **Path** | `data/near_optimal_but_plateauing.csv` |
| **App label** | Near-optimal but plateauing |
| **Rows** | 56 |
| **Date range** | ~2026-01-05 to 2026-03-01 |

## Training pattern (design intent)

- High consistency (~7 runs/week)
- ~70–75 km/week
- Balanced mix: easy, threshold, interval/VO2, long
- Volume and component trends flat — no clear progression signal

## Workout types in file

`easy`, `threshold`, `interval`, `long` — alias normalisation required.

## Expected primary limiter

| Field | Expected |
|-------|----------|
| `primary_key` | `progression` |
| `limiter` | Progression |
| `headline` | Your structure is sound, but progression is too static |

## Expected metrics (after alias normalisation)

| Metric | Expected range | Observed (broken) |
|--------|----------------|-------------------|
| `days_with_run_last_28` | 26–28 | 28 |
| `consistency_label` | `high` | high |
| `recent_avg_weekly_km` | 70–78 | 74.0 |
| `volume_trend` | `flat` | flat |
| `volume_pattern` | `plateau` | plateau |
| `threshold_sessions_last_28` | 3–5 | 4 |
| `vo2_sessions_last_28` | 3–5 | **0** (bug) |
| `long_runs_last_28` | 6–10 | **0** (bug) |
| `quality_runs_last_28` | 6–10 | 4 (undercount) |

## Progression selection path

After hard gates pass (km ≥ 50, long runs present, quality present, threshold present):

- `build_limiter_scores` → `progression` score = 55 when:
  - `volume_pattern == "plateau"`
  - `weekly_km >= 60`
  - `quality_sessions >= 3`
- Ranked score ≥ 55 → `progression`

## Expected supporting signals

| Signal title | Priority | Required |
|--------------|----------|----------|
| Volume plateau | medium | **Yes** |
| Limited progression across key levers | medium | **Yes** (if flat_count ≥ 2) |
| Strong consistency | low | Likely |

## Expected prescription theme

- Progress **one lever only** (volume OR long run OR quality)
- Do not combine volume and intensity increases
- Review response before next change

## Explanation logic

Training structure is broadly healthy but too static. The next step is a small controlled progression in one dimension.

## Pass/fail criteria

| Result | Condition |
|--------|-----------|
| **PASS** | `primary_key == "progression"` |
| **FAIL** | `long_run` (current) or `maintenance` if scores too low |

## Current validation status

**FAIL** — returns `long_run` due to label bug.

## Post-fix verification

Confirm `progression` score ≥ 55 and no earlier hard gate intercepts. If result is `maintenance`, review `progression_flat_count` and plateau detection.
