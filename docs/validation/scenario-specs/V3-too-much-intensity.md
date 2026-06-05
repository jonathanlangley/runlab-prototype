# V3 — Too Much Intensity

## Purpose

Validate that a runner with **adequate frequency** but **too much quality relative to easy running** and **moderate volume** receives the **aerobic_support** limiter.

## Data file

| Field | Value |
|-------|-------|
| **Path** | `data/too_much_intensity.csv` |
| **App label** | Too much intensity |
| **Rows** | 56 |
| **Date range** | ~2026-01-05 to 2026-03-01 |

## Training pattern (design intent)

- High consistency (~7 runs/week)
- ~55–65 km/week
- Roughly equal mix of threshold, VO2/interval, easy, long
- Quality density high; easy running insufficient to support hard work

## Workout types in file

`interval`, `threshold`, `easy`, `long` — requires alias normalisation.

## Expected primary limiter

| Field | Expected |
|-------|----------|
| `primary_key` | `aerobic_support` |
| `limiter` | Aerobic support |
| `headline` | Your hard sessions need more aerobic support |

## Expected metrics (after alias normalisation)

| Metric | Expected range | Observed (broken) |
|--------|----------------|-------------------|
| `days_with_run_last_28` | 26–28 | 28 |
| `consistency_label` | `high` | high |
| `recent_avg_weekly_km` | 55–65 | 59.0 |
| `quality_run_pct` | ≥ 0.35 | **0.286** (interval not counted) |
| `easy_run_pct` | < 0.70 | 0.286 |
| `threshold_sessions_last_28` | 6–10 | 8 |
| `vo2_sessions_last_28` | 6–10 | **0** (bug) |
| `long_runs_last_28` | 6–10 | **0** (bug) |

## Aerobic support hard gate

Requires **all**:

- `quality_run_pct >= 0.35`
- `easy_run_pct < 0.70`
- `recent_avg_weekly_km < 70`

With alias fix, quality% should exceed 0.35. If still below, may need scenario tuning or threshold adjustment (document in changelog).

## Expected supporting signals

| Signal title | Priority | Required |
|--------------|----------|----------|
| Intensity imbalance | high | **Yes** (after alias fix) |
| Moderate volume | medium | Likely |
| Strong consistency | low | Likely |

## Expected prescription theme

- Build volume with **mostly easy** running
- **One** quality session only (threshold preferred)
- **No** races or VO2 sessions this week
- Support hard work with aerobic base

## Explanation logic

Hard sessions are already present; the issue is insufficient easy volume underneath. Add easy miles, don't add intensity.

## Pass/fail criteria

| Result | Condition |
|--------|-----------|
| **PASS** | `primary_key == "aerobic_support"` + Intensity imbalance signal |
| **FAIL** | `long_run` (current bug) or `volume` / `quality` |
| **REVIEW** | If quality% still < 0.35 after alias fix — tune scenario or gate threshold |

## Current validation status

**FAIL** — engine returns `long_run` due to `long_runs_last_28 == 0` (label bug).

## Post-fix verification

1. Normalise `long` → `long run`, `interval` → `vo2`
2. Re-run; confirm `quality_run_pct >= 0.35`
3. Confirm aerobic_support gate fires before score-based selection
4. If gate still fails, check whether easy% threshold needs scenario adjustment
