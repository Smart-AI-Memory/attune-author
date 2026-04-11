---
type: error
feature: doc-gen-pipeline
depth: error
generated_at: 2026-04-11T05:00:38.136729+00:00
source_hash: dcd99211b2080853c45dbe17f061733f0b7ff80387279d574d2bd011d8114aa2
status: generated
---

# Doc Gen Pipeline errors

The doc gen pipeline orchestrates three-stage documentation generation (outline, write, review) using LLM calls. Failures typically occur during API communication, content parsing, or configuration validation.

## Common error signatures

- **`ValueError: Invalid doc_type`** — Unsupported document type passed to generation stages
- **`FileNotFoundError`** — Target source file doesn't exist when calling `generate_docs()`
- **`KeyError`** — Missing required fields in `DocGenConfig` or malformed outline parsing
- **`ConnectionError`** — LLM client API failures during `build_outline()`, `write_content()`, or `review_content()`
- **`TypeError: Expected DocGenConfig`** — Invalid configuration object passed to pipeline functions

## Where errors originate

Pipeline failures typically start at these entry points:

- `generate_docs()` in `src/attune_author/doc_gen/pipeline.py` — Main orchestrator that validates inputs and coordinates all three stages
- `build_outline()` in `src/attune_author/doc_gen/stages.py` — First stage that creates document structure from source content
- `write_content()` in `src/attune_author/doc_gen/stages.py` — Second stage that generates content from the outline
- `review_content()` in `src/attune_author/doc_gen/stages.py` — Final stage that polishes the draft
- `parse_outline_sections()` in `src/attune_author/doc_gen/stages.py` — Utility that extracts section headers for content generation

## How to diagnose

1. **Check the stage where failure occurred.** Look at the function name in your traceback:
   - `generate_docs()` failures often indicate file access or configuration problems
   - `build_outline()` failures suggest LLM API issues or invalid source content
   - `write_content()` failures typically mean outline parsing problems or API limits
   - `review_content()` failures point to draft format issues or token limits

2. **Validate your configuration.** Ensure `DocGenConfig` has all required fields (doc_type, audience, model, max_tokens) and that the LLM client is properly initialized.

3. **Examine the input content.** Large source files may exceed token limits, and empty or malformed source content can cause outline generation to fail.

4. **Test individual stages.** Run `build_outline()`, `write_content()`, and `review_content()` separately with the same inputs to isolate which stage is failing.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
