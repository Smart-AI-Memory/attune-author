---
type: tip
feature: template-generation
depth: tip
generated_at: 2026-04-11T04:47:36.270039+00:00
source_hash: c984ed6eeee4ee72f8b218ec3aebe243eb03ae557e252ba48d52da016704935e
status: generated
---

# Use `generate_feature_templates()` as your starting point

Start with `generate_feature_templates()` when you need to create help documentation from code. This function handles the complete workflow from feature definition to rendered markdown templates, including file organization and conflict detection.

## Why this works

The function encapsulates the complexity of AST inspection, template selection, and file management in a single call. Trying to orchestrate these steps manually leads to inconsistent outputs and missed edge cases that the main function already handles.

## The tradeoff

You get less control over individual template generation steps. If you need to customize how specific templates are rendered or where they're written, you'll need to work with the `GeneratedTemplate` and `GenerationResult` classes directly.

## Source files

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
