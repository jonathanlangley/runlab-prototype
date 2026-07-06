# RunLab Documentation

This folder documents how RunLab analyses training data, selects a **primary limiter**, and produces recommendations.

## What RunLab does (and does not do)

RunLab identifies **one primary training limiter** — the single factor most likely holding the runner back **right now** — and recommends what to focus on next. It does **not** attempt to flag every possible issue in a training block.

| RunLab does | RunLab does not |
|-------------|-----------------|
| Select a primary limiter via **deterministic rules** | Let AI choose the limiter |
| Produce supporting signals as evidence | Replace a human coach |
| Explain the decision in coach-style language (AI layer) | Diagnose injury or medical issues |
| Suggest a next-week focus | Generate daily workout plans |

**The rules make the decision. AI explains the decision but does not make it.**

## Documentation map

### Decision engine

How the pipeline works end to end.

| Document | Contents |
|----------|----------|
| [overview.md](decision-engine/overview.md) | Pipeline: data → metrics → signals → focus → report |
| [canonical-schema.md](decision-engine/canonical-schema.md) | Required columns, workout types, known aliases |
| [limiter-framework.md](decision-engine/limiter-framework.md) | All nine limiter types and when they apply |
| [metrics-reference.md](decision-engine/metrics-reference.md) | Metrics computed from training data |
| [signals-catalog.md](decision-engine/signals-catalog.md) | Rule-based signals and priorities |
| [focus-rules.md](decision-engine/focus-rules.md) | How the primary limiter is chosen |
| [confidence-scoring.md](decision-engine/confidence-scoring.md) | Confidence labels and limitations |
| [prescription-logic.md](decision-engine/prescription-logic.md) | Next-week plan and prescription actions |

### Validation

Pre-beta testing of controlled demo scenarios.

| Document | Contents |
|----------|----------|
| [validation-pack.md](validation/validation-pack.md) | Master validation guide and current status |
| [scenario-specs/](validation/scenario-specs/) | Expected output per core scenario |
| [classifier-expectations.md](validation/classifier-expectations.md) | Auto-classification test fixtures |
| [beta-readiness-checklist.md](validation/beta-readiness-checklist.md) | Gate criteria before real-user beta |

### Reviews

Strategic and implementation reviews.

| Document | Contents |
|----------|----------|
| [FABLE_REVIEW.md](reviews/FABLE_REVIEW.md) | Independent strategic review (historical artefact — do not edit) |
| [CONSENSUS_REVIEW.md](reviews/CONSENSUS_REVIEW.md) | Consensus synthesis and implementation guide |

### Other

| Document | Contents |
|----------|----------|
| [FOUNDER_NOTES.md](FOUNDER_NOTES.md) | Product and validation priorities (internal) |
| [NEXT_STEPS.md](NEXT_STEPS.md) | Action plan from validation through beta |
| [changelog/rule-changes.md](changelog/rule-changes.md) | History of rule and threshold changes |

## Current validation goal

**6/6 core demo scenarios must pass** automated and manual validation before engaging beta testers.

As of 2026-07-06:

- **6/6 scenarios pass** (automated in `tests/test_demo_scenarios.py`)
- Workout-type alias normalisation implemented
- V6 `declining_load.csv` exists and is registered in the app

See [validation-pack.md](validation/validation-pack.md) for details.

## Archived code trees

The repository contains legacy backup directories (`src_pre/`, `src_pre2/`, `pybackup1.0/`, `backup/`) with divergent earlier engine and app implementations. **Only `src/` and `app.py` are active.** Do not import from backup trees. They are retained for historical reference pending founder review before deletion.

## Source code map

| Module | Role |
|--------|------|
| `src/data_loader.py` | Column mapping, cleaning, run filter |
| `src/metrics.py` | Weekly summary and 28-day metrics |
| `src/signals.py` | Rule-based signal generation |
| `src/focus.py` | Limiter selection, prescriptions, confidence |
| `src/report_engine.py` | Pipeline orchestration |
| `src/ai_explainer.py` | Coach-style explanation (post-decision) |
| `src/runlab_classifier_v1.py` | Optional workout-type classification |

## How to use these docs

1. Read [decision-engine/overview.md](decision-engine/overview.md) for the big picture.
2. Read [validation/validation-pack.md](validation/validation-pack.md) before changing rules or scenarios.
3. Update [changelog/rule-changes.md](changelog/rule-changes.md) whenever thresholds or priority order change.
4. Re-run the validation suite after any engine change (`pytest`).
