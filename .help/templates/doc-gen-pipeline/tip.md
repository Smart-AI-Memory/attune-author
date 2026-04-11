---
type: tip
feature: doc-gen-pipeline
depth: tip
generated_at: 2026-04-11T05:01:39.561154+00:00
source_hash: dcd99211b2080853c45dbe17f061733f0b7ff80387279d574d2bd011d8114aa2
status: generated
---

# Tip: working effectively with doc gen pipeline

## Start with `generate_docs()` for complete documentation workflows

Call `generate_docs()` instead of the individual stage functions (`build_outline()`, `write_content()`, `review_content()`) unless you need to inspect or modify intermediate outputs. The pipeline orchestrates all three stages automatically and handles error propagation between them.

The stage functions are useful when you want to debug a specific phase or implement custom review logic, but they require you to manage the data flow manually.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
