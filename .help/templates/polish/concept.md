---
type: concept
feature: polish
depth: concept
generated_at: 2026-04-14T16:04:11.762604+00:00
source_hash: 39a4215a31cf6bfa17f5b898ad071827d406cbe4dc8d2744f17fe7fd680d6891
status: generated
---

# Polish

## How it works

The polish feature improves auto-generated help templates by passing them through an LLM with template-specific editing instructions.

When you call `polish_template()`, the system builds a source summary from your codebase information and combines it with a template-type-specific system prompt. For example, concept templates get instructions to lead with clear definitions and use concrete examples, while troubleshooting templates get guidance on structuring diagnostic steps.

The LLM receives both the original template and a summary of the actual source code (classes, functions, docstrings) to ensure accuracy. In strict mode, the function raises `PolishError` if the polish pass fails, giving you control over whether to fall back to unpolished content.

## Core components

- **`polish_template()`** — Main entry point that orchestrates the LLM polish pass for a given template and feature
- **`get_system_prompt()`** — Retrieves editing instructions tailored to specific template types (concept, troubleshooting, etc.)
- **`build_source_summary()`** — Creates concise summaries of your source code to ground the LLM's editing decisions
- **`PolishError`** — Exception raised when polish fails in strict mode

## Configuration

You can control polish behavior through the `ATTUNE_AUTHOR_STRICT_POLISH` environment variable. When enabled, polish failures raise exceptions instead of silently continuing with unpolished templates.
