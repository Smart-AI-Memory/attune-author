---
type: concept
feature: doc-gen-pipeline
depth: concept
generated_at: 2026-04-14T14:12:55.930928+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Doc Gen Pipeline

A three-stage documentation generation system that uses large language models to create higher-quality help content through outline planning, content writing, and review phases.

## Pipeline architecture

The documentation generation follows a deliberate sequence where each stage builds on the previous one:

1. **Outline stage** — Creates a structured plan using `build_outline()` to define sections and content hierarchy
2. **Write stage** — Generates draft content with `write_content()` based on the approved outline structure
3. **Review stage** — Refines and polishes the draft using `review_content()` for final output quality

You initiate the entire pipeline through `generate_docs()`, which orchestrates these stages and returns a `DocGenResult` containing the outline, draft, and final content.

## Configuration options

`DocGenConfig` controls how the pipeline behaves across all three stages:

- **Document targeting** — Set `doc_type` (like 'api-reference') and `audience` (like 'developers') to shape content style
- **Model selection** — Choose the LLM via the `model` field (defaults to 'claude-sonnet-4-20250514')
- **Token limits** — Control output length separately for each stage with `max_outline_tokens`, `max_write_tokens`, and `max_review_tokens`
- **Content focus** — Use `section_focus` to emphasize specific topics and `sections_per_chunk` to manage processing batches

## Output structure

`DocGenResult` preserves the complete generation history so you can inspect intermediate steps:

- `content` — The final polished documentation
- `outline` — The structural plan from stage one
- `draft` — The raw content from stage two before review
- `stages_completed` — Tracks which pipeline phases finished successfully
- `source_path` — Records the input file or content location

This incremental approach lets you debug generation issues by examining where the pipeline produced unexpected results.
