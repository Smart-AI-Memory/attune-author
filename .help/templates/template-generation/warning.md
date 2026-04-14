---
type: warning
feature: template-generation
depth: warning
generated_at: 2026-04-14T13:58:07.702185+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Template Generation cautions

## What to watch for

Template generation creates markdown help files from feature definitions and source code analysis. The process involves file I/O, hash validation, and template depth matching that can fail silently or produce unexpected results.

## Risk areas

**Overwriting existing templates without validation.** The `overwrite` parameter in `generate_feature_templates()` defaults to `False`, but when set to `True`, it replaces files without checking if they contain manual edits. You can lose custom content if you overwrite templates that were hand-modified after generation.

**Invalid feature names causing runtime errors.** The function raises `ValueError` with the message "Invalid feature name: {...}" when passed malformed feature identifiers. This happens during validation, not at call time, so errors can surface deep in a generation batch.

**Source hash mismatches indicating stale templates.** Each `GeneratedTemplate` includes a `source_hash` field that tracks the source files used for generation. If the hash doesn't match current source files, the template may contain outdated information, but the system won't automatically regenerate it.

**Depth filtering excluding expected templates.** When you specify a `depths` parameter, only templates matching those depth names are generated. The valid depths are defined in `_CORE_DEPTH_NAMES` and related constants, but passing an unrecognized depth silently generates no output rather than failing fast.

## How to avoid problems

**Check for existing files before enabling overwrite.** Before setting `overwrite=True`, verify that target files either don't exist or contain only generated content by checking their frontmatter status field.

**Validate feature names early.** Test feature name validity with a minimal generation call before running batch operations. The validation logic catches malformed names, but only after setup work is complete.

**Compare source hashes after generation.** After generating templates, check that the `source_hash` in the result matches your expectations. A mismatch suggests the generation used different source files than intended.

**Use explicit depth lists.** Instead of relying on defaults, explicitly specify the `depths` parameter with values from the documented constants to ensure you generate exactly the template types you need.

## Source files

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
