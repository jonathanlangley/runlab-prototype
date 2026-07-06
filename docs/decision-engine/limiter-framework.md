# Limiter Framework

RunLab selects **one primary limiter** — the training factor that most limits progress **right now**. Other issues may exist; they appear as supporting signals, not co-equal priorities.

**The deterministic rules in `focus.py` make this decision. AI does not.**

## Why one limiter?

Self-coached runners typically fail by changing too much at once. RunLab optimises for:

1. **Clarity** — one headline focus
2. **Sequencing** — fix rhythm before volume, volume before intensity, etc.
3. **Explainability** — each limiter maps to a known coaching pattern

## The nine limiters

| `primary_key` | Limiter label | Typical runner situation |
|---------------|---------------|--------------------------|
| `consistency` | Consistency | Too few run days; irregular rhythm |
| `volume` | Aerobic volume | Weekly km too low for performance goals |
| `aerobic_support` | Aerobic support | Too much quality relative to easy volume |
| `load_stability` | Training load stability | Volume declining or highly variable at moderate+ load |
| `long_run` | Long run stimulus | No long run detected in last 28 days |
| `threshold` | Threshold support | Missing or irregular threshold work |
| `quality` | Quality stimulus | Adequate base but no structured faster work |
| `progression` | Progression | Sound structure but static across levers |
| `maintenance` | No major limiter | Broadly healthy; small careful progression |

## Headlines and timeframes

Each limiter maps to user-facing copy in `FOCUS_RULES` (`src/focus.py`):

| Key | Headline | Typical timeframe |
|-----|----------|-----------------|
| `consistency` | Your training rhythm is not repeatable enough yet | 2–3 weeks |
| `volume` | Your training is limited by aerobic volume, not intensity | 3–4 weeks |
| `aerobic_support` | Your hard sessions need more aerobic support | 3–6 weeks |
| `load_stability` | Your training load needs to stabilise before progressing | 2–3 weeks |
| `long_run` | Your long run is the missing endurance anchor | 3–4 weeks |
| `threshold` | Your training needs a controlled threshold stimulus | 3–4 weeks |
| `quality` | Your week needs one clearer quality stimulus | 3–4 weeks |
| `progression` | Your structure is sound, but progression is too static | 2–4 weeks |
| `maintenance` | Your current rhythm is healthy, so progress carefully | 2–4 weeks |

## Priority order (tie-breaking)

When the scored limiter model is used (after hard gates), tie-breaking follows `PRIMARY_ORDER`:

```
consistency → aerobic_support → volume → load_stability → long_run
→ threshold → quality → progression → maintenance
```

Earlier in this list wins when scores are similar.

## Hard gates vs scored selection

`choose_primary_limiter()` applies **hard gates first** (see [focus-rules.md](focus-rules.md)). These can override the score model:

1. Run days < 4/week → `consistency`
2. High quality % + low easy % + km < 70 → `aerobic_support`
3. Weekly km < 50 → `volume`
4. Declining volume trend + km ≥ 50 → `load_stability`
5. **Long runs in 28d == 0 → `long_run`**
6. **No quality sessions + km ≥ 50 → `quality`**
7. **No threshold + quality ≤ 2 → `threshold`**
8. Else → highest score if ≥ 55, else `maintenance`

**Validation note:** Gate 5 is sensitive to workout-type labelling. Mislabelled `long` sessions trigger false `long_run` limiters.

## Secondary limiter

A secondary focus may be set via `choose_secondary_limiter()` when another domain scores ≥ 55 and is allowed for the primary. Shown as `secondary_focus` in the report. Secondary does not replace the primary prescription.

## What RunLab will not surface as primary limiter

- Injury or pain
- Sleep, nutrition, HRV (not in current metrics)
- Race tactics or periodisation phase
- Strength training gaps
- Multiple simultaneous equal-priority issues

These may be relevant to a real coach; they are **out of scope** for the current engine.

## Coaching philosophy embedded in rules

The engine reflects a **performance-oriented adult marathon / half-marathon** coaching model:

- Aerobic base before intensity
- Consistency before load
- One lever at a time when progressing
- ~50–70+ km/week as a meaningful volume band for development
- Long run as weekly endurance anchor

Runners far outside this model (beginners, low mileage, juniors) may receive limiters that feel mismatched until rules are segmented by persona.

## Related documents

- [focus-rules.md](focus-rules.md) — decision tree and score model
- [signals-catalog.md](signals-catalog.md) — evidence behind each limiter
- [prescription-logic.md](prescription-logic.md) — recommended actions per limiter
