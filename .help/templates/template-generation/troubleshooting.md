---
type: troubleshooting
feature: template-generation
depth: troubleshooting
generated_at: 2026-04-11T04:47:06.320912+00:00
source_hash: c984ed6eeee4ee72f8b218ec3aebe243eb03ae557e252ba48d52da016704935e
status: generated
---

# Troubleshoot template generation

## Before you start

Template generation creates markdown help files from feature definitions and source code AST inspection. When this process fails, you typically see missing files, malformed templates, or runtime errors during generation.

## Symptom table

| If you observe | Check |
|----------------|-------|
| `FileNotFoundError` during generation | Verify `help_dir` and `project_root` paths exist and are readable |
| Empty or malformed template output | Inspect the `GeneratedTemplate.content` field in the returned `GenerationResult` |
| Generation succeeds but files aren't written | Check if `overwrite=False` and target files already exist |
| AST parsing errors | Validate that source files contain syntactically valid Python |

## Step-by-step diagnosis

1. **Reproduce with minimal arguments.**
   Create a test case calling `generate_feature_templates()` with only the required `feature` and `help_dir` parameters. Remove optional arguments like `depths` and `overwrite` to isolate the core failure.

2. **Check the GenerationResult object.**
   Examine the returned `GenerationResult` to see which templates were created and their status. Look at individual `GeneratedTemplate` objects for specific error details.

3. **Verify file system permissions.**
   Ensure the process can read from `project_root` and write to `help_dir`. Test with a simple file write to the target directory.

4. **Enable debug logging.**
   Set your logging level to `DEBUG` before calling `generate_feature_templates()`. The generator logs template creation steps and any parsing issues.

5. **Inspect the feature definition.**
   Validate that the `Feature` object contains the expected metadata and source file references that the generator needs.

## Common fixes

- **Create missing directories.** Run `mkdir -p <help_dir>` if the target directory doesn't exist.

- **Set overwrite flag.** Add `overwrite=True` to your `generate_feature_templates()` call if you need to replace existing files.

- **Fix file permissions.** Use `chmod +r` on source files and `chmod +w` on the help directory if you see permission errors.

- **Update Python syntax.** Template generation parses source files as Python AST. Fix any syntax errors in your source code before running generation.

- **Check feature source paths.** Ensure the `Feature` object references valid, existing source files that the generator can read and parse.

## Source files

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
