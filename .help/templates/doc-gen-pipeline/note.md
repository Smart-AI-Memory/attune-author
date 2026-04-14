---
type: note
feature: doc-gen-pipeline
depth: note
generated_at: 2026-04-14T14:14:42.151122+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Note: doc gen pipeline

## Context

The doc gen pipeline implements a three-stage approach to documentation generation: outline, write, and review. This multi-stage design produces higher-quality help output by breaking LLM work into focused, planned steps rather than generating documentation in a single pass.

## Pipeline structure

The pipeline centers around two main data classes:

- `DocGenResult` — Captures the output of each generation stage, including the final content, intermediate outline and draft, completed stages list, and source file path
- `DocGenConfig` — Controls pipeline behavior through settings like document type (defaults to "api-reference"), target audience ("developers"), AI model selection, and token limits for each stage

The generation process flows through three functions that correspond to the pipeline stages:

1. `build_outline()` — Creates a structured documentation plan from source content
2. `write_content()` — Generates draft documentation following the outline, with optional section focus
3. `review_content()` — Polishes the draft for clarity and completeness

You can run the full pipeline through `generate_docs()`, which orchestrates all stages and returns a `DocGenResult`, or call individual stage functions for more granular control.

The pipeline requires the Anthropic AI dependency. If you encounter an `AnthropicCallError`, install it with `pip install 'attune-author[ai]'`.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
