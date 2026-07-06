# RunLab.ai — Independent Strategic Review

## Metadata

| Field | Value |
|-------|-------|
| **Reviewer** | Fable (independent multi-role review: startup founder, CTO, product strategist, endurance coaching expert, AI systems architect, seed-stage investor) |
| **Date** | 6 July 2026 |
| **Review type** | Independent strategic, technical, and commercial due diligence |
| **Repository** | RunLab.ai (`runlab-prototype`) |
| **Scope** | Complete repository, live website (`runlab.ai`, `prototype.runlab.ai`), `VISION_AND_STRATEGY.md`, roadmap and planning documents |
| **Status** | Historical artefact – do not edit |

---

**TL;DR up front:** The thinking is unusually good; the evidence is unusually thin. The single most alarming finding is not in the strategy — it's the gap between the strategy and the repository. You have ~25 polished markdown documents, a "constitution," a validation framework, and a horizon model… and an engine that fails 3 of its 5 runnable test scenarios because of a bug your own docs estimate at **1–2 hours to fix**, which remains unfixed. Zero automated tests exist. The sixth scenario file was never created. `docs/NEXT_STEPS.md` states plainly: *"No application code has been changed yet."* You are at risk of becoming a strategist of a product rather than the builder of one. Everything else in this review is secondary to that observation.

---

## 1. Product Thesis

**Is the problem real?** Partially. "Data-rich, judgment-poor" is a genuine and well-articulated insight. Plateaued self-coached runners do exist in volume, and the two failure modes you name (dashboard paralysis, changing everything at once) are real.

**But the thesis quietly conflates two different claims:**

1. Coaching judgment is valuable. **True.**
2. A deterministic rules engine with 8 hard gates, 9 limiter categories, and hardcoded thresholds (`quality_pct >= 0.35`, `weekly_km < 50`) constitutes coaching judgment. **Unproven, and probably overstated.**

What you've actually built is a decision tree encoding textbook heuristics — "consistency before volume, base before intensity." That's the part of coaching judgment that's *already written down* in every good training book. The part that makes a coach worth £150/month is exactly what your engine excludes by design: injury history, life stress, individual response to stimulus, race context, how this athlete handled the last three builds. Your own `limiter-framework.md` lists these as out of scope. So the honest framing is: RunLab automates the *cheapest* 60% of coaching judgment — the part your target user (analytical, structured, sub-3-adjacent) is most likely to already know. There's an uncomfortable irony in the wedge: the runner most capable of exporting a CSV and acting on structured advice is the runner who least needs a flowchart to tell them their easy volume is low.

**Is diagnosis-only a sustainable place to compete?** This is the weakest pillar of the thesis, and the strategy doc treats it as the strongest. Three problems:

- **Diagnosis is naturally a feature, not a product.** It wants to live where the data already is (Garmin, Strava) or where the execution happens (Runna, TrainingPeaks). A standalone diagnosis tool has both a data-acquisition problem *and* an action-handoff problem: "your limiter is volume" — now the user leaves your product to act on it, and returns… when?
- **The market has voted, repeatedly, for plans over diagnosis.** Runna grew fast enough that Strava bought it. Nobody has grown a diagnosis-only product. That's not proof the layer is unserved because it's hard — it may be unserved because demand pools at the execution layer where daily habit and payment naturally live.
- **The claim that diagnosis is "unserved by software" is factually shaky.** Garmin's Training Status and Load Focus (Firstbeat) already tell users "anaerobic shortage / low aerobic shortage / unproductive / recovery" — that *is* a deterministic limiter diagnosis, on richer physiological data than you'll ever see from a CSV, shipped on tens of millions of wrists. It's badly explained and generic, which is your genuine opening — but the layer is not empty.

**Verdict on thesis:** Real problem, honest framing of the coaching act, but the standalone commercial container for it is doubtful. The thesis works better as a wedge into something (coach tooling, an embedded judgment service) than as the destination.

---

## 2. Differentiation

**"Rules decide, AI explains" is a philosophy, not a moat.** It's a genuinely good philosophy — but any competent team could replicate the entire architecture in weeks. The engine is ~7 Python modules; the coaching heuristics are from the public training canon. There is no proprietary data, no proprietary algorithm, no network effect, no switching cost. What you actually have is *positioning* (opinionated, restrained, anti-dashboard) — valuable for a small player, but not defensible against a motivated incumbent.

Against each named competitor:

- **Strava (+ Runna):** The most dangerous. They own the data, the social graph, the adaptive-plan engine, and 150M+ registered users. Athlete Intelligence is descriptive today; making it prescriptive ("here's the one thing limiting you") is an obvious roadmap item, and post-acquisition they have Runna's coaching logic to power it. Could they build your capability? Yes, in one to two quarters. Note also platform risk: Strava has been tightening API terms around third-party AI use of its data — your future ingestion path runs through a company that just became your competitor.
- **Garmin:** Already ships deterministic limiter-adjacent diagnosis (Load Focus, Training Status) plus Connect+ AI insights at $6.99/month. Their weakness is exactly yours to exploit: the advice reads as template-generated and unaccountable. But the capability gap is presentation and opinion, not technology.
- **TrainingPeaks / Final Surge:** Own the coach workflow. If your Horizon 3 (coach platform) is right, they are one product cycle away from "roster triage" — and coaches already live in their software.
- **Runna / Coopah:** Different buyer today, as you correctly note. But Runna-inside-Strava with "why this plan changed" explanations would absorb much of your value prop for the mass market.

**What would remain unique if an incumbent copied you:** willingness to be narrow, willingness to say "do less," no engagement incentive, and a coach-like voice with a stated philosophy. These are real but thin — they are brand attributes, not structural barriers.

**The only durable moat available to you** is the one your own doc identifies in §12: a longitudinal outcome dataset (which prescriptions actually resolved which limiters, for whom). Everything should be judged by whether it accelerates reaching that asset. The problem: an episodic product cannot collect it, and incumbents already have longitudinal data at scale. The window for this moat is real but narrower than the doc implies.

---

## 3. Strategic Direction

**What's right:** The sequencing discipline (engine → beta → revenue → scale) is genuinely rarer than you'd think and correct. The deferred list is excellent. The refusal to become Runna is correct.

**What's wrong:**

1. **Your validation gate is circular.** The 6/6 scenarios were authored by the same person who wrote the rules, using synthetic CSVs designed to exhibit the patterns the rules detect. Passing them proves internal consistency, not correctness. They are unit tests wearing a validation costume. Necessary, yes — but the doc treats "6/6 green" as the moment the engine is "correct," and it isn't.
2. **The beta metric measures the wrong thing.** "≥70% limiter agreement" from 5–10 runners recruited from your own network, scored by you, measures *plausibility and social compliance*, not correctness. A flattering wrong diagnosis gets agreement; a correct uncomfortable one ("run less") gets disagreement. You need a blind coach panel (2–3 coaches independently diagnosing the same anonymized data, compared against the engine) as the primary gate, with runner agreement as a secondary signal. Your own docs mention coach review only as "optional."
3. **A6 (the coach hypothesis) is "deliberately unexamined" — that's a sequencing error.** It's your strongest commercial hypothesis and it costs *nothing* to test: ten coach interviews require no code. If coaches say "I'd never let software second-guess my judgment, but I'd kill for X," that reshapes the whole company, and you should know it before spending 18 months on the individual product.
4. **Distribution is entirely deferred.** The plan validates the product for ~6 weeks and then… has no demand-side milestones at all. "Community-led, word of mouth" is a hope, not a plan. Demand validation (landing-page conversion, waitlist growth, content traction) can run in parallel with engine validation at near-zero cost.
5. **The repo contradicts itself.** `README2.md`'s roadmap lists *"AI-assisted training plan generation"* and *"expanded runner personas (beginner → competitive)"* — both explicitly named as fatal traps in `VISION_AND_STRATEGY.md` §7. One of these documents is lying about the strategy. Fix that today; it's the kind of drift the constitution exists to prevent, already happening in your own repo.
6. **Missing milestone: the real-data ingestion reality check.** Your `data/Beta1.csv` (a real-world-style export) has *no `workout_type` column at all*. Real Strava exports won't have your labels. That means the auto-classifier — currently the least validated component, with a broken test fixture (`with_classification.csv` is identical to `without_classification.csv`, no ground truth) — becomes load-bearing for every real user. The entire "engine correctness" question for real runners routes through classification quality, and the roadmap barely acknowledges it.

**Is the product trying to be too many things?** No — the strategy is admirably narrow. The failure mode here is the opposite: too much strategizing per unit of shipped validation.

---

## 4. Technical Architecture

**What's right:** The `data → metrics → signals → focus → explanation` pipeline is the correct shape. The engine modules are genuinely Streamlit-free. The AI explainer is properly leashed (post-decision, prompt-forbidden from overriding, template fallback, vendor-swappable). This is better architecture than most prototypes.

**Risks that will get expensive:**

1. **The central promise has no enforcement mechanism.** "Rules decide" is only auditable if rule behavior is pinned by executable tests. There are zero tests and no CI. There is also no `ENGINE_VERSION` anywhere in code, despite the strategy calling versioned coaching models "the single most important architectural investment." Right now a threshold edit silently changes every diagnosis with no trace. For a product whose entire pitch is accountability, this is the most on-the-nose gap possible.
2. **Thresholds are magic numbers scattered through `focus.py`,** not externalized config. The "coaching model as versioned artifact" abstraction should exist *before* beta, not after — because beta will generate rule changes, and you need to know which model version produced which diagnosis.
3. **Horizon 2 has zero architectural groundwork.** The prescribe→observe→confirm loop — "the most important idea in this document" — requires identity, persistence, report history, and scheduled re-analysis. The current system has no accounts, no database, no stored state, and a Streamlit surface that is a dead end for all of it. That's fine for now, but recognize that Horizon 2 is effectively a second product build, not an iteration. Budget for it mentally. The cheap insurance you *can* buy today: design the outcome-capture schema (diagnosis ID, model version, prescription, follow-up window, outcome) and start filling it manually from beta session one.
4. **Leaks in the boundary:** `report_engine.py` imports `ui_text` (presentation copy inside the orchestration layer) and `config.py` imports Streamlit for secrets. Small now; they're exactly the entanglements that block the headless/API future you say you want.
5. **Confidence scoring is a trust liability as shipped.** It measures score separation, not correctness, and your docs admit it can be "confidently wrong." Shipping a confidence label that doesn't mean confidence, in a product whose brand is honesty, is self-undermining. Either calibrate it or rename/remove it before real users see it.
6. **Hygiene:** four parallel backup trees (`src_pre/`, `src_pre2/`, `pybackup1.0/`, `backup/`) with divergent engine logic. Git is the backup. Delete them.

**Does the architecture support the futures you name?** Explainability: yes, by design. Coach tooling and API/enterprise: yes *in shape*, provided the ui_text/config leaks are fixed. Future AI: yes — a deterministic, auditable engine is actually an ideal *tool for an AI agent to call*, which matters enormously in §7 below.

---

## 5. Commercial Strategy

**The honest read: the individual-runner business is a hobby-scale business, and the doc half-knows it.**

- **One-off assessment (£15–30):** Reasonable as a willingness-to-pay probe; hopeless as a business. Sequential math: a narrow persona (self-coached, plateaued, 40–90 km/week, will export a CSV, will pay for advice-only) reached through word of mouth, buying once. Even excellent execution yields hundreds of pounds a month. Fine — the doc frames it as validation, not revenue. Just don't confuse a passed A4 test with a business.
- **£8–15/month subscription:** Anchoring problem. Runna costs roughly the same and delivers a full adaptive plan *plus* implicit diagnosis, inside the Strava ecosystem. You'd be charging plan-money for advice-only. The subscription is only honest *and* only sellable once the longitudinal loop demonstrably works — which per your own roadmap is 12+ months away, during which the incumbents keep moving.
- **Coach platform:** The best hypothesis, but the doc is naive about coaches. A coach's judgment *is their product* — a tool whose pitch is "software that makes the diagnosis" threatens their identity and margin. What coaches actually pay for is workflow, admin relief, and athlete communication (which is why TrainingPeaks wins). RunLab's realistic coach-shaped product is *triage and second opinion inside existing workflow* — which points toward being a feature or integration partner of TrainingPeaks/Final Surge rather than a standalone platform. That might still be a fine business (or an acquisition path), but it's a different one than "coach platform." Ten interviews would tell you. Do them now.
- **B2B/enterprise (clubs, brands, federations):** Unexamined in the docs; probably correctly so at this stage, but note that "judgment engine as embeddable service" (see §7) is the more plausible enterprise story than a direct SaaS.

**Biggest commercial risk:** every step can *pass* and still not compound — runners can agree with the diagnosis (A1 ✓), some can pay once (A4 ✓), and you still have no retention, no distribution engine, and no moat by month 18. The strategy has strong falsification gates for the product and none for the *business*.

---

## 6. Founder Blind Spots

This is the section to read twice.

1. **Strategy-writing as displacement activity.** The repo is the evidence: a 260-line vision document of genuinely high quality, a full validation framework, scenario specs, a changelog discipline — and an unfixed bug estimated at 1–2 hours that invalidates most of your demos, no tests, and a missing CSV file. Writing eloquent strategy feels like progress and is completely within your control; fixing the engine and having ten awkward beta conversations risks disconfirmation. You have optimized for the former. The vision doc even diagnoses this ("the documentation is ahead of the code") — which brings us to:
2. **Self-aware ≠ self-correcting.** The document pre-empts every objection: it names the traps, ranks its own risks, lists its own unproven assumptions. This is impressive and also a sophisticated form of armor — *acknowledging* a risk in writing can feel like *mitigating* it. The alias bug has been "documented and understood" across at least four documents. Documentation of a known defect is not a mitigation; it's a confession.
3. **Determinism elevated from means to identity.** "Rules decide, AI explains — *permanently*" is declared constitutional before a single user has confirmed they care about the distinction. Users don't buy decision architectures; they buy being right, being understood, and being told what to do. Determinism is your *current best method* for consistency and auditability — treat it as an empirical bet to be defended by evidence, not a religious commitment. The constitution as written forbids you from ever discovering that (say) rules-as-guardrails with model-based reasoning inside them produces diagnoses users trust *more*. Locking that door "permanently" is attachment, not strategy.
4. **The one-limiter dogma.** Plausible, elegant, on-brand — and unproven (your own A2). The whole brand is built on it before the first structured beta. Hold it as a hypothesis. If beta users consistently ask "but what about X too?", that's data, not weakness of character.
5. **You are the persona.** Data analyst, sub-3 marathoner, 40–90 km/week — the wedge is a mirror. That's fine for wedge selection (you understand the user) and dangerous for evidence evaluation (your network beta will be people like you, who agree with training philosophy like yours, scored by you). Design the beta to make disconfirmation *structurally possible*: blind coach panel, verbatim disagreements weighted over agreements.
6. **Features founders love that customers rarely care about,** all present here: the explainability *narrative* (users want good advice, not architecture disclosures on the landing page — note your homepage leads with "deterministic, structured logic," which is founder-speak, not user-speak); the PDF report; the nine-limiter taxonomy (could likely collapse to five with no user-visible loss and much easier validation); the confidence label.

---

## 7. Future Resilience (5–10 years)

**The uncomfortable truth: your core competitive premise depreciates with model capability.** The strategy's bet is that LLM-first coaches will be "glossy, confident, generically wrong" and that legible determinism wins the trust war. That describes 2024–2025 models. Over 5–10 years, models with tool access over a runner's *complete* Garmin/Strava history — able to reason, converse, remember, and *show their work* — will plausibly out-diagnose a nine-node decision tree, and will be able to present legible reasoning too. "Deterministic" as a consumer-facing trust signal weakens every year. Consistency of output, which you list as a core property, is not something most consumers value in a coach at all (humans coaches aren't deterministic; they're *accountable*).

What survives, in order of durability:

1. **The outcome dataset.** "Which prescriptions actually resolved which limiters, for whom" — no model capability improvement replaces ground truth you own. This was true in §2 and it's truer here. It is the *only* asset on your list that compounds with time.
2. **Calibrated track record as product.** "RunLab's diagnoses were confirmed correct in N% of followed cases" is a claim no LLM can make and no incumbent currently dares to. Accountability, not determinism, is the durable version of your trust thesis.
3. **The judgment engine as an agent-callable service.** Here's the genuinely good news: in a world of personal AI assistants, standalone consumer apps get disintermediated — but *tools that agents call* get amplified. A versioned, auditable, deterministic coaching-judgment API is exactly the kind of component an AI assistant wants to delegate to (verifiable, consistent, liability-friendly). Your architecture is accidentally well-shaped for this future. The strategic implication: invest in the headless, versioned, API-first engine *now* (which you should do anyway for coach tooling), and treat the Streamlit app as a disposable demo surface. This is the one place where the doc's instincts and the 10-year future align perfectly — lean into it.
4. **Brand/community with a stated philosophy.** Modest but real.

**Assumptions likely to become obsolete:** "LLM coaches are generically wrong" (eroding now); "users will export CSVs" (already mostly false); "richer physiological data is a distraction" (defensible today; by ~2030 a diagnosis ignoring HRV/sleep/readiness reads as willfully blind — the canonical schema should be designed to *accept* those inputs even while rules ignore them); "the app is the product" (the engine is the product; the app is one client).

**What to design in today to avoid a rewrite:** engine version stamps on every output; outcome-capture schema; a canonical input schema with optional physiological fields; a hard headless boundary (kill the `ui_text` import); and coaching models as named, versioned, swappable rule sets.

---

## 8. Things Not To Build

Your deferred list is already good. Making it sharper — **never build:**

- **Daily plan generation.** The doc says never; `README2.md` says "roadmap." Delete it from README2 today. This is the single most dangerous temptation because it looks like the obvious monetization of a prescription.
- **A chat coach.** The second most dangerous. It will feel like the natural AI evolution, it will demo brilliantly, and it converts your accountable engine into exactly the stochastic-coach product you exist to oppose. If conversation ever comes, it's a thin Q&A layer *about* a decision already made.
- **Readiness/HRV scoring as a product surface.** Accept the data in the schema eventually; never compete with WHOOP/Garmin on daily readiness.
- **Social/community/gamification features.** Instant brand suicide for "the anti-dashboard."
- **A mobile app** before the loop exists. Episodic products don't need home-screen real estate.
- **More limiter types.** Nine is already more than you can validate; the pressure will be toward more granularity. Resist. Consider collapsing to five.
- **The junior platform,** ever, as an extension (your docs are right — separate product or nothing).
- **More strategy documents.** Seriously: declare a documentation freeze until the test suite is green. The docs are done. They are ahead of reality and every additional page widens the gap.

**Reject on sight from beta users:** "one more chart," "compare me to other runners," "sync my sleep," "just give me a plan for next week." Each is the commoditization pull with a friendly face.

---

## 9. Biggest Risks, Ranked

1. **Founder execution risk — strategizing over shipping.** The repo's own evidence (unfixed 2-hour bug, 0 tests, missing V6 file, 25 strategy/spec documents). Solo, evenings and weekends, with a displacement pattern already visible. Nothing else on this list matters if this doesn't change.
2. **Demand risk — diagnosis-only may have no repeatable buyer.** A1/A4 unproven; the market's revealed preference is plans and dashboards. The product can be *right* and still not be *wanted* at a price that sustains it.
3. **Validation-design risk — false confidence from circular tests.** Self-authored synthetic scenarios plus a self-scored "agreement" metric from a friendly network can green-light a wrong engine.
4. **Real-world data risk.** Real exports lack workout labels; the classifier is the least validated component with broken test fixtures; ingestion quality silently determines diagnosis quality. The engine may pass 6/6 and fail on the first real Strava export.
5. **Incumbent absorption.** Strava+Runna and Garmin Connect+ are one product cycle from "here's the one thing limiting you" cards. Your window is roughly 12–24 months to build the assets they can't copy (outcome data, coach relationships).
6. **Episodic value ceiling.** One-shot product, no retention mechanics, and the honest subscription is gated behind a Horizon 2 that requires a substantially new build.
7. **Platform/data-access risk.** Strava owns your ingestion path *and* your closest competitor, and has been tightening API terms around third-party AI use.
8. **Trust-destruction risk.** One confidently-wrong diagnosis per user is all you get; the miscalibrated confidence label amplifies this.
9. **Depreciation of the core differentiator.** Legible reasoning stops being scarce as models improve; determinism-as-moat has a shelf life.
10. **Economic sustainability of the founder.** 2–3 years of evenings/weekends against funded, accelerating incumbents, with hobby-scale interim revenue. Burnout and quiet abandonment is the most common way projects like this actually die.

---

## 10. Biggest Opportunities, Ranked

1. **Fix the engine and lock it with tests — this week.** Highest leverage-per-hour in the company: ~2 hours for the alias fix, one evening for pytest scenarios V1–V6, an hour for CI. It converts your entire "rules decide" pitch from slogan to demonstrable fact.
2. **Blind coach-panel validation on real data.** Replaces circular validation with the closest available ground truth, and doubles as coach discovery (opportunity 3).
3. **Coach interviews now.** Ten conversations, zero code. Tests A6, your strongest commercial hypothesis, and may legitimately re-sequence the company toward the higher-value market 12 months earlier.
4. **Outcome capture from beta session one.** Even a spreadsheet: diagnosis, engine version, prescription, 6-week follow-up, resolved or not. This is day one of the only compounding moat available to you.
5. **The headless judgment engine / future agent-callable API.** Formalize the engine as a versioned, UI-free service. Serves coach tooling, enterprise, and the personal-AI-assistant future simultaneously, at modest cost since the architecture is already close.
6. **"Second opinion" partner positioning.** Be the diagnosis that plugs into TrainingPeaks/Final Surge/plan tools rather than a competitor to everything. More realistic than a standalone coach platform, and the plausible acquisition narrative.
7. **Founder-led content as distribution.** The sub-3 data-analyst credibility is a real, non-transferable asset currently generating zero distribution. Public engine write-ups, real (anonymized) diagnosis breakdowns, "why your Garmin status is lying to you" — builds the trust brand while validation runs.
8. **Calibrated confidence as a public product feature.** "We track whether we were right" is a category-defining move no competitor will dare copy quickly, because their engagement models can't survive that accountability.
9. **Narrow the taxonomy.** Five limiters diagnosed superbly beats nine diagnosed plausibly; halves the validation burden and sharpens the brand.
10. **Adjacent endurance sports via the coaching-model abstraction** — real, but only after running is won; the abstraction (opportunity 5) is what keeps this cheap later.

---

## 11. Overall Assessment

### Strengths

- The problem diagnosis (judgment gap, not data gap) is genuinely insightful and well-argued.
- Sequencing discipline — validate before beta, beta before revenue, revenue before scale — is rare and correct.
- The trap analysis (§7 of the vision doc) is exactly right; most founders never see those traps until they're inside them.
- The architecture shape (pipeline, leashed AI, engine/UI separation) is right for every future you might choose.
- The docs are honest about failures — a real cultural asset, if it converts into action.

### Weaknesses

- **Execution inversion:** documentation quality dramatically exceeds code reality; known critical defects persist unfixed while strategy accretes.
- **Validation theater risk:** self-authored scenarios and a self-scored agreement metric are structurally incapable of disconfirming the founder.
- **No demand-side plan at all** — distribution is a hope deferred indefinitely.
- **Standalone economics are weak** at every stage of the monetization ladder, and the strongest commercial hypothesis (coaches) is deliberately untested.
- **Determinism as permanent constitution** rather than falsifiable bet — the doc's deepest conviction is also its least examined.
- The repo actively contradicts the strategy (`README2.md` roadmap).

### Immediate Corrections (5)

1. **Declare a strategy freeze and ship.** No new documents until: alias fix merged, V6 created, 6/6 passing, pytest suite green, CI running. Per your own estimates this is under a week of evenings.
2. **Redesign validation around disconfirmation:** blind coach panel on real (not synthetic) data as the primary gate; runner agreement demoted to secondary; real Strava exports through the classifier as a mandatory scenario class.
3. **Pull coach discovery forward.** Ten interviews in the next 30 days. A6 is too load-bearing to leave "deliberately unexamined."
4. **Reconcile the artifacts.** Delete plan-generation and persona-expansion from `README2.md`; delete the four backup trees; add `ENGINE_VERSION` and externalize thresholds into a versioned config. Make the repo tell the same story as the strategy.
5. **Downgrade "rules decide, AI explains — permanently" to "…until evidence says otherwise."** Keep the leash; drop the theology. Simultaneously *upgrade* the commitment to accountability: engine versioning, outcome tracking, calibrated confidence. Accountability is the durable form of your trust thesis; determinism is just its current implementation.

### Highest-Leverage Next Actions (5)

1. This week: alias fix + `declining_load.csv` + 6/6 + pytest + CI. (Your `NEXT_STEPS.md` Steps 1–4, which are correct — execute them.)
2. Next two weeks: run 5 *real* Strava exports (yours and friends') through the full pipeline including the classifier; document every failure; fix the classifier fixtures.
3. In parallel: book 10 coach interviews and recruit the blind panel (2–3 coaches, 5 anonymised datasets each, independent diagnoses vs. engine).
4. Start the outcome log — spreadsheet-grade is fine — from the first beta session.
5. One public artifact per month (engine write-up, real diagnosis breakdown) to begin compounding distribution while validation runs.

### Final Verdict

**Continue with significant adjustments.**

The strategic thinking is above the bar; the wedge is well-chosen; the architecture is sound; the traps are correctly mapped. This is not a "pivot" or "pause" situation — the core hypothesis deserves its test, and the test is cheap and near.

But the adjustments are not cosmetic. Three things must change or this fails slowly: **(1)** the founder's ratio of shipping to strategizing must invert, starting this week, with the test suite as the proof; **(2)** validation must be rebuilt to be capable of proving the founder wrong — coach panels and real data, not synthetic scenarios and friendly agreement; **(3)** the business must be given its own falsification gates — coach discovery now, a demand signal by month three, and an honest checkpoint at month six: if the coach channel is dead *and* individual willingness-to-pay is weak, the right move is to reposition the engine as an embedded/API judgment service or wind down gracefully — not to spend years two and three polishing a diagnosis nobody is buying.

One closing note, because it's the thing an investor would actually underwrite or decline on: the vision document is good enough that it could sustain you emotionally for two years without the product ever being validated. That is its danger. The document's own test — *"does this make the judgment more correct, more trusted, or more scalable?"* — currently indicts the document itself. The most strategic thing in this repository is a 2-hour bug fix. Go do it.
