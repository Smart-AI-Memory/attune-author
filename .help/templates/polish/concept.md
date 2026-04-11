---
type: concept
feature: polish
depth: concept
generated_at: 2026-04-11T04:48:02.490984+00:00
source_hash: 024a299e9a8252b83e070c5a5297e1292dd243e8eddc631dcf298bae31fb8dc0
status: generated
---

# Polish

The polish feature refines auto-generated help templates through an LLM rewrite pass that applies template-specific style rules and grounds improvements in actual source code.

## Core components

**PolishError** — Exception raised when the polish operation fails in strict mode, allowing you to enforce quality standards.

**Template polishing** — The `polish_template` function takes a raw generated template and rewrites it using specialized prompts for each template type (concept, guide, reference).

**Source summarization** — The system builds concise summaries from your codebase's public classes, functions, and docstrings to ensure polished templates stay accurate to the actual implementation.

## System prompt customization

Each template type gets its own system prompt through `get_system_prompt`. For example, concept templates receive instructions to lead with clear definitions and use noun phrases for headings, while other template types get different style guidance.

The prompts include anti-patterns—specific phrases like "manages core functionality" that the LLM should avoid because they sound formulaic.

## Quality enforcement

You can run polish in strict mode to catch cases where the LLM fails to improve a template. When strict mode is enabled, `PolishError` gets raised if the polish operation doesn't succeed, letting you maintain consistent documentation quality across your project.
