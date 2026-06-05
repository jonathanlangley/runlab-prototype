# V6 — Declining Load

## Purpose

Validate that a runner with **adequate consistency and moderate-high volume** but a **declining volume trend** receives the **load_stability** limiter.

## Data file

| Field | Value |
|-------|-------|
| **Path** | `data/declining_load.csv` |
| **App label** | **Not registered in app yet** |
| **Status** | **FILE NOT CREATED** |

## Training pattern (design specification)

When creating this CSV, target:

| Attribute | Target |
|-----------|--------|
| Run days/week | ≥ 5 (must **not** trigger consistency gate) |
| Recent weekly km | 55–65 (must be **≥ 50**, ideally < 70) |
| Prior block km | 15–25% higher than recent block |
| `volume_trend` | `declining` (recent 4wk avg ≥8% below prior 4wk) |
| Quality mix | Moderate — avoid aerobic_support gate (keep quality% < 0.35 OR easy% ≥ 0.70) |
| Long runs | ≥ 1 per week labelled **`long run`** (canonical) |
| History | ≥ 8 weeks of data for trend reliability |

### Example structure (8 weeks)

- Weeks 1–4: ~65–70 km, stable 5–6 run days
- Weeks 5–8: ~52–58 km, same frequency, shorter runs
- Include threshold or quality occasionally so pattern is realistic

## Expected primary limiter

| Field | Expected |
|-------|----------|
| `primary_key` | `load_stability` |
| `limiter` | Training load stability |
| `headline` | Your training load needs to stabilise before progressing |

## Hard gate

```python
if volume_trend == "declining" and recent_avg_weekly_km >= 50:
    return "load_stability"
```

**Precedence:** fires after consistency, aerobic_support, and volume gates. V6 must have km ≥ 50 and run days ≥ 4/week.

## Expected metrics

| Metric | Expected range |
|--------|----------------|
| `days_with_run_last_28` | 20–28 |
| Run days/week | ≥ 5 |
| `recent_avg_weekly_km` | 52–65 |
| `prior_avg_weekly_km` | 62–75 |
| `volume_change_pct` | ≤ -8% |
| `volume_trend` | `declining` |
| `long_runs_last_28` | ≥ 3 |

## Expected supporting signals

| Signal title | Priority | Required |
|--------------|----------|----------|
| Declining volume | high | **Yes** |
| Strong or moderate consistency | low/medium | Likely |

## Expected prescription theme

- **Stabilise** volume (narrow km range ~±5%)
- Repeat similar weekly structure
- Max one quality session
- Avoid changing multiple levers

## Explanation logic

Recent load has dropped. Rebuild a predictable week before pushing fitness or intensity.

## Pass/fail criteria

| Result | Condition |
|--------|-----------|
| **PASS** | `primary_key == "load_stability"` + Declining volume signal |
| **FAIL** | `consistency` (run days too low) or `volume` (km < 50) or `long_run` (no long runs) |

## Current validation status

**NOT RUN** — scenario file does not exist.

## Implementation checklist

- [ ] Create `data/declining_load.csv` per spec above
- [ ] Use canonical workout types only
- [ ] Register in `src/runlab_config.py` (when code changes allowed)
- [ ] Add to automated test parametrisation
- [ ] Run manual validation and record in changelog
