# Classifier Expectations

Documents expected behaviour of `src/runlab_classifier_v1.py` for the **upload path** when `workout_type` is missing or unknown.

**Not used for demo scenarios** — demo CSVs have pre-filled `workout_type` and bypass auto-classification in the demo flow.

## Purpose

Before beta users upload Strava exports without workout labels, verify that `fill_missing_workout_types()` produces sensible canonical types using:

- Pace vs runner profile (5K / HM / marathon times)
- Activity title and description keywords
- Distance and duration

## Canonical output vocabulary

Classifier must output only:

`easy` | `threshold` | `vo2` | `long run` | `race`

## Test fixtures

| File | Purpose |
|------|---------|
| `data/without_classification.csv` | Rows without `workout_type`; titles/descriptions carry intent |
| `data/with_classification.csv` | Reference labels for same rows (manual ground truth) |
| `data/runlab_classifier_test.csv` | Additional edge cases |

## `without_classification.csv` row expectations (draft)

Test with profile: `current_5k_time = "22:00"` (adjust when formalising tests).

| Date | Title / description hints | Expected type |
|------|---------------------------|---------------|
| 2026-04-01 | Easy run | `easy` |
| 2026-04-02 | Tempo session, WU 4M tempo CD | `threshold` |
| 2026-04-03 | Recovery run | `easy` |
| 2026-04-04 | Long run steady, 18 km | `long run` |
| 2026-04-05 | 10x400 track session | `vo2` |
| 2026-04-06 | Shakeout jog | `easy` |
| 2026-04-07 | Medium long run, 12 km | `long run` or `easy` (document acceptable range) |
| 2026-04-08 | Progressive run steady to hard | `threshold` or `vo2` |
| 2026-04-09 | Parkrun race effort | `race` |
| 2026-04-10 | Morning run (neutral) | `easy` (pace-dependent) |
| 2026-04-11 | 6x800 session | `vo2` |

**Note:** Ground truth for borderline rows should be confirmed by founder/coach review and locked in tests as acceptable alternatives where reasonable.

## Classifier rules (summary)

Classification uses `classify_workout_type()`:

1. Text keywords: race, tempo/threshold, hills, reps pattern, strides
2. Pace band vs profile-derived bands
3. Distance heuristics: short / medium / long run candidate
4. Default: `easy`

Preserves existing valid canonical labels — only fills missing/unknown.

## Unknown / missing detection

`_is_missing_workout_type()` treats as missing:

- null, blank, `nan`, `none`, `unknown`, `n/a`
- any value **not** in `VALID_WORKOUT_TYPES`

Therefore `long`, `interval`, `tempo` on upload are treated as **missing** and may be overwritten by classifier — different from demo path which keeps raw labels through `clean_data()`.

## Pipeline order issue (known)

App currently runs classification **before** `clean_data()` in `runlab_data.py`. Classifier expects `distance_km` and `duration_min` — non-RunLab CSV column names may fail.

**Planned fix:** classify after `clean_data()`. Document in [../changelog/rule-changes.md](../changelog/rule-changes.md) when fixed.

## Pass criteria (classifier track)

| Criterion | Target |
|-----------|--------|
| Row-level accuracy on `without_classification.csv` | ≥ 90% exact match to reference |
| Borderline rows | Documented acceptable alternatives |
| No valid user label overwritten | `easy`/`threshold`/etc. preserved |
| All outputs in canonical vocabulary | 100% |

Classifier pass is required for **upload beta**, not for **6/6 demo scenario gate**.

## Automated tests (planned)

```python
# tests/test_classifier.py — not implemented yet
def test_fill_missing_workout_types(without_classification_fixture, profile):
    ...
```
