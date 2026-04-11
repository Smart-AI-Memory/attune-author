---
type: warning
feature: staleness-and-maintenance
depth: warning
generated_at: 2026-04-11T04:53:53.511494+00:00
source_hash: ef4c74abf7547edaa6f0d693a7097d1cff76652402f49144080c3f03136dfb6e
status: generated
---

# Staleness and maintenance cautions

## What to watch for

The staleness detection system tracks when help templates fall behind their source code and can automatically regenerate outdated files. Several aspects of this automation can cause unexpected behavior if you're not aware of how they work.

## Risk areas

### Hash computation misses relevant changes

`compute_source_hash()` only tracks specific file types when building the hash for staleness detection. If your feature depends on configuration files, data files, or other assets outside the standard source patterns, changes to those files won't trigger regeneration. Your templates will appear current while actually being stale.

### Selective staleness checks skip features silently

When you pass a `features` list to `check_staleness()` or `run_maintenance()`, any features not in that list are ignored completely — they don't appear in counts or reports. This can hide widespread staleness if you're only checking a subset of features during development.

### Dry-run mode doesn't validate write permissions

`run_maintenance()` with `dry_run=True` reports what would be regenerated but doesn't test whether the actual write operations would succeed. You might see a clean dry-run report, then hit permission errors or disk space issues when running the real maintenance.

### Git hook assumes clean repository state

`run_hook()` is designed for post-commit automation and expects to find changed files from the most recent commit. If you run it in a repository with uncommitted changes or in a detached HEAD state, `get_changed_files()` may return unexpected results or miss relevant changes entirely.

### Maintenance results don't distinguish failure types

`MaintenanceResult` counts successful regenerations but doesn't track which features failed to regenerate or why. A result showing `stale_count=5` and `regenerated_count=3` tells you that 2 features remain stale, but not whether they failed due to syntax errors, missing dependencies, or other issues.

## How to avoid problems

1. **Verify hash coverage for complex features.** If your feature uses non-standard file types, test that changes to those files actually trigger staleness detection. Run `check_staleness()` before and after modifying the files to confirm they're included in the hash.

2. **Use full maintenance runs for production.** When running maintenance in CI or production environments, avoid the `features` parameter unless you specifically need to limit scope. A full scan catches staleness that selective checks might miss.

3. **Test write permissions before maintenance.** In environments where disk space or permissions might be constrained, run a dry-run first, but also verify that the target directory is writable and has sufficient space for the expected regenerations.

4. **Check repository state before hook execution.** If you're calling `run_hook()` programmatically rather than from an actual Git hook, ensure you're in a clean repository state with committed changes that represent the actual modifications you want to detect.

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
