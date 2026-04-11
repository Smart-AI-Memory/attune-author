---
type: troubleshooting
feature: bootstrap
depth: troubleshooting
generated_at: 2026-04-11T04:52:17.972045+00:00
source_hash: ba3e45edbaf44fba671f221a61e39cae7381b0b1c8ce9a02129f76b20bc6f331
status: generated
---

# Troubleshoot bootstrap

## Before you start

The bootstrap feature scans your project directory structure and Python package layout to propose an initial features manifest.

## Symptom table

| If you observe | Check |
|----------------|-------|
| Unexpected exception during scan | Python traceback points to the file and line causing the error |
| Empty or incomplete feature proposals | Project directory structure and whether Python packages have `__init__.py` files |
| Wrong feature types proposed | File extensions and directory names that bootstrap uses for detection |
| Manifest conversion fails | Format and content of the ProposedFeature objects returned by scan |

## Step-by-step diagnosis

1. **Reproduce the failure with a minimal project.**
   Create a simple test directory with just the structure needed to trigger the issue. Run `scan_project()` directly with this minimal setup to confirm the failure occurs without other project complexity.

2. **Verify the project path.**
   Confirm that the `project_root` parameter points to an existing directory with read permissions. Bootstrap needs to traverse the directory tree to discover features.

3. **Check what bootstrap detects.**
   Add debug prints or use a debugger to inspect the list of `ProposedFeature` objects returned by `scan_project()`. Look for missing features you expected or unexpected features that shouldn't be there.

4. **Test manifest conversion separately.**
   If scanning works but `proposals_to_manifest()` fails, test the conversion step in isolation with known good `ProposedFeature` objects to isolate whether the issue is in detection or conversion.

## Common fixes

- **Fix project structure.** Bootstrap relies on standard Python package conventions. Add missing `__init__.py` files to directories that should be packages, or move files to expected locations.

- **Check file permissions.** Ensure the bootstrap process has read access to all project directories and files:
  ```bash
  find /path/to/project -type d -not -readable
  find /path/to/project -type f -not -readable
  ```

- **Validate the project root path.** Use an absolute path or verify the current working directory:
  ```python
  from pathlib import Path
  project_path = Path("/absolute/path/to/project").resolve()
  proposals = scan_project(project_path)
  ```

- **Handle empty projects gracefully.** If your project has no detectable features yet, bootstrap should return an empty list rather than fail. Check that your code handles this case.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
