---
type: warning
feature: template-generation
depth: warning
generated_at: 2026-04-14T16:02:55.278438+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Template Generation cautions

## What to watch for

Template generation creates markdown help files from feature definitions and source code analysis. The process involves file system operations, hash validation, and template type selection that can fail in non-obvious ways.

## Risk areas

**Hash mismatches between runs**
The `source_hash` field tracks whether source files have changed between generation runs. If you modify source files but don't regenerate templates, you'll work with stale documentation that doesn't reflect the current codebase.

**Overwrite protection blocking updates**
By default, `generate_feature_templates()` sets `overwrite=False` to prevent accidentally destroying manual edits. This means updated source code won't refresh existing templates unless you explicitly enable overwriting or delete the old files first.

**Invalid feature names causing silent failures**
The function raises `ValueError` for invalid feature names, but the validation logic isn't exposed. Features that don't match expected naming patterns will fail generation without clear guidance on what constitutes a valid name.

**Template depth filtering**
When you specify custom `depths`, only templates matching those depth names generate. The system recognizes core depths (`concept`, `task`, `reference`) and problem types (`error`, `warning`, `troubleshooting`, `faq`), but won't warn you if your depth list excludes templates you expect.

## How to avoid problems

**Check hash consistency before editing**
Compare the `source_hash` in existing templates against current source files. If they differ, regenerate templates before making manual changes to avoid working with outdated content.

**Use overwrite mode deliberately**
When updating documentation after code changes, explicitly set `overwrite=True` and backup any manual edits first. The default protection prevents data loss but can create staleness if you're not aware of it.

**Validate feature names early**
Test feature name validity with a small generation run before processing large batches. The error message format is 'Invalid feature name: {name}' but doesn't specify what makes names valid.

**Review depth selections**
When using custom `depths` parameters, cross-reference against the constants `_CORE_DEPTH_NAMES` and problem template sets to ensure you're generating the template types you need.

## Source files

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
