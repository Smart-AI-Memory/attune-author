---
type: concept
feature: polish
depth: concept
generated_at: 2026-04-14T13:59:21.756891+00:00
source_hash: cc9d97e96d238e30cf1d9fe96dacf73df94080aa66763e646494a334efc5ce52
status: generated
---

# Polish

Polish is an LLM-powered refinement system that transforms auto-generated help templates into polished documentation following Google's style guide.

## How it works

The polish feature takes raw generated templates and improves them through a structured LLM pass. It uses template-specific system prompts that include rules for different documentation types (concept, reference, tutorial) and common anti-patterns to avoid.

The system builds a source summary from your codebase's public classes, functions, and module docstrings, then sends both the draft template and this context to an LLM for rewriting. This ensures the polished output stays accurate to your actual code while improving readability and structure.

## Core components

- **`polish_template()`** — The main entry point that coordinates the LLM rewrite process
- **`build_source_summary()`** — Extracts key information from your codebase to ground the LLM's output
- **`get_system_prompt()`** — Selects template-specific writing rules and style guidelines
- **`PolishError`** — Signals when the polish pass fails in strict mode

## Error handling

The polish feature can operate in strict mode (controlled by the `ATTUNE_AUTHOR_STRICT_POLISH` environment variable). When enabled, LLM failures raise `PolishError` exceptions rather than falling back gracefully. This helps catch quality issues during development while allowing more resilient behavior in production.
