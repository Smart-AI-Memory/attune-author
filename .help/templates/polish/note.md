---
type: note
feature: polish
depth: note
generated_at: 2026-04-11T04:49:30.657640+00:00
source_hash: 024a299e9a8252b83e070c5a5297e1292dd243e8eddc631dcf298bae31fb8dc0
status: generated
---

# Note: polish

## Context

The polish feature improves auto-generated help templates through an LLM rewrite pass. It uses template-specific system prompts and source code summaries to produce documentation that follows Google's developer documentation style guide.

## Content

The polish feature provides an LLM-based post-processing step for generated templates. After attune-author generates a help template from source code analysis, the polish pass rewrites the content to improve clarity, structure, and adherence to documentation standards.

The feature centers on the `polish_template()` function, which takes a generated template and returns a polished version. It uses different system prompts based on the template type (concept, task, reference, or note) to ensure appropriate tone and structure for each documentation format.

Supporting functions include:
- `build_source_summary()` — Creates concise summaries of source code structure for the LLM context
- `get_system_prompt()` — Retrieves template-type-specific prompts that guide the rewrite process

The `PolishError` exception handles cases where the LLM fails to produce valid output, particularly when running in strict mode.

## Source files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

**Tags:** `polish`, `llm`, `anthropic`, `quality`
