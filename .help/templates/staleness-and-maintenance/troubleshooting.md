---
type: troubleshooting
feature: staleness-and-maintenance
depth: troubleshooting
generated_at: 2026-04-14T14:06:19.355677+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Troubleshoot staleness and maintenance

## Before you start

The staleness and maintenance system detects when generated help templates are out of sync with their source files and automatically regenerates stale ones. Issues typically involve hash mismatches, file detection problems, or regeneration failures.

## Symptom table

| If you observe | Check |
|----------------|-------|
| Templates not regenerating despite source changes | Run `check_staleness()` manually and examine the `StalenessReport.stale_features` list |
| Hash mismatch errors | Compare `current_hash` vs `stored_hash` in the `FeatureStaleness` object for the affected feature |
| Files missing from staleness check | Inspect `matched_files` field to see which source files were detected |
| Post-commit hook not triggering | Verify `get_changed_files()` returns the expected file paths |
| Regeneration skipped unexpectedly | Check `MaintenanceResult.skipped_manual` for features marked as manual-only |

## Step-by-step diagnosis

1. **Reproduce with a single feature.**
   Isolate the problem by running staleness detection on one feature:
   ```python
   report = check_staleness(manifest, help_dir, project_root, features=['your-feature'])
   print(report.stale_features)
   ```

2. **Check hash computation.**
   Verify that source file hashing works correctly:
   ```python
   current_hash, matched_files = compute_source_hash(feature, project_root)
   print(f"Hash: {current_hash}")
   print(f"Files: {matched_files}")
   ```

3. **Enable detailed logging.**
   Set logging to `DEBUG` level before calling maintenance functions. The system logs file discovery, hash comparisons, and regeneration decisions.

4. **Examine maintenance results.**
   Run maintenance with dry_run enabled to see what would happen:
   ```python
   result = run_maintenance(help_dir, project_root, dry_run=True)
   print(f"Stale: {result.stale_count}")
   print(f"Failed: {result.failed}")
   ```

5. **Test the hook mechanism.**
   If using the post-commit hook, verify file change detection:
   ```python
   changed_files = get_changed_files(project_root)
   print(f"Changed files: {changed_files}")
   ```

## Common fixes

- **Clear stale hash cache.** Delete stored hash files in your help directory and re-run maintenance to force fresh hash computation.

- **Fix file permissions.** Ensure the maintenance process can read source files and write to the help directory:
  ```bash
  chmod -R u+rw /path/to/help/dir
  chmod -R u+r /path/to/source/files
  ```

- **Update excluded directories.** If source files are in non-standard locations, check that they're not being filtered out by `_EXCLUDED_DIRS` (includes `__pycache__`, `.git`, `node_modules`, etc.).

- **Verify feature manifest.** Ensure your feature is properly defined in the manifest with correct source file patterns.

- **Check Git status.** The hook relies on Git to detect changed files. Ensure you're in a Git repository and the relevant files are committed:
  ```bash
  git status
  git log --name-only -1
  ```

- **Regenerate manually.** If automatic maintenance fails, force regeneration of specific features:
  ```python
  result = run_maintenance(help_dir, project_root, features=['problematic-feature'])
  ```

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
