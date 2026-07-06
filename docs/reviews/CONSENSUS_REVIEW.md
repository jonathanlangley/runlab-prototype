# RunLab.ai — Consensus Review

## Metadata

| Field | Value |
|-------|-------|
| **Date** | 6 July 2026 |
| **Review type** | Consensus synthesis (repository + `VISION_AND_STRATEGY.md` + independent review) |
| **Inputs** | [`FABLE_REVIEW.md`](FABLE_REVIEW.md), [`VISION_AND_STRATEGY.md`](../../VISION_AND_STRATEGY.md), [`docs/NEXT_STEPS.md`](../NEXT_STEPS.md), current repository state |
| **Purpose** | Practical implementation guide for the next phase of RunLab.ai |
| **Status** | Living document — update when decisions are made or evidence changes |

---

## How to read this document

This consensus does **not** treat the independent review as authoritative. It triangulates three sources:

1. **Current strategy** — what RunLab has already decided and documented well
2. **Independent review** — external challenge and blind spots
3. **Repository reality** — what is actually built, broken, or missing

Each recommendation is classified:

| Classification | Meaning |
|----------------|---------|
| **Accept** | Adopt as stated; aligns with strategy and review |
| **Accept with modification** | Adopt the direction, but with adjusted scope, timing, or framing |
| **Validate before deciding** | Correct concern, but action depends on evidence not yet available |
| **Reject** | Do not adopt; current strategy is correct, or recommendation is premature or wrong |

---

## Where the current strategy is already correct

The independent review confirms several strategic choices that should **not** be changed:

- **Engine → beta → revenue → scale sequencing** — correct and rare; keep it
- **Narrow wedge** (self-coached HM/marathon, plateaued, 40–90 km/week) — correct; do not dilute
- **Refusal to become Runna / daily plan generator** — correct; this is the most dangerous trap
- **Refusal to become a dashboard** — correct
- **Rules decide, AI explains (as architecture)** — correct for now; the leash on AI is right
- **Horizon 2 prescribe→observe→confirm loop** — correct as the pivotal product evolution
- **One-off paid assessment before subscription** — correct commercial sequencing
- **Deferred list** (Strava API, accounts, coach platform build, juniors, HRV) — correct
- **Pipeline architecture** (`data → metrics → signals → focus → explanation`) — correct shape
- **Documentation honesty** about known failures — valuable cultural asset

These are strengths. The consensus does not recommend revisiting them.

---

## Recommendation register

### Product thesis

| # | Recommendation (from independent review) | Classification | Rationale | Expected impact | Priority |
|---|------------------------------------------|----------------|-----------|-----------------|----------|
| P1 | Diagnosis-only may not be a sustainable standalone product | **Validate before deciding** | The concern is real (market prefers plans; incumbents encroach), but A1/A4 are unproven. Premature pivot to "embedded service only" would abandon a testable hypothesis before it is tested. | High if validated wrong; low cost to defer until beta | Medium |
| P2 | Thesis works better as wedge into coach tooling / embedded service than destination | **Accept with modification** | Adopt as *parallel hypothesis*, not replacement. Individual runner product remains the validation vehicle; coach/API positioning is the contingency and long-term ceiling. Add to strategy as explicit fork, not silent assumption. | Clarifies commercial path without abandoning current wedge | Medium |
| P3 | Engine automates only the "cheapest 60%" of coaching judgment | **Accept** | Honest framing. Does not invalidate the product — it sets correct expectations for beta and marketing. Users still benefit from prioritisation and sequencing even if they "know" the advice in abstract. | Better beta design; sharper copy | Low |
| P4 | Garmin Load Focus / Training Status already occupy the diagnosis layer | **Accept with modification** | Factually correct. RunLab's opening is *quality of explanation and prioritisation*, not novelty of the layer. Position against "generic, unaccountable" diagnosis — not "no diagnosis exists." | Sharper competitive positioning | Low |

---

### Differentiation and moat

| # | Recommendation | Classification | Rationale | Expected impact | Priority |
|---|----------------|----------------|-----------|-----------------|----------|
| D1 | "Rules decide, AI explains" is philosophy, not moat | **Accept** | Correct. Do not confuse architectural principle with competitive barrier. Moat must be built separately. | Prevents false confidence in defensibility | Medium |
| D2 | Longitudinal outcome dataset is the only durable moat | **Accept** | Aligns with `VISION_AND_STRATEGY.md` §12. This is the compounding asset. Everything else is execution. | Defines what to optimise for from beta onward | High |
| D3 | Incumbents could replicate in 1–2 quarters | **Accept** | Realistic. Window is 12–24 months to build assets they cannot easily copy (outcome data, coach relationships, calibrated track record). | Urgency on validation and outcome capture | High |
| D4 | Reposition as "second opinion" integration partner vs. standalone competitor | **Accept with modification** | Strong long-term direction, but premature as primary positioning before individual product validates. Adopt as Horizon 3+ narrative and partnership exploration, not current GTM. | Better acquisition/partnership story later | Low (now) / High (later) |
| D5 | Brand attributes (narrow, anti-dashboard, stated philosophy) are real but thin | **Accept** | Useful for community-led GTM; not sufficient alone. Invest in brand via content, not ads. | Supports word-of-mouth wedge | Medium |

---

### Strategic direction and validation

| # | Recommendation | Classification | Rationale | Expected impact | Priority |
|---|----------------|----------------|-----------|-----------------|----------|
| S1 | 6/6 synthetic scenarios prove consistency, not correctness | **Accept with modification** | Correct critique, but scenarios remain necessary as regression tests. Keep 6/6 as **gate 1** (internal consistency); add **gate 2** (real data + coach panel) before commercialisation. Do not discard synthetic validation — extend it. | Prevents false confidence without abandoning existing framework | High |
| S2 | Replace runner agreement as primary beta metric with blind coach panel | **Accept with modification** | Coach panel should be **co-primary**, not sole gate. Runners still matter (they are the buyer). Target: ≥70% runner agreement **and** ≥60% coach agreement on same anonymised datasets. Either failing triggers rule work. | Strongest available validation upgrade | High |
| S3 | Pull coach discovery (A6) forward — 10 interviews now | **Accept** | Zero-code, high-leverage. Current strategy defers A6 too long given it is the strongest commercial hypothesis. Does not require building coach platform — only interviews. | May re-sequence company 12 months earlier if validated | High |
| S4 | Add demand-side milestones in parallel with engine validation | **Accept with modification** | Correct that distribution is deferred too far. Add lightweight demand signals now: waitlist growth, one public content piece/month, landing-page conversion tracking. Do not launch paid acquisition. | Reduces "product passes, business fails" risk | Medium |
| S5 | Real Strava exports through classifier as mandatory validation class | **Accept** | Critical gap. `Beta1.csv` and real exports lack workout labels; classifier is load-bearing and least validated. Must run before beta, not after. | Prevents "6/6 pass, first real user fails" | High |
| S6 | Fix README2.md roadmap contradiction (plan generation, persona expansion) | **Accept** | Repo contradicts strategy. Simple fix; prevents drift. | Restores single source of truth | High |
| S7 | Declare documentation freeze until test suite green | **Accept with modification** | Correct spirit — stop strategizing, start shipping. Frame as "no new strategy docs until Steps 1–4 of NEXT_STEPS complete," not permanent freeze. Existing docs may receive factual updates (validation status, changelog). | Forces execution | High |

---

### Technical architecture

| # | Recommendation | Classification | Rationale | Expected impact | Priority |
|---|----------------|----------------|-----------|-----------------|----------|
| T1 | Fix alias normalisation bug; achieve 6/6; add pytest + CI | **Accept** | Already in `NEXT_STEPS.md`. Independent review confirms this is the highest-leverage work in the company. Non-negotiable. | Converts "rules decide" from slogan to demonstrable fact | **High** |
| T2 | Add `ENGINE_VERSION` and versioned coaching model config | **Accept with modification** | Aligns with strategy §9. Implement lightweight version stamp on every report output now; full externalised threshold config can follow after first beta rule changes. Minimum viable: version string + changelog link in report metadata. | Enables accountability and outcome tracking | High |
| T3 | Externalise all thresholds from `focus.py` into config | **Validate before deciding** | Architecturally correct long-term, but premature before beta generates rule changes. Start with version stamp; externalise thresholds when first post-beta rule edit is needed. | Avoids over-engineering before validation | Medium |
| T4 | Remove `ui_text` import from `report_engine.py`; fix `config.py` Streamlit coupling | **Accept with modification** | Correct direction for headless/API future. Defer until after beta unless it blocks testing. Small refactor; do alongside T2 if touching report output. | Unblocks future API/coach surfaces | Medium |
| T5 | Design outcome-capture schema now; fill manually from beta session one | **Accept** | Cheap insurance for the only compounding moat. Spreadsheet-grade is fine. Schema: diagnosis ID, engine version, primary limiter, prescription, follow-up date, outcome (resolved / not / unknown). | Day one of outcome dataset | High |
| T6 | Calibrate or remove confidence label before real users | **Accept with modification** | Do not remove — rename to reflect what it measures ("signal clarity" or "limiter separation") until calibrated against outcomes. Removing loses a future trust feature; miscalibrated label destroys trust now. | Prevents trust-destruction on launch | Medium |
| T7 | Delete backup trees (`src_pre/`, `src_pre2/`, `pybackup1.0/`, `backup/`) | **Accept** | Git is the backup. Four divergent engine trees increase confusion risk. Delete after confirming `src/` is sole active tree. | Repo hygiene; reduces bus factor | Medium |
| T8 | Design canonical schema to accept optional physiological fields (HRV, sleep) even if rules ignore them | **Accept with modification** | Correct 5–10 year thinking. Add optional columns to schema docs now; no engine work until post-validation. | Future-proofs without scope creep | Low |
| T9 | Treat Streamlit app as disposable demo surface; invest in headless engine | **Accept with modification** | Correct long-term. For next 3 months, Streamlit remains the beta surface. Headless extraction is medium-term, not immediate. | Right architecture, right timing | Medium (3-month horizon) |
| T10 | Fix classifier test fixtures (`with_classification.csv` has no ground truth) | **Accept** | Broken fixture undermines classifier validation. Must fix before real-data validation (S5). | Enables classifier quality gate | High |

---

### Commercial strategy

| # | Recommendation | Classification | Rationale | Expected impact | Priority |
|---|----------------|----------------|-----------|-----------------|----------|
| C1 | One-off assessment is validation, not a business | **Accept** | Aligns with current strategy. Keep £15–30 one-off as A4 test; do not plan around it as revenue. | Prevents false commercial confidence | Low |
| C2 | Subscription only honest after Horizon 2 loop exists | **Accept** | Already in strategy. No change. | Prevents dishonest monetisation | — |
| C3 | Coach platform is best hypothesis but naive about coach psychology | **Accept with modification** | Correct that coaches are the ceiling. Reframe from "software makes the diagnosis" to "triage and second opinion inside existing workflow." Test via interviews (S3), not build. | Better product-market fit if coach path validates | High (discovery) |
| C4 | Add business falsification gates (demand signal by month 3; checkpoint at month 6) | **Accept** | Strategy has product gates but no business gates. Add: by month 3, measure waitlist/content traction; by month 6, if coach channel dead AND individual WTP weak, evaluate embedded/API repositioning. | Prevents slow failure | Medium |
| C5 | Individual-runner standalone economics are hobby-scale | **Accept** | Correct math. Does not invalidate the wedge as validation vehicle. Informs honest expectations and checkpoint timing. | Realistic planning | Low |

---

### Founder blind spots and product principles

| # | Recommendation | Classification | Rationale | Expected impact | Priority |
|---|----------------|----------------|-----------|-----------------|----------|
| F1 | Strategy-writing as displacement activity | **Accept** | Repo evidence is unambiguous. Ratio of docs to passing tests is inverted. | Forces execution focus | High |
| F2 | Downgrade "permanently" on rules-decide constitution | **Accept with modification** | Keep the AI leash permanently. Reframe determinism as *current best method*, not eternal law. Wording change in constitution only; no architectural change. Accountability (versioning, outcome tracking) becomes the durable commitment instead. | Preserves flexibility without abandoning principle | Medium |
| F3 | One-limiter framing is hypothesis, not dogma | **Validate before deciding** | Correct that A2 is unproven. Hold one-limiter as default; treat beta feedback asking for multiple limiters as data, not failure. Do not collapse taxonomy (see R1) before beta. | Prevents premature product change | Medium |
| F4 | Design beta for disconfirmation (blind coach panel, weight disagreements) | **Accept** | See S2. Structural change to beta protocol. | Strongest validation upgrade | High |
| F5 | Landing page leads with founder-speak ("deterministic logic") not user-speak | **Accept with modification** | Valid critique. Reframe public copy around outcome ("find the one thing holding you back") not architecture. Keep determinism in "how it works" section for trust-oriented users. | Better conversion | Medium |
| F6 | Collapse nine limiters to five | **Reject** | Premature before beta. Nine limiters map to distinct coaching patterns and prescriptions. Collapsing now reduces validation granularity and prescription specificity without evidence users find nine confusing. Revisit only if beta shows limiter confusion. | Avoids unnecessary refactor pre-validation | — |

---

### Things not to build

| # | Recommendation | Classification | Rationale | Expected impact | Priority |
|---|----------------|----------------|-----------|-----------------|----------|
| R1 | Never build daily plan generation | **Accept** | Already in strategy §7. Remove from README2.md. | Prevents fatal drift | High |
| R2 | Never build chat coach | **Accept with modification** | Correct as primary interface. Allow thin Q&A *about* an existing diagnosis later (Horizon 2+). Not now. | Protects core architecture | — |
| R3 | Never build readiness/HRV scoring as product surface | **Accept** | Already deferred. Accept data in schema (T8); do not productise. | Prevents scope creep | — |
| R4 | Never build social/gamification | **Accept** | Brand suicide for anti-dashboard positioning. | Protects brand | — |
| R5 | No mobile app before loop exists | **Accept** | Episodic product does not need home-screen presence. | Saves effort | — |
| R6 | No more strategy documents until test suite green | **Accept with modification** | See S7. | Forces execution | High |
| R7 | No junior platform as extension | **Accept** | Already in strategy. Separate product or nothing. | Prevents persona dilution | — |

---

### Future resilience (5–10 years)

| # | Recommendation | Classification | Rationale | Expected impact | Priority |
|---|----------------|----------------|-----------|-----------------|----------|
| L1 | Determinism-as-moat depreciates; accountability-as-moat endures | **Accept** | Reframe trust thesis from "deterministic" to "accountable and trackable." Engine versioning + outcome dataset are the durable assets. | Correct long-term positioning | Medium |
| L2 | Engine as agent-callable service is the 10-year shape | **Accept with modification** | Architecturally aligned. Do not build API now. Preserve headless boundary (T4) so this is cheap later. | Future-proofs without premature build | Medium (3-month) / High (long-term) |
| L3 | Personal AI assistants disintermediate standalone apps | **Accept** | Confirms engine > app as the asset. Streamlit is demo; engine is product. | Validates architecture investment | Low (awareness) |
| L4 | Richer physiological data becomes expected by ~2030 | **Accept with modification** | Schema readiness (T8) now; engine integration only post-validation and post-loop. | Future-proofs | Low |

---

## Immediate actions (next 2 weeks)

These are ordered by dependency and leverage.

| # | Action | Source | Priority |
|---|--------|--------|----------|
| 1 | **Fix workout-type alias normalisation** in `src/data_loader.py` (`long` → `long run`, `interval`/`intervals` → `vo2`, `tempo` → `threshold`) | T1, `NEXT_STEPS.md` Step 1 | High |
| 2 | **Create `data/declining_load.csv`** (V6 scenario) per scenario spec | T1, `NEXT_STEPS.md` Step 3 | High |
| 3 | **Re-run all six scenarios; achieve 6/6 pass**; update validation-pack status | T1, `NEXT_STEPS.md` Steps 2–3 | High |
| 4 | **Add `tests/test_demo_scenarios.py`** (parametrised V1–V6) and `tests/test_workout_type_normalisation.py`; run green | T1, `NEXT_STEPS.md` Step 4 | High |
| 5 | **Add CI** (GitHub Actions or pre-push hook running pytest) | T1 | High |
| 6 | **Add `ENGINE_VERSION` to report output** (minimum viable versioning) | T2 | High |
| 7 | **Fix README2.md** — remove plan generation and persona expansion from roadmap | S6 | High |
| 8 | **Fix classifier fixtures** — add ground-truth labels to `with_classification.csv` | T10 | High |
| 9 | **Run 3–5 real Strava exports** through full pipeline including classifier; document failures | S5 | High |
| 10 | **Reconcile README2.md and strategy** — ensure single narrative | S6 | High |
| 11 | **Rename confidence label** to reflect measured property (e.g. "signal clarity") until calibrated | T6 | Medium |
| 12 | **Create outcome-capture spreadsheet template** | T5 | Medium |
| 13 | **Book first 3 coach interviews** | S3 | Medium |

**Documentation freeze applies:** no new strategy or spec documents until items 1–5 are complete.

---

## Medium-term actions (next 3 months)

| # | Action | Source | Priority |
|---|--------|--------|----------|
| 1 | **Complete beta-readiness checklist**; recruit 5–10 structured beta testers | `NEXT_STEPS.md` Steps 5–6 | High |
| 2 | **Run blind coach panel** (2–3 coaches, 5 anonymised datasets each) alongside runner beta | S2 | High |
| 3 | **Score beta with dual gate:** ≥70% runner agreement AND ≥60% coach agreement | S2 | High |
| 4 | **Complete 10 coach interviews**; document findings; update A6 status | S3 | High |
| 5 | **Start outcome log** from beta session one (manual spreadsheet) | T5, D2 | High |
| 6 | **Publish one public content piece** (engine write-up or anonymised diagnosis breakdown) | S4, D5 | Medium |
| 7 | **Track waitlist / landing-page conversion** as demand signal | S4, C4 | Medium |
| 8 | **Delete backup trees** after confirming `src/` is sole active codebase | T7 | Medium |
| 9 | **Refactor report_engine / config** to remove UI coupling (if not done in immediate phase) | T4 | Medium |
| 10 | **Update landing page copy** — lead with user outcome, not architecture | F5 | Medium |
| 11 | **Month-3 demand checkpoint:** evaluate waitlist growth and content traction | C4 | Medium |
| 12 | **Go/no-go on one-off paid pilot** only if dual validation gate passes | `NEXT_STEPS.md` Step 7 | High |
| 13 | **Document optional physiological fields** in canonical schema (no engine work) | T8 | Low |

---

## Long-term strategic direction

The consensus preserves the core vision with three explicit adjustments:

### What stays

- RunLab is a **coaching judgment layer**, not a running app, dashboard, or plan generator
- **Individual runner product** remains the validation vehicle and proof of concept
- **Horizon 2 loop** (prescribe → observe → confirm) is the pivotal product evolution
- **Rules decide, AI explains** remains the architecture; AI never chooses the limiter
- **Outcome dataset** is the primary long-term moat to build
- **Narrow wedge** until won; no persona dilution

### What changes

1. **Validation model:** Synthetic scenarios remain gate 1 (regression); real data + coach panel become gate 2 (correctness). Runner agreement alone is insufficient.

2. **Trust thesis reframing:** From "deterministic" (depreciating consumer signal) to "accountable" (versioned engine, tracked outcomes, calibrated confidence). Determinism remains the implementation; accountability becomes the brand.

3. **Commercial contingency:** Coach/API/embedded-service path is an explicit parallel hypothesis, tested via interviews now and validated at month-6 checkpoint — not a silent fallback.

4. **Engine > app:** Streamlit remains the beta surface for 3 months. Medium-term investment shifts toward headless, versioned engine callable by future surfaces (coach dashboard, API, AI agents).

5. **Business gates added:** Month 3 (demand signal), month 6 (coach channel + individual WTP checkpoint). Failure on both triggers evaluation of embedded/API repositioning — not indefinite polishing.

### Horizon map (consensus-adjusted)

| Horizon | Focus | Gate to proceed |
|---------|-------|-----------------|
| **0** (now → weeks) | Engine correct: alias fix, 6/6, tests, CI, version stamp | All immediate actions complete |
| **1** (weeks → 2 months) | Dual validation: runner beta + coach panel on real data | ≥70% runner AND ≥60% coach agreement |
| **1b** (parallel) | Coach discovery: 10 interviews; demand signals | Findings documented; A6 updated |
| **2** (6–18 months) | Prescribe→observe→confirm loop; outcome dataset begins compounding | Horizon 1 passed; retention demonstrated |
| **3** (18 months+) | Coach triage / API / integration partner — shape determined by A6 findings | Engine credibly right; coach hypothesis validated or killed |

---

## Repository changes required

| Change | File(s) | When |
|--------|---------|------|
| Alias normalisation | `src/data_loader.py` | Immediate |
| V6 scenario file | `data/declining_load.csv`, `src/runlab_config.py` | Immediate |
| Automated tests | `tests/test_demo_scenarios.py`, `tests/test_workout_type_normalisation.py` | Immediate |
| CI config | `.github/workflows/test.yml` (or equivalent) | Immediate |
| Engine version stamp | `src/focus.py` or `src/report_engine.py`, report output | Immediate |
| README2 roadmap fix | `README2.md` | Immediate |
| Classifier fixture fix | `data/with_classification.csv` | Immediate |
| Confidence label rename | `src/focus.py`, `docs/decision-engine/confidence-scoring.md`, UI copy | Immediate |
| Outcome log template | `docs/validation/outcome-log-template.md` (or spreadsheet in repo) | Immediate |
| Beta protocol update | `docs/validation/beta-readiness-checklist.md`, `docs/NEXT_STEPS.md` | After immediate phase |
| Add coach panel gate | `docs/validation/validation-pack.md` | After immediate phase |
| Delete backup trees | `src_pre/`, `src_pre2/`, `pybackup1.0/`, `backup/` | Medium-term |
| Remove UI coupling | `src/report_engine.py`, `src/config.py` | Medium-term |
| Optional physiological fields | `docs/decision-engine/canonical-schema.md` | Medium-term |
| Constitution wording update | `VISION_AND_STRATEGY.md` §5 principle 2 | Medium-term (after beta) |
| Add business gates | `VISION_AND_STRATEGY.md` §8 or `docs/FOUNDER_NOTES.md` | Medium-term |
| Link reviews in docs map | `docs/README.md` | Immediate |

---

## Summary verdict

**Continue with significant adjustments** — unchanged from the independent review, but with clearer boundaries:

- **Accept wholesale:** execution urgency, validation upgrades, outcome capture, repo hygiene, things-not-to-build list, business gates, trust reframing
- **Accept with modification:** coach path (interviews now, build later), validation gates (extend, don't replace), versioning (minimum viable now, full config later), public copy, constitution wording
- **Validate before deciding:** standalone vs. embedded commercial container, one-limiter vs. multi-limiter, threshold externalisation timing
- **Reject:** collapse limiters to five (premature), abandon synthetic validation (still needed as regression), build API/headless now (premature), pivot to coach platform before individual validation

The most important single action remains unchanged: **fix the alias bug, pass 6/6, add tests, run CI.** Everything else in this document is downstream of that.

---

*Related documents: [`FABLE_REVIEW.md`](FABLE_REVIEW.md) (independent review, historical), [`VISION_AND_STRATEGY.md`](../../VISION_AND_STRATEGY.md) (strategy), [`NEXT_STEPS.md`](../NEXT_STEPS.md) (action plan)*
