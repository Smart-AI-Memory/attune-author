---
type: note
feature: doc-gen-pipeline
depth: note
generated_at: 2026-04-11T05:01:44.707092+00:00
source_hash: dcd99211b2080853c45dbe17f061733f0b7ff80387279d574d2bd011d8114aa2
status: generated
---

# Note: doc gen pipeline

## Context

The doc-gen-pipeline implements a three-stage approach to documentation generation: outline, write, and review. This multi-stage process produces higher-quality documentation by breaking the generation task into focused steps rather than attempting to generate complete documentation in a single LLM call.

## Pipeline stages

The pipeline separates documentation generation into three distinct stages:

1. **Outline** (`build_outline()`) — Creates a structured outline based on source content and target document type
2. **Write** (`write_content()`) — Generates documentation content following the outline structure
3. **Review** (`review_content()`) — Reviews and polishes the draft documentation for clarity and accuracy

The `generate_docs()` function orchestrates all three stages automatically, while individual stage functions allow for custom workflows.

## API structure

The pipeline exposes both configuration classes and stage functions:

**Configuration classes:**
- `DocGenConfig` — Pipeline configuration including model settings and output preferences
- `DocGenResult` — Structured result containing generated documentation and metadata

**Stage functions:**
- `generate_docs()` — Main entry point that runs the complete pipeline
- `build_outline()`, `write_content()`, `review_content()` — Individual stage functions
- `parse_outline_sections()` — Utility for extracting section structure from outlines

All stage functions accept common parameters for LLM client configuration, content targeting (document type, audience), and generation limits.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
