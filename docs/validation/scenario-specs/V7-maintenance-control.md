# V7 — Maintenance Control (Optional)

## Purpose

**Negative / control scenario.** Validate that a broadly healthy, balanced runner receives **maintenance** (no major limiter) rather than a forced correction.

**Not required for the 6/6 beta gate.** Useful for preventing over-prescription.

## Data file

| Field | Value |
|-------|-------|
| **Path** | **TBD** — e.g. `data/maintenance_control.csv` |
| **App label** | Not registered |
| **Status** | **NOT CREATED** |

## Training pattern (design specification)

| Attribute | Target |
|-----------|--------|
| Run days/week | 5–6 |
| Weekly km | 60–70 |
| Mix | easy majority, 1 threshold/week, 1 long run/week, occasional VO2 |
| Trends | Slight rising or flat volume; not declining |
| `volume_pattern` | not `plateau` with all levers static (or progression score < 55) |

Could adapt from a curated subset of well-formed data — `data/optimal_training.csv` uses a **non-canonical schema** and cannot be loaded without transformation.

## Expected primary limiter

| Field | Expected |
|-------|----------|
| `primary_key` | `maintenance` |
| `limiter` | No major limiter |
| `headline` | Your current rhythm is healthy, so progress carefully |

## Expected metrics

| Metric | Expected range |
|--------|----------------|
| `recent_avg_weekly_km` | 58–72 |
| `consistency_label` | `moderate` or `high` |
| `long_runs_last_28` | ≥ 3 |
| `quality_runs_last_28` | ≥ 2 |
| `volume_trend` | `flat` or `rising` |

## Expected supporting signals

| Signal title | Priority |
|--------------|----------|
| Training balance broadly healthy | low |
| Progression signals acceptable | low |
| Solid or moderate volume | low/medium |

No **high** priority problem signals expected.

## Expected prescription theme

- Maintain current structure
- Small progression only if feeling good
- Keep hard/easy separation
- Avoid unnecessary intensity

## Pass/fail criteria

| Result | Condition |
|--------|-----------|
| **PASS** | `primary_key == "maintenance"` |
| **FAIL** | Any corrective limiter unless founder documents why over-prescription is intended |

## Use in validation

- Run after V1–V6 pass
- Guards against engine that always finds something wrong
- Optional for beta gate

## Current validation status

**NOT IMPLEMENTED**
