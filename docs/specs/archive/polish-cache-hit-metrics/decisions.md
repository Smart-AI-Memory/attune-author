# Decisions — Polish prompt-cache hit-rate telemetry

**Status:** ✅ DONE (2026-06-06) — shipped to [Unreleased]. The Draft
"gated on briefing-followup batch" note was superseded by this file's
own "Execution gate" ("Not blocking"). One deviation: attune-author has
no telemetry JSONL, so the metric uses the existing in-process
faithfulness-counter pattern (INFO summary at end of run) rather than a
new JSONL file; the threshold warning is current-run, not cross-run.
See `tasks.md` for the per-phase record.
**Owner:** Patrick

---

## Problem

`attune_author/polish.py` uses Anthropic's prompt caching
(`cache_control`) on its 6000-token system prompt (added in
PR #12). Caching is configured, but we have no visibility into
whether it's actually firing in practice.

When prompt caching works: Anthropic's response usage block
reports `cache_creation_input_tokens` and
`cache_read_input_tokens`. The cache-hit rate = read /
(read + creation).

Today, polish ignores these fields. The cache config could
silently regress (e.g., prompt content changes break the cache
boundary, model alias drift invalidates cached entries) without
anyone noticing.

## Decision

Track prompt-cache hit rate in attune-author's telemetry as a
first-class metric. Surface in:

1. CLI output — print a one-line summary at end of polish run
   ("Cache hit: 87% (1241/1421 tokens)")
2. Telemetry file — append per-run to a structured log
3. Optional periodic report — if telemetry crosses a
   threshold (e.g., <50% hit rate over the last 10 runs),
   warn

## What's in scope

- Read `usage.cache_creation_input_tokens` and
  `usage.cache_read_input_tokens` from Anthropic responses
- Compute hit rate per polish call
- Surface to user + telemetry
- Add a threshold warning

## What's NOT in scope

- Changing the cache strategy itself
- Per-polish-stage breakdown (just whole-call for now)
- Tracking cache costs in dollars (token-level only)

## Alternatives considered

1. **Trust the cache, don't measure** — current state. Real
   risk: silent regression on prompt edits.
2. **Manual periodic check by running polish + grepping
   logs** — works but doesn't surface drift to anyone
   automatically.
3. **Add per-stage cache tracking** (system prompt, examples,
   etc.) — more granular but heavy. Defer to Phase 2.

## Acceptance criteria

- Hit rate computed and printed at end of every polish run
- Per-run hit rate logged to telemetry
- Documentation in attune-author README explaining what the
  metric means
- One test exercising the hit-rate compute path against a
  mocked Anthropic response

## Effort

Low. Single file change in `polish.py`, small telemetry
addition, one test. ~1-2 hours.

## Execution gate

Not blocking. Spec approved when this PR merges; execution can
happen whenever someone has bandwidth (probably alongside the
next attune-author feature work).

---

(per-phase decisions appended as work happens)
