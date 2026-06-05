# Next Steps

Action plan from the current state (decision-engine docs complete, **1–2/6 scenarios passing**) through structured beta. **No application code has been changed yet** for these steps.

Related docs:

- [validation-pack.md](validation/validation-pack.md) — scenario specs and rubric
- [beta-readiness-checklist.md](validation/beta-readiness-checklist.md) — gate before beta
- [FOUNDER_NOTES.md](FOUNDER_NOTES.md) — strategic context

---

## Overview

```
Fix normalisation → Re-run scenarios → 6/6 pass → Automated tests
        → Beta-readiness checklist → 5–10 beta testers → Limiter agreement
                → Only then consider commercialisation
```

**Current phase:** deterministic limiter validation.  
**Not now:** revenue, subscriptions, Strava API, coach platform.

---

## Step 1 — Fix workout type normalisation

**Goal:** Metrics and focus rules see canonical workout types regardless of demo CSV aliases.

**Actions:**

1. Add alias mapping in `src/data_loader.py` during `clean_data()`:
   - `long` → `long run`
   - `interval`, `intervals` → `vo2`
   - `tempo` → `threshold`
2. Optionally align demo CSV labels to canonical vocabulary (belt-and-braces)
3. Update [canonical-schema.md](decision-engine/canonical-schema.md) alias table status from "not implemented" to "implemented"
4. Log change in [rule-changes.md](changelog/rule-changes.md)

**Success criteria:**

- `long_runs_last_28` and `vo2_sessions_last_28` count correctly on V3–V5 files
- No regression on V1–V2 primary limiters

**Estimated effort:** 1–2 hours

---

## Step 2 — Re-run validation scenarios

**Goal:** Confirm engine behaviour against documented expectations after normalisation fix.

**Actions:**

1. Manually run each scenario in the app (**Try demo scenarios**) or via `generate_runlab_report()`
2. Record actual `primary_key`, key metrics, and top signals per [scenario-specs/](validation/scenario-specs/)
3. Update pass/fail status in [validation-pack.md](validation/validation-pack.md)
4. Update [rule-changes.md](changelog/rule-changes.md) with results

**Scenarios to run:**

| ID | File | Expected `primary_key` |
|----|------|------------------------|
| V1 | `data/inconsistent_training.csv` | `consistency` |
| V2 | `data/sample_runs.csv` | `volume` |
| V3 | `data/too_much_intensity.csv` | `aerobic_support` |
| V4 | `data/high_volume_no_quality.csv` | `quality` |
| V5 | `data/near_optimal_but_plateauing.csv` | `progression` |
| V6 | `data/declining_load.csv` | `load_stability` |

**Success criteria:**

- Each scenario documented with actual vs expected output
- Any remaining failures have a written root-cause note

**Estimated effort:** 1–2 hours (after V6 file exists)

---

## Step 3 — Achieve 6/6 passing scenarios

**Goal:** All core validation scenarios pass the rubric in [validation-pack.md](validation/validation-pack.md).

**Blocking work:**

1. **Create V6** — `data/declining_load.csv` per [V6-declining-load.md](validation/scenario-specs/V6-declining-load.md)
2. Register V6 in `src/runlab_config.py` when code changes are allowed
3. If V3 still fails after alias fix, tune scenario data or review `quality_pct >= 0.35` gate — document decision in changelog
4. Review whether `long_runs == 0` hard gate ordering needs adjustment (see open questions in FOUNDER_NOTES)

**Per-scenario PASS requires:**

- Correct `primary_key`
- Expected signals present
- No contradictory high-priority signals
- Prescription theme matches limiter

**Success criteria:**

- **6/6 PASS** on primary limiter
- Founder manual review: agree with ≥5/6 limiter choices

**Estimated effort:** 3–6 hours (including V6 creation and any rule tweaks)

---

## Step 4 — Add automated regression tests

**Goal:** Prevent silent engine regressions when rules or data change.

**Actions:**

1. Create `tests/test_demo_scenarios.py` with parametrized cases for V1–V6
2. Assert `focus["primary_key"]` and optionally key metrics (with tolerances)
3. Add `tests/test_workout_type_normalisation.py` for alias mapping
4. Add `tests/test_classifier.py` for `without_classification.csv` (upload path)
5. Run `pytest` locally; add CI or pre-push habit

**Success criteria:**

- All tests green
- Changing a rule without updating tests causes a visible failure

**Estimated effort:** 1 evening

---

## Step 5 — Complete beta-readiness checklist

**Goal:** Explicit sign-off that engine is ready for real runners.

**Actions:**

Work through every item in [beta-readiness-checklist.md](validation/beta-readiness-checklist.md):

- 6/6 scenarios pass
- Alias fix implemented
- V6 file exists
- Automated tests added and passing
- Classifier runs after `clean_data()` (upload path)
- Beta users get full report unlock
- Feedback mechanism prepared
- Founder sign-off recorded

**Success criteria:**

- Checklist fully ticked with date and sign-off line completed

**Estimated effort:** 1–2 hours (mostly verification)

---

## Step 6 — Recruit 5–10 structured beta testers

**Goal:** Test whether real runners agree with limiter diagnoses — not to maximise signups.

**Only start after Steps 1–5 complete.**

**Target persona:**

Self-coached HM/marathon runner, plateaued, Strava user, in your network (1st/2nd degree).

**Actions:**

1. Prepare beta invite (what RunLab does, time required, feedback obligation)
2. Prepare Strava export guide (even if import is manual CSV for now)
3. Create feedback form:
   - Limiter accuracy (1–5)
   - What limiter would you have chosen?
   - Would you act on the prescription?
   - Would you pay for a one-off assessment? (optional — not charging yet)
4. Personally invite **8–15 people**; expect **5–10 completions**
5. Offer 10-minute setup help (concierge onboarding)
6. Remove beta-code friction for invited testers

**Success criteria:**

- 5–10 completed sessions with uploaded data and feedback form
- Verbatim quotes captured for limiter agreement and surprises

**Estimated effort:** 2–4 weeks calendar time (alongside day job)

---

## Step 7 — Validate limiter agreement before commercialisation

**Goal:** Decide whether the engine is credible enough to charge anyone.

**Actions:**

1. Score each session: **Agree** / **Mostly agree** / **Disagree** with primary limiter
2. Cluster disagreement patterns (e.g. always wrong on volume, always suggests quality)
3. If ≥70% agree/mostly agree → consider **one-off paid assessment** pilot
4. If <70% → return to Step 3 (rule refinement), not marketing
5. Optional: 2–3 coaches review 5 anonymised PDFs for secondary validation
6. Log findings in [rule-changes.md](changelog/rule-changes.md)

**Success criteria for commercialisation readiness:**

| Metric | Threshold |
|--------|-----------|
| Limiter agreement | ≥70% agree or mostly agree |
| No dominant failure cluster | <3/10 sessions same wrong pattern without fix plan |
| Founder confidence | Would send report to a club mate without apology |

**First commercial step (when ready):** one-off paid assessment (£15–25), **not** monthly subscription until retention mechanics exist.

**Estimated effort:** 1–2 weeks after beta sessions complete

---

## Consolidated success criteria

| Milestone | Criteria |
|-----------|----------|
| **Engine validated** | 6/6 scenarios pass + automated tests green |
| **Beta ready** | Beta-readiness checklist signed off |
| **Beta complete** | 5–10 structured sessions with feedback |
| **Commercialisation ready** | ≥70% limiter agreement; systematic failures addressed |
| **Revenue validation** | First paid one-off assessments (after above) |

---

## Deferred work

Do after engine + beta validation, not in parallel:

| Item | Why deferred |
|------|--------------|
| Import-layer / adapter refactor | Engine must be correct on known data first |
| Strava API OAuth | CSV export sufficient for beta |
| Monthly subscription / Stripe | Episodic product; retention not built |
| Historical limiter tracking | Retention feature; post-validation |
| Coach roster dashboard | After individual limiter credibly validated |
| Garmin / Coros / TrainingPeaks imports | After Strava CSV path works |
| V7 maintenance control scenario | Optional; not blocking 6/6 |
| Landing page / marketing scale | After limiter agreement proven |

---

## Explicitly out of scope (for now)

Do not work on these until commercialisation readiness criteria are met:

- **£1,500/month MRR targets** as a near-term driver
- **Junior athlete development platform**
- **Readiness / HRV / sleep integrations**
- **Historical block comparison**
- **Daily workout plan generation** (Runna competitor path)
- **Strava API + OAuth + sync state**
- **User accounts, database, stored reports**
- **Coach intelligence platform build** (hypothesis only until engine validates)
- **Broad "all runners" positioning**
- **Paid subscription without retention loop**
- **Cold outreach / ads for volume signups**

---

## Suggested timeline (evenings/weekends)

| Weeks | Focus |
|-------|-------|
| **1** | Steps 1–3: normalisation, V6 file, 6/6 pass |
| **2** | Step 4–5: tests + checklist sign-off |
| **3–5** | Step 6: recruit and run 5–10 beta sessions |
| **6** | Step 7: agreement analysis + go/no-go on one-off paid pilot |

Adjust if rule refinement loops are needed after Step 3.

---

## Decision gates

| Gate | If pass | If fail |
|------|---------|---------|
| After Step 3 | Proceed to tests + beta prep | Fix rules/data; do not recruit beta |
| After Step 7 | Pilot one-off paid assessments | More rule work or narrow persona |
| After paid pilot | Consider coach wedge or retention features | Revisit positioning; do not scale marketing |

---

## Quick reference — what to do this week

1. Implement workout-type alias normalisation
2. Create `data/declining_load.csv`
3. Re-run all six scenarios and update validation-pack status
4. Fix any remaining failures before writing tests

Do **not** recruit beta testers until 6/6 passes.
