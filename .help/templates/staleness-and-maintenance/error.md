---
type: error
feature: staleness-and-maintenance
depth: error
generated_at: 2026-04-14T16:10:44.579453+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Staleness and maintenance errors

Failures that occur when detecting outdated help templates or regenerating them to match current source code.

## Common error signatures

- `FileNotFoundError: [Errno 2] No such file or directory` — Missing source files during hash computation or template paths during staleness checks
- `OSError: [Errno 13] Permission denied` — Insufficient permissions to read source files or write regenerated templates
- `ValueError: Invalid feature name` — Feature not found in manifest during staleness checking
- `subprocess.CalledProcessError` — Git command failures when retrieving changed files for commit hooks
- `KeyError` — Missing hash entries in stored staleness data

## Where errors originate

Most staleness and maintenance failures occur in these key functions:

- `compute_source_hash()` — File system errors when reading source files to calculate SHA-256 hashes
- `check_staleness()` — Manifest lookup failures and hash comparison errors
- `run_maintenance()` — Template regeneration failures and file write permissions
- `get_changed_files()` — Git command execution errors in commit hook scenarios
- `run_hook()` — Post-commit hook failures when checking repository state

## How to diagnose

1. **Check file permissions and paths.** Most failures stem from missing source files or insufficient write permissions for template directories. Verify that all paths in the feature manifest exist and are readable.

2. **Examine the staleness report structure.** If `check_staleness()` fails, inspect the `FeatureStaleness` entries to identify features with missing or corrupted hash data. The `stored_hash` field will be `None` for features that have never been processed.

3. **Validate Git repository state.** For commit hook failures, ensure you're running from within a Git repository and that the most recent commit contains the expected source file changes.

4. **Test with a single feature.** Isolate the problem by running maintenance on one feature at a time using the `features` parameter. This helps distinguish between systematic issues and feature-specific problems.

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
