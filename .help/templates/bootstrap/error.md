---
type: error
feature: bootstrap
depth: error
generated_at: 2026-04-14T16:08:43.324970+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Bootstrap errors

Project scanning and manifest generation failures that prevent automatic feature discovery during project initialization.

## Common error signatures

- `FileNotFoundError` when the project root path doesn't exist or is inaccessible
- `PermissionError` when scanning encounters directories without read permissions
- `ValueError` when proposal conversion fails due to invalid feature data
- `OSError` during filesystem operations while traversing project directories

## Where errors originate

Bootstrap failures typically start in these core functions:

- `scan_project()` — Project traversal and feature discovery errors
- `proposals_to_manifest()` — Validation and conversion errors when building the manifest

## How to diagnose

1. **Verify the project root path.** Check that the path passed to `scan_project()` exists and is readable. Bootstrap skips common directories like `.git`, `__pycache__`, and `node_modules` but requires access to the project root.

2. **Check for permission issues.** If scanning fails on specific subdirectories, ensure your process has read permissions for the entire project tree.

3. **Validate ProposedFeature data.** When `proposals_to_manifest()` fails, examine the `confidence` field values in your proposals. Invalid confidence levels or malformed feature data can cause conversion errors.

4. **Review file detection logic.** Bootstrap looks for entry points like `main.py`, `app.py`, and configuration patterns containing "config", "settings", or "conf". Missing expected files may result in empty or incomplete feature proposals.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
