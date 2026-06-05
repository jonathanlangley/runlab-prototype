# V4 — High Volume, No Quality

## Purpose

Validate that a runner with **strong volume and consistency** but **no threshold/VO2 work** receives the **quality** limiter.

## Data file

| Field | Value |
|-------|-------|
| **Path** | `data/high_volume_no_quality.csv` |
| **App label** | High volume, low quality |
| **Rows** | 56 |
| **Date range** | ~2026-01-05 to 2026-03-01 |

## Training pattern (design intent)

- Very high consistency (~7 runs/week)
- ~90–95 km/week
- Only `easy` and `long` sessions — no structured quality
- Aerobic base is strong; performance stimulus is missing

## Workout types in file

`easy`, `long` only — `long` requires alias normalisation.

## Expected primary limiter

| Field | Expected |
|-------|----------|
| `primary_key` | `quality` |
| `limiter` | Quality stimulus |
| `headline` | Your week needs one clearer quality stimulus |

## Expected metrics (after alias normalisation)

| Metric | Expected range | Observed (broken) |
|--------|----------------|-------------------|
| `days_with_run_last_28` | 26–28 | 28 |
| `consistency_label` | `high` | high |
| `recent_avg_weekly_km` | 88–98 | 93.8 |
| `quality_runs_last_28` | 0 | 0 |
| `long_runs_last_28` | 6–10 | **0** (bug) |
| `easy_run_pct` | > 0.80 | 0.857 |
| `volume_trend` | `flat` | flat |

## Quality hard gate

Fires when:

- `quality_runs_last_28 == 0`
- `recent_avg_weekly_km >= 50`

**Blocked today** by earlier gate: `long_runs_last_28 == 0` → `long_run`.

After alias fix, long runs are present → gate 5 passes → gate 7 should fire → `quality`.

## Expected supporting signals

| Signal title | Priority | Required |
|--------------|----------|----------|
| Low quality density | medium | **Yes** |
| Solid volume base | low | **Yes** |
| Strong consistency | low | Likely |
| Volume plateau | medium | Possible |

## Expected prescription theme

- Add **one structured faster session** (400s or 800s)
- Controlled effort — not all-out
- Maintain volume; rest of week easy

## Explanation logic

The aerobic base is in place. The missing element is a clear quality stimulus to drive performance adaptation.

## Pass/fail criteria

| Result | Condition |
|--------|-----------|
| **PASS** | `primary_key == "quality"` + Low quality density signal |
| **FAIL** | `long_run` (current) or `volume` |

## Current validation status

**FAIL** — returns `long_run` due to label bug.

## Overlap note

Similar structure to `consistent_plateau.csv` (also easy + long). V4 differs by **higher volume** (~94 vs ~74 km). Both should resolve to `quality` after fix. Consider keeping only one in long-term suite.
