# Rule Changes Changelog

Log every change to decision-engine rules, thresholds, scenario files, or validation expectations.

Format:

```
## YYYY-MM-DD — Short title
**Changed:** files or rules
**Reason:** why
**Scenarios re-tested:** V1–V6 results
**Notes:** any follow-up
```

---

## 2026-06-05 — Initial validation documentation

**Changed:** Created `docs/` validation and decision-engine documentation.

**Reason:** Document current engine behaviour and establish 6/6 scenario validation gate before beta.

**Scenarios tested (engine as shipped, no code changes):**

| Scenario | Expected | Actual | Result |
|----------|----------|--------|--------|
| V1 Inconsistent | `consistency` | `consistency` | PASS |
| V2 Low volume | `volume` | `volume` | PASS |
| V3 Too much intensity | `aerobic_support` | `long_run` | FAIL |
| V4 High volume no quality | `quality` | `long_run` | FAIL |
| V5 Structured plateau | `progression` | `long_run` | FAIL |
| V6 Declining load | `load_stability` | — | NOT CREATED |

**Root cause identified:** Demo CSVs use `long` and `interval` workout labels. Metrics engine counts only `long run` and `vo2`. `choose_primary_limiter()` gate 5 (`long_runs_last_28 == 0`) intercepts before intended limiters.

**Planned fixes (not implemented yet):**

1. Alias normalisation in `data_loader.py`: `long` → `long run`, `interval`/`intervals` → `vo2`, `tempo` → `threshold`
2. Update demo CSV labels to canonical vocabulary
3. Create `data/declining_load.csv` for V6
4. Add `tests/test_demo_scenarios.py`

**Notes:** V2 passes on primary limiter but emits false "No long run stimulus" signal until aliases fixed.

---

## Template for future entries

```markdown
## YYYY-MM-DD — Title

**Changed:** 
**Reason:** 
**Scenarios re-tested:** 
| Scenario | Expected | Actual | Result |
|----------|----------|--------|--------|
| V1 | | | |
...

**Notes:**
```
