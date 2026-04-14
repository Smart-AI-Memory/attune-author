---
type: note
feature: polish
depth: note
generated_at: 2026-04-14T14:00:56.978485+00:00
source_hash: cc9d97e96d238e30cf1d9fe96dacf73df94080aa66763e646494a334efc5ce52
status: generated
---

# Note: polish

## Context

The polish feature improves generated documentation templates through an LLM-powered rewriting pass. It uses template-specific system prompts and source code summaries to ensure accuracy while enhancing readability.

## How it works

The polish process operates in two phases:

1. **Source summarization** — `build_source_summary()` extracts key information from the codebase (classes, functions, constants) into a concise format for the LLM prompt
2. **Template rewriting** — `polish_template()` sends the generated template and source summary to an LLM with template-type-specific instructions

The system prompts vary by template type (concept, task, reference, note) and include anti-patterns to avoid formulaic language that commonly appears in auto-generated content.

## Error handling

In strict mode (controlled by the `ATTUNE_AUTHOR_STRICT_POLISH` environment variable), polish failures raise `PolishError` rather than falling back to the unpolished template. This ensures quality gates in CI/CD pipelines.

## Source files

- `src/attune_author/polish.py` — Core polish logic and source summarization
- `src/attune_author/polish_prompts.py` — Template-specific system prompts

**Tags:** `polish`, `llm`, `anthropic`, `quality`
