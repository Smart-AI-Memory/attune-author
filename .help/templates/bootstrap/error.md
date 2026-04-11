---
type: error
feature: bootstrap
depth: error
generated_at: 2026-04-11T04:51:56.429823+00:00
source_hash: ba3e45edbaf44fba671f221a61e39cae7381b0b1c8ce9a02129f76b20bc6f331
status: generated
---

# Bootstrap errors

Bootstrap errors occur when project scanning fails or when converting scan results to a feature manifest goes wrong.

## Common error signatures

- `OSError` or `PermissionError` when `scan_project()` cannot read directories or files
- `ValueError` when project structure doesn't match expected Python package layout
- `TypeError` when `proposals_to_manifest()` receives invalid or malformed `ProposedFeature` objects
- `FileNotFoundError` when scanning a project root that doesn't exist

## Where errors originate

Bootstrap errors come from two main functions:

- `scan_project()` — Fails when the project root is inaccessible, has unexpected structure, or contains unreadable files
- `proposals_to_manifest()` — Fails when the list of proposals contains invalid data or cannot be converted to a valid manifest format

## How to diagnose

1. **Verify the project root path.** Check that the path passed to `scan_project()` exists and points to a valid Python project directory.

2. **Check filesystem permissions.** Ensure you have read access to the project directory and its subdirectories. Bootstrap needs to traverse the entire project structure.

3. **Examine the project layout.** Bootstrap expects standard Python package structure. Missing `__init__.py` files or non-standard directory organization may cause scanning to fail.

4. **Validate proposal objects.** If `proposals_to_manifest()` fails, inspect the `ProposedFeature` objects returned by scanning. They should have all required attributes populated correctly.

5. **Test with a minimal project.** Create a simple Python package with basic structure to isolate whether the issue is environment-specific or related to your project's layout.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
