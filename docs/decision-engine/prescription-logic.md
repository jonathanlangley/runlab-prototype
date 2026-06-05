# Prescription Logic

After the primary limiter is selected, RunLab builds:

1. **`next_week_plan`** — structured targets (run days, km range, quality count, long run)
2. **`prescription`** — four plain-language action lines for the report

**Module:** `src/focus.py` — `build_next_week_plan()`, `build_prescription()`

Prescriptions are **deterministic templates**, not AI-generated.

## Volume and run-day helpers

### `recommend_volume_target(current_km)`

| Current weekly km | Target range (approx) |
|-------------------|----------------------|
| < 30 | current+8 to current+15 (min 20) |
| 30–50 | current+8 to current+12 |
| 50–70 | current+5 to current+8 |
| ≥ 70 | current+3 to current+6 |

### `recommend_run_days_target(current_run_days/week)`

| Current | Target |
|---------|--------|
| < 4 | 5 |
| < 5.5 | 6 |
| else | round(current) |

## Next-week plan by primary limiter

| Primary | Run days | Volume | Quality sessions | Long run |
|---------|----------|--------|------------------|----------|
| `consistency` | Increased | Controlled / modest increase | 0 if <3 days/wk else 1 | As needed |
| `volume` | Increased | Increase via easy miles | 1 threshold | Weekly if low |
| `aerobic_support` | Maintained/increased | Increase easy volume | 1 (threshold preferred) | Weekly |
| `load_stability` | Stable | ±5% of current | Max 1–2 | Maintain |
| `long_run` | Maintained | Maintain | Minimal | **Weekly** |
| `threshold` | Maintained | Maintain | 1 threshold-focused | Maintain |
| `quality` | Maintained | Maintain | 1 VO2-style | Maintain |
| `progression` | Maintained | Small optional bump | 1 | Maintain |
| `maintenance` | Maintain | Maintain | Controlled | Maintain |

`easy_volume` flag: `increase` for consistency/volume/aerobic_support; else `maintain`.

`avoid` string warns against adding hard sessions or changing multiple levers.

## Prescription themes by limiter

### `consistency`

- Run more days, even if short
- Keep volume controlled
- All easy — no hard sessions
- Repeatability over impressiveness

### `volume`

- Add easy kilometres
- One controlled threshold session
- No second hard session

### `aerobic_support`

- Build easy volume
- One quality session only (threshold)
- No races or VO2 this week

### `load_stability`

- Hold volume steady
- Repeat last week's structure
- Max one quality session
- Don't change multiple levers

### `long_run`

- One 75–90 min comfortable long run
- Easy pace — not a progression run
- Minimise other quality

### `threshold`

- One controlled threshold session (e.g. 3×8 min, 4×6 min, 20 min continuous)
- Controlled effort
- Rest of week easy

### `quality`

- One structured faster session (e.g. 400s or 800s)
- Not all-out
- Rest of week easy

### `progression`

- Progress **one** lever only
- Do not combine volume and intensity increases
- Review response before next progression

### `maintenance`

- Maintain structure
- Small progression only if feeling good
- Separate hard and easy days clearly

## Full prescription text

Exact strings are in `build_prescription()` — `src/focus.py` lines 334–409. Update scenario specs if prescription copy changes.

## Validation

Scenario pass criteria include **prescription theme** match (not necessarily exact string match):

| Limiter | Theme keywords expected |
|---------|-------------------------|
| consistency | easy, repeatable, short runs |
| volume | easy running, threshold |
| aerobic_support | easy volume, one quality, no VO2/race |
| load_stability | stable, repeat structure |
| long_run | long run, comfortable, 75–90 |
| threshold | threshold, controlled |
| quality | faster session, structured |
| progression | one thing only |
| maintenance | maintain, careful |

## AI explanation relationship

`ai_explainer.py` paraphrases the limiter and prescription themes. If AI text diverges from prescription, the deterministic prescription in `focus.prescription` is the source of truth.
