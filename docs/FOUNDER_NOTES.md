# Founder Notes (Internal)

Internal priorities for RunLab validation and beta. Not user-facing.

For the concrete action plan, see [NEXT_STEPS.md](NEXT_STEPS.md).

---

## What RunLab is

RunLab is a **decision engine**, not a dashboard.

It does not aim to show runners more data. It aims to answer one question:

> **What is the single training limiter holding me back right now — and what should I focus on next week?**

The deterministic rules in `signals.py` and `focus.py` make that decision. AI explains the decision in coach-style language; **it does not make the decision.**

---

## Current phase

**Deterministic limiter validation** — not monetisation, not import-layer refactor, not coach platform build.

Sequence of truth:

```
Engine validation  →  Beta validation  →  Revenue validation
     (now)              (next)               (later)
```

**Revenue validation comes after engine validation.** Payment proves willingness to exchange money; it does not prove the limiter framework is correct. Do not optimise for MRR until controlled scenarios pass and beta testers agree with diagnoses.

The product hypothesis being tested:

> Self-coached adult endurance runners benefit from one clear primary limiter and a next-week focus, derived deterministically from recent training data.

That hypothesis is **unproven** until:

1. **6/6 core demo scenarios pass** — see [validation/validation-pack.md](validation/validation-pack.md)
2. **5–10 structured beta sessions** yield ≥70% limiter agreement

---

## Current target user

**Now:** self-coached **half-marathon and marathon** runners who feel plateaued, train with some structure, and can export recent activity data.

**Not now:** beginners, daily-plan seekers (Runna-shaped buyers), coached athletes, juniors, or broad "all runners."

Positioning draft:

> *RunLab tells self-coached HM/marathon runners their #1 training limiter — and what to focus on next week — from recent training data.*

---

## Future hypotheses (not current MVP)

### Coach intelligence platform (strongest long-term commercial hypothesis)

If the limiter engine validates, the same pipeline may create more value for **coaches** than for individual runners:

- Batch reports across a roster
- "Whose limiter needs attention first?"
- Higher ARPU, fewer customers needed

**Sequencing:** individual runner validation first → coach tools later, if engine is credible.

### Junior athlete development (separate future opportunity)

Junior athletics is **not** a natural extension of the current MVP.

| Adult self-coached MVP | Junior development |
|------------------------|-------------------|
| Performance optimisation | Long-term development |
| Runner makes decisions | Coach / parent decides |
| Marathon/HM volume logic | Age-appropriate, often lower volume |
| Current rules in `focus.py` | Would need a separate rules fork |

Treat juniors as a **separate product category** if pursued at all — not a near-term roadmap item.

---

## Current priority

**6/6 validation scenario pass before beta testers.**

| Status (2026-07-06) | Scenarios |
|-----------------------------|-----------|
| **PASS** | V1–V6 (6/6) |

Beta testers should **not** be engaged until the validation suite passes. See [beta-readiness-checklist.md](validation/beta-readiness-checklist.md).

---

## What matters now

1. **6/6 core scenarios pass** — [validation-pack.md](validation/validation-pack.md)
2. **Workout-type normalisation** — `long` / `interval` / `tempo` → canonical vocabulary
3. **Create V6 scenario** — `data/declining_load.csv`
4. **Automated regression tests** — lock expected limiters per scenario
5. **Structured beta (5–10)** — only after validation gate clears

---

## What does not matter now

- Monthly subscription / MRR targets (£1,500/month is a later milestone)
- Import-layer architecture (Phase 1 refactor)
- Strava API OAuth
- Coach dashboard / multi-athlete UI
- Junior athletics platform
- Landing page polish inside the repo
- Readiness scoring, block comparison, retention/history features

---

## Known critical issue

Demo CSV files use workout labels `long` and `interval`. The metrics engine counts only:

- `long run` (not `long`)
- `vo2` (not `interval`)

This causes `long_runs_last_28 = 0` in most demos and triggers the **`long_run` hard gate** in `choose_primary_limiter()` before the intended limiter is evaluated.

**Fix implemented:** alias normalisation in `data_loader.py` (2026-07-06).

Details: [canonical-schema.md](decision-engine/canonical-schema.md), [rule-changes.md](changelog/rule-changes.md).

---

## Validation philosophy

- **Product validation before business validation** — limiter agreement before charging
- **Episodic value is OK for now** — one-off diagnosis is the current product shape; retention features come later
- **First commercial step (when ready)** — one-off paid assessment, not monthly subscription without retention mechanics
- **Beta testers are for disconfirming the engine** — structured feedback, not friendly encouragement
- **Small beta pool is fine** — 5–10 strong-fit runners beats 40 weak outreach

---

## Target beta persona (when ready)

Self-coached adult, **half-marathon or marathon** focus, plateaued, Strava user, willing to export data and complete a structured feedback form.

Recruit from existing network: club, coach contacts, colleagues — not cold mass marketing.

---

## Success criteria before beta

| Gate | Threshold |
|------|-----------|
| Core scenario automated pass | **6/6** |
| Founder manual agreement | ≥5/6 limiters "accurate" or "mostly accurate" |
| Classifier fixture (upload path) | ≥90% row accuracy on `without_classification.csv` |
| Known alias issue | Documented **and fixed** |
| Beta-readiness checklist | Fully signed off |

---

## Success criteria before commercialisation

| Gate | Threshold |
|------|-----------|
| Beta limiter agreement | ≥70% of sessions |
| Willingness to pay (asked after report) | ≥30% say yes to one-off assessment |
| No systematic limiter failure mode | Documented in changelog |

---

## Open questions to resolve via validation

1. Is `long_runs == 0` hard gate the right priority vs `quality` / `aerobic_support`?
2. Does `quality_pct >= 0.35` threshold for aerobic support match real "too much intensity" cases?
3. Should `consistent_plateau` and `high_volume_no_quality` remain separate scenarios?
4. Is baseline mixed stimulus useful only as a UI demo (not validation)?
5. After engine validates, does coach review agree more or less than runner self-assessment?

Log answers in [changelog/rule-changes.md](changelog/rule-changes.md) as rules evolve.
