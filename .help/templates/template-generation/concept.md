---
type: concept
feature: template-generation
depth: concept
generated_at: 2026-04-26T19:46:21.981322+00:00
source_hash: e3ad2679109ec5bb81db1607254855a0f32feadedbce291531797eb11bf09912
status: generated
---

# Template Generation

Template generation creates markdown help files from feature definitions and source code analysis. Instead of writing documentation manually, you define a feature and the system inspects your code to generate structured templates automatically.

## How the generation process works

The system takes a feature name, analyzes the corresponding source files, and creates multiple template types (concept, task, reference, quickstart) from the same code. Each template serves a different reader need while staying synchronized with the actual implementation.

The generation pipeline follows these steps:

1. **Feature lookup** — Maps the feature name to source files in your project
2. **AST inspection** — Parses Python files to extract classes, functions, and docstrings
3. **Template rendering** — Uses Jinja2 templates to transform code analysis into structured markdown
4. **Multi-depth output** — Creates concept, task, and reference versions with appropriate detail levels

## Core data structures

**`GeneratedTemplate`** represents one output file:
- `feature` — The feature name this template documents
- `depth` — Template type (concept, task, reference, quickstart)
- `path` — Where the generated file was written
- `source_hash` — Checksum for detecting when source code changes

**`GenerationResult`** represents the complete output for a feature:
- `feature` — The feature being documented
- `templates` — List of all generated template files
- `source_hash` — Combined checksum of all source files
- `matched_files` — Which source files contributed to the generation

## Template categories by purpose

The generator creates templates in four categories:

| Category | Template types | When to generate |
|----------|---------------|------------------|
| **Core depth** | concept, task, reference | Every feature gets these three |
| **Problem-solving** | error, warning, troubleshooting, faq | When code handles specific error cases |
| **Guidance** | quickstart, tip, note, comparison | For features with multiple approaches |
| **Project docs** | how-to, tutorial, cli-reference, architecture | Project-wide documentation needs |

Most features start with the core depth templates. The generator analyzes your code to determine which additional categories apply.

## Generation control

The `generate_feature_templates` function accepts these parameters:

- `depths` — Which template types to create (defaults to concept, task, reference)
- `overwrite` — Whether to replace existing templates
- `use_rag` — Whether to incorporate context from existing documentation

The function raises `ValueError` for invalid feature names that don't map to any source files.
