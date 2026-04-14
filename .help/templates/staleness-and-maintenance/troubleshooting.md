---
type: troubleshooting
feature: staleness-and-maintenance
depth: troubleshooting
generated_at: 2026-04-14T16:11:12.727240+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Troubleshoot staleness and maintenance

## Before you start

The staleness and maintenance system tracks changes to your source files and regenerates help templates when they become outdated. When this process fails, your documentation may be missing or incorrect.

## Symptom table

| If you observe | Check |
|----------------|-------|
| Templates not regenerating after code changes | Run `check_staleness()` manually and verify `is_stale` flags in the output |
| "File not found" errors during hash computation | Check that source files exist and `_EXCLUDED_DIRS` isn't filtering required files |
| Hash mismatches on identical files | Verify file encoding and line endings match between stored and computed hashes |
| Post-commit hook not running | Confirm `run_hook()` is configured in your Git hooks and the help directory path is correct |
| Regeneration succeeds but templates still show as stale | Check if `stored_hash` field is being updated after successful regeneration |

## Step-by-step diagnosis

1. **Test staleness detection in isolation.**
   Run the staleness check for a single feature to isolate the problem:
   ```python
   from attune_author.staleness import check_staleness
   report = check_staleness(manifest, help_dir, project_root, features=["your_feature"])
   print(f"Stale features: {report.stale_features}")
   ```

2. **Verify hash computation.**
   Check if source file hashing works correctly:
   ```python
   from attune_author.staleness import compute_source_hash
   hash_value, matched_files = compute_source_hash(feature, project_root)
   print(f"Hash: {hash_value}, Files: {matched_files}")
   ```

3. **Check maintenance execution.**
   Run maintenance manually to see detailed results:
   ```python
   from attune_author.maintenance import run_maintenance
   result = run_maintenance(help_dir, project_root, dry_run=True)
   print(f"Failed: {result.failed}, Skipped: {result.skipped_manual}")
   ```

4. **Inspect Git integration.**
   Test the commit hook detection:
   ```python
   from attune_author.maintenance import get_changed_files
   changed = get_changed_files(project_root)
   print(f"Changed files: {changed}")
   ```

## Common fixes

- **Fix file path issues.** Verify your project root and help directory paths are absolute and correct:
  ```bash
  python -c "from pathlib import Path; print(Path.cwd().resolve())"
  ```

- **Update stored hashes.** If hashes are persistently mismatched, delete stored hash files and regenerate:
  ```bash
  find . -name "*.hash" -delete
  python -m attune_author.maintenance --force-regenerate
  ```

- **Configure Git hooks properly.** Ensure the post-commit hook calls `run_hook()` with correct paths:
  ```bash
  echo '#!/bin/bash\npython -c "from attune_author.maintenance import run_hook; run_hook(\"/path/to/help\", \"/path/to/project\")"' > .git/hooks/post-commit
  chmod +x .git/hooks/post-commit
  ```

- **Clear excluded directories.** If source files are being ignored, check they're not in `_EXCLUDED_DIRS` (includes `__pycache__`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `node_modules`, `.git`).

- **Handle encoding issues.** Ensure consistent file encoding across environments:
  ```bash
  git config core.autocrlf false  # Prevent line ending changes
  ```

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
