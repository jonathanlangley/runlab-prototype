# Focus Rules

The primary limiter is selected in `src/focus.py` by `determine_focus()`, which calls:

1. `build_limiter_scores(metrics)` — domain scores 0–100
2. `choose_primary_limiter(metrics, scores)` — hard gates + ranking
3. `choose_secondary_limiter(primary, scores)` — optional secondary
4. Template copy from `FOCUS_RULES`
5. `build_next_week_plan()` and `build_prescription()`

**AI does not participate in this step.**

## Decision flow (hard gates first)

```
START
  │
  ├─ run_days_per_week < 4? ──────────────────────────► consistency
  │
  ├─ quality_pct ≥ 0.35 AND easy_pct < 0.70 AND km < 70? ► aerobic_support
  │
  ├─ weekly_km < 50? ─────────────────────────────────► volume
  │
  ├─ volume_trend == declining AND weekly_km ≥ 50? ─────► load_stability
  │
  ├─ long_runs_last_28 == 0? ───────────────────────────► long_run
  │
  ├─ quality_sessions == 0 AND weekly_km ≥ 50? ────────► quality
  │
  ├─ threshold_sessions == 0 AND quality_sessions ≤ 2? ─► threshold
  │
  └─ ELSE rank by build_limiter_scores
        highest score if ≥ 55 ──────────────────────────► that domain
        else ───────────────────────────────────────────► maintenance
```

## Hard gate reference

| Order | Condition | Result `primary_key` |
|-------|-----------|----------------------|
| 1 | `days_with_run_last_28 / 4 < 4` | `consistency` |
| 2 | `quality_run_pct ≥ 0.35` AND `easy_run_pct < 0.70` AND `recent_avg_weekly_km < 70` | `aerobic_support` |
| 3 | `recent_avg_weekly_km < 50` | `volume` |
| 4 | `volume_trend == "declining"` AND `recent_avg_weekly_km ≥ 50` | `load_stability` |
| 5 | `long_runs_last_28 == 0` | `long_run` |
| 6 | `quality_runs_last_28 == 0` AND `recent_avg_weekly_km ≥ 50` | `quality` |
| 7 | `threshold_sessions_last_28 == 0` AND `quality_runs_last_28 ≤ 2` | `threshold` |
| 8 | Score-based | See below |

Gate 6 (quality) runs before gate 7 (threshold) so high-volume runners with **no** quality sessions receive `quality`, not `threshold`.

### Known validation issue: Gate 5 (resolved)

Gate 5 runs **before** gates 6–7. If long runs exist but are labelled `long` instead of `long run`, the engine returns `long_run` incorrectly.

**Status:** resolved — alias normalisation in `data_loader.py` (2026-07-06).

## Score model (`build_limiter_scores`)

When no hard gate fires, domains receive scores. Simplified summary:

| Domain | High score triggers (indicative) |
|--------|----------------------------------|
| `consistency` | < 4 run days/week |
| `volume` | < 50 km/week |
| `aerobic_support` | High quality %, low easy %, moderate km |
| `load_stability` | Declining or volatile volume patterns |
| `long_run` | 0 long runs, or ≤ 2 in 28d |
| `threshold` | 0 threshold sessions |
| `quality` | 0 quality sessions with base present |
| `progression` | Plateau pattern, km ≥ 60, quality ≥ 3 |

Exact thresholds in `src/focus.py` lines 123–204.

**Progression score shortcut:**

```python
progression = 55 if (
    volume_pattern == "plateau"
    and weekly_km >= 60
    and quality_sessions >= 3
) else 20
```

## Ranking and minimum score

```python
ranked = sorted(scores, key=lambda: (-score, PRIMARY_ORDER index))
primary = ranked[0] if score >= 55 else "maintenance"
```

`PRIMARY_ORDER`:

```
consistency, aerobic_support, volume, load_stability, long_run,
threshold, quality, progression, maintenance
```

## Secondary limiter

`choose_secondary_limiter()` only considers domains allowed for the primary (see `allowed_by_primary` dict) with score ≥ 55. May return `None`.

## Focus output structure

Key fields in `focus` dict:

| Field | Description |
|-------|-------------|
| `primary_key` | Machine limiter id |
| `limiter` | User-facing label |
| `headline` | Report hero title |
| `detail` | Why this is the limiter |
| `prescription` | List of 4 action strings |
| `next_week_plan` | run_days, target_km_range, quality_sessions, long_run |
| `confidence_label` | High / Medium / Lower confidence |
| `decision_scores` | Full score dict (debug) |
| `secondary_focus` | Optional headline |

## Changing focus rules

Any change to gates, thresholds, or `PRIMARY_ORDER` requires:

1. Entry in [changelog/rule-changes.md](../changelog/rule-changes.md)
2. Re-run of all 6 core scenario validations
3. Update affected scenario specs

Do not engage beta testers until validation suite passes after rule changes.
