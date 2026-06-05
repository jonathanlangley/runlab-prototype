# V1 — Inconsistent Training

## Purpose

Validate that **low training frequency** and irregular rhythm trigger the **consistency** limiter before volume or structure levers.

## Data file

| Field | Value |
|-------|-------|
| **Path** | `data/inconsistent_training.csv` |
| **App label** | Inconsistent training |
| **Rows** | 20 |
| **Date range** | ~2026-01-05 to 2026-02-27 |

## Training pattern (design intent)

- Sparse run days (~2.5 days/week in last 28 days)
- Low weekly volume (~17 km/week)
- Declining / volatile volume pattern
- Mix of easy, threshold, interval, long — but frequency is the dominant issue

## Workout types in file

Uses non-canonical labels: `long`, `interval` (see alias note below).

## Expected primary limiter

| Field | Expected |
|-------|----------|
| `primary_key` | `consistency` |
| `limiter` | Consistency |
| `headline` | Your training rhythm is not repeatable enough yet |

## Expected metrics (last 28 days, approximate)

| Metric | Expected range | Observed (engine run) |
|--------|----------------|----------------------|
| `days_with_run_last_28` | 9–11 | 10 |
| Run days/week | 2.3–2.8 | 2.5 |
| `consistency_label` | `very low` | very low |
| `recent_avg_weekly_km` | 15–20 | 17.2 |
| `volume_trend` | `declining` | declining |
| `volume_pattern` | `volatile` | volatile |

## Expected supporting signals

| Signal title | Priority | Required |
|--------------|----------|----------|
| Low consistency | high | **Yes** |
| Declining volume | high | **Yes** |
| Low volume | high | Likely (km < 50) |

## Expected prescription theme

- Increase run **days** (target ~5/week)
- Keep volume **controlled** (~25–32 km)
- **All easy** — no structured hard sessions
- Repeatability over volume

## Explanation logic

Training frequency is too low and irregular. The runner should establish a repeatable weekly rhythm before increasing load or intensity. Hard sessions are not the priority.

## Confidence

Expect **High confidence** — consistency gate fires early with clear separation.

## Pass/fail criteria

| Result | Condition |
|--------|-----------|
| **PASS** | `primary_key == "consistency"` + Low consistency signal present |
| **FAIL** | Any other primary limiter |

## Current validation status

**PASS** — only core scenario that passes with engine as shipped.

## Notes

- Label bug (`long`/`interval`) affects long-run and VO2 **counts** but does not change consistency gate (run days < 4/week).
- After alias normalisation, still expect `consistency` — verify no regression.
