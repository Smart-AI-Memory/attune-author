---
type: troubleshooting
feature: template-generation
depth: troubleshooting
generated_at: 2026-04-14T16:03:10.346790+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Troubleshoot template generation

## Before you start

Template generation creates markdown help files by inspecting your source code and feature definitions. When it fails, the issue is usually in the source parsing, template rendering, or file system operations.

## Symptom table

| If you observe | Check |
|----------------|-------|
| `ValueError: Invalid feature name` | Feature argument matches an existing feature directory name |
| Empty `GenerationResult.templates` list | Source files exist at `project_root` and match the feature pattern |
| Templates generated but content is wrong | Source code AST structure and template variables in the Jinja2 templates |
| File permission errors during generation | Write permissions on `help_dir` and `overwrite=True` if files exist |
| Templates missing expected depth categories | `depths` parameter includes valid values from `_CORE_DEPTH_NAMES` |

## Step-by-step diagnosis

1. **Verify your inputs**
   Confirm the feature name, help directory path, and project root are correct:
   ```python
   result = generate_feature_templates(
       feature=your_feature,
       help_dir="docs/help",
       project_root=".",
       overwrite=True
   )
   print(f"Matched files: {result.matched_files}")
   ```

2. **Check file discovery**
   Examine which source files the generator found:
   ```python
   result = generate_feature_templates(feature, help_dir, project_root)
   if not result.matched_files:
       print("No source files matched the feature pattern")
   ```

3. **Enable detailed logging**
   Set logging to DEBUG level to see template processing details:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

4. **Test with minimal parameters**
   Try generation with default depths to isolate depth-specific issues:
   ```python
   result = generate_feature_templates(feature, help_dir, project_root)
   # Instead of passing custom depths parameter
   ```

## Common fixes

- **Fix feature name mismatch**: Ensure the feature name exactly matches your feature directory. Check for typos, case sensitivity, and special characters.

- **Create missing directories**: The generator requires the help directory to exist:
  ```bash
  mkdir -p docs/help
  ```

- **Set overwrite permission**: If templates already exist, use `overwrite=True`:
  ```python
  generate_feature_templates(feature, help_dir, project_root, overwrite=True)
  ```

- **Verify source file structure**: The generator expects standard Python module structure. Ensure your feature's source files are properly organized and importable.

- **Check template depth configuration**: Use only valid depth names. The available depths are `concept`, `task`, `reference`, `error`, `warning`, `troubleshooting`, `faq`, `quickstart`, `tip`, `note`, and `comparison`.

## Source files

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
