---
feature: polish
depth: concept
generated_at: 2026-06-06T23:19:48.555770+00:00
source_hash: 79da77a01c4b4a11716e33f5673ee64882fe6354c51b6cf999aee80d9dbe4b7e
status: generated
---

# Polish

## How it works

Improve generated template quality with an LLM rewrite pass that uses per-type system prompts and source-grounded summaries
.

The main building blocks are:

- **`PolishError`** — Raised when the polish pass fails in strict mode.
- **`PolishCacheStats`** — Aggregate prompt-cache token usage across polish calls.

Under the hood, this feature spans 2 source
files covering:

- Per-type system prompts and anti-patterns for the polish pass.

## What connects to it

This feature relates to: polish, llm, anthropic, quality.

Other parts of the codebase interact with
polish through these interfaces:

| Interface | Purpose | File |
|-----------|---------|------|
| `PolishError` | Raised when the polish pass fails in strict mode. | `src/attune_author/polish.py` |
| `PolishCacheStats` | Aggregate prompt-cache token usage across polish calls. | `src/attune_author/polish.py` |
