# RAG Evaluation Baselines — attune-author v0.3.9

> ⚠️ **PENDING RE-MEASURE (2026-06-04).** The question set's ground-truth
> answers were refreshed against current code (v0.14.2) — see
> `specs/rag-gate-accuracy-baseline/`. The numbers in this file were measured
> against the *stale* v0.3.9 ground truth and are **superseded**: a treated
> answer that is correct against current code was previously graded "partial"
> against the old ground truth, so the strict-accuracy figures below understate
> current quality. **Re-run `make eval` (full 25 × 2 models, ~$3–8) to
> regenerate this table**, then drop this banner and update the header version.

Measured scores from `benchmarks/hallucination-v0.3.9/` used to ground the
thresholds in `eval_config.yaml`. Run `make eval` to regenerate.

## Score Summary

25 questions × 2 models × 2 conditions = 100 entries (99 valid; 1 judge error).

| Model  | Condition | Faithfulness     | Strict Accuracy  |
| :----- | :-------- | :--------------- | :--------------- |
| sonnet | baseline  | 92.0% (23/25)    | 24.0% (6/25)     |
| sonnet | treated   | 100.0% (24/24) † | 100.0% (24/24) † |
| opus   | baseline  | 92.0% (23/25)    | 36.0% (9/25)     |
| opus   | treated   | 100.0% (25/25)   | 100.0% (25/25)   |

† `q30|sonnet|treated` has verdict=`error` (judge JSON parse failure on a
  non-JSON response). Excluded from treated totals; 24 valid entries used.

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
