---
type: faq
feature: doc-gen-pipeline
depth: faq
generated_at: 2026-04-11T05:01:22.477846+00:00
source_hash: dcd99211b2080853c45dbe17f061733f0b7ff80387279d574d2bd011d8114aa2
status: generated
---

# Doc Gen Pipeline FAQ

## What is the doc gen pipeline?

A three-stage documentation generator that creates higher-quality output by breaking the process into outline, write, and review phases.

## When should I use the doc gen pipeline?

Use it when you need structured, high-quality documentation generated from source code or content. The three-stage approach produces better results than single-pass generation, especially for complex documentation types.

## What's the main entry point?

Start with `generate_docs()` — it orchestrates the entire pipeline and handles configuration automatically. If you need more control over individual stages, use:

- `build_outline()` to create a structured outline first
- `write_content()` to generate content from an existing outline
- `review_content()` to polish draft documentation

## How do I configure the pipeline?

Pass a `DocGenConfig` object to `generate_docs()`, or let it use defaults. The config controls document type, target audience, AI model selection, and output limits.

## What does each stage do?

- **Outline stage**: Analyzes your source content and creates a structured documentation plan
- **Write stage**: Generates full content following the outline structure
- **Review stage**: Polishes the draft for clarity, accuracy, and style

## How do I debug pipeline issues?

Run `pytest -k "doc-gen-pipeline" -v` to check if the core functionality works. If tests pass but your code fails, add debug logging at the problem point and check the `DocGenResult` object for stage-specific error details.

## Where are the source files?

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
