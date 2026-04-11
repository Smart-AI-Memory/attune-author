---
type: task
feature: staleness-and-maintenance
depth: task
generated_at: 2026-04-11T04:53:24.836034+00:00
source_hash: ef4c74abf7547edaa6f0d693a7097d1cff76652402f49144080c3f03136dfb6e
status: generated
---

# Work with staleness and maintenance

Use staleness detection and maintenance when you need to keep help templates synchronized with their source code by detecting outdated templates and regenerating them automatically.

## Prerequisites

- Access to the project source code
- Familiarity with the files under src/attune_author/staleness.py

## Check template staleness

1. **Import the staleness module:**
   ```python
   from attune_author.staleness import check_staleness
   ```

2. **Run staleness detection:**
   Call `check_staleness()` with your manifest, help directory, and project root to get a `StalenessReport`.

3. **Review the results:**
   Check `report.stale_count()` for the number of outdated templates and `report.stale_features()` for the list of affected features.

## Run maintenance operations

1. **Import the maintenance module:**
   ```python
   from attune_author.maintenance import run_maintenance
   ```

2. **Execute maintenance:**
   Call `run_maintenance()` to check staleness and regenerate outdated templates. Use `dry_run=True` to preview changes without modifying files.

3. **Verify the results:**
   Check `result.regenerated_count()` to confirm how many templates were updated.

## Set up automatic maintenance

1. **Configure the post-commit hook:**
   Call `run_hook()` from your Git post-commit hook to automatically check and update templates after each commit.

2. **Test the hook:**
   Make a commit that changes source files and verify that the hook detects and regenerates the corresponding templates.

## Verify success

After running maintenance, confirm that:
- The staleness count decreases to zero or an expected number
- Modified templates reflect recent source code changes
- No unexpected files were regenerated in dry-run mode

## Key files

- `src/attune_author/staleness.py` — Core staleness detection logic
- `src/attune_author/maintenance.py` — Maintenance operations and Git integration
