---
type: concept
feature: doc-gen-pipeline
depth: concept
generated_at: 2026-04-12T04:20:55.484949+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Doc Gen Pipeline

## How it works

The doc gen pipeline is a three-stage system that generates documentation by having an LLM first create an outline, then write content from that outline, and finally review and polish the result.

Each stage builds on the previous one:

1. **Outline stage** — `build_outline()` analyzes your source content and creates a structured plan for the documentation
2. **Writing stage** — `write_content()` uses the outline to generate draft documentation, optionally focusing on specific sections
3. **Review stage** — `review_content()` polishes the draft by checking it against the original source

You control the entire process through `generate_docs()`, which orchestrates all three stages and returns a `DocGenResult` with the final documentation.

## Configuration and results

**`DocGenConfig`** holds your pipeline settings, including the target audience, document type, and LLM parameters like model choice and token limits.

**`DocGenResult`** contains the generated documentation along with metadata about the generation process.

The pipeline can parse outline sections with `parse_outline_sections()` to enable focused writing on specific parts of your documentation.

## Integration points

Other parts of the codebase interact with the doc gen pipeline through these interfaces:

| Interface | Purpose | File |
|-----------|---------|------|
| `DocGenResult` | Result of document generation. | `src/attune_author/doc_gen/pipeline.py` |
| `DocGenConfig` | Configuration for the document generation pipeline. | `src/attune_author/doc_gen/config.py` |
