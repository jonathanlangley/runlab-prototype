# Confidence Scoring

RunLab displays a **confidence label** on each report. This reflects how clearly the engine believes the primary limiter is separated from alternatives — **not** whether the limiter is objectively correct.

**Module:** `build_decision_confidence()` in `src/focus.py`

## Output labels

| Label | When | User-facing note |
|-------|------|------------------|
| **High confidence** | score ≥ 75 | "The main limiter is clear and supported by enough recent training data." |
| **Medium confidence** | score ≥ 55 | "This is the clearest next focus, but it should be reviewed after another short block." |
| **Lower confidence** | score < 55 | "The pattern is either broadly healthy or the data is limited…" |

## How the score is calculated

```python
data_score = 20 if weeks >= 6 else 12 if weeks >= 4 else 6
score = min(100, max(0,
    primary_score
    + data_score
    + max(0, separation // 2)
    - 20
))
```

Where:

- `primary_score` — domain score from `build_limiter_scores`
- `separation` — primary score minus secondary score
- `weeks` — `weeks_of_data` from metrics

## What confidence does NOT measure

| Confidence is NOT | Why it matters |
|-----------------|----------------|
| Ground truth accuracy | Wrong limiter can still show "High confidence" |
| Coach agreement | No external validation built in |
| Data label quality | Mislabelled `long`/`interval` can produce confident wrong limiters |
| Runner goal fit | Same rules for all personas |

**Validation implication:** treat confidence as an internal clarity metric. Beta feedback must explicitly ask: *"Is the limiter correct?"* independent of confidence label.

## Factors that inflate confidence

- Long dataset (≥6 weeks)
- Large gap between primary and secondary domain scores
- High primary domain score (≥ 75)

## Factors that reduce confidence

- Short history (< 4 weeks)
- Multiple domains scoring similarly
- `maintenance` primary (often lower separation)

## Progression confidence (separate metric)

`metrics["progression_confidence"]` in `metrics.py` is used only by `rule_progression` in signals — not for the report confidence label.

| Weeks of data | `progression_confidence` |
|---------------|--------------------------|
| ≥ 8 | high |
| ≥ 6 | medium |
| < 6 | low |

## Display in UI

Rendered in `src/ui_report_sections.py` from `focus.confidence_label` and `focus.confidence_note` when present.

## Future improvements (not implemented)

- Lower confidence when workout types are inferred vs labelled
- Lower confidence when `weeks_of_data` < 4
- Explicit "limited data" flag on upload path

Document any such changes in [changelog/rule-changes.md](../changelog/rule-changes.md).
