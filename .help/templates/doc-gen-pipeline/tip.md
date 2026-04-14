---
type: tip
feature: doc-gen-pipeline
depth: tip
generated_at: 2026-04-14T14:14:36.001633+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Use generate_docs() for most documentation tasks

Start with the high-level `generate_docs()` function unless you need fine-grained control over individual stages. This function orchestrates the three-stage pipeline (outline → write → review) and handles configuration automatically.

The individual stage functions (`build_outline()`, `write_content()`, `review_content()`) are useful when you want to inspect intermediate results or when building custom workflows, but they require you to manage the Anthropic client and pass configuration between stages manually.

**Why:** The pipeline's value comes from the multi-stage approach — jumping straight to individual stages usually means you're duplicating orchestration logic that `generate_docs()` already handles.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
