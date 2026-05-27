# Decisions — Regen / staleness hash mismatch

**Status:** root cause confirmed 2026-05-27 — original hypothesis (budget truncation of hash inputs) was wrong; actual cause is LLM-polished frontmatter laundering. Fix direction concrete. Implementation TBD.
**Owner:** Patrick
**Filed:** 2026-05-25 (handoff from attune-gui Phase 2 blockers; see [attune-gui docs/specs/living-docs-regen-automation/decisions.md](https://github.com/Smart-AI-Memory/attune-gui/blob/main/docs/specs/living-docs-regen-automation/decisions.md#phase-2-blockers-discovered-2026-05-23))

## Root cause (verified 2026-05-27)

The original hypothesis (budget-truncated hash input) was wrong.
`compute_source_hash` is called exactly ONCE at
`generator.py:355` (inside `prepare_polish_phase`) and produces
a deterministic value off the FULL source set. Verified by
calling it twice in a row — idempotent. The `source_hash`
variable flows through to `_render_template` at line 1452
which writes it into the rendered template's frontmatter
correctly.

**The actual bug is in `apply_polish_results` at
`generator.py:468`:**

```python
final_content = polished_by_depth.get(entry.depth, entry.rendered_content)
...
entry.out_path.write_text(final_content, encoding="utf-8")
```

When LLM polish ran, the polished content REPLACES the rendered
template **including the frontmatter the LLM regenerated as part
of its output**. The LLM is given the rendered template (with
correct frontmatter) as input context, polishes the body, and
returns the whole document — but its emitted frontmatter has a
single-character transcription error in the `source_hash` field.

**Reproducible evidence (attune-ai spec-engine, 2026-05-27):**

```
frontmatter source_hash: f8ced22b02899aa25ff409636e659830c6ba856d70de6ddd1a9bf1cbe37a1337
computed source_hash:    f8ced22b02899aa25ff709636e659830c6ba856d70de6ddd1a9bf1cbe37a1337
                                            ^
                                            position 19: f4 vs f7
```

Single-char difference at byte 19 of a 64-char SHA-256 hex
digest. Pure LLM hallucination of the value it was supposed to
echo verbatim. Same `compute_source_hash` function called twice
in the same Python process returns identical values; the
divergence is solely between "what was hashed and written into
the prompt" and "what the LLM emitted as its frontmatter copy."

## Confirmed fix direction

Strip frontmatter from `final_content` after polish and
re-inject the canonical frontmatter from
`entry.rendered_content`. The LLM polishes the BODY; the
frontmatter (especially `source_hash`, `generated_at`,
`feature`, `depth`, `name`) is non-negotiable deterministic
metadata that must survive the polish step exactly.

**Sketch (in `apply_polish_results` around line 468):**

```python
final_content = polished_by_depth.get(entry.depth, entry.rendered_content)
if entry.depth in polished_by_depth:
    # The LLM may have perturbed the frontmatter — re-inject
    # the canonical one from the rendered template.
    final_content = _replace_frontmatter(
        polished_body=final_content,
        canonical_frontmatter=_extract_frontmatter(entry.rendered_content),
    )
```

Where `_extract_frontmatter` returns the `---\n...\n---\n`
prefix from `entry.rendered_content`, and `_replace_frontmatter`
strips whatever frontmatter the LLM produced and prepends the
canonical one. Both can use `_FRONTMATTER_RE` from
`staleness.py` (or a local equivalent).

Even better long-term: send the LLM the body only (strip
frontmatter from its input context), have it return the body
only, and assemble the final document deterministically. Bigger
refactor but eliminates the "did the LLM accidentally edit
metadata" failure mode entirely.

## Problem

Running `attune-author regenerate` writes a new `source_hash` value to a
template's YAML frontmatter, but immediately running `attune-author
regenerate --dry-run` (or `status`) on the same feature **still reports
it as stale**. The loop never reaches a fixed point — every PR using
the new attune-gui CI `fail-if-stale` gate would fail forever.

Discovered while implementing Phase 2 of attune-gui's
`living-docs-regen-automation` spec. Phase 2 (CI fail-if-stale)
is **parked** until this bug is fixed and attune-gui can pin a new
attune-author release.

## Hypothesis

Two different hash *inputs* (not algorithms) are being compared:

- The **staleness check** path (e.g. `attune-author status`, `compute_source_hash` /
  `compute_semantic_hash` in [src/attune_author/staleness.py](../../../src/attune_author/staleness.py))
  hashes the *full* set of source files matched by the feature glob.
- The **regenerate-write** path appears to hash a **budget-truncated** view
  of the same source — evidenced by `ground_truth.budget: dropped X to fit
  budget` log lines emitted during regen. Whatever ends up in the frontmatter's
  `source_hash` field is therefore not the same value the staleness check
  later recomputes from disk.

Two consequences:

1. The frontmatter hash *cannot* match what `status` computes → permanent
   staleness.
2. Even if a contributor regenerates, the `source_hash` in the artifact
   is a hash of "what fit in the LLM context window," which is not a
   semantically useful fingerprint for "is this artifact aligned with
   the source."

## Verification needed

Before designing the fix, confirm the hypothesis:

1. **Reproduce.** On any attune-author-managed corpus with at least one
   feature whose source set exceeds the ground-truth budget:
   ```bash
   attune-author regenerate <feature>
   attune-author status <feature>   # or: attune-author regenerate --dry-run <feature>
   ```
   Expected (after fix): `fresh`. Actual: `stale`.

2. **Trace which hash is written.** Find the code path that produces the
   `source_hash` value written to frontmatter during regen. The hash is
   referenced at:
   - [src/attune_author/generator.py:355](../../../src/attune_author/generator.py#L355) —
     `compute_source_hash(feature, root)` call
   - [src/attune_author/generator.py:1452](../../../src/attune_author/generator.py#L1452) —
     where `source_hash:` is written into the frontmatter string
   - [src/attune_author/staleness.py:211](../../../src/attune_author/staleness.py#L211) —
     `compute_source_hash` definition (delegates to `compute_semantic_hash`
     for pure-Python features)
   Look for any *other* hash computation happening after the budget step
   that might be writing to the same field.

3. **Trace which hash is read.** The status/dry-run path reads from
   frontmatter via `_read_frontmatter_value(text, "source_hash")` in
   [src/attune_author/staleness.py](../../../src/attune_author/staleness.py#L249),
   then compares it against a freshly computed `compute_source_hash` of the
   on-disk source. Confirm both sides use the same definition of "source."

## Fix directions (not yet chosen)

| Option | Pro | Con |
|---|---|---|
| **Always write the full-set hash** to frontmatter (regardless of what the LLM sees). | Single source of truth. Staleness check works against the fingerprint that actually represents the source. | Requires touching whichever step currently overwrites `source_hash` with a budget-truncated value. |
| **Always read the budget-truncated view on the status side** too. | Symmetric. | The budget can change between runs (model swap, prompt edits). Yesterday's hash matches today's source only by coincidence. Worse semantics. |
| **Stop hashing the source in regen entirely**; let the staleness check own the hash. After regen, run staleness check to compute and write. | Conceptually clean. One hash, one writer. | Two-pass write; second pass mutates the just-written file. |

The first option is most likely correct, but step 2 above must confirm
*where* the wrong hash gets written before choosing.

## Out of scope (for this spec)

- Redesigning the ground-truth budget itself.
- Changing what frontmatter fields are written (`source_hash` stays; semantics
  of its value changes).
- attune-gui Phase 2 design refresh — that lives in
  [attune-gui's spec](https://github.com/Smart-AI-Memory/attune-gui/blob/main/docs/specs/living-docs-regen-automation/decisions.md).
  Once this fix lands and attune-gui can pin a new attune-author release,
  Phase 2 will likely switch from `make regen-all && git diff --exit-code`
  to `attune-author status --dry-run` (no `ANTHROPIC_API_KEY` needed in CI,
  resolves the policy conflict noted in PR
  [Smart-AI-Memory/attune-gui#62](https://github.com/Smart-AI-Memory/attune-gui/pull/62)).

## Phase outline (when this spec is approved)

- **Phase 1** — Reproduce the bug in a failing unit test (verification step 1
  above, plus a test in `tests/test_staleness.py` or new file). State the
  expected vs. actual hash values.
- **Phase 2** — Trace and fix. Pick a Fix direction based on Phase 1 findings.
- **Phase 3** — Cut release. Bump attune-author (likely 0.14.1 patch). Update
  attune-gui's dependency pin in `pyproject.toml`. Unblock attune-gui Phase 2.
