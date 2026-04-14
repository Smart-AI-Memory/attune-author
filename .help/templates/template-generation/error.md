---
type: error
feature: template-generation
depth: error
generated_at: 2026-04-14T13:57:57.478670+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Template Generation errors

Template generation failures occur when the system cannot create help documentation files from feature definitions and source code analysis.

## Common error signatures

- `ValueError: Invalid feature name: {feature_name}` — The feature name passed to `generate_feature_templates()` doesn't match expected naming patterns or references a non-existent feature

## Where errors originate

Template generation errors primarily stem from the `generate_feature_templates()` function in `src/attune_author/generator.py`. This function orchestrates the entire generation process, from feature validation through template file creation.

## How to diagnose

1. **Verify the feature name.** Check that the feature parameter passed to `generate_feature_templates()` matches an actual feature in your project. Invalid feature names trigger `ValueError` exceptions immediately.

2. **Check file system permissions.** If generation fails during file writing, verify that the help directory path is writable and that no permission restrictions block template file creation.

3. **Validate source file integrity.** Generation relies on AST parsing of source files. If source files contain syntax errors or are corrupted, template generation will fail when attempting to extract metadata.

4. **Examine the overwrite setting.** When `overwrite=False` (default), generation skips existing template files. If you expect new templates but don't see them, check whether files already exist at the target paths.

5. **Inspect the depths parameter.** Template generation creates files for specific documentation depths (concept, task, reference) and problem types (error, warning, troubleshooting, faq). Invalid depth names or mismatched template types can cause generation to skip expected outputs.

## Source files

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
