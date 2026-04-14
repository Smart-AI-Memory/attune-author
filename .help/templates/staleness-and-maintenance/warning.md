---
type: warning
feature: staleness-and-maintenance
depth: warning
generated_at: 2026-04-14T16:10:57.879495+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Staleness and maintenance cautions

## What to watch for

When using the staleness detection and maintenance system, you risk inconsistent help content if templates become outdated or regeneration fails silently.

## Risk areas

### Hash mismatches during concurrent builds

The `compute_source_hash()` function scans source files to detect changes, but it can miss modifications that happen between the hash calculation and file system operations. This creates a window where staleness detection reports templates as current when they actually need regeneration.

**Mitigation:** Run maintenance operations from a single process when possible, especially in CI environments where parallel builds might modify source files.

### Silent failures in post-commit hooks

The `run_hook()` function returns `None` when no changes are detected, making it difficult to distinguish between "nothing to do" and "hook failed to run." Failed hooks leave templates stale without warning.

**Mitigation:** Check the return value explicitly and log when maintenance runs versus when it's skipped. Consider using `run_maintenance()` directly for better error visibility.

### Feature filtering inconsistencies

Both `check_staleness()` and `run_maintenance()` accept a `features` parameter to limit which templates are processed. When this list doesn't match the actual feature set, you get partial staleness reports that miss outdated templates.

**Mitigation:** Either process all features (pass `None`) or validate that your feature list matches what's actually in the manifest before filtering.

### Cache directory exclusions

The `_EXCLUDED_DIRS` constant filters out common cache directories when scanning for source files. If your project uses non-standard cache locations, those files might be included in hash calculations, causing false staleness reports.

**Mitigation:** Review the excluded directories list and ensure it covers your project's caching patterns, or add custom filtering in your maintenance workflow.

## How to avoid problems

1. **Verify staleness detection before regenerating.** Run `check_staleness()` independently to confirm which templates actually need updates before calling `run_maintenance()`.

2. **Handle maintenance failures explicitly.** Check the `failed` list in `MaintenanceResult` and treat any failures as build errors rather than warnings.

3. **Test with realistic file structures.** Create test scenarios that include nested directories, symlinks, and cache files to ensure staleness detection works correctly in your environment.

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
