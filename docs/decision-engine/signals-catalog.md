# Signals Catalog

Signals are **evidence statements** derived from metrics. They do **not** select the primary limiter — that happens in `determine_focus()`.

**Module:** `src/signals.py`  
**Entry point:** `derive_signals(metrics)` → sorted list (high priority first)

Each signal is a dict:

```python
{
    "title": str,
    "detail": str,
    "priority": "high" | "medium" | "low",
    "rule_id": str,
}
```

## Rule groups

### 1. Consistency (`rule_consistency`)

| Condition | Title | Priority |
|-----------|-------|----------|
| `consistency_label` in `very low`, `low` | Low consistency | high |
| `consistency_label` == `moderate` | Moderate consistency | medium |
| else | Strong consistency | low |

### 2. Volume (`rule_volume`)

Always emits at least one volume level signal:

| Condition | Title | Priority |
|-----------|-------|----------|
| `recent_avg_weekly_km` < 50 | Low volume | high |
| 50 ≤ km < 70 | Moderate volume | medium |
| km ≥ 70 | Solid volume base | low |

Plus volume trend signal:

| `volume_trend` | Title | Priority |
|----------------|-------|----------|
| `flat` | Volume plateau | medium |
| `declining` | Declining volume | high |
| else | Volume progressing | low |

Plus pattern signals (when matched):

| `volume_pattern` | Title | Priority |
|------------------|-------|----------|
| `peaked_then_dipped` | Recent dip after peak volume | medium |
| `volatile` | Volatile weekly volume | medium |

### 3. Threshold (`rule_threshold`)

| Condition | Title | Priority |
|-----------|-------|----------|
| `threshold_sessions_last_28` == 0 | No threshold work detected | high |
| `threshold_sessions_per_week` < 1.0 | Limited threshold stimulus | medium |
| else | Threshold support in place | low |

### 4. Long run (`rule_long_run`)

| Condition | Title | Priority |
|-----------|-------|----------|
| `long_runs_last_28` == 0 | No long run stimulus | high |
| `long_runs_last_28` < 3 | Minimal long run stimulus | medium |
| else | Long run support in place | low |

**Affected by `long` vs `long run` label bug.**

### 5. Balance (`rule_balance`)

May emit multiple signals:

| Condition | Title | Priority |
|-----------|-------|----------|
| `quality_run_pct` > 0.40 AND `easy_run_pct` < 0.70 | Intensity imbalance | high |
| `quality_run_pct` < 0.10 | Low quality density | medium |
| `vo2_per_week` ≥ 1.0 AND `threshold_per_week` < 0.75 | VO2-heavy relative to threshold | medium |
| none of above | Training balance broadly healthy | low |

### 6. Progression (`rule_progression`)

| Condition | Title | Priority |
|-----------|-------|----------|
| Strong structure AND `progression_confidence` == `low` | Well-structured but static | medium |
| `progression_flat_count` ≥ 2 | Limited progression across key levers | medium |
| else | Progression signals acceptable | low |

**Strong structure** requires:

- `consistency_label == "high"` (≥6 run days/week)
- `recent_avg_weekly_km` ≥ 50
- `threshold_sessions_per_week` ≥ 1.0
- `long_runs_last_28` ≥ 3

## Signal → domain mapping

Used when attaching supporting signals to focus (`SIGNAL_TO_DOMAIN` in `focus.py`):

| `rule_id` | Domain |
|-----------|--------|
| `consistency` | consistency |
| `volume`, `volume_trend` | volume |
| `volume_pattern` | load_stability |
| `long_run` | long_run |
| `threshold` | threshold |
| `balance` | aerobic_support |
| `progression` | progression |

## Top signals in report

`report_engine.build_top_signals()` selects up to 3 signals with category diversity for the product report. Not all high-priority signals appear in the headline section.

## Signals vs primary limiter

| Concept | Role |
|---------|------|
| **Signal** | Evidence; many per report |
| **Primary limiter** | Single decision output |

Example: a runner may show "Low volume" (high) and "No threshold work" (high) but still receive `consistency` as primary if run days/week < 4.

## Validation usage

Scenario specs should list **expected high/medium signals**, not only the limiter. See `docs/validation/scenario-specs/`.

When `long`/`interval` labels are unnormalised, expect false **No long run stimulus** signals on scenarios that include long runs labelled `long`.
