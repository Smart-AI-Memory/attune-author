---
type: faq
feature: template-generation
depth: faq
generated_at: 2026-04-14T16:03:24.956355+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Template Generation FAQ

## What is template generation?

Template generation creates markdown help files automatically by analyzing your source code and feature definitions.

## When should I use template generation?

Use template generation when you want to create documentation automatically instead of writing help files manually. It's especially useful for maintaining consistent documentation that stays in sync with your code.

## What's the main entry point?

Use `generate_feature_templates()` to create help templates for a specific feature. This function analyzes your source code and generates the appropriate markdown files based on what it finds.

## What types of templates can be generated?

The system can generate several template types:

- **Core templates**: concept, task, and reference pages
- **Problem-solving templates**: error, warning, troubleshooting, and FAQ pages
- **Guidance templates**: quickstart, tip, note, and comparison pages

## What information do I get back after generation?

You get a `GenerationResult` that tells you:
- Which feature was processed
- What templates were created (each with its own path and metadata)
- Which source files were analyzed
- A hash of the source content for change detection

## How do I debug generation issues?

Run the related tests first: `pytest -k "template-generation" -v`. If tests pass but your code fails, add `logger.debug` statements at suspected failure points and re-run with logging enabled.

## Can I regenerate existing templates?

By default, existing templates won't be overwritten. Set `overwrite=True` in `generate_feature_templates()` if you want to replace existing files.

## Where are the source files?

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
