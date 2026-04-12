---
type: concept
feature: template-generation
depth: concept
generated_at: 2026-04-12T04:18:01.441617+00:00
source_hash: fac9c2bf60f422bb00b839a6c2ae022747745371b4a85621dd89daba9515f706
status: generated
---

# Template Generation

Template generation creates markdown help files by analyzing source code and applying Jinja2 templates to feature definitions.

## Process overview

When you run template generation, the system inspects your source code's Abstract Syntax Tree (AST) to extract class and function information, then renders this data through meta-templates to produce structured help documentation.

The `generate_feature_templates()` function orchestrates this process, taking a feature definition and producing markdown files in your specified help directory. You can control which template depths to generate and whether to overwrite existing files.

## Output structure

Template generation produces two types of results:

- **`GeneratedTemplate`** — Represents a single rendered markdown file, containing the template content and metadata about what was generated
- **`GenerationResult`** — Aggregates all templates created for a feature, providing a complete picture of the generation outcome

## Integration points

Other parts of the codebase interact with template generation through these interfaces:

| Interface | Purpose | File |
|-----------|---------|------|
| `GeneratedTemplate` | Result of generating one template file. | `src/attune_author/generator.py` |
| `GenerationResult` | Result of generating templates for a feature. | `src/attune_author/generator.py` |
