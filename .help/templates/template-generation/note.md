---
type: note
feature: template-generation
depth: note
generated_at: 2026-04-11T04:47:42.255894+00:00
source_hash: c984ed6eeee4ee72f8b218ec3aebe243eb03ae557e252ba48d52da016704935e
status: generated
---

# Note: template generation

## Context

The template generation feature creates markdown help templates by inspecting feature definitions and source code AST structures. This process transforms code into documentation templates that can be polished into final help content.

## Implementation structure

The feature centers on the `generate_feature_templates()` function, which analyzes source code and produces templates for different documentation types (concepts, tasks, references, and notes).

Two result classes capture the generation output:

- `GeneratedTemplate` — Represents a single generated template file with its content and metadata
- `GenerationResult` — Contains the collection of all templates generated for a feature

The generation process reads feature definitions, inspects source code using AST parsing, and renders Jinja2 templates to produce structured markdown files with consistent frontmatter and section organization.

## Source files

- `src/attune_author/generator.py`
