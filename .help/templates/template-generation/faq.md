---
type: faq
feature: template-generation
depth: faq
generated_at: 2026-04-11T04:47:20.393796+00:00
source_hash: c984ed6eeee4ee72f8b218ec3aebe243eb03ae557e252ba48d52da016704935e
status: generated
---

# Template Generation FAQ

## What is template generation?

Template generation creates markdown help files automatically by analyzing your source code and feature definitions.

## When should I use template generation?

Use template generation when you want to create initial drafts of help documentation from your existing code. It's especially useful for generating consistent documentation structure across multiple features or when starting documentation for a new codebase.

## How do I generate templates for a feature?

Call `generate_feature_templates()` with your feature definition, help directory path, and project root. This function returns a `GenerationResult` containing all the generated template files.

## What gets generated?

Template generation creates markdown files based on your feature's structure and the source code it references. The exact templates depend on your feature configuration and the types of code elements found.

## Can I control which templates are generated?

Yes, you can specify the `depths` parameter to control which template types are generated. You can also use the `overwrite` parameter to determine whether existing files should be replaced.

## How do I debug generation issues?

Start by running `pytest -k "template-generation" -v` to check if the core functionality works. If tests pass but your generation fails, add debug logging at the point where generation stops working.

## Where is the source code?

The template generation code is in `src/attune_author/generator.py`.

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
