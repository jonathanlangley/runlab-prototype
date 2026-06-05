# Decision Engine Overview

RunLab transforms running activity data into a **single primary limiter** and a **next-week focus**. The decision is made by deterministic Python rules. AI is used only to explain the outcome.

## Pipeline

```
Raw activities (CSV)
        ↓
   clean_data()          ← column mapping, run filter, derived fields
        ↓
   weekly_summary()      ← per-week aggregates
   overall_metrics()     ← 28-day snapshot + trends
        ↓
   derive_signals()      ← rule-based evidence (multiple signals)
        ↓
   determine_focus()     ← ONE primary limiter + prescription
        ↓
   report assembly        ← product report, balance, structure, PDF
        ↓
   generate_ai_explanation()  ← coach-style prose (optional)
```

**Entry point:** `generate_runlab_report()` in `src/report_engine.py`

## Design principles

### One primary limiter

RunLab deliberately selects **one** primary limiter, not a ranked list of equal issues. Supporting signals provide evidence, but the report centres on a single priority.

Rationale: self-coached runners rarely need twelve observations. They need clarity on **what to change first**.

### Deterministic decision

Given the same cleaned data and metrics, the engine always produces the same `primary_key`. There is no model sampling, no LLM routing, no randomness.

### AI as explanation layer only

`src/ai_explainer.py` receives the focus decision already made. The prompt explicitly instructs the model **not to override** the RunLab recommendation. If OpenAI is unavailable, template fallback text is used.

### 28-day analysis window

Most limiter logic uses the **last 28 days** of activities (inclusive), anchored to the latest activity date in the dataset. Weekly trends compare recent four weeks vs prior four weeks where enough history exists.

## Limiter types (summary)

| `primary_key` | User-facing limiter |
|---------------|---------------------|
| `consistency` | Consistency |
| `volume` | Aerobic volume |
| `aerobic_support` | Aerobic support |
| `load_stability` | Training load stability |
| `long_run` | Long run stimulus |
| `threshold` | Threshold support |
| `quality` | Quality stimulus |
| `progression` | Progression |
| `maintenance` | No major limiter |

See [limiter-framework.md](limiter-framework.md) for full detail.

## What the engine assumes

- **Adult self-coached endurance runner** training for performance (especially half-marathon / marathon cadence)
- **Running activities only** after `clean_data()` filtering
- **Workout types** in canonical vocabulary (see [canonical-schema.md](canonical-schema.md))
- **Monday-start training weeks** for weekly aggregation

These assumptions are appropriate for the current MVP. They are **not** appropriate for junior development programmes without a separate rules fork.

## Outputs consumed by the UI

| Output key | Purpose |
|------------|---------|
| `focus` | Primary limiter, headline, prescription, next-week plan |
| `signals` | All derived signals (sorted by priority) |
| `top_signals` | Subset shown in report (max 3, category diversity) |
| `metrics` | Raw numbers for charts and evidence |
| `product_report` | User-facing report object |
| `ai_text` | Coach explanation |
| `used_ai` | Whether OpenAI was called successfully |

## Related documents

- [canonical-schema.md](canonical-schema.md) — input data requirements
- [metrics-reference.md](metrics-reference.md) — what gets measured
- [signals-catalog.md](signals-catalog.md) — evidence rules
- [focus-rules.md](focus-rules.md) — how one limiter is chosen
- [prescription-logic.md](prescription-logic.md) — what to do next week
- [confidence-scoring.md](confidence-scoring.md) — confidence label semantics
