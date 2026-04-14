---
type: concept
feature: doc-gen-pipeline
depth: concept
generated_at: 2026-04-14T16:17:53.986879+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Doc Gen Pipeline

## How it works

The doc gen pipeline transforms source code into polished documentation through three sequential AI-powered stages: outline generation, content writing, and review.

Instead of generating documentation in a single step, this pipeline breaks the process into focused phases. First, `build_outline` creates a structured plan for the documentation. Then `write_content` expands that outline into full prose, optionally focusing on specific sections. Finally, `review_content` polishes the draft for clarity and consistency.

You configure the pipeline through `DocGenConfig`, which lets you specify the target audience (like "developers"), document type (like "api-reference"), and token limits for each stage. The pipeline tracks its progress in `DocGenResult`, recording the content from each stage and which stages completed successfully.

## Core components

**`DocGenConfig`** stores your pipeline preferences, including the AI model to use (`claude-sonnet-4-20250514` by default), maximum tokens per stage, and how many outline sections to process in each writing chunk.

**`DocGenResult`** captures everything the pipeline produces: the final content, intermediate outline and draft versions, completed stages, and the original source file path.

**Stage functions** handle the AI interactions:
- `build_outline` analyzes source code and creates a documentation structure
- `write_content` converts outline sections into readable prose
- `review_content` refines the draft for publication quality

## Integration points

You start the pipeline by calling `generate_docs()` with a source file path and optional configuration. The function coordinates all three stages and returns a complete `DocGenResult`.

The pipeline requires the Anthropic AI library — if it's not installed, you'll get an `AnthropicCallError` with installation instructions for the `attune-author[ai]` extra.
