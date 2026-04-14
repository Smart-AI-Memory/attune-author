---
type: error
feature: staleness-and-maintenance
depth: error
generated_at: 2026-04-14T14:05:46.626630+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Staleness And Maintenance errors

Help template maintenance failures occur during staleness detection, hash computation, or automated regeneration of out-of-date templates.

## Common error signatures

- `FileNotFoundError: [Errno 2] No such file or directory` — Feature source files moved or deleted since last hash computation
- `PermissionError: [Errno 13] Permission denied` — Help directory or template files not writable during regeneration
- `ValueError: Feature 'feature-name' not found in manifest` — Requested feature missing from the feature manifest
- `OSError: [Errno 28] No space left on device` — Insufficient disk space during template regeneration
- `subprocess.CalledProcessError` — Git command failed when checking for changed files in post-commit hook

## Where errors originate

Staleness and maintenance errors typically originate from these functions:

- `compute_source_hash()` — Fails when feature source files are missing, unreadable, or when the feature definition is invalid
- `check_staleness()` — Errors during manifest loading, hash computation, or when stored hash files are corrupted
- `run_maintenance()` — Failures during staleness checking, template regeneration, or when help directory is not writable
- `get_changed_files()` — Git command failures or when not running in a Git repository
- `run_hook()` — Propagates errors from maintenance runs or when project structure is invalid

## How to diagnose

1. **Identify the operation that failed.** Check whether the error occurred during staleness detection (hash comparison), template regeneration, or Git operations. The function name in the traceback indicates which phase failed.

2. **Verify file system permissions.** If you see `PermissionError`, confirm that the help directory and its template files are writable. Maintenance operations require write access to update both templates and hash storage files.

3. **Check feature manifest integrity.** When `ValueError` mentions missing features, verify that the feature manifest file exists and contains entries for all features being processed. Stale manifest data can cause maintenance to attempt operations on non-existent features.

4. **Validate Git repository state.** For post-commit hook failures, ensure you're running in a Git repository with at least one commit. The `get_changed_files()` function requires Git history to determine which files changed.

5. **Examine hash storage consistency.** Staleness detection compares current source hashes with stored values. If stored hash files are missing or corrupted, maintenance will treat all features as stale and attempt full regeneration.

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
