---
type: concept
feature: doc-gen-pipeline
depth: concept
generated_at: 2026-04-11T05:00:10.627990+00:00
source_hash: dcd99211b2080853c45dbe17f061733f0b7ff80387279d574d2bd011d8114aa2
status: generated
---

# Doc Gen Pipeline

## How it works

The doc gen pipeline orchestrates a three-stage process for creating documentation: outline, write, and review. Instead of generating documentation in a single pass, this approach breaks the work into deliberate phases that produce higher-quality output.

Here's how the stages connect:

1. **Outline stage** — `build_outline()` analyzes your source content and creates a structured plan that defines what sections the documentation should cover
2. **Write stage** — `write_content()` takes that outline and fills in each section with actual documentation content
3. **Review stage** — `review_content()` polishes the draft by checking for clarity, completeness, and consistency

You start the entire process with `generate_docs()`, which accepts a target file or content string and runs it through all three stages automatically.

## Core components

**`DocGenConfig`** controls pipeline behavior like which LLM model to use, token limits, target audience, and documentation type. You can pass a custom config to `generate_docs()` or let it use sensible defaults.

**`DocGenResult`** contains the final documentation along with any metadata about the generation process. This gives you both the output and information about how it was created.

The pipeline also includes `parse_outline_sections()` to extract section titles from outlines, which helps coordinate the writing stage's focus on specific parts of the documentation.

## Integration points

Other parts of the codebase interact with the doc gen pipeline through these interfaces:

| Interface | Purpose | File |
|-----------|---------|------|
| `DocGenResult` | Result of document generation. | `src/attune_author/doc_gen/pipeline.py` |
| `DocGenConfig` | Configuration for the document generation pipeline. | `src/attune_author/doc_gen/config.py` |
