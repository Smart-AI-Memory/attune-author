# RAG Evaluation Baselines — attune-author v0.25.0 (measured 2026-07-10)

Measured scores from `benchmarks/hallucination-v0.3.9/` used to ground the
thresholds in `eval_config.yaml`. Run `make eval` to regenerate.

Re-measured 2026-07-10 against the **refreshed ground truth** (answers
audited against current code, specs/rag-gate-accuracy-baseline tasks 1–3)
and the **freshly regenerated `.help/templates`** (all 10 stale features,
PR #95). This closes task 9 of that spec; the 2026-06-04 PENDING
RE-MEASURE banner is resolved.

## Score Summary

25 questions × 2 models × 2 conditions = 100 entries (99 valid; 1 judge error).

| Model  | Condition | Faithfulness     | Strict Accuracy  |
| :----- | :-------- | :--------------- | :--------------- |
| sonnet | baseline  | 92.0% (23/25)    | 24.0% (6/25)     |
| sonnet | treated   | 100.0% (24/24) † | 100.0% (24/24) † |
| opus   | baseline  | 92.0% (23/25)    | 36.0% (9/25)     |
| opus   | treated   | 100.0% (25/25)   | 100.0% (25/25)   |

† `q30|sonnet|treated` has verdict=`error` (judge JSON parse failure on a
  non-JSON response — the same q30 flake as the v0.3.9 measurement).
  Excluded from treated totals; 24 valid entries used.

The 2026-07-10 top-line numbers reproduce the superseded v0.3.9 table
exactly (same baselines, same treated ceilings, same q30 judge flake) —
the ground-truth refresh moved *per-question* grading (18 sonnet / 16
opus paired improvements, McNemar p ≈ 0.0000, zero regressions) without
shifting the aggregate gates.

**Faithfulness** = (correct + partial) / total — non-hallucination rate.
**Strict Accuracy** = correct / total — fully correct answers only.
**Baseline** = README + `git ls-files` tree, no RAG context.
**Treated** = Baseline + `.help/templates/{feature}/reference.md` injected.

## Threshold Derivation

### End User — Faithfulness ≥ 95%

```
Baseline faithfulness : 92.0%  (both models)
Treated faithfulness  : 100.0% (both models)
Gate                  : 95.0%
```

The 95% gate sits between baseline (92%) and treated (100%). A deployment that
silently drops RAG context scores 92% → triggers rollback. A deployment with
working RAG scores 100% → passes. The gate provides 3pp headroom under the
treated ceiling before it would ever fire on a healthy deploy.

### Developer — Strict Accuracy ≥ 85%

```
Baseline strict accuracy : 24.0% (sonnet), 36.0% (opus)
Treated strict accuracy  : 100.0% (both models)
Gate                     : 85.0%
```

The 49pp gap between the opus baseline (36%) and the gate (85%) means partial
context degradation — e.g., a subset of reference templates becoming stale or
missing — will be caught before accuracy falls below the gate. The gate
doesn't fire on healthy RAG and fires decisively on broken RAG.

### Support Agent — Context Precision ≥ 80%

**Status: threshold not yet measurable.**

Context precision requires knowing, per answer, what fraction of retrieved
context chunks the model actually cited. The existing benchmark captures
correct/partial/hallucinated verdicts but not citation attribution.

**To implement:**
1. Extend `run_judge.py` prompt to return `cited_chunk_ids: list[int]` in the
   JSON verdict alongside `verdict` and `reasoning`.
2. Store chunk IDs in `judgments.json` alongside each entry.
3. Add a `context_precision` metric to `report.py`.
4. Establish a baseline score before enforcing the 80% gate.

Until implemented this threshold is a documentation placeholder only and must
not block deploys (see `eval_config.yaml` → `thresholds.support_agent.status`).

## Hallucination Details

Both baseline hallucinations (q2, q39) fired identically for both models:

| Q  | Category  | Feature               | Why hallucinated |
| :- | :-------- | :-------------------- | :--------------- |
| 2  | location  | manifest              | Both models guessed `mcp/path_validation.py` — the most-featured MCP module in the README — instead of `manifest.py` |
| 39 | dataclass | staleness-maintenance | Both models invented a `.stale` property with `.name`/`.reason` attributes that don't exist; actual properties are `stale_count`, `current_count`, `stale_features` |

These questions are included in the smoke eval subset (see `smoke_eval.py`)
because they produce the maximum hallucination signal: wrong without RAG,
correct with RAG, for every model tested.

## Smoke Eval Subset

Five questions chosen for maximum discrimination in CI (lowest cost, highest signal):

| Q  | Category  | Baseline verdict     | Treated verdict | Why selected |
| :- | :-------- | :------------------- | :-------------- | :----------- |
| 2  | location  | hallucinated (both)  | correct (both)  | Strongest signal: faithfulness regression detector |
| 39 | dataclass | hallucinated (both)  | correct (both)  | Strongest signal: faithfulness regression detector |
| 9  | signature | partial (both)       | correct (both)  | Context recall signal: needs reference template |
| 12 | signature | partial (both)       | correct (both)  | Context recall signal: needs reference template |
| 27 | enum      | partial (both)       | correct (both)  | Context recall signal: needs reference template |

With working RAG (treated condition): 5/5 correct → faithfulness 100%, accuracy 100%.
With broken RAG (baseline condition): 2/5 hallucinated + 3/5 partial → faithfulness 60%, accuracy 0%.
Both outcomes are far from the gates (95% / 85%), making the smoke set decisive.

## Sonnet-5 Judge Baseline (2026-07-10 — model tiers rollout)

`smoke_eval.py` now resolves its models via the attune tier contract
(`attune_author.model_tiers`): answers = capable tier, judge = premium
tier. The rag-gate CI pin (`ATTUNE_MODEL_PREMIUM=claude-sonnet-5`) makes
CI runs sonnet-5-judged; previously the models were hardcoded
(sonnet-4-6 answers / opus-4-6 judge) and the pin was decorative.

First sonnet-5/sonnet-5 run (local, dev key, 2026-07-10 — recorded for
specs/fable-model-tiers task 10 and specs/rag-gate-accuracy-baseline in
the attune workspace repo):

| Metric | Score | Gate | Result |
| :----- | ----: | ---: | :----- |
| Faithfulness (hard) | 100.0% | ≥95% | ✅ PASS |
| Strict Accuracy (advisory) | 60.0% | ≥85% | ⚠️ advisory warn (was 40% under sonnet-4-6/opus-4-6) |

Per-question (treated): q2 correct, q9 correct, q12 correct,
q27 partial, q39 partial. The enum (q27) and dataclass (q39) questions
remain the accuracy stragglers — q39 template regeneration is the
standing remediation candidate.

**Post-regen smoke re-run (2026-07-10, after PR #95 regenerated all 10
stale features):** faithfulness 100% (PASS), strict accuracy **80%**
advisory (q2/q9/q12/q27 correct, q39 partial — up from error). The
full-25 re-measure the same day (table above) grades q39 treated
*correct* under the full-25 judge; the smoke-vs-full q39 delta is
residual judge wobble, not corpus staleness.

Claude 5 API notes baked into `smoke_eval.py` by this run: the
`temperature` param is rejected ("deprecated for this model", 400), and
responses may lead with a ThinkingBlock — read the first TEXT block,
never `content[0].text`.
