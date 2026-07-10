---
type: concept
name: polish-concept
feature: polish
depth: concept
generated_at: 2026-07-10T13:05:53.031192+00:00
source_hash: cee35117856c8654705dabf8225b46da419f67a138180fcc5b5a7008b62e2cd0
status: generated
scaffold_hash: bb1bf50947c02598b6024d4c333703f1289048360e75e67ded12a2310168a2de
---

# Polish

The polish pass is an LLM rewrite step that improves auto-generated
help templates before you publish them. It takes a rough draft, a
source-grounded summary of the code the template describes, and a
per-type system prompt, and returns cleaner markdown that stays
faithful to the source.

## How it works

The flow has three stages:

1. **Summarize the source.** `build_source_summary` condenses public
   classes, functions, module docstrings, and signatures into a
   compact ground-truth block. This is what keeps the LLM from
   inventing APIs — it can only reference what appears in the
   summary.
2. **Build the prompt.** `build_polish_prompt` pairs that summary
   with a system prompt from `get_system_prompt`, which selects
   rules and anti-patterns specific to the template type (a concept
   gets different guidance than an error template).
3. **Call the model.** `polish_template` sends the prompt and
   returns the rewritten markdown. Results are cached on disk, so
   re-running the pass over unchanged templates is cheap.

Two failure modes matter:

- In strict mode — enabled per call via the `strict` parameter or
  process-wide through the `STRICT_ENV_VAR` environment variable
  (`ATTUNE_AUTHOR_STRICT_POLISH`) — a failed polish raises
  `PolishError` instead of falling back to the unpolished draft.
- Cache behavior is observable: `PolishCacheStats` aggregates
  prompt-cache token usage (`calls`, `creation_tokens`,
  `read_tokens`) and exposes `total_tokens` and `hit_rate`. You can
  snapshot it with `polish_cache_stats()`, print an end-of-run
  summary with `format_polish_cache_summary()`, or reset counters
  with `reset_polish_cache_telemetry()`. `clear_cache()` deletes
  every cached entry and returns the count removed.

The implementation spans two modules: `attune_author.polish` (the
pass itself, caching, and telemetry) and
`attune_author.polish_prompts` (per-type system prompts and
anti-patterns).

## Connection points

Callers interact with polish through a small public surface:

| Interface | Purpose | File |
|-----------|---------|------|
| `polish_template` | Polish one generated template; the main entry point | `src/attune_author/polish.py` |
| `build_source_summary` | Produce the ground-truth summary fed into the prompt | `src/attune_author/polish.py` |
| `PolishError` | Raised when the polish pass fails in strict mode | `src/attune_author/polish.py` |
| `PolishCacheStats` | Aggregate prompt-cache token usage across polish calls | `src/attune_author/polish.py` |
| `get_system_prompt` | Select the per-type system prompt for a polish call | `src/attune_author/polish_prompts.py` |

If you're generating templates, you typically call
`build_source_summary` once per feature, then `polish_template` per
draft, and read `format_polish_cache_summary()` at the end of the
run to see how much the cache saved.
