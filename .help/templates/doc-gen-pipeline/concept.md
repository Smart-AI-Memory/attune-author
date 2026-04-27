---
type: concept
feature: doc-gen-pipeline
depth: concept
generated_at: 2026-04-26T19:49:52.268283+00:00
source_hash: ed1e0ee4f61601566ddf49801a234a64d93605b2683aafe5ee4f86d48d8dd885
status: generated
---

# Doc Gen Pipeline

A three-stage documentation generation process that creates higher-quality help content by having an LLM plan, write, and polish documentation rather than generating it in a single pass.

## Architecture

The pipeline breaks documentation generation into distinct phases that mirror how human writers work:

1. **Outline** — Analyze source code and create a structured plan
2. **Write** — Generate content section by section following the outline
3. **Review** — Polish the draft for clarity, accuracy, and style

Each stage uses focused prompts and token limits to produce better results than a monolithic "write documentation" approach. The outline stage caps at 1,000 tokens to force concise planning, while writing and review stages get 8,000 tokens each for detailed work.

## Configuration options

| Setting | Default | Purpose |
|---------|---------|---------|
| `doc_type` | `'api-reference'` | Format to generate (API docs, README, tutorial) |
| `audience` | `'developers'` | Target reader level (affects complexity and examples) |
| `model` | `'claude-sonnet-4-20250514'` | LLM model for all stages |
| `sections_per_chunk` | `4` | How many outline sections to write at once |
| `section_focus` | `[]` | Specific sections to prioritize or generate exclusively |

You configure the pipeline through `DocGenConfig`, then call `generate_docs()` with a source file path. The function returns a `DocGenResult` containing the final content plus intermediate artifacts (outline, draft) and metadata about which stages completed successfully.

## Stage breakdown

**Outline stage** (`build_outline`) reads your source code and creates a structured plan showing what sections the documentation needs and what each should cover. This prevents the writing stage from wandering or missing important details.

**Write stage** (`write_content`) generates prose for each section in the outline. It processes sections in chunks (4 by default) to stay within token limits while maintaining context across related sections.

**Review stage** (`review_content`) takes the complete draft and polishes it for clarity, technical accuracy, and style consistency. It can catch issues like unclear explanations, missing context, or inconsistent terminology that emerge when sections are written separately.

## When stages fail

If any stage encounters an error, the pipeline stops and returns what it completed successfully. You get partial results rather than losing all work when one step fails. The `stages_completed` field in `DocGenResult` shows which phases finished so you can resume or debug from the failure point.

The pipeline requires the `attune-author[ai]` extra for Anthropic API access. Without it, `generate_docs()` raises `AnthropicCallError` with installation instructions.
