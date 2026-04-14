---
type: warning
feature: staleness-and-maintenance
depth: warning
generated_at: 2026-04-14T14:06:00.627235+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Staleness And Maintenance cautions

## What to watch for

The staleness detection system tracks when your source code changes make help templates outdated. Watch for hash mismatches that cause unnecessary regeneration and maintenance operations that skip files you expect to update.

## Risk areas

### Hash computation includes unexpected files

`compute_source_hash()` walks your entire feature directory tree, excluding common cache folders like `__pycache__` and `.git`. If your feature contains large data files, temporary outputs, or nested repositories, the hash calculation becomes slow and may include files that shouldn't trigger regeneration.

**Mitigation:** Review `matched_files` in the `FeatureStaleness` result to see which files influenced the hash. Add directories to `_EXCLUDED_DIRS` if they contain build artifacts or other non-source content.

### Maintenance operations fail silently on permission errors

`run_maintenance()` catches file system errors and adds affected features to the `failed` list without raising exceptions. A feature marked as failed won't get regenerated even if it's stale, leaving your templates outdated.

**Mitigation:** Check `MaintenanceResult.failed` after maintenance runs. Ensure your help directory is writable and that no other processes have files open during regeneration.

### Post-commit hook misses uncommitted changes

`run_hook()` uses `get_changed_files()` to identify which features need checking based on the most recent commit. If you have uncommitted changes that affect feature source files, the hook won't detect the staleness until after your next commit.

**Mitigation:** Run manual maintenance with `run_maintenance()` before committing when you're unsure about template freshness. The hook is meant for automated consistency, not comprehensive detection.

### Dry run mode conceals real file system issues

Setting `dry_run=True` in `run_maintenance()` skips the actual file writing but still performs staleness detection and hash computation. This can mask permission problems, disk space issues, or path resolution failures that would surface during actual regeneration.

**Mitigation:** Follow up dry runs with actual maintenance operations in a test environment to verify that file operations succeed.

## How to avoid problems

1. **Monitor staleness reports regularly.** Use `format_status_report()` to get human-readable summaries of which features are stale. Address staleness quickly to avoid accumulating outdated templates.

2. **Test maintenance operations in isolation.** Run `check_staleness()` independently before calling `run_maintenance()` to understand what will change. Use the `features` parameter to limit operations to specific features during testing.

3. **Validate feature manifests after changes.** Source file additions or deletions can break the feature discovery logic that maintenance depends on. Ensure your `FeatureManifest` correctly identifies all source files before running maintenance.

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
