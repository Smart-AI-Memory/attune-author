---
type: task
feature: staleness-and-maintenance
depth: task
generated_at: 2026-04-14T14:05:24.056338+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Work with staleness and maintenance

Use staleness and maintenance when you need to detect outdated help templates and automatically regenerate them to stay synchronized with source code changes.

## Prerequisites

- Access to the project source code
- Familiarity with the files under `src/attune_author/staleness.py` and `src/attune_author/maintenance.py`

## Check for stale templates

1. Call `check_staleness()` with your feature manifest, help directory, and project root:

   ```python
   from attune_author.staleness import check_staleness

   report = check_staleness(manifest, "docs/help", ".")
   ```

2. Examine the `StalenessReport` to see which features are outdated:

   ```python
   print(f"Stale features: {report.stale_features}")
   print(f"Total stale: {report.stale_count}")
   ```

The report shows `True` for `is_stale` when a feature's current source hash differs from its stored hash.

## Run maintenance to regenerate templates

1. Execute `run_maintenance()` to check staleness and regenerate outdated templates:

   ```python
   from attune_author.maintenance import run_maintenance

   result = run_maintenance("docs/help", ".", features=["my-feature"])
   ```

2. Check the results to verify what was updated:

   ```python
   print(f"Regenerated: {result.regenerated_count} templates")
   print(f"Failed: {result.failed}")
   ```

3. Use `dry_run=True` to preview changes without writing files:

   ```python
   result = run_maintenance("docs/help", ".", dry_run=True)
   ```

You know maintenance succeeded when `result.failed` is empty and `regenerated_count` matches your expectations.

## Set up automatic maintenance with git hooks

1. Configure the post-commit hook to run maintenance automatically:

   ```python
   from attune_author.maintenance import run_hook

   # In your git post-commit hook
   result = run_hook("docs/help", ".")
   ```

2. The hook only processes features whose source files changed in the most recent commit.

3. Verify the hook works by making a source change and committing — check that related help templates update automatically.

## Key files

- `src/attune_author/staleness.py` — Staleness detection and hash computation
- `src/attune_author/maintenance.py` — Template regeneration and git hook logic
