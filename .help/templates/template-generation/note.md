---
type: note
feature: template-generation
depth: note
generated_at: 2026-04-14T13:58:56.643762+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Note: template generation

## Context

The template generation system renders markdown help templates by combining feature definitions with source code AST inspection. It creates structured documentation files based on predefined template types and code analysis.

## Core types

The system defines three categories of template types through module constants:

- **Core depths**: concept, task, and reference templates
- **Problem templates**: error, warning, troubleshooting, and FAQ templates
- **Guidance templates**: quickstart, tip, note, and comparison templates

## Data structures

Template generation uses two main dataclasses to track results:

**GeneratedTemplate** represents a single generated template file with:
- Feature name and template depth
- Output file path and source content hash

**GenerationResult** aggregates the complete generation outcome with:
- Feature name and source hash
- List of all generated templates
- Files that matched the generation criteria

## Generation process

The `generate_feature_templates()` function drives template creation by:
- Accepting a Feature definition and target help directory
- Optionally filtering to specific template depths
- Supporting overwrite control for existing files
- Returning a GenerationResult with all created templates

The function validates feature names and raises `ValueError` for invalid inputs.

## Source files

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
