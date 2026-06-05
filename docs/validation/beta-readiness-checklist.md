# Beta Readiness Checklist

Gate criteria before engaging real-runner beta testers. All items should be checked explicitly.

**Do not engage beta testers until the validation suite passes.**

---

## 1. Decision engine validation

| # | Item | Status |
|---|------|--------|
| 1.1 | V1 inconsistent → `consistency` PASS | ☐ |
| 1.2 | V2 low volume → `volume` PASS | ☐ |
| 1.3 | V3 too much intensity → `aerobic_support` PASS | ☐ |
| 1.4 | V4 high volume no quality → `quality` PASS | ☐ |
| 1.5 | V5 structured plateau → `progression` PASS | ☐ |
| 1.6 | V6 declining load → `load_stability` PASS | ☐ |
| 1.7 | **6/6 core scenarios PASS** | ☐ |

## 2. Data and schema

| # | Item | Status |
|---|------|--------|
| 2.1 | Workout-type alias normalisation implemented (`long`, `interval`, `tempo`) | ☐ |
| 2.2 | Demo CSV labels aligned OR aliases handle all demo files | ☐ |
| 2.3 | `data/declining_load.csv` created for V6 | ☐ |
| 2.4 | [canonical-schema.md](../decision-engine/canonical-schema.md) matches implementation | ☐ |

## 3. Automated regression

| # | Item | Status |
|---|------|--------|
| 3.1 | `tests/test_demo_scenarios.py` added | ☐ |
| 3.2 | All tests pass locally | ☐ |
| 3.3 | Workout-type normalisation tests added | ☐ |
| 3.4 | Tests run on every commit (CI or pre-push habit) | ☐ |

## 4. Classifier (upload path)

| # | Item | Status |
|---|------|--------|
| 4.1 | Classification runs after `clean_data()` | ☐ |
| 4.2 | `without_classification.csv` ≥90% accuracy | ☐ |
| 4.3 | Strava export guide documented for beta users | ☐ |

## 5. Product and UX (minimum)

| # | Item | Status |
|---|------|--------|
| 5.1 | Beta testers get **full report** (no preview-only gate) | ☐ |
| 5.2 | Feedback mechanism defined (form or email questions) | ☐ |
| 5.3 | "Rules decide, AI explains" visible in report footer | ☐ |

## 6. Founder review

| # | Item | Status |
|---|------|--------|
| 6.1 | Manual review: ≥5/6 scenarios "limiter agree" | ☐ |
| 6.2 | Known failure modes documented (persona limits, injury blind spot) | ☐ |
| 6.3 | [rule-changes.md](../changelog/rule-changes.md) up to date | ☐ |

## 7. Explicitly out of scope for first beta

These are NOT required to check off:

- Monthly subscription / payments
- Strava API OAuth
- User accounts / history
- Coach multi-athlete dashboard
- Junior athletics support

---

## Sign-off

| Field | Value |
|-------|-------|
| Date | |
| Core scenarios pass | /6 |
| Founder | |
| Ready for beta | YES / NO |

If **NO**, return to [validation-pack.md](validation-pack.md) remediation order.
