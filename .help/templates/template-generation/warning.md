---
type: warning
feature: template-generation
depth: warning
generated_at: 2026-04-11T04:46:55.098991+00:00
source_hash: c984ed6eeee4ee72f8b218ec3aebe243eb03ae557e252ba48d52da016704935e
status: generated
---

# Template Generation cautions

## What to watch for

Template generation creates markdown help files by analyzing source code and feature definitions. The process involves file I/O, AST parsing, and template rendering that can fail in non-obvious ways.

## Risk areas

### File overwrite conflicts

The `overwrite` parameter in `generate_feature_templates()` defaults to `False`, which means existing template files will be preserved even if the source code has changed. This can leave you with outdated help content that doesn't match your current implementation.

### Path resolution errors

Template generation expects specific directory structures for `help_dir` and `project_root`. If these paths don't exist or point to unexpected locations, the function will fail silently or create templates in the wrong directory.

### Incomplete depth filtering

When you specify `depths` to limit which template types get generated, the function only creates templates for those depths. If you later need additional template types, you'll need to run generation again with different parameters or risk having incomplete documentation.

### AST parsing limitations

The template generator relies on static analysis of your source code. Dynamic features like monkey-patching, runtime class modifications, or code that depends on external state won't be captured accurately in the generated templates.

## How to avoid problems

1. **Set explicit overwrite behavior.** Always specify `overwrite=True` when you want templates to reflect current source code, or `overwrite=False` when you want to preserve manual edits.

2. **Verify paths before generation.** Check that your `help_dir` and `project_root` arguments point to the correct locations and have appropriate write permissions.

3. **Generate complete template sets.** Either omit the `depths` parameter to generate all template types, or explicitly list all the depths you need for comprehensive documentation.

4. **Review generated content.** Template generation is a starting point, not a final product. Always review the generated markdown to ensure it accurately represents your code's behavior.

## Source files

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
