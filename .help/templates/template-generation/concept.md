---
type: concept
feature: template-generation
depth: concept
generated_at: 2026-04-11T04:46:26.557539+00:00
source_hash: c984ed6eeee4ee72f8b218ec3aebe243eb03ae557e252ba48d52da016704935e
status: generated
---

# Template Generation

## How it works

Template generation creates markdown help files by analyzing source code and applying Jinja2 templates to extract documentation from feature definitions and AST inspection.

When you call `generate_feature_templates()`, the system examines your source files to understand the structure of classes, functions, and modules, then renders this information into formatted help templates. You can control which template depths to generate and whether to overwrite existing files.

## Generation workflow

The process produces two types of results:

- **`GeneratedTemplate`** — Contains the rendered content and metadata for a single template file
- **`GenerationResult`** — Aggregates all templates generated for a complete feature, tracking success status and any errors

## Template creation process

Template generation connects to several core systems:

| Component | Role | Location |
|-----------|------|----------|
| `GeneratedTemplate` | Holds individual template output and generation metadata | `src/attune_author/generator.py` |
| `GenerationResult` | Collects all templates for a feature with status tracking | `src/attune_author/generator.py` |

The system relies on AST parsing to extract structural information from Python source files, then applies Jinja2 meta-templates to transform this data into readable documentation.
