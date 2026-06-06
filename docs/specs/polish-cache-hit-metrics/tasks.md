# Tasks — Polish prompt-cache hit-rate telemetry

**Status:** ✅ DONE (2026-06-06) — shipped to [Unreleased]. See the
"Deviation" note under Phases 3–4: attune-author has no JSONL
telemetry, so the metric follows the existing in-process
faithfulness-counter pattern (reset at run start, INFO summary at run
end) instead of a new JSONL subsystem. Acceptance criteria in
`decisions.md` are all met.

## Phase 1 — Read the cache fields

- [x] **1.1** Captured via a new `on_cache_usage(creation, read, model)`
      callback on `doc_gen._anthropic.call_anthropic` (polish can't see
      `response.usage` directly — `call_anthropic` returns only text).
      `_log_cache_usage` now returns `(creation, read)`.
- [x] **1.2** Compute hit rate: `read / max(read + creation, 1)`
      (`PolishCacheStats.hit_rate`)
- [x] **1.3** `PolishCacheStats` dataclass added in `polish.py`

## Phase 2 — Surface to user

- [x] **2.1** End-of-run summary logged at INFO via
      `format_polish_cache_summary()`:
      `Polish cache hit: 87% (1241 read / 1421 total tokens, 6 call(s))`
- [x] **2.2** Graceful when both are zero:
      `Polish cache: no cacheable tokens observed (cache not configured?)`

## Phase 3 — Log to telemetry  *(deviation, see note)*

- [x] **3.1** ~~Append per-call to existing telemetry JSONL~~ →
      **There is no telemetry JSONL in attune-author.** Adopted the
      existing in-process counter idiom (`_polish_cache_telemetry()` +
      `reset_polish_cache_telemetry()`, mirroring
      `generator._faithfulness_telemetry`), surfaced via the INFO
      end-of-run summary in `maintenance.py`. Building a JSONL
      subsystem would contradict the spec's "low effort, single file"
      scope and the codebase's telemetry pattern.
- [x] **3.2** Aggregate fields: calls, creation_tokens, read_tokens,
      derived hit_rate, model (model accepted by the callback; per-model
      breakdown explicitly out of scope per decisions.md).

## Phase 4 — Threshold warning  *(deviation: current-run, not cross-run)*

- [x] **4.1–4.3** `format_polish_cache_summary()` appends a `WARNING`
      when the **current run's** hit rate < 50% (`_CACHE_HIT_WARN_THRESHOLD`)
      and ≥1 cacheable token was seen, with a pointer to the README.
      Cross-run rolling history (last N records) is deferred — it would
      require the persistent JSONL layer this spec deliberately avoided.

## Phase 5 — Test

- [x] **5.1** `tests/unit/test_polish_cache_metrics.py`: mocks Anthropic
      responses with known cache_creation/cache_read values; asserts the
      callback fires (incl. the zero case), hit-rate math, accumulator,
      summary line, and threshold warning (16 tests).
- [ ] **5.2** Integration test (optional) — **skipped**: would require a
      live API key (real prompt-cache hits can't be observed against a
      mock). The unit tests cover the compute path; left optional as the
      spec allowed.

## Phase 6 — Docs

- [x] **6.1** README "Cache hit rate" subsection — meaning, healthy
      ranges, what to do when it drops.
- [x] **6.2** CHANGELOG [Unreleased] entry added.

## Out of scope

- Per-stage cache breakdown (system / examples / messages)
- Cost-in-dollars tracking (token-level only)
- Cache strategy changes
- Cross-package telemetry aggregation
