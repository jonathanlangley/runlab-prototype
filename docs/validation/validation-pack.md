# Validation Pack

Master guide for validating RunLab's deterministic decision engine **before** engaging real-user beta testers.

## Purpose

Prove that on **controlled demo scenarios**, RunLab:

1. Computes expected metrics from known training patterns
2. Emits expected supporting signals
3. Selects the **expected primary limiter**
4. Produces prescriptions aligned with that limiter

**Beta testers should not be engaged until this validation suite passes.**

## Core principles (restated)

| Principle | Detail |
|-----------|--------|
| **One primary limiter** | RunLab identifies the main limiter, not every issue |
| **Rules decide** | `signals.py` + `focus.py` make the decision |
| **AI explains only** | `ai_explainer.py` does not select or change the limiter |
| **Canonical workout types** | `easy`, `threshold`, `vo2`, `long run`, `race` |
| **Known aliases** | `long`, `interval`, `intervals`, `tempo` must map to canonical forms |

## Validation goal

### **6/6 core scenarios passing**

| ID | Scenario | File | Expected `primary_key` | Current status |
|----|----------|------|------------------------|----------------|
| V1 | Inconsistent training | `data/inconsistent_training.csv` | `consistency` | **PASS** |
| V2 | Low aerobic volume | `data/sample_runs.csv` | `volume` | **PASS** |
| V3 | Too much intensity | `data/too_much_intensity.csv` | `aerobic_support` | **PASS** |
| V4 | High volume, no quality | `data/high_volume_no_quality.csv` | `quality` | **PASS** |
| V5 | Structured plateau | `data/near_optimal_but_plateauing.csv` | `progression` | **PASS** |
| V6 | Declining load | `data/declining_load.csv` | `load_stability` | **PASS** |

**Optional control:** [V7-maintenance-control.md](scenario-specs/V7-maintenance-control.md) — not required for 6/6 gate.

### Observed pass rate

**6 / 6** — enforced by `tests/test_demo_scenarios.py` and CI.

## Root cause of prior failures (resolved 2026-07-06)

Demo CSVs use workout labels `long` and `interval`. Metrics count only `long run` and `vo2`.

Effect:

- `long_runs_last_28 = 0` despite long sessions in file
- `vo2_sessions_last_28 = 0` despite interval sessions
- `choose_primary_limiter()` gate 5 (`long_runs == 0`) fires → incorrect `long_run` limiter

**Remediation (planned, not implemented):**

1. Normalise aliases in `data_loader.py`
2. Update demo CSV labels to canonical vocabulary
3. Add automated regression tests
4. Create `data/declining_load.csv` for V6

## Pass/fail rubric

### Per-scenario PASS requires ALL:

| # | Criterion |
|---|-----------|
| 1 | `focus.primary_key` matches expected value exactly |
| 2 | `focus.limiter` matches expected user-facing label |
| 3 | Key metrics within documented tolerance (see scenario spec) |
| 4 | At least one expected **high** or **medium** signal present |
| 5 | No contradictory **high** signal (e.g. "No long run" when long runs exist after normalisation) |
| 6 | Prescription theme matches limiter family |
| 7 | Report generates without error |

### Per-scenario FAIL if ANY:

- Wrong `primary_key`
- Known label bug causes wrong metric counts that drive the decision
- Engine error or empty report

### Suite-level PASS (beta gate):

| Gate | Requirement |
|------|-------------|
| Core scenarios | **6/6** PASS |
| Founder manual review | ≥5/6 "agree" or "mostly agree" on limiter |
| Alias normalisation | Implemented and documented |
| V6 file | Exists and passes |
| Automated tests | Added and CI-green (planned next step) |

## How to run validation (manual)

1. Start app: `streamlit run app.py`
2. Select **Try demo scenarios**
3. Choose scenario
4. Open **Report** tab (demos are fully unlocked)
5. Compare output to scenario spec in `scenario-specs/`
6. Record actual metrics and limiter in spreadsheet or changelog

**Future:** `pytest tests/test_demo_scenarios.py` will automate steps 2–5.

## Scenario spec index

| Doc | Scenario |
|-----|----------|
| [V1-inconsistent.md](scenario-specs/V1-inconsistent.md) | Inconsistent training |
| [V2-low-volume.md](scenario-specs/V2-low-volume.md) | Low aerobic volume |
| [V3-too-much-intensity.md](scenario-specs/V3-too-much-intensity.md) | Too much intensity |
| [V4-high-volume-no-quality.md](scenario-specs/V4-high-volume-no-quality.md) | High volume, no quality |
| [V5-structured-plateau.md](scenario-specs/V5-structured-plateau.md) | Structured plateau |
| [V6-declining-load.md](scenario-specs/V6-declining-load.md) | Declining load |
| [V7-maintenance-control.md](scenario-specs/V7-maintenance-control.md) | Maintenance control (optional) |

## Classifier validation (separate track)

Upload-path auto-classification is validated against `data/without_classification.csv`.

See [classifier-expectations.md](classifier-expectations.md). Classifier validation is required **before upload beta** but is **not** part of the 6/6 demo gate.

## Recommended remediation order

| Step | Action | Blocks beta? |
|------|--------|--------------|
| 1 | Document expected behaviour (this pack) | — |
| 2 | Normalise workout-type aliases in `data_loader.py` | Yes |
| 3 | Re-run 6 scenarios; update status table | Yes |
| 4 | Create `data/declining_load.csv` | Yes |
| 5 | Add automated tests | Yes |
| 6 | Review `long_runs == 0` gate ordering | Recommended |
| 7 | Founder sign-off on [beta-readiness-checklist.md](beta-readiness-checklist.md) | Yes |
| 8 | Engage beta testers | Only after 6/6 |

## Recording results

Log each validation run and rule change in [../changelog/rule-changes.md](../changelog/rule-changes.md).

Include:

- Date
- Scenario ID
- Pass/fail
- Actual vs expected `primary_key`
- Notes on metric deltas
