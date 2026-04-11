---
type: error
feature: template-generation
depth: error
generated_at: 2026-04-11T04:46:44.555477+00:00
source_hash: c984ed6eeee4ee72f8b218ec3aebe243eb03ae557e252ba48d52da016704935e
status: generated
---

# Template Generation errors

Template generation failures occur when creating help documentation templates from feature definitions and source code analysis.

## Common error signatures

- `FileNotFoundError` when source files referenced in the feature definition don't exist
- `PermissionError` when the help directory is not writable or files cannot be overwritten
- `ValueError` when feature definitions contain invalid depth specifications or malformed metadata
- `TemplateNotFound` from Jinja2 when meta-template files are missing
- `UndefinedError` from Jinja2 when template variables lack required data from AST inspection

## Where errors originate

Template generation errors start in the main generation function:

- `generate_feature_templates()` in `src/attune_author/generator.py` — Generate help templates for a feature.

This function coordinates file discovery, AST parsing, template rendering, and file writing. Failures in any of these steps bubble up as exceptions.

## How to diagnose

1. **Check file permissions and paths.** Verify that your `help_dir` is writable and that all source files in the feature definition exist at the specified paths relative to `project_root`.

2. **Validate the feature definition.** Ensure the `Feature` object has valid depth values and that referenced source files contain the expected classes and functions.

3. **Examine the generation result.** When `generate_feature_templates()` completes successfully, inspect the returned `GenerationResult` object for any `GeneratedTemplate` entries with error states.

4. **Test with `overwrite=True`.** If generation fails silently, existing template files might be blocking writes. Set the `overwrite` parameter to force file replacement.

5. **Verify meta-template availability.** Template generation relies on Jinja2 meta-templates. Check that the template loader can find the required template files for your specified depths.

## Source files

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
