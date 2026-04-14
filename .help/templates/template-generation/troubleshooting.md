---
type: troubleshooting
feature: template-generation
depth: troubleshooting
generated_at: 2026-04-14T13:58:21.636816+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Troubleshoot template generation

## Before you start

The template generation feature creates markdown help templates from feature definitions and source code AST inspection. When it fails, you typically see missing output files, malformed content, or ValueError exceptions.

## Symptom table

| If you observe | Check |
|----------------|-------|
| ValueError: "Invalid feature name" | Feature parameter passed to `generate_feature_templates()` |
| Empty `GenerationResult.templates` list | `matched_files` field and file discovery in project root |
| Missing template files in help directory | `overwrite` parameter and existing file conflicts |
| Incorrect `source_hash` values | Source file modification times and content changes |
| Wrong template depth generated | `depths` parameter against `_CORE_DEPTH_NAMES` constants |

## Step-by-step diagnosis

1. **Reproduce with minimal parameters.**
   Call `generate_feature_templates()` with only the required `feature`, `help_dir`, and `project_root` arguments. Remove optional `depths` and `overwrite` parameters to isolate the core failure.

2. **Verify input paths and feature names.**
   Check that `help_dir` and `project_root` exist and are readable. Confirm the feature name matches your project's feature definitions.

3. **Examine the GenerationResult fields.**
   Print the returned `GenerationResult` object to inspect:
   - `matched_files`: Shows which source files were discovered
   - `templates`: Lists successfully generated templates
   - `source_hash`: Indicates if source content was processed

4. **Enable debug logging for file operations.**
   Template generation involves file I/O and path resolution. Enable DEBUG-level logging to trace file discovery and template writing operations.

## Common fixes

- **Fix invalid feature names.** The feature parameter must match your project's defined features exactly. Check spelling and case sensitivity.

- **Set overwrite=True for existing files.** If templates already exist in the help directory, set `overwrite=True` to replace them:
  ```python
  result = generate_feature_templates(feature, help_dir, project_root, overwrite=True)
  ```

- **Verify project structure.** The function expects your project root to contain discoverable source files. Ensure your Python files are in standard locations like `src/` or at the project root.

- **Specify explicit depths.** If you need only certain template types, pass the `depths` parameter:
  ```python
  result = generate_feature_templates(feature, help_dir, project_root, depths=['concept', 'task'])
  ```

- **Check file permissions.** Ensure the help directory is writable and source files are readable by the process running template generation.

## Source files

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
