---
type: error
feature: staleness-and-maintenance
depth: error
generated_at: 2026-04-11T04:53:40.048486+00:00
source_hash: ef4c74abf7547edaa6f0d693a7097d1cff76652402f49144080c3f03136dfb6e
status: generated
---

# Staleness And Maintenance errors

This page covers failures that occur when checking whether help templates are out of sync with their source code or when regenerating stale templates.

## Common error signatures

- `FileNotFoundError: [Errno 2] No such file or directory` — Missing source files during hash computation or template paths that don't exist
- `PermissionError: [Errno 13] Permission denied` — Insufficient write permissions when regenerating templates
- `ValueError: Invalid feature name` — Feature specified in staleness check doesn't exist in the manifest
- `subprocess.CalledProcessError` — Git commands fail when checking for changed files in post-commit hooks
- `JSONDecodeError` — Corrupted feature manifest prevents staleness checking

## Where errors originate

Most staleness and maintenance failures happen in these functions:

- `compute_source_hash()` — Fails when source files are missing, unreadable, or when the feature's source file list is invalid
- `check_staleness()` — Raises exceptions when the manifest is corrupted, help directory doesn't exist, or feature names are invalid
- `run_maintenance()` — Fails during template regeneration if write permissions are missing or the generation process crashes
- `get_changed_files()` — Git command failures when the working directory isn't a repository or Git isn't available
- `run_hook()` — Combines all the above failure modes when triggered by post-commit hooks

## How to diagnose

1. **Check file permissions and paths.** Most failures stem from missing source files, inaccessible help directories, or insufficient write permissions for regeneration.

2. **Verify your feature manifest.** If `check_staleness()` fails with JSON errors, inspect your feature manifest file for syntax errors or corruption.

3. **Test Git availability.** When `get_changed_files()` fails, verify that you're in a Git repository and that the `git` command is available in your PATH.

4. **Run maintenance manually first.** Before relying on post-commit hooks, test `run_maintenance()` directly to isolate hook-specific issues from core staleness detection problems.

5. **Check source file patterns.** If hash computation fails for specific features, verify that the feature's source file patterns in the manifest correctly match existing files.

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
