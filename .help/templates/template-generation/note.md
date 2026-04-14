---
type: note
feature: template-generation
depth: note
generated_at: 2026-04-14T16:03:49.554663+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Note: template generation

## Context

The template generation system creates markdown help files by analyzing feature definitions and source code through AST (Abstract Syntax Tree) inspection. This automated process ensures that documentation stays synchronized with the codebase.

## Template types

The generator recognizes three categories of templates:

- **Core depths**: concept, task, and reference documentation
- **Problem-solving**: error, warning, troubleshooting, and FAQ templates
- **Guidance**: quickstart, tip, note, and comparison templates

## Generation workflow

When you call `generate_feature_templates()`, the system:

1. Analyzes the specified feature's source files using AST inspection
2. Creates `GeneratedTemplate` instances for each template type
3. Returns a `GenerationResult` containing all generated templates and metadata

Each `GeneratedTemplate` tracks the feature name, template depth, file path, and a hash of the source content. The `GenerationResult` aggregates these templates along with the list of source files that were analyzed.

## Source files

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
