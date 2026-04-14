---
type: troubleshooting
feature: bootstrap
depth: troubleshooting
generated_at: 2026-04-14T14:04:10.223773+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Troubleshoot bootstrap

## Before you start

The bootstrap feature scans your project directory to discover Python modules, entry points, and configuration files, then proposes features for inclusion in your manifest.

## Symptom table

| If you observe | Check |
|----------------|-------|
| `scan_project()` returns empty list | Verify the project root path exists and contains Python files |
| Missing expected features in proposals | Check if files are in skip directories (`_SKIP_DIRS`) or lack recognized patterns |
| `ProposedFeature` has wrong confidence level | Examine the detection logic for entry points (`_ENTRY_POINT_NAMES`) and config patterns (`_CONFIG_PATTERNS`) |
| `proposals_to_manifest()` fails | Validate that all `ProposedFeature` objects have required fields populated |

## Step-by-step diagnosis

1. **Verify project structure and permissions.**
   Confirm the project root path is accessible and contains the expected files:
   ```bash
   ls -la /path/to/project
   find /path/to/project -name "*.py" | head -10
   ```

2. **Check for excluded directories.**
   The scanner skips common directories like `.git`, `__pycache__`, and `node_modules`. If your features are in an excluded path, they won't be detected:
   ```python
   from attune_author.bootstrap import _SKIP_DIRS
   print(_SKIP_DIRS)
   ```

3. **Test scanning in isolation.**
   Run `scan_project()` directly to see what it discovers:
   ```python
   from attune_author.bootstrap import scan_project
   proposals = scan_project("/path/to/your/project")
   for p in proposals:
       print(f"{p.name}: {p.confidence} ({p.reason})")
   ```

4. **Examine entry point detection.**
   The scanner looks for specific filenames to identify entry points. Check if your main files match the expected patterns:
   ```python
   from attune_author.bootstrap import _ENTRY_POINT_NAMES
   print(_ENTRY_POINT_NAMES)
   ```

5. **Review configuration file detection.**
   Configuration features are identified by filename patterns. Verify your config files use recognized naming:
   ```python
   from attune_author.bootstrap import _CONFIG_PATTERNS
   print(_CONFIG_PATTERNS)
   ```

## Common fixes

- **Move files out of skip directories.** If important code is in `dist/` or `build/`, move it to `src/` or the project root.

- **Rename entry point files.** Change `run.py` to `main.py` or another recognized entry point name to improve detection confidence.

- **Add missing file extensions.** The scanner focuses on `.py` files for Python projects. Ensure your modules have the correct extension.

- **Check file permissions.** On Unix systems, ensure the scanner can read your project files:
  ```bash
  chmod -R +r /path/to/project
  ```

- **Update project structure.** If using a non-standard layout, consider reorganizing to match common Python project conventions that the scanner expects.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
