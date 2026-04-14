---
type: concept
feature: template-generation
depth: concept
generated_at: 2026-04-14T13:57:33.828836+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Template Generation

Template generation creates markdown help files by analyzing source code and applying predefined template structures for different content types.

## How template generation works

When you run template generation, the system inspects your source code's AST (Abstract Syntax Tree) to extract information about classes, functions, and modules. It then uses this data to populate Jinja2 meta-templates, producing structured markdown files for documentation.

The process distinguishes between three categories of templates:

- **Core templates** (`concept`, `task`, `reference`) — foundational documentation types
- **Problem-solving templates** (`error`, `warning`, `troubleshooting`, `faq`) — help users resolve issues
- **Guidance templates** (`quickstart`, `tip`, `note`, `comparison`) — provide additional context and learning aids

## Template generation results

Two data structures capture the outcomes of template generation:

**`GeneratedTemplate`** represents a single generated file and includes:
- The feature name and template depth (like `concept` or `task`)
- The file path where the template was written
- A source hash for tracking changes

**`GenerationResult`** represents the complete output for a feature and contains:
- A list of all generated templates
- The files that matched during source analysis
- An overall source hash for the feature

## Core function

The `generate_feature_templates()` function orchestrates template creation. You provide it with a feature definition, help directory path, and project root, and it returns a `GenerationResult` with details about what was generated. You can optionally specify which template depths to create or whether to overwrite existing files.
