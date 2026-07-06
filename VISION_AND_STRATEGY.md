# RunLab.ai — Vision & Strategy

*The single strategic reference for RunLab.ai. Written to be read by future engineers, product managers, investors, employees — and by the founder six months from now.*

*This is not documentation. It is the argument for why RunLab should exist, what it is trying to become, and the test every future decision should be measured against. For how the system works today, see [`docs/`](docs/README.md). For what to build next, see [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md).*

---

## 0. The one-sentence thesis

**RunLab is not a running app. It is a model of coaching judgment — a system that looks at a runner's recent training and answers the single question a good coach answers and no dashboard ever will: *"What is the one thing holding you back right now, and what should you do about it next?"***

Everything in this document follows from that sentence. If a proposed feature, hire, or fundraising story does not sharpen or scale that judgment, it is a distraction — however reasonable it sounds in isolation.

---

## 1. The problem

Endurance runners have never had more data and never had less clarity.

A self-coached marathoner today wears a watch that captures pace, heart rate, cadence, power, elevation, HRV and sleep. Strava, Garmin Connect, TrainingPeaks and WHOOP each render that data as charts, scores and trends. The runner ends up with a dozen numbers moving in a dozen directions and no answer to the only question that matters:

> **What should I change to get faster — and what should I change *first*?**

This is not a data problem. It is a **judgment problem**. The market has comprehensively solved *measurement* and left *interpretation* to the athlete. Two failure modes result, and they are the reasons runners plateau, get injured, or quit:

1. **Paralysis by dashboard.** More metrics create more anxiety and more second-guessing, not better training.
2. **Changing everything at once.** The classic self-coached error: add mileage, add intensity, add a long run and a new session type in the same block, then be unable to tell what helped, what hurt, and what to do next.

A good coach cuts through both. They ignore twenty observations, name the *one* limiter that matters this month, prescribe a change to a single lever, and wait to see the response. That is a scarce, expensive, high-trust service. **RunLab exists to make that specific judgment available to runners who do not have — and often do not want — a human coach.**

---

## 2. Why RunLab should exist

Three structural facts make this the right product at the right time:

- **Coaching judgment is the last unsolved layer of the endurance stack.** Data capture is solved. Plan generation is crowded (Runna, TrainingPeaks templates, countless PDFs). Diagnosis and prioritisation — the actual coaching act — is unserved by software because it is hard, opinionated, and easy to get wrong. Difficulty is the opportunity.
- **The self-coached endurance runner is a large, underserved, high-intent segment.** They are analytical enough to export their data and motivated enough to act on advice, but a human coach is too expensive, too high-commitment, or too rigid for them. They are currently self-medicating with Reddit threads, YouTube, and half-remembered training-book heuristics.
- **Trust is now the scarce commodity, not intelligence.** In a market about to be flooded with generically confident "AI running coaches," a system whose reasoning is legible, consistent, and defensible is *more* valuable, not less. RunLab's deterministic core is not a limitation of the prototype era. It is the durable competitive position.

If RunLab did not exist, a serious self-coached runner would keep making the same two mistakes above, indefinitely. That is the gap.

---

## 3. Who it is for

### The wedge (now)

**Self-coached half-marathon and marathon runners who feel plateaued, train with some structure, and can export recent training data.**

This is deliberately narrow, and the narrowness is correct. This runner:

- has enough training history for the engine to reason about (4+ weeks, ideally 8+);
- trains in the volume band the current coaching model understands (~40–90 km/week);
- experiences a real, recurring pain ("I've stalled and I don't know why");
- can act on advice without a coach's permission;
- and is reachable through clubs, communities, and word of mouth rather than paid acquisition.

The current engine's assumptions — adult, performance-oriented, marathon/half cadence, Monday-start weeks — encode *this runner specifically*. That is a feature, not an accident. **Do not dilute the wedge to chase "all runners" before the wedge is won.** A diagnosis that is precisely right for one runner is worth more than one that is vaguely plausible for everyone.

### Who it is explicitly *not* for (yet)

- **Beginners** — their limiter is almost always "just run consistently," which needs a different, gentler model and a different tone.
- **Daily-plan seekers** — this is the Runna buyer. RunLab is not a plan generator and should not become one (see §7).
- **Coached athletes** — they already have the judgment layer RunLab provides.
- **Juniors** — long-term *development* is a different objective from adult *optimisation*, decided by coaches and parents, at lower volumes, under a duty of care. Treat this as a separate product category if pursued at all, never a roadmap tweak.

### Who it is *ultimately* for (the second act)

**Coaches and the runners they manage.** The same engine that diagnoses one runner can triage a roster: *"Across your 20 athletes, whose limiter needs attention this week, and why?"* This is a higher-value, lower-volume, higher-retention business (see §8). It is the second act, earned only after the engine is proven on individuals — not a pivot to reach for early.

---

## 4. What makes RunLab genuinely different

Most "AI coaching" products differentiate on model or data. RunLab differentiates on **architecture and restraint**. Four things separate it, and they compound:

1. **It decides, it does not describe.** Competitors show you your data. RunLab makes a call: one primary limiter, one next focus, one lever to move. The willingness to be *specific and wrong sometimes* — and therefore *specific and right often* — is the product. A tool that hedges everything is just another dashboard.

2. **The rules decide; the AI only explains.** This is RunLab's constitutional principle, and it is the deepest differentiator. The limiter is chosen by deterministic logic in [`src/focus.py`](src/focus.py). The language model in [`src/ai_explainer.py`](src/ai_explainer.py) is explicitly forbidden from overriding that decision and falls back to templated prose if unavailable. This produces three properties no LLM-first competitor can easily match:
   - **Consistency** — identical input yields identical advice, every time.
   - **Accountability** — every recommendation can be traced to a rule and improved deliberately.
   - **Trust** — the runner is coached by a stated philosophy, not by a stochastic guess wearing a coach's voice.

3. **Sequencing is built into the philosophy.** The engine encodes a coaching order of operations — consistency before load, aerobic base before intensity, one lever at a time. It doesn't just find problems; it knows which to fix *first*. That embedded sequencing is genuine domain expertise made into software.

4. **It optimises for the runner's next decision, not their engagement.** RunLab is designed to be *used briefly and trusted*, not to maximise time-in-app. In a market of dopamine dashboards, a tool that respects the athlete's attention is a differentiator — and, eventually, a brand.

None of these depend on having more data or a bigger model than Strava or Garmin. That is precisely why they are defensible: RunLab is not trying to win the arms race everyone else is losing money in.

---

## 5. Product principles — the constitution

These are the tests. When a decision is genuinely hard, resolve it against these, in order.

1. **Clarity over completeness.** One limiter, one focus, one lever. If a feature adds information without adding a decision, it is a step backwards. The moment the report starts to look like a dashboard, we have lost.

2. **Rules decide, AI explains — permanently.** This is not MVP scaffolding to be replaced when models improve. As LLMs get more persuasive, the pressure to "just let the model decide" will intensify. **Resist it.** The engine's legibility is the asset. AI may explain, summarise, converse, and personalise *tone* — it may never silently choose the limiter.

3. **Earn trust before revenue; earn revenue before scale.** The founder's sequence is correct and worth restating as law: **engine validation → beta validation → revenue validation → scale.** Payment proves willingness to pay; it does not prove the diagnosis is right. Never optimise for MRR while the diagnosis is unproven.

4. **Be specific and be accountable for it.** A confident, wrong-but-improvable answer beats a vague, unfalsifiable one. Every diagnosis must be checkable against reality, and every systematic error must be logged and fixed in the rules (see [`docs/changelog/rule-changes.md`](docs/changelog/rule-changes.md)).

5. **Honesty about confidence and scope.** Say what the engine can't see — injury, illness, life stress, nutrition, terrain, race context. A coaching tool that pretends to omniscience destroys the trust that is its entire value. Under-claiming is a feature.

6. **Narrow and correct beats broad and plausible.** Win one persona completely before serving the next. Every new persona is a new coaching model, not a config flag (see §7 and §12).

7. **The athlete's long-term health outranks their short-term progress.** RunLab will sometimes tell a motivated runner to do *less*. That advice — protecting them from themselves — is often the most valuable and most trust-building thing the product does.

---

## 6. How the product should evolve (3–5 years)

Four horizons. Each is gated by the previous one *actually succeeding* — not by time elapsed.

### Horizon 0 — Make the engine correct (now → next weeks)
**Nothing else matters until this is done.** The product's central claim is currently unproven: only 1–2 of 6 validation scenarios pass, and a known workout-label normalisation bug (`long`/`interval` not mapped to canonical types) fires a false `long_run` limiter across most demos. This is the single highest-leverage work in the entire company.
- Fix alias normalisation; get **6/6 core scenarios passing** with automated regression tests.
- Convert the (excellent) validation documentation into executing `pytest` suites. **Right now the documentation is ahead of the code** — a strength in intent, a liability if left unresolved. Docs that describe behaviour the engine doesn't yet exhibit are debt.
- **Do not recruit a single beta tester until the suite is green.**

### Horizon 1 — Prove the judgment on real runners (next)
- 5–10 structured beta sessions with strong-fit runners; target **≥70% limiter agreement**.
- Treat beta as *disconfirmation*, not encouragement. The goal is to find where the engine is wrong, cluster the failure modes, and fix the rules.
- Reduce onboarding friction with concierge setup (manual CSV, a human helping) before building any automated import.

### Horizon 2 — Close the loop and earn retention (6–18 months)
This is the pivotal evolution, and it is the most important idea in this document. Today RunLab is **episodic** — a one-off diagnosis. The durable product is **longitudinal**:

> Diagnose the limiter → prescribe one lever → the runner trains → RunLab observes the next block → confirms whether the limiter resolved → diagnoses the next one.

This "prescribe → observe → confirm" loop does three things at once:
- It **creates retention** honestly (the runner returns to see if they fixed it and what's next), replacing engagement-farming with genuine value.
- It **turns RunLab into a coaching *relationship***, not a coaching *report* — which is what a human coach actually provides.
- It **generates the outcome data that improves the engine.** Did runners who followed the volume prescription actually break their plateau? That is the ground truth the rules should eventually be tuned against.

Retention should be earned by *demonstrated progress over time*, never by a subscription paywall over a fundamentally episodic experience. Build the loop, then charge for it (see §8).

### Horizon 3 — The coach intelligence platform (18 months+)
Once the engine is credibly right for individuals, the same pipeline becomes a **triage and oversight tool for coaches**: batch limiter analysis across a roster, "whose training needs attention first," and a defensible second opinion. Higher ARPU, fewer customers, stickier relationships (see §8). This is the strongest long-term commercial hypothesis in the business — and it is only unlockable *after* Horizons 0–2.

**Explicitly deferred across all horizons** (in priority-inverted order of temptation): daily-plan generation, subscription-before-retention, junior platform, HRV/sleep/readiness scoring, broad "all runners" positioning, and paid acquisition at scale. Each is a plausible-sounding way to lose.

---

## 7. The strategic fork: what RunLab must *not* become

Two adjacent products will exert constant gravitational pull. Both are traps, and naming them now prevents an expensive drift later.

**Trap 1 — Become another dashboard.** The path of least resistance. Every beta user will ask for "just one more chart." Each is individually reasonable; collectively they turn the decision engine back into the data-soup the product was built to escape. **Guardrail:** supporting analysis stays supporting. The report leads with a decision, always. Charts justify the decision; they never replace it.

**Trap 2 — Become Runna (a daily-plan generator).** More seductive, because it looks like a bigger market and an obvious "next step" from prescriptions. But daily-plan generation is crowded, commoditised, and — critically — a *different product with a different buyer* (the beginner/plan-seeker, explicitly not RunLab's user). It also destroys the trust advantage: a wrong daily plan is a wrong instruction; a diagnosis is a considered opinion the athlete still owns.

**The recommendation is unambiguous: RunLab's territory is diagnosis and prioritisation — the coach's judgment layer that sits *above* both dashboards and plans.** A dashboard tells you what happened. A plan tells you what to do every day. RunLab tells you *what matters and why* — and lets you (or your coach, or eventually a plan tool) execute. That layer is scarce, defensible, and the only one where "rules decide, AI explains" is a genuine moat rather than a constraint. Integrating *outward* to plan tools and *inward* from data sources is fine. *Becoming* either is fatal.

---

## 8. Commercial strategy

**Sequencing (non-negotiable):** validate the engine → validate willingness to pay → then scale. Revenue is a *later* proof, not an early goal.

**Monetisation, in order of what to build:**

1. **One-off paid assessment (£15–30).** The first honest commercial step. The product is currently episodic, so the pricing should be too. This validates willingness to pay *without* the dishonesty of a subscription over a one-shot experience. Target: **≥30% of beta users say yes** after seeing a report.
2. **Progress subscription (only after Horizon 2).** Once the prescribe→observe→confirm loop exists, a recurring "training intelligence" subscription (roughly £8–15/month) becomes honest, because the runner is paying for *ongoing judgment and demonstrated progress*, not repeated access to the same static report. Retention must be earned by the loop, never enforced by a paywall.
3. **Coach platform (Horizon 3, highest ceiling).** Per-seat or per-roster pricing for coaches managing multiple athletes. Fewer customers, materially higher ARPU, far stickier — a coach who runs their whole roster through RunLab does not casually churn. This is where the durable, defensible revenue most likely lives.

**Go-to-market:** community-led and trust-led, not paid. Running clubs, coach networks, and word of mouth in a segment where credibility is everything and cold ads convert poorly. The founder's credibility (analytics background + sub-3 marathoner + years of personal data) is a real, non-transferable asset — the brand should be built on demonstrated judgment, not marketing spend.

**What proves the business:** not signups, not MRR, not time-in-app. The metric that matters is **limiter agreement and acted-upon prescriptions** — runners who received a diagnosis, believed it, acted on it, and improved. Everything commercial is downstream of that.

---

## 9. High-level technical direction

*Direction, not implementation. The goal is to protect the architecture's core virtue — legible, improvable coaching logic — as the system grows.*

- **Keep a hard boundary between the decision engine and everything else.** Data ingestion, the deterministic engine, the explanation layer, and the interface must remain cleanly separable. The engine is the crown jewel; it should be independently testable, portable across surfaces (web, coach dashboard, API), and never entangled with UI or a specific LLM vendor. The current `data → metrics → signals → focus → explanation` pipeline is the right shape; preserve it.

- **Treat the coaching logic as a first-class, versioned model.** Thresholds and rules encode a coaching philosophy. They deserve version control, changelogs (already established), regression tests, and eventually calibration against outcome data. The engine should evolve toward a **"coaching model" abstraction** — a named, versioned set of rules — so that new personas become *new models*, not tangled conditionals bolted onto the marathoner logic. This is the single most important architectural investment for scaling beyond the wedge.

- **Automated validation is the backbone, not an afterthought.** The validation framework is unusually mature for the stage — but it must *run*. Every rule change should trip a failing test if it silently regresses a scenario. No engine change ships without a green suite. This is what makes "the rules decide" a credible promise rather than a slogan.

- **Ingestion is an adapter problem — solve it late, solve it once.** Manual CSV is correct for beta. Strava/Garmin/Coros/TrainingPeaks integrations belong *behind a normalisation layer* that maps any source into the canonical schema. Build this only after the engine is proven; a perfect importer feeding a wrong engine is wasted work. The known label-normalisation bug is a preview of how much ingestion quietly determines engine correctness — take it seriously.

- **AI stays at the edges, on a leash.** The language model explains, and later may converse and personalise tone. It must always be: overridable by rules, gracefully degradable to templates (as it is today), vendor-swappable, and incapable of changing the diagnosis. As models improve, expand what AI is *allowed to say*, never what it is *allowed to decide*.

- **Make confidence mean something real, over time.** Today's confidence score measures *separation between limiters*, not *correctness* — and can be confidently wrong (the docs are admirably honest about this). As beta and outcome data accrue, confidence should be **calibrated against actual agreement and outcomes**, and lowered when workout types are inferred rather than labelled or when history is thin. Confidence that reflects reality is a trust multiplier.

- **Repository hygiene as a proxy for engineering discipline.** The repo carries multiple parallel backup trees (`src_pre/`, `src_pre2/`, `pybackup1.0/`, `backup/`). Understandable for a solo prototype; unacceptable the moment a second engineer joins. Before the first hire, consolidate to a single source of truth, delete the shadow copies (git is the backup), and let the discipline already evident in the *docs* extend to the *code*.

- **Personal data is a duty, not just an asset.** Training data is sensitive and, combined with identity, revealing. Privacy, consent, retention limits, and clear "this is not medical advice" boundaries must be designed in before accounts and stored history exist — not retrofitted after.

---

## 10. Product risks

Ordered by how likely they are to actually kill the product.

1. **The engine is quietly wrong.** The existential risk. A diagnosis that is confidently incorrect is worse than no diagnosis, because it destroys trust and can lead a runner to train badly. *Mitigation:* the entire Horizon 0–1 validation discipline exists for this. It is correctly prioritised above everything.

2. **Over-fitting to one persona.** The rules encode the ~40–90 km/week adult marathoner. Applied outside that band (beginners, low-mileage, masters, ultra) they produce plausible-sounding but wrong advice — and the confidence label won't flag it. *Mitigation:* the versioned "coaching model" abstraction; explicit persona boundaries; refusing to serve personas the model doesn't yet understand.

3. **The commoditisation pull.** Constant pressure to become a dashboard or a plan generator (§7). Drift here is slow, reasonable-feeling, and fatal. *Mitigation:* the constitution (§5) and a product owner willing to say no.

4. **Episodic value ceiling.** A one-off diagnosis is easy to try once and never return to. *Mitigation:* the prescribe→observe→confirm loop (Horizon 2) is the structural answer; retention through demonstrated progress, not paywalls.

5. **Ingestion friction kills the funnel.** Manual CSV export is a real barrier for all but the most motivated. *Mitigation:* concierge onboarding during beta; a proper import adapter only once the engine earns it.

6. **The "AI coach" gold rush prices trust incorrectly — for a while.** Well-funded, LLM-first competitors will ship glossy, confident, generically-wrong coaches and may win attention short-term. *Mitigation:* patience and positioning. RunLab's bet is that trust and correctness win the runners who matter, and that the deterministic core is the harder thing to copy. This bet must be held with conviction, not abandoned at the first competitive scare.

7. **Solo-founder / bus-factor risk.** Deep domain knowledge and product taste currently live in one person's head. *Mitigation:* this document; the docs suite; converting tacit judgment into tested rules; disciplined hiring.

---

## 11. Assumptions that must be validated

State them plainly so they can be proven or killed, not quietly assumed true.

- **A1 — The core bet.** Self-coached HM/marathon runners genuinely benefit from a *single* limiter plus a next-week focus. *Test:* ≥70% limiter agreement in structured beta. **Unproven.**
- **A2 — One-limiter framing is a feature, not a limitation.** Runners find a single focus clarifying rather than reductive. *Test:* qualitative beta feedback; do users act, or do they want the full list? **Unproven.**
- **A3 — Rules can approximate coaching judgment well enough.** A deterministic model captures enough of what a good coach does to be trusted. *Test:* beta agreement + optional coach review of anonymised reports. **Partially testable now.**
- **A4 — Willingness to pay for episodic insight.** ≥30% will pay for a one-off assessment. *Test:* post-report intent, then an actual paid pilot. **Unproven.**
- **A5 — The loop drives retention.** Runners return to check whether they fixed their limiter. *Test:* return and re-run rates once Horizon 2 exists. **Not yet testable.**
- **A6 — The coach hypothesis.** Coaches will pay meaningfully more for roster triage. *Test:* interviews now, a pilot later. **Deliberately unexamined until the engine is proven.**
- **A7 — Data accessibility.** Enough target runners can and will get their data into RunLab. *Test:* beta onboarding completion rates. **Partially known — assume it's harder than it looks.**

**The most dangerous assumption is A1.** If it fails, no amount of engineering or marketing saves the product — and no other assumption is worth testing first. Sequence validation accordingly.

---

## 12. Major opportunities

- **Own "the coaching judgment layer" as a category.** Everyone else is fighting over data capture and plan delivery. The interpretation layer between them is unclaimed, defensible, and the natural home for trustworthy AI. First-mover advantage here is real.
- **The coach platform (largest prize).** B2B2C to coaches is higher ARPU, lower volume, and far stickier than direct-to-runner. The individual product is arguably the *proof of concept and lead-generator* for the coach business.
- **A proprietary outcome dataset.** The prescribe→observe→confirm loop can generate something no competitor has: *what advice actually worked, for whom.* Over years this becomes the moat — coaching logic tuned against real longitudinal outcomes, not just textbook heuristics. This is the compounding asset.
- **Trusted second opinion / integration layer.** RunLab need not own the whole stack. It can be *the diagnosis* that plugs into the tools runners already use — a partner to Strava/Garmin/plan apps rather than a competitor to all of them.
- **Adjacent endurance sports.** Cycling, triathlon and rowing share the same structural problem (data-rich, judgment-poor) and the same limiter logic (aerobic base, load, intensity balance, progression). Only after running is won — but the engine abstraction is what makes it possible.
- **Brand as the anti-dashboard.** In a market drowning athletes in numbers, "the tool that tells you the one thing that matters" is a genuinely differentiated, defensible brand position with real emotional pull.

---

## 13. The long-term vision

**RunLab.ai should become the trusted judgment layer of endurance training — the system a serious runner (or their coach) turns to for the answer to "what should I do next, and why."**

Not the app with the most charts. Not the cheapest plan generator. Not the loudest AI coach. The one that is *right*, that *says why*, and that a runner *trusts* — because its reasoning is legible, its philosophy is stated, and its track record is earned over time and validated against real outcomes.

If RunLab succeeds, "run it through RunLab" becomes the reflexive first step when a runner stalls, or when a coach reviews their roster on a Monday morning — the way a developer reaches for a profiler when code is slow. It becomes infrastructure for training decisions: quiet, trusted, and definitive.

**The test for every future decision — feature, hire, partnership, or fundraise — is a single question:**

> *Does this make RunLab's judgment more correct, more trusted, or more scalable — without compromising the clarity, determinism, and honesty that make that judgment worth trusting in the first place?*

If yes, do it. If no — however large the market it promises, however loudly a competitor is chasing it — it is not RunLab.

---

*This document is intended to outlast any particular feature, model, or funding round. Revisit it when a decision is genuinely hard, when the roadmap feels crowded, or when a tempting adjacency (a dashboard, a daily plan, a new persona, a bigger model) starts to look like the obvious next move. It usually isn't. Update this document deliberately, with reasons — and only when the strategy has actually changed, not merely the weather.*
