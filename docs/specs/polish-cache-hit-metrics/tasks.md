# Tasks — Polish prompt-cache hit-rate telemetry

## Phase 1 — Read the cache fields

- [ ] **1.1** In `attune_author/polish.py`, capture
      `response.usage.cache_creation_input_tokens` and
      `response.usage.cache_read_input_tokens` from each
      Anthropic API call
- [ ] **1.2** Compute hit rate:
      `read / max(read + creation, 1)`
- [ ] **1.3** Add a `PolishCacheStats` dataclass for
      structured passing

## Phase 2 — Surface to user

- [ ] **2.1** Print a one-line summary at end of polish run:
      `Polish complete · cache hit: 87% (1241 read / 1421 total tokens)`
- [ ] **2.2** Format gracefully when both are zero (no cache
      configured)

## Phase 3 — Log to telemetry

- [ ] **3.1** Append per-call to existing telemetry JSONL
      (wherever attune-author writes telemetry)
- [ ] **3.2** Fields: timestamp, model, hit_rate,
      read_tokens, creation_tokens, polish_target

## Phase 4 — Threshold warning

- [ ] **4.1** When invoked, read last N (e.g., 10) telemetry
      records
- [ ] **4.2** Compute rolling mean hit rate
- [ ] **4.3** If <50%, print a warning at end of run with
      pointer to docs

## Phase 5 — Test

- [ ] **5.1** Unit test: mock an Anthropic response with known
      cache_creation / cache_read values; assert hit rate
      computed correctly
- [ ] **5.2** Integration test (optional): run polish twice
      back-to-back; second run should report >0% cache hit

## Phase 6 — Docs

- [ ] **6.1** README section: "Cache hit rate" — what it means,
      what good values look like, what to do if it drops
- [ ] **6.2** Link from CHANGELOG when feature ships

## Out of scope

- Per-stage cache breakdown (system / examples / messages)
- Cost-in-dollars tracking (token-level only)
- Cache strategy changes
- Cross-package telemetry aggregation
