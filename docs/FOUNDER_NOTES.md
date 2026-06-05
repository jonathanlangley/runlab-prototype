# Founder Notes (Internal)

Internal priorities for RunLab validation and beta. Not user-facing.

## Current phase

**Decision-engine validation** — not monetisation, not import-layer refactor.

The product hypothesis is:

> Self-coached adult endurance runners benefit from one clear primary limiter and a next-week focus, derived deterministically from recent training data.

That hypothesis is **unproven** until controlled scenarios pass and real runners agree with the diagnosis.

## What matters now

1. **6/6 core scenarios pass** — see [validation/validation-pack.md](validation/validation-pack.md)
2. **Workout-type normalisation** — `long` / `interval` must map to canonical labels before metrics run
3. **Automated regression tests** — to be added after docs; not started yet
4. **Structured beta** — only after validation gate clears

## What does not matter now

- Monthly subscription / MRR
- Import-layer architecture (Phase 1)
- Strava API
- Coach dashboard / multi-athlete
- Junior athletics platform (separate product category)
- Landing page polish inside the repo

## Known critical issue (as of doc creation)

Demo CSV files use workout labels `long` and `interval`. The metrics engine counts only:

- `long run` (not `long`)
- `vo2` (not `interval`)

This causes `long_runs_last_28 = 0` in most demos and triggers the **`long_run` hard gate** in `choose_primary_limiter()` before the intended limiter is evaluated.

**Fix planned:** normalise aliases in `data_loader.py` and align demo CSV labels. **Not implemented yet.**

## Validation philosophy

- **Product validation before business validation** — agreement on limiter accuracy before charging
- **Episodic value is OK for now** — one-off diagnosis is the current product shape; retention features come later
- **Beta testers are for disconfirming the engine** — not for friendly encouragement

## Target beta persona (when ready)

Self-coached adult, marathon or half-marathon focus, plateaued, Strava user, willing to export data and give structured feedback.

## Success criteria before beta

| Gate | Threshold |
|------|-----------|
| Core scenario automated pass | 6/6 |
| Founder manual agreement | ≥5/6 limiters |
| Classifier fixture (upload path) | ≥90% row accuracy on `without_classification.csv` |
| Known alias issue | Documented and fixed |

## Open questions to resolve via validation

1. Is `long_runs == 0` hard gate the right priority vs `quality` / `aerobic_support`?
2. Does `quality_pct >= 0.35` threshold for aerobic support match real "too much intensity" cases?
3. Should `consistent_plateau` and `high_volume_no_quality` remain separate scenarios?
4. Is baseline mixed stimulus useful only as a UI demo (not validation)?

Log answers in [changelog/rule-changes.md](changelog/rule-changes.md) as rules evolve.
