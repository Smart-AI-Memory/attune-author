---
type: concept
feature: template-generation
depth: concept
generated_at: 2026-04-14T16:02:22.372661+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Template Generation

Template generation creates markdown help files by analyzing source code and applying predefined templates to feature definitions.

## Core process

The system generates help templates in three stages:

1. **Feature analysis** — Inspects source code using AST parsing to extract classes, functions, and documentation
2. **Template selection** — Chooses appropriate template types based on predefined categories:
   - Core depths: concept, task, reference
   - Problem-solving: error, warning, troubleshooting, FAQ
   - Guidance: quickstart, tip, note, comparison
3. **Content generation** — Renders markdown files using Jinja2 templates populated with the analyzed source data

## Data structures

**`GeneratedTemplate`** represents a single output file with its feature name, template depth, file path, and source hash for tracking changes.

**`GenerationResult`** bundles all templates created for a feature, including the list of source files that were analyzed and matched during generation.

## Integration points

Other parts of the system interact with template generation through the `generate_feature_templates()` function, which accepts a feature definition, target directory, and optional parameters for template depths and file overwriting behavior.
