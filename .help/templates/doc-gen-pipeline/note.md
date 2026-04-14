---
type: note
feature: doc-gen-pipeline
depth: note
generated_at: 2026-04-14T16:19:38.964605+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Note: doc gen pipeline

## Context

The documentation generation pipeline uses a three-stage approach (outline, write, review) to produce higher-quality help content through planned LLM rewrites rather than single-pass generation.

## Pipeline stages

Each stage calls the Anthropic API with stage-specific prompts and token limits:

1. **Outline stage** (`build_outline()`) — Creates a structured outline from source content, defaulting to 1,000 tokens
2. **Write stage** (`write_content()`) — Generates full documentation content from the outline, defaulting to 8,000 tokens
3. **Review stage** (`review_content()`) — Polishes the draft content, defaulting to 8,000 tokens

You can run the full pipeline with `generate_docs()` or call individual stages directly for more control.

## Configuration and results

`DocGenConfig` controls the pipeline behavior, including document type (defaults to 'api-reference'), target audience (defaults to 'developers'), and the AI model (defaults to 'claude-sonnet-4-20250514'). The `sections_per_chunk` and `section_focus` fields let you process large documents in smaller pieces or emphasize specific sections.

`DocGenResult` captures the pipeline output, storing the final content along with intermediate artifacts (outline and draft) and tracking which stages completed successfully.

## Source files

- `src/attune_author/doc_gen/pipeline.py` — Main orchestration and `generate_docs()` function
- `src/attune_author/doc_gen/stages.py` — Individual stage implementations
- `src/attune_author/doc_gen/config.py` — Configuration dataclass

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
