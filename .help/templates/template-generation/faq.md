---
type: faq
feature: template-generation
depth: faq
generated_at: 2026-04-14T13:58:35.456509+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Template Generation FAQ

## What is template generation?

Template generation creates markdown help files from your source code and feature definitions. It inspects your code's AST (Abstract Syntax Tree) to automatically generate documentation templates.

## When should I use template generation?

Use template generation when you want to automatically create help documentation from your codebase. It's particularly useful for maintaining up-to-date documentation as your code evolves.

## How do I generate templates for a feature?

Call `generate_feature_templates()` with your feature definition, help directory, and project root. This function returns a `GenerationResult` containing all the generated templates.

## What types of templates can be generated?

The system generates several template types:
- Core templates: concept, task, reference
- Problem templates: error, warning, troubleshooting, faq
- Guidance templates: quickstart, tip, note, comparison

## Can I control which templates are created?

Yes, use the `depths` parameter in `generate_feature_templates()` to specify which template types you want. If you don't specify depths, all applicable templates are generated.

## What happens if a template file already exists?

By default, existing files are not overwritten. Set `overwrite=True` to replace existing templates.

## How do I debug generation issues?

Run `pytest -k "template-generation" -v` to test the generation system. If tests pass but you're still having issues, add logging statements and check for common problems like invalid feature names or missing source files.

## Where is the generation code located?

The template generation code is in `src/attune_author/generator.py`.

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
